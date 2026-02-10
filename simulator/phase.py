from simulator.session import Session


class Phase:
    def __init__(self):
        self.sessions = []

    def __repr__(self):
        return self.sessions

    def append_session(self, session: Session):
        self.sessions.append(session)
