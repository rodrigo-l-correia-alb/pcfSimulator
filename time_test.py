from datetime import datetime, timedelta, timezone

from scipy.stats import chi2

import simulator.config as config

if __name__ == '__main__':

    now_utc = datetime.now(timezone.utc)
    current_quota = 1000  # mb
    quota_per_request = current_quota / 10
    print("Session start:", now_utc)
    print("Initial quota:", current_quota)
    print("Quota per request:", quota_per_request)

    session_duration = chi2.rvs(df=config.SESSION_DURATION_DF,
                                loc=config.SESSION_DURATION_LOC,
                                scale=config.SESSION_DURATION_SCALE)

    test_end_utc = now_utc + timedelta(seconds=session_duration)
    print("Supposed session end:", test_end_utc)

    number_of_requests = 1

    while True:
        consumption_rate = chi2.rvs(df=config.CONSUMPTION_RATE_DF,
                                    loc=config.CONSUMPTION_RATE_LOC,
                                    scale=config.CONSUMPTION_RATE_SCALE)

        request_interval = 104857600 / consumption_rate

        remaining_time = test_end_utc - now_utc
        now_utc += timedelta(seconds=request_interval)
        number_of_requests += 1

        if now_utc > test_end_utc:
            estimated_quota = (quota_per_request * remaining_time.total_seconds()) / request_interval

            current_quota -= estimated_quota
            print("Test exceeded possible duration")
            print("Giving quota:", estimated_quota)
            break

        print("Giving quota, current quota:", current_quota)
        current_quota -= quota_per_request

    print("Session Duration:", session_duration)
    print("Number of requests:", number_of_requests)
    print("Final quota:", current_quota)
