from simulator.event import Event
from simulator.status import Status


class State:
    def __init__(self,
                 current_quota: float,
                 current_threshold: float,
                 current_status: Status,
                 total_requests_contingency: int = 0,
                 total_request_central: int = 0,
                 total_requests: int = 0,
                 total_used_quota: int = 0,
                 total_losses: int = 0):
        self.current_quota = current_quota
        self.current_threshold = current_threshold
        self.current_status = current_status
        self.total_requests_contingency = total_requests_contingency
        self.total_request_central = total_request_central
        self.total_requests = total_requests
        self.total_used_quota = total_used_quota
        self.total_losses = total_losses

    def __repr__(self):
        return (f"State: Current Quota = {self.current_quota}, "
                f"Current Threshold = {self.current_threshold}, "
                f"Current Status = {self.current_status}, "
                f"Total Requests Contingency = {self.total_requests_contingency}, "
                f"Total Requests Central = {self.total_request_central}, "
                f"Total Used Quota = {self.total_used_quota}, "
                f"Total Losses = {self.total_losses}")

    def update_from_event(self, event: Event):
        self.current_quota -= event.reported

        if self.current_quota < 0:
            self.total_losses += abs(self.current_quota)
            self.current_quota = 0

        self.current_quota += event.top_up
        self.total_used_quota += event.reported
        self.total_requests += event.requests_central + event.requests_contingency
        self.total_request_central += event.requests_central
        self.total_requests_contingency += event.requests_contingency

    def print_final_results(self):
        losses_percentage = (
            self.total_losses / self.total_used_quota
            if self.total_used_quota else 0.0
        )
        central_usage_percentage = (
            self.total_request_central / self.total_requests
            if self.total_requests else 0.0
        )
        contingency_usage_percentage = (
            self.total_requests_contingency / self.total_requests
            if self.total_requests else 0.0
        )

        rows = [
            ("Total requests", f"{self.total_requests:,}"),
            (
                "Central requests",
                f"{self.total_request_central:,} ({central_usage_percentage:.2%})",
            ),
            (
                "Contingency requests",
                f"{self.total_requests_contingency:,} ({contingency_usage_percentage:.2%})",
            ),
            ("Total used quota", f"{self.total_used_quota:,}"),
            (
                "Total losses",
                f"{self.total_losses:,} ({losses_percentage:.2%})",
            ),
        ]

        col1_width = max(len(r[0]) for r in rows)
        col2_width = max(len(r[1]) for r in rows)

        line = f"+-{'-' * col1_width}-+-{'-' * col2_width}-+"

        print("\nFinal results")
        print(line)
        print(f"| {'Metric'.ljust(col1_width)} | {'Value'.ljust(col2_width)} |")
        print(line)

        for metric, value in rows:
            print(f"| {metric.ljust(col1_width)} | {value.ljust(col2_width)} |")

        print(line)
