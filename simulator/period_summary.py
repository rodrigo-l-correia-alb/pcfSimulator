class PeriodSummary:
    def __init__(self, cnt_requests: int,
                 cnt_percentage: float,
                 losses_percentage: float,
                 losses_volume: int
                 ):
        self.cnt_requests = cnt_requests
        self.cnt_percentage = cnt_percentage
        self.losses_percentage = losses_percentage
        self.losses_volume = losses_volume
