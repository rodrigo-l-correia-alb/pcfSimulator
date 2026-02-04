import random
from random import randint

from scipy.stats import norm

import simulator.config as config
from simulator.event import Event
from simulator.state import State
from simulator.status import Status


def get_configs():
    initial_amount_mean = config.INITIAL_AMOUNT_MEAN
    initial_amount_std = config.INITIAL_AMOUNT_STD
    min_amount_before_top_up_mean = config.MIN_AMOUNT_BEFORE_TOP_UP_MEAN
    min_amount_before_top_up_std = config.MIN_AMOUNT_BEFORE_TOP_UP_STD

    initial_amount_norm = (norm(
            loc=initial_amount_mean,
            scale=initial_amount_std)
                           .rvs()
                           )

    min_amount_before_top_up_norm = norm(loc=min_amount_before_top_up_mean, scale=min_amount_before_top_up_std).rvs()

    return initial_amount_norm, min_amount_before_top_up_norm


def get_random_top_up():
    return norm(loc=config.TOP_UP_AMOUNT_MEAN, scale=config.TOP_UP_AMOUNT_STD).rvs()


if __name__ == "__main__":
    initial_amount, min_amount_before_top_up = get_configs()

    print("Initial Amount:", initial_amount)
    print("Minimum Amount Before Top Up:", min_amount_before_top_up)

    state = State(initial_amount, config.INITIAL_THRESHOLD)
    event = Event(0, 0, 0, 0)

    for _ in range(config.NUMBER_OF_ITERATIONS):
        state.current_status = state.future_status

        number_of_requests = randint(config.MIN_REQUESTS, config.MAX_REQUESTS)

        if state.current_status is Status.CENTRAL:
            change_in_quota = random.uniform(0, state.current_quota)
            event.requests_central = number_of_requests


        else:
            change_in_quota = random.uniform(0, state.current_quota + 0.01 * state.current_quota)
            event.requests_contingency = number_of_requests

        if state.current_quota < min_amount_before_top_up:
            event.top_up = get_random_top_up()
            print("Top up is going to occur with value: ", event.top_up)

        event.reported = change_in_quota

        print("Before update: ", state)
        state.update_from_event(event)
        event.top_up = 0

        if state.current_quota < state.current_threshold:
            state.future_status = Status.CENTRAL
        else:
            state.future_status = Status.CONTINGENCY

        if state.current_status is Status.CENTRAL and state.future_status is Status.CONTINGENCY:
            # TODO: Close phase one

            print("Close phase one")

        if state.current_status is Status.CONTINGENCY and state.future_status is Status.CENTRAL:
            # TODO: Close phase two
            # TODO: Close period
            print("Close phase two")
            print("Close period")

            # TODO: threshold_delta = call_predict?

        print("After update: ", state)
    state.print_final_results()
