from simulator.period import Period


def _session_to_dict(session):
    return {
        "date": session.date,
        "duration": session.duration,
        "used": int(round(session.used)),
        "losses": int(round(session.losses)),
        "account": session.account,
        "requests": session.requests,
        "handler": session.handler.value,
    }


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
                "phase_one": [
                    _session_to_dict(s)
                    for s in phase_one_current_period.sessions
                ],
                "phase_two": [
                    _session_to_dict(s)
                    for s in phase_two_current_period.sessions
                ]
            }
        }
    }

    return report
