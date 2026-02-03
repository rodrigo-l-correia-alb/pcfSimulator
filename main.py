import random
from random import randint

import yaml
from scipy.stats import norm

from simulator.event import Event
from simulator.state import State
from simulator.status import Status

number_of_iterations = 100
config_path = "simulator/config/configs.yml"


def get_configs():
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    initial_amount_mean = cfg['initial_amount']['mean']
    initial_amount_std = cfg['initial_amount']['std']
    min_amount_before_top_up_mean = cfg['min_amount_before_top_up']['mean']
    min_amount_before_top_up_std = cfg['min_amount_before_top_up']['std']
    top_up_amount_mean = cfg['top_up_amount']['mean']
    top_up_amount_std = cfg['top_up_amount']['std']

    initial_amount_norm = (norm(
            loc=initial_amount_mean,
            scale=initial_amount_std)
                           .rvs()
                           )

    min_amount_before_top_up_norm = (norm(
            loc=min_amount_before_top_up_mean,
            scale=min_amount_before_top_up_std)
                                     .rvs()
                                     )

    top_up_amount_norm = (norm(
            loc=top_up_amount_mean,
            scale=top_up_amount_std).rvs()
                          )

    return initial_amount_norm, min_amount_before_top_up_norm, top_up_amount_norm


if __name__ == "__main__":
    initial_amount, min_amount_before_top_up, top_up_amount = get_configs()

    print("Initial Amount:", initial_amount)

    state = State(initial_amount, 3221225472, Status.CENTRAL)
    event = Event(0, 0, 0, 0)

    for _ in range(number_of_iterations):
        number_of_requests = randint(1, 13)

        if state.current_status is Status.CENTRAL:
            change_in_quota = random.uniform(0, state.current_quota)
            event.requests_central = number_of_requests
        else:
            change_in_quota = random.uniform(0, state.current_quota + 0.01 * state.current_quota)
            event.requests_contingency = number_of_requests

        event.reported = change_in_quota

        if state.current_quota < min_amount_before_top_up:
            event.top_up = top_up_amount

        if state.current_quota < state.current_threshold:
            state.current_status = Status.CONTINGENCY
        else:
            state.current_status = Status.CENTRAL

        print(event)
        print("Before Update:", state)
        state.update_from_event(event)
        print("After Update:", state)

    state.print_final_results()
