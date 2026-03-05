# backend/state.py — Shared in-memory state between pipeline thread and API
import time

class AppState:
    def __init__(self):
        self.alerts          = []          # all alerts fired this session
        self.current_tracks  = []          # live tracks right now
        self.latest_frame    = None        # latest annotated JPEG bytes
        self.is_running      = False       # pipeline running?
        self.uptime_start    = time.time()
        self.total_frames    = 0
        self.persons_now     = 0

# Single shared instance imported everywhere
state = AppState()