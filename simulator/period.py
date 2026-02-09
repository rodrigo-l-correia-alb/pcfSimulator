from simulator.phase import Phase


class Period:
    def __init__(self,
                 phase_one: Phase = None,
                 phase_two: Phase = None
                 ):
        self.phase_one = phase_one
        self.phase_two = phase_two

    def __repr__(self) -> str:
        cls = self.__class__.__name__

        def indent(text: str, spaces: int = 2) -> str:
            pad = " " * spaces
            return "\n".join(pad + line if line else line for line in text.splitlines())

        return (
            f"{cls}(\n"
            f"  phase_one=\n{indent(repr(self.phase_one), 4)},\n"
            f"  phase_two=\n{indent(repr(self.phase_two), 4)}\n"
            f")"
        )

    def calculate_summary(self):
        cnt_requests = 0
        ctg_requests = 0

        used_volume = 0
        losses_volume = 0

        for session in self.phase_one.sessions:
            cnt_requests += session.requests
            used_volume += session.used

        for session in self.phase_two.sessions:
            ctg_requests += session.requests
            used_volume += session.used
            losses_volume += session.losses

        total_requests = cnt_requests + ctg_requests

        cnt_percentage = round(cnt_requests / total_requests * 100, 2)
        losses_percentage = round(losses_volume / used_volume * 100, 2)

        return cnt_requests, cnt_percentage, losses_percentage, losses_volume
