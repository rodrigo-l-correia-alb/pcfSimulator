from datetime import datetime

from simulator.status import Status


class Session:
    def __init__(self,
                 date: datetime,
                 duration: float = 0.0,
                 used: float = 0.0,
                 losses: float = 0.0,
                 requests: int = 0.0,
                 handler: Status = Status.CENTRAL,
                 ):
        self.date = date
        self.duration = duration
        self.used = used
        self.losses = losses
        self.account = "account"
        self.requests = requests
        self.handler = handler

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        date_str = self.date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # keep only milliseconds
        return (
            f"{cls}(\n"
            f'  "date": "{date_str}",\n'
            f"  duration={self.duration:.2f},\n"
            f"  used={self.used:.2f},\n"
            f"  losses={self.losses:.2f},\n"
            f'  "account": "{self.account}",\n'
            f"  requests={self.requests},\n"
            f'  "handler": "{self.handler.value}"\n'
            f")"
        )
