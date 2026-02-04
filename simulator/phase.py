from simulator.event import Event


class Phase:
    def __init__(self,
                 used: float = 0.0,
                 losses: float = 0.0,
                 requests: int = 0.0,
                 handler: str = ""
                 ):
        self.date = 0.0
        self.duration = 0.0
        self.used = used
        self.losses = losses
        self.account = 0.0
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

    def update_from_event(self, event: Event, handler):
        self.used += event.reported
        self.requests += event.requests_contingency + event.requests_central
        self.losses += event.losses
        self.handler = handler
