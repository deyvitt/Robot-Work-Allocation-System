# ~/RobotWorkAllocationSystem/models.py

"""
Data models for the Robot Work Allocation System.

Defines core data structures used throughout the application.
All models use Python dataclasses for immutability, type safety, and clean repr().
"""

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class RobotSpec:
    """Specification for a robot type: name, hours provided, and daily cost."""
    name: str
    hours: int
    cost: int

# ✅ Module-level dictionary (correct usage)
ROBOT_SPECS: Dict[str, RobotSpec] = {
    "Bravo": RobotSpec("Bravo", 3, 2),
    "Charlie": RobotSpec("Charlie", 5, 3),
    "Delta": RobotSpec("Delta", 8, 4)
}

@dataclass(frozen=True)
class Inventory:
    """
    Represents the available count of each robot type in the active fleet.
    
    Attributes:
        bravo: Count of Bravo robots (3 hours, $2/day)
        charlie: Count of Charlie robots (5 hours, $3/day)
        delta: Count of Delta robots (8 hours, $4/day)
    """
    bravo: int
    charlie: int
    delta: int

    def __post_init__(self) -> None:
        """Validate that all robot counts are non-negative."""
        if self.bravo < 0 or self.charlie < 0 or self.delta < 0:
            raise ValueError("Robot counts must be non-negative integers.")

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary with capitalised keys for solver compatibility."""
        return {"Bravo": self.bravo, "Charlie": self.charlie, "Delta": self.delta}

    def total_capacity(self) -> int:
        """Calculate maximum work hours this inventory can provide."""
        return self.bravo * 3 + self.charlie * 5 + self.delta * 8

    def __repr__(self) -> str:
        return f"Inventory(B:{self.bravo}, C:{self.charlie}, D:{self.delta})"


@dataclass
class AllocationResult:
    """
    Result of an allocation attempt, whether successful or not.
    
    Attributes:
        bravo/charlie/delta: Number of each robot type assigned
        total_hours: Sum of hours provided by assigned robots
        total_cost: Total daily charging cost for assigned robots
        is_valid: False if allocation failed due to constraints
        error: Human-readable error message (PDF-compliant) when is_valid is False
    """
    bravo: int = 0
    charlie: int = 0
    delta: int = 0
    total_hours: int = 0
    total_cost: float = 0.0
    is_valid: bool = True
    error: Optional[str] = None

    def __post_init__(self) -> None:
        """Normalise error field and validate numeric fields."""
        if self.error == "":
            self.error = None
        if self.is_valid:
            if any(v < 0 for v in [self.bravo, self.charlie, self.delta, self.total_hours, self.total_cost]):
                raise ValueError("AllocationResult numeric fields must be non-negative when valid.")

    def __repr__(self) -> str:
        status = "valid" if self.is_valid else f"invalid: {self.error}"
        return (f"AllocationResult(B:{self.bravo}, C:{self.charlie}, D:{self.delta}, "
                f"hrs:{self.total_hours}, cost:${self.total_cost:.2f}, {status})")
