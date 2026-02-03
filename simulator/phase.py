from simulator.event import Event


class Phase:
    def __init__(self,
                 used: float,
                 losses: float,
                 requests: int,
                 handler: str
                 ):
        self.date = 0.0
        self.duration = 0.0
        self.used = used
        self.losses = losses
        self.account = 0.0
        self.requests = requests
        self.handler = handler

    def update_from_event(self, event: Event, losses, handler):
        self.used += event.reported
        self.requests += event.requests_contingency + event.requests_central
        self.losses += losses
        self.handler = handler
