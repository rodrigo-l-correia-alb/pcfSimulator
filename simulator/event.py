class Event:
    def __init__(self,
                 requests_central: int = 0,
                 requests_contingency: int = 0,
                 reported: float = 0,
                 top_up: float = 0,
                 losses: float = 0
                 ):
        self.requests_central = requests_central
        self.requests_contingency = requests_contingency
        self.reported = reported
        self.top_up = top_up
        self.losses = losses

    def __repr__(self):
        return (f"Event(requests_central={self.requests_central}, "
                f"requestsContingency={self.requests_contingency}, "
                f"reported={self.reported}, top_up={self.top_up})")
