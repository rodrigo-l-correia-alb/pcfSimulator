from simulator.session import Session


class Phase:
    def __init__(self):
        self.sessions = []

    def __repr__(self):
        print(self.sessions)

    def append_session(self, session: Session):
        self.sessions.append(session)
