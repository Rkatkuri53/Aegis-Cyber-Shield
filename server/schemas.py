import time

class AegisState:
    def __init__(self):
        self.last_analysis = None
        self.diag_session_id = f"diag_{int(time.time())}"
        self.last_reset = time.time()
        self.swarm_active = False
        self.mirage_active = False
