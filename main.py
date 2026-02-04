import json
import os
import random
from random import randint

from scipy.stats import norm

import simulator.config as config
from simulator.event import Event
from simulator.period import Period
from simulator.phase import Phase
from simulator.report_service import build_report
from simulator.state import State
from simulator.status import Status


def get_configs():
    initial_amount_mean = config.INITIAL_AMOUNT_MEAN
    initial_amount_std = config.INITIAL_AMOUNT_STD
    min_amount_before_top_up_mean = config.MIN_AMOUNT_BEFORE_TOP_UP_MEAN
    min_amount_before_top_up_std = config.MIN_AMOUNT_BEFORE_TOP_UP_STD

    initial_amount_norm = abs(norm(loc=initial_amount_mean, scale=initial_amount_std).rvs())

    min_amount_before_top_up_norm = abs(
            norm(loc=min_amount_before_top_up_mean, scale=min_amount_before_top_up_std).rvs())

    return initial_amount_norm, min_amount_before_top_up_norm


def get_random_top_up():
    return abs(norm(loc=config.TOP_UP_AMOUNT_MEAN, scale=config.TOP_UP_AMOUNT_STD).rvs())


if __name__ == "__main__":
    initial_amount, min_amount_before_top_up = get_configs()

    print("Initial Amount:", initial_amount)
    print("Minimum Amount Before Top Up:", 100)  # min_amount_before_top_up)
    print("Number of iterations:", config.NUMBER_OF_ITERATIONS)

    state = State(initial_amount, config.INITIAL_THRESHOLD)

    isFirstPeriod = True

    phase_one = None
    phase_two = None
    current_phase = None

    period_one = None
    period_two = None

    report_counter = 1

    for _ in range(config.NUMBER_OF_ITERATIONS):
        temp_status = state.current_status
        state.current_status = state.future_status

        event = Event()

        number_of_requests = randint(config.MIN_REQUESTS, config.MAX_REQUESTS)

        if temp_status is Status.CENTRAL and state.current_status is Status.CONTINGENCY:
            print("Current quota before closing phase one:", state.current_quota)
            phase_one = current_phase
            current_phase = None

        if temp_status is Status.CONTINGENCY and state.current_status is Status.CENTRAL:
            print("Current quota before closing phase two:", state.current_quota)
            phase_two = current_phase
            current_phase = None

            current_period = Period(phase_one, phase_two)

            if isFirstPeriod:
                period_one = current_period
                isFirstPeriod = False
            else:
                period_two = current_period
                print("First period:", period_one)
                print("Second period:", period_two)

                report = build_report(period_one, period_two)

                os.makedirs(config.REPORTS_FOLDER, exist_ok=True)
                filename = os.path.join(config.REPORTS_FOLDER, f"report_{report_counter}.json")

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json.dumps(report, indent=4))

                threshold_delta = 0  # call predict method: predict(report)
                state.current_threshold *= (1 + threshold_delta)

                print(f"Report saved to {filename}")

                report_counter += 1
                period_one = period_two

        if state.current_status is Status.CENTRAL:
            change_in_quota = random.uniform(1, state.current_quota)
            event.requests_central = number_of_requests
        else:
            change_in_quota = random.uniform(0, state.current_quota + 0.1 * state.current_quota)
            event.requests_contingency = number_of_requests

        event.reported = change_in_quota

        if state.current_quota < min_amount_before_top_up:
            event.top_up = get_random_top_up()
            print("Top up is going to occur with value: ", event.top_up)

        state.update_from_event(event)

        if current_phase is None:
            current_phase = Phase()

        current_phase.update_from_event(event, state.current_status.value)

        if state.current_quota < state.current_threshold:
            state.future_status = Status.CENTRAL
        else:
            state.future_status = Status.CONTINGENCY

    state.print_final_results()
