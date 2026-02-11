from simulator.session import Session


class Phase:
    def __init__(self):
        self.sessions = []

    def __repr__(self):
        return repr(self.sessions)

    def append_session(self, session: Session):
        self.sessions.append(session)

    def get_last_session(self) -> Session | None:
        if not self.sessions:
            return None
        return self.sessions[-1]
