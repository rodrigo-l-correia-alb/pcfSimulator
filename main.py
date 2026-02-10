import json
import logging
import os
from datetime import datetime, timedelta, timezone

import simulator.config as config
from simulator.period import Period
from simulator.phase import Phase
from simulator.report_service import build_report
from simulator.session import Session
from simulator.state import State
from simulator.status import Status

logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)


def json_converter(o):
    if isinstance(o, datetime):
        return o.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    return str(o)


if __name__ == "__main__":
    initial_amount = config.get_initial_amount()
    min_amount_before_top_up = config.get_min_amount_before_top_up()
    start_time = datetime.now(timezone.utc)

    log.info(
            "Simulation started | initial_quota=%s min_before_topup=%s start_time=%s",
            initial_amount,
            min_amount_before_top_up,
            start_time.isoformat()
    )

    time_tracker = start_time
    status_tracker = Status.CENTRAL
    state = State(initial_amount, config.INITIAL_THRESHOLD)

    phase = Phase()
    previous_period = Period()
    current_period = Period()

    isFirstPeriod = True

    granted_quota_ctg = None
    threshold_ctg = None

    report_counter = 1
    session_counter = 1

    for _ in range(config.NUMBER_OF_SESSIONS):
        if state.current_quota < min_amount_before_top_up:
            top_up = config.get_top_up_amount()

            log.info(
                    "Top-up triggered | before=%s top_up=%s",
                    state.current_quota,
                    top_up
            )

            state.current_quota += top_up

        if state.current_quota == 0:
            time_tracker += timedelta(seconds=config.get_zero_amount_top_up_delay())
            continue

        granted_quota_ctg = state.current_quota * config.CTG_QUOTA_BLOCK_SIZE
        threshold_ctg = state.current_quota * config.CTG_THRESHOLD_PERCENTAGE

        session_duration = config.get_session_duration()
        session_end = time_tracker + timedelta(seconds=session_duration)
        duration_tracker = 0
        session = Session(date=time_tracker, duration=session_duration, handler=state.current_status)

        log.debug(
                "Session started | start=%s duration=%s status=%s quota=%s",
                time_tracker.isoformat(),
                session_duration,
                state.current_status.name,
                state.current_quota
        )

        number_of_requests = 1

        while True:
            if time_tracker >= session_end:
                break

            consumption_rate = config.get_consumption_rate()
            request_interval = config.GRANTED_STATE_UNIT / consumption_rate
            log.info("Request interval: %d", request_interval)

            remaining_time = (session_end - time_tracker).total_seconds()
            log.info("Remaining time: %d", remaining_time)
            time_tracker += timedelta(seconds=request_interval)
            number_of_requests += 1

            if state.current_status == Status.CENTRAL:
                if time_tracker > session_end:
                    time_tracker = session_end
                    estimated_quota = (config.GRANTED_QUOTA_CNT * remaining_time) / request_interval
                    if estimated_quota > state.current_quota:
                        estimated_quota = state.current_quota
                    duration_tracker += remaining_time
                    session.used += estimated_quota
                    state.current_quota -= estimated_quota

                    log.debug(
                            "Session end (CENTRAL - time exhausted) | used=%s remaining_quota=%s",
                            session.used,
                            state.current_quota
                    )
                    break

                if state.current_quota < config.GRANTED_QUOTA_CNT:
                    session.used += state.current_quota
                    state.current_quota = 0

                    log.debug(
                            "Session end (CENTRAL - quota exhausted) | used=%s",
                            session.used
                    )
                    break

                session.used += config.GRANTED_QUOTA_CNT
                state.current_quota -= config.GRANTED_QUOTA_CNT

                log.debug(
                        "Giving quota in CENTRAL | granted=%s used=%s remaining_quota=%s",
                        config.GRANTED_QUOTA_CNT,
                        session.used,
                        state.current_quota
                )
            else:
                if time_tracker > session_end:
                    time_tracker = session_end
                    duration_tracker += remaining_time
                    estimated_quota = (granted_quota_ctg * remaining_time) / request_interval
                    if estimated_quota > state.current_quota:
                        estimated_quota = state.current_quota
                    session.used += estimated_quota
                    state.current_quota -= estimated_quota

                    log.debug(
                            "Session end (CTG - time exhausted) | granted=%s used=%s remaining_quota=%s",
                            estimated_quota,
                            session.used,
                            state.current_quota
                    )
                    break

                if state.current_quota < config.CTG_MIN_QUOTA:
                    session.used += state.current_quota
                    state.current_quota = 0

                    log.debug(
                            "Session end (CTG - below min quota) | used=%s quota=%s",
                            session.used,
                            state.current_quota
                    )

                    break

                if state.current_quota < threshold_ctg:
                    log.debug(
                            "Session end (CTG - below threshold) | used=%s quota=%s threshold=%s",
                            session.used,
                            state.current_quota,
                            threshold_ctg
                    )

                    break

                amount_to_subtract = min(int(state.current_quota), int(granted_quota_ctg))
                session.used += amount_to_subtract
                state.current_quota -= amount_to_subtract

                log.debug(
                        "Giving quota in CONTINGENCY | granted=%s used=%s remaining_quota=%s",
                        granted_quota_ctg,
                        session.used,
                        state.current_quota
                )

                granted_quota_ctg = state.current_quota * config.CTG_QUOTA_BLOCK_SIZE

        session.requests = number_of_requests

        if session.used < 0:
            log.error("NEGATIVE DETECTED: session.used=%s | state.quota=%s", session.used, state.current_quota)
            log.error("Session: %s", session)

        if session.used != 0:
            state.update_from_session(session)
            phase.append_session(session)

        log.info(
                "Session closed | start=%s duration=%s status=%s requests=%s used=%s quota_after=%s",
                session.date.isoformat(),
                session.duration,
                session.handler.name,
                session.requests,
                session.used,
                state.current_quota
        )

        status_tracker = state.current_status

        if 0 < state.current_quota < state.current_threshold:
            state.current_status = Status.CENTRAL
        else:
            state.current_status = Status.CONTINGENCY

        if status_tracker != state.current_status:
            log.info(
                    "Status change | %s -> %s | quota=%s threshold=%s",
                    status_tracker.name,
                    state.current_status.name,
                    state.current_quota,
                    state.current_threshold
            )

        if status_tracker == Status.CENTRAL and state.current_status == Status.CONTINGENCY:
            current_period.phase_one = phase
            phase = Phase()

            log.info(
                    "Phase one closed | sessions=%s",
                    len(current_period.phase_one.sessions)
            )

        if status_tracker == Status.CONTINGENCY and state.current_status == Status.CENTRAL:
            current_period.phase_two = phase
            phase = Phase()

            log.info(
                    "Phase two closed | sessions=%s",
                    len(current_period.phase_two.sessions)
            )

            if isFirstPeriod:
                previous_period = current_period
                current_period = Period()
                isFirstPeriod = False
            else:
                report = build_report(previous_period, current_period)

                log.info("Period closed -> generating report %s", report_counter)

                os.makedirs(config.REPORTS_FOLDER, exist_ok=True)
                filename = os.path.join(config.REPORTS_FOLDER, f"report_{report_counter}.json")

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json.dumps(report, indent=4, default=json_converter))

                log.info(f"Report saved to %s", filename)
                report_counter += 1

                previous_period = current_period
                current_period = Period()

    log.info("Simulation finished")
    log.info("Report counter: %s", report_counter)
    state.log_final_results(log)
