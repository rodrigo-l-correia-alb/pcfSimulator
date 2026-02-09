from datetime import datetime, timedelta, timezone

import simulator.config as config
from simulator.period import Period
from simulator.phase import Phase
from simulator.session import Session
from simulator.state import State
from simulator.status import Status


def finish_session(phase: Phase, session: Session):
    phase.append_session(session)


# def finish_period(period: Period, phase_one: Phase, phase_two: Phase):


if __name__ == "__main__":
    initial_amount = config.get_initial_amount()
    min_amount_before_top_up = config.get_min_amount_before_top_up()
    start_time = datetime.now(timezone.utc)
    time_tracker = start_time

    state = State(initial_amount, config.INITIAL_THRESHOLD)

    phase_one = Phase()
    phase_two = Phase()

    granted_quota_ctg = None
    threshold_ctg = None

    for _ in range(config.NUMBER_OF_SESSIONS):
        session_duration = config.get_session_duration()
        session = Session(date=time_tracker, duration=session_duration)

        session_end = time_tracker + timedelta(seconds=session_duration)

        if state.current_quota < state.current_threshold:
            state.current_status = Status.CENTRAL
            session.handler = Status.CENTRAL.value
        else:
            state.current_status = Status.CONTINGENCY
            session.handler = Status.CONTINGENCY.value
            granted_quota_ctg = state.current_quota * config.CTG_QUOTA_BLOCK_SIZE
            threshold_ctg = state.current_quota * config.CTG_THRESHOLD_PERCENTAGE

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

                    session.used += estimated_quota
                    state.current_quota -= estimated_quota

                if state.current_quota < config.GRANTED_QUOTA_CNT:
                    finish_session(phase_one, session)
                    break
            else:
                if state.current_quota < config.CTG_MIN_QUOTA:
                    session.used += state.current_quota
                    state.current_quota = 0

                if state.current_quota < threshold_ctg:
                    finish_session(phase_two, session)
                    break

    print(state)

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
