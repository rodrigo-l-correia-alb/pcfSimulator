import json


def build_report(data):
    report = {
        "risk": 0.5,
        "observation": {
            "previous_period_summary": {
                "cnt_requests": 0.0,
                "cnt_percentage": 0.0,
                "losses_percentage": 0.0,
                "losses_volume": 0.0
            },
            "current_period": {
                "phase_one": [{
                    "date": 0.0,
                    "duration": 0.0,
                    "used": 0.0,
                    "losses": 0.0,
                    "account": 0.0,
                    "requests": 0.0,
                    "handler": "CNT"
                }],
                "phase_two": [{
                    "date": 0.0,
                    "duration": 0.0,
                    "used": 0.0,
                    "losses": 0.0,
                    "account": 0.0,
                    "requests": 0.0,
                    "handler": "CTG"
                }]
            }
        }
    }
    return json.dumps(report, indent=4)
