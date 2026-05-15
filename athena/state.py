from enum import Enum


class AppState(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"


class GlobalState:
    def __init__(self):
        self._state = AppState.IDLE
    
    def get_state(self) -> AppState:
        return self._state
    
    def set_state(self, state: AppState):
        self._state = state


global_state = GlobalState()
