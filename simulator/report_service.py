from simulator.period import Period


def build_report(previous_period: Period,
                 current_period: Period
                 ):
    (previous_period_cnt_requests,
     previous_period_cnt_percentage,
     previous_period_losses_percentage,
     previous_period_losses_volume) = previous_period.calculate_summary()

    phase_one_current_period = current_period.phase_one
    phase_two_current_period = current_period.phase_two

    report = {
        "risk": 0.5,
        "observation": {
            "previous_period_summary": {
                "cnt_requests": previous_period_cnt_requests,
                "cnt_percentage": previous_period_cnt_percentage,
                "losses_percentage": previous_period_losses_percentage,
                "losses_volume": int(round(previous_period_losses_volume))
            },
            "current_period": {
                "phase_one": [{
                    "date": phase_one_current_period.date,
                    "duration": phase_one_current_period.duration,
                    "used": int(round(phase_one_current_period.used)),
                    "losses": int(round(phase_one_current_period.losses)),
                    "account": phase_one_current_period.account,
                    "requests": phase_one_current_period.requests,
                    "handler": phase_one_current_period.handler,
                }],
                "phase_two": [{
                    "date": phase_two_current_period.date,
                    "duration": phase_two_current_period.duration,
                    "used": int(round(phase_two_current_period.used)),
                    "losses": int(round(phase_two_current_period.losses)),
                    "account": phase_two_current_period.account,
                    "requests": phase_two_current_period.requests,
                    "handler": phase_two_current_period.handler,
                }]
            }
        }
    }

    return report
