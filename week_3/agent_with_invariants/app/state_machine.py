"""
State Machine для FSM Task Mode.
Определяет допустимые переходы между состояниями.
"""

STATES = [
    "IDLE",
    "PLANNING",
    "WAITING_APPROVAL",
    "EXECUTING",
    "VALIDATING",
    "DONE",
    "PAUSED"
]

VALID_TRANSITIONS = {
    "IDLE": ["PLANNING"],
    "PLANNING": ["WAITING_APPROVAL"],
    "WAITING_APPROVAL": ["EXECUTING", "IDLE"],
    "EXECUTING": ["EXECUTING", "VALIDATING", "PAUSED"],
    "VALIDATING": ["DONE", "PLANNING"],
    "DONE": ["IDLE"],
    "PAUSED": ["EXECUTING"]
}


class StateError(Exception):
    """Ошибка при недопустимом переходе."""
    pass


def can_transition(from_state: str, to_state: str) -> bool:
    """Проверяет допустимость перехода."""
    if from_state not in VALID_TRANSITIONS:
        return False
    return to_state in VALID_TRANSITIONS[from_state]


def transition(from_state: str, to_state: str) -> str:
    """
    Выполняет переход.
    Возвращает новое состояние.
    Raises StateError при недопустимом переходе.
    """
    if not can_transition(from_state, to_state):
        raise StateError(f"Недопустимый переход: {from_state} -> {to_state}")
    return to_state
