from simulator.phase import Phase


class Period:
    def __init__(self,
                 phase_one: Phase,
                 phase_two: Phase
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
        cnt_requests = self.phase_one.requests
        total_requests = self.phase_two.requests + self.phase_two.requests

        cnt_percentage = round(cnt_requests / total_requests * 100, 2)

        losses_volume = self.phase_two.losses
        used_volume = self.phase_one.used + self.phase_two.used

        losses_percentage = round(losses_volume / used_volume * 100, 2)

        return cnt_requests, cnt_percentage, losses_percentage, losses_volume
