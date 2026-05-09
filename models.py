from dataclasses import dataclass
from typing import Dict

@dataclass
class RobotSpec:
    name: str
    hours: int
    cost: int

ROBOT_SPECS: Dict[str, RobotSpec] = {
    "Bravo": RobotSpec("Bravo", 3, 2),
    "Charlie": RobotSpec("Charlie", 5, 3),
    "Delta": RobotSpec("Delta", 8, 4)
}

@dataclass
class Inventory:
    bravo: int
    charlie: int
    delta: int

    def to_dict(self) -> Dict[str, int]:
        return {"Bravo": self.bravo, "Charlie": self.charlie, "Delta": self.delta}

@dataclass
class AllocationResult:
    bravo: int = 0
    charlie: int = 0
    delta: int = 0
    total_hours: int = 0
    total_cost: int = 0
    is_valid: bool = True
    error: str = ""
