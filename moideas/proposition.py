from typing import NamedTuple
from enum import Enum, auto

class Proposition(Enum):
    P = auto()
    Q = auto()

class Signal(NamedTuple):
    proposition: Proposition

    @property
    def truth_value(self) -> bool:
        if self.proposition == Proposition.P:
            return True
        return False