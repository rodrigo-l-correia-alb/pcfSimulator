from simulator.phase import Phase


class Period:
    def __init__(self,
                 phase_one: Phase,
                 phase_two: Phase
                 ):
        self.phase_one = phase_one
        self.phase_two = phase_two

    def calculate_summary(self):
        cnt_requests = self.phase_one.requests
        total_requests = self.phase_two.requests + self.phase_two.requests

        cnt_percentage = round(cnt_requests / total_requests * 100, 2)

        losses_volume = self.phase_two.losses
        used_volume = self.phase_one.used + self.phase_two.used

        losses_percentage = round(losses_volume / used_volume * 100, 2)

        return cnt_requests, cnt_percentage, losses_percentage, losses_volume
