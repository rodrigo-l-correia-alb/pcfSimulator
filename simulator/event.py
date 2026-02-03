class Event:
    def __init__(self,
                 requests_central: int,
                 requests_contingency: int,
                 reported: float,
                 top_up: float
                 ):
        self.requests_central = requests_central
        self.requests_contingency = requests_contingency
        self.reported = reported
        self.top_up = top_up

    def __repr__(self):
        return (f"Event(requests_central={self.requests_central}, "
                f"requestsContingency={self.requests_contingency}, "
                f"reported={self.reported}, top_up={self.top_up})")
