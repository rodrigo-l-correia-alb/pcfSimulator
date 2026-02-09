from datetime import datetime


class Session:
    def __init__(self,
                 date: datetime,
                 duration: float,
                 used: float = 0.0,
                 losses: float = 0.0,
                 requests: int = 0.0,
                 handler: str = ""
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
        return (
            f"{cls}(\n"
            f"  date={self.date:.2f},\n"
            f"  duration={self.duration:.2f},\n"
            f"  used={self.used:.2f},\n"
            f"  losses={self.losses:.2f},\n"
            f"  account={self.account:.2f},\n"
            f"  requests={self.requests},\n"
            f"  handler='{self.handler}'\n"
            f")"
        )
