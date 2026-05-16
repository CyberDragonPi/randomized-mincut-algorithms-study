from dataclasses import dataclass, field

@dataclass
class VisitedMonitor:
    V: int
    visited: list[int] = field(init=False)

    def __post_init__(self):
        self.visited = [0] * self.V