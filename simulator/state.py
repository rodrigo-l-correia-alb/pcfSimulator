from simulator.session import Session
from simulator.status import Status


class State:
    def __init__(self,
                 current_quota: float,
                 current_threshold: float,
                 current_status: Status = Status.CENTRAL,
                 total_requests_contingency: int = 0,
                 total_request_central: int = 0,
                 total_requests: int = 0,
                 total_used_quota: float = 0,
                 total_losses: float = 0
                 ):
        self.current_quota = current_quota
        self.current_threshold = current_threshold
        self.current_status = current_status
        self.total_requests_contingency = total_requests_contingency
        self.total_request_central = total_request_central
        self.total_requests = total_requests
        self.total_used_quota = total_used_quota
        self.total_losses = total_losses

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return (
            f"{cls}(\n"
            f"  current_quota={self.current_quota:.2f},\n"
            f"  current_threshold={self.current_threshold:.2f},\n"
            f"  current_status={self.current_status.name},\n"
            f"  total_requests_contingency={self.total_requests_contingency},\n"
            f"  total_request_central={self.total_request_central},\n"
            f"  total_requests={self.total_requests},\n"
            f"  total_used_quota={self.total_used_quota:.2f},\n"
            f"  total_losses={self.total_losses:.2f}\n"
            f")"
        )

    def update_from_session(self, session: Session):
        if self.current_quota < 0 and self.current_status is Status.CONTINGENCY:
            self.total_losses += abs(self.current_quota)
            session.losses = abs(self.current_quota)
            self.current_quota = 0

        self.total_used_quota += session.used
        self.total_requests += session.requests

        if session.handler == Status.CENTRAL:
            self.total_request_central += session.requests
        else:
            self.total_requests_contingency += session.requests

    def log_final_results(self, log):
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
            ("Total used quota", f"{int(self.total_used_quota):,}"),
            (
                "Total losses",
                f"{int(self.total_losses):,} ({losses_percentage:.2%})",
            ),
        ]

        col1_width = max(len(r[0]) for r in rows)
        col2_width = max(len(r[1]) for r in rows)

        line = f"+-{'-' * col1_width}-+-{'-' * col2_width}-+"

        lines = []
        lines.append("")
        lines.append("Final results")
        lines.append(line)
        lines.append(f"| {'Metric'.ljust(col1_width)} | {'Value'.ljust(col2_width)} |")
        lines.append(line)

        for metric, value in rows:
            lines.append(f"| {metric.ljust(col1_width)} | {value.ljust(col2_width)} |")

        lines.append(line)

        log.info("\n".join(lines))
