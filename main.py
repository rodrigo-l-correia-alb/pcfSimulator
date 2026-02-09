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
        level=logging.INFO,
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

    for _ in range(config.NUMBER_OF_SESSIONS):
        if state.current_quota < min_amount_before_top_up:
            top_up = config.get_top_up_amount()

            log.info(
                    "Top-up triggered | before=%s top_up=%s",
                    state.current_quota,
                    top_up
            )

            state.current_quota += top_up

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
            consumption_rate = config.get_consumption_rate()
            request_interval = config.GRANTED_STATE_UNIT / consumption_rate

            remaining_time = session_end - time_tracker
            time_tracker += timedelta(seconds=request_interval)

            number_of_requests += 1

            if state.current_status == Status.CENTRAL:
                if time_tracker > session_end:
                    time_tracker = session_end
                    estimated_quota = (config.GRANTED_QUOTA_CNT * remaining_time.total_seconds()) / request_interval
                    duration_tracker += remaining_time.total_seconds()
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
            else:
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

                session.used += granted_quota_ctg
                state.current_quota -= granted_quota_ctg
                granted_quota_ctg = state.current_quota * config.CTG_QUOTA_BLOCK_SIZE

        session.requests = number_of_requests
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

                print(f"Report saved to {filename}")
                report_counter += 1

                previous_period = current_period
                current_period = Period()

    log.info("Simulation finished")
    state.print_final_results()

    # isFirstPeriod = True
    #
    # phase_one = None
    # phase_two = None
    # current_phase = None
    #
    # period_one = None
    # period_two = None
    #
    # report_counter = 1
    #
    # for _ in range(config.NUMBER_OF_ITERATIONS):
    #     temp_status = state.current_status
    #     state.current_status = state.future_status
    #
    #     event = Event()
    #
    #     if temp_status is Status.CENTRAL and state.current_status is Status.CONTINGENCY:
    #         print("Phase one closed:", current_phase)
    #         phase_one = current_phase
    #         current_phase = None
    #
    #     if temp_status is Status.CONTINGENCY and state.current_status is Status.CENTRAL:
    #         print("Phase two closed:", current_phase)
    #         phase_two = current_phase
    #         current_phase = None
    #
    #         current_period = Period(phase_one, phase_two)
    #
    #         if isFirstPeriod:
    #             period_one = current_period
    #             isFirstPeriod = False
    #         else:
    #             period_two = current_period
    #             print("First period:", period_one)
    #             print("Second period:", period_two)
    #
    #             report = build_report(period_one, period_two)
    #
    #             os.makedirs(config.REPORTS_FOLDER, exist_ok=True)
    #             filename = os.path.join(config.REPORTS_FOLDER, f"report_{report_counter}.json")
    #
    #             with open(filename, "w", encoding="utf-8") as f:
    #                 f.write(json.dumps(report, indent=4))
    #
    #             # response = requests.post(config.URL, json=report)
    #             # threshold_delta = response.json().get("action")
    #             # print(threshold_delta)
    #             # state.current_threshold *= (1 + threshold_delta)
    #
    #             print(f"Report saved to {filename}")
    #
    #             report_counter += 1
    #             period_one = period_two
    #
    #     if state.current_status == Status.CENTRAL:
    #         number_of_requests = 0
    #         while True:
    #
    #
    #             if state.current_quota < min_amount_before_top_up:
    #                 event.top_up = config.get_top_up_amount()
    #                 state.current_quota += event.top_up
    #
    #             number_of_requests += 1
    #     else:
    #         change_in_quota = random.uniform(0, state.current_quota + 0.1 * state.current_quota)
    #         event.requests_contingency = number_of_requests
    #         event.requests_central = 0
    #
    #     event.reported = change_in_quota
    #
    #     if event.reported == 0:
    #         continue
    #
    #     state.update_from_event(event)
    #
    #     if current_phase is None:
    #         current_phase = Phase()
    #
    #     current_phase.update_from_event(event, state.current_status.value)
    #
    #     if state.current_quota < state.current_threshold:
    #         state.future_status = Status.CENTRAL
    #     else:
    #         state.future_status = Status.CONTINGENCY
    #
    # state.print_final_results()
