# ~/RobotWorkAllocationSystem/utils.py

"""
Utility functions for the Robot Work Allocation System.

This module provides:
- Input parsing and validation helpers
- Core bounded brute-force allocation solver
- Formatting and capacity calculation utilities

All functions use British English spellings in documentation and user-facing strings.
The solver is optimised for three robot types and guarantees termination within
~1000 iterations for typical inputs.

Public API:
    parse_inventory_input, parse_clients_input, calculate_max_capacity,
    solve_allocation, format_allocation
"""

import logging
from typing import Dict, List, Optional
from models import Inventory, AllocationResult, ROBOT_SPECS

logger = logging.getLogger(__name__)

# Explicit public API definition
__all__ = [
    "parse_inventory_input",
    "parse_clients_input",
    "calculate_max_capacity",
    "solve_allocation",
    "format_allocation",
]

def parse_inventory_input(b: int, c: int, d: int) -> Inventory:
    """
    Parse and validate robot count inputs.
    Args:
        b: Bravo robot count (must be ≥ 0)
        c: Charlie robot count (must be ≥ 0)
        d: Delta robot count (must be ≥ 0)
    Returns:
        Inventory instance with validated counts
    Raises:
        ValueError: If any count is negative
    Example:
        >>> parse_inventory_input(2, 3, 1)
        Inventory(bravo=2, charlie=3, delta=1)
    """
    if b < 0 or c < 0 or d < 0:
        raise ValueError("Robot counts must be non-negative integers.")
    return Inventory(bravo=b, charlie=c, delta=d)


def parse_clients_input(raw: str) -> List[int]:
    """
    Parse client work hours from a delimited string.
    Accepts comma-separated, space-separated, or mixed delimiters.
    Strips whitespace and filters empty tokens.
    Args:
        raw: Input string (e.g. "12, 16, 17" or "20 15 10")
    Returns:
        List of positive integers representing client requests
    Raises:
        ValueError: If input is empty, contains non-numeric values,
                   or includes non-positive integers. Message matches
                   Everest Engineering specification exactly.
    Example:
        >>> parse_clients_input("12, 16, 17")
        [12, 16, 17]
        >>> parse_clients_input("20 15")
        [20, 15]
    """
    try:
        # Normalize commas AND semicolons to spaces, then split on whitespace
        clients = [int(x.strip()) for x in raw.replace(",", " ").replace(";", " ").split() if x.strip()]
        if not clients:
            raise ValueError("Empty input")
        if any(h <= 0 for h in clients):
            raise ValueError("Non-positive value")
        logger.debug("Parsed client requests: %s", clients)
        return clients
    except ValueError as original_exc:
        # Preserve context while returning spec-compliant message
        logger.warning("Client input parsing failed: %s", original_exc)
        raise ValueError(
            "Invalid input. Please enter positive integers separated by spaces, commas or semicolons."
        ) from original_exc


def calculate_max_capacity(inv: Inventory) -> int:
    """
    Calculate maximum work hours the active fleet can provide.
    Uses robot specifications from models.ROBOT_SPECS for maintainability.
    Args:
        inv: Inventory instance with available robot counts
    Returns:
        Total hours achievable if all robots are deployed
    Example:
        >>> inv = Inventory(bravo=1, charlie=1, delta=1)
        >>> calculate_max_capacity(inv)
        16  # 1×3 + 1×5 + 1×8
    """
    return (
        inv.bravo * ROBOT_SPECS["Bravo"].hours
        + inv.charlie * ROBOT_SPECS["Charlie"].hours
        + inv.delta * ROBOT_SPECS["Delta"].hours
    )


def solve_allocation(
    requested: int,
    inventory: Dict[str, int],
    objective: str = "cost",
) -> AllocationResult:
    """
    Core bounded brute-force allocation solver.

    Searches the solution space of (Bravo, Charlie, Delta) combinations
    to find an assignment that meets the requested hours while optimising
    for the specified objective.

    Time complexity: O(B × C × D) where bounds are capped at
    (requested // hours_per_robot) + 2, keeping iterations < 1000
    for typical inputs.

    Args:
        requested: Total work hours required (must be > 0)
        inventory: Available robot counts {"Bravo": int, "Charlie": int, "Delta": int}
        objective: "hours" to minimise excess (Level 1) or "cost" to minimise charging fees (Levels 2-4)
    Returns:
        AllocationResult with:
            - Robot counts if successful (is_valid=True)
            - PDF-compliant error message if impossible (is_valid=False)
    Raises:
        ValueError: If objective is not "hours" or "cost"

    Note:
        Returns error states instead of raising exceptions to allow
        callers to handle allocation failures gracefully in both CLI
        and web contexts.
    """
    # Validate objective parameter early
    if objective not in {"hours", "cost"}:
        raise ValueError(f"Unknown objective: '{objective}'. Must be 'hours' or 'cost'.")

    logger.debug(
        "Solving allocation: requested=%dh, objective=%s, inventory=%s",
        requested, objective, inventory
    )

    # Constraint 2: Invalid Input (exact PDF error string)
    if requested <= 0:
        logger.warning("Invalid request: hours=%d (must be positive)", requested)
        return AllocationResult(
            error="Error: Work hours must be a positive integer.", is_valid=False
        )

    # Constraint: Zero Robots (exact PDF error string)
    if sum(inventory.values()) == 0:
        logger.warning("Allocation failed: no robots available")
        return AllocationResult(
            error="Error: No robots available for assignment.", is_valid=False
        )

    # Extract robot specs from single source of truth (models.py)
    specs = {
        name: {"hours": spec.hours, "cost": spec.cost}
        for name, spec in ROBOT_SPECS.items()
    }

    # Tight bounds to keep iterations < 1000 even for large requests
    max_b = min(inventory.get("Bravo", 0), (requested // specs["Bravo"]["hours"]) + 2)
    max_c = min(inventory.get("Charlie", 0), (requested // specs["Charlie"]["hours"]) + 2)
    max_d = min(inventory.get("Delta", 0), (requested // specs["Delta"]["hours"]) + 2)

    logger.debug(
        "Solver bounds: B[0..%d], C[0..%d], D[0..%d]", max_b, max_c, max_d
    )

    best: Optional[AllocationResult] = None
    best_meta: Optional[Dict[str, int]] = None
    iterations = 0

    for b in range(max_b + 1):
        for c in range(max_c + 1):
            for d in range(max_d + 1):
                iterations += 1
                if b == 0 and c == 0 and d == 0:
                    continue

                hrs = (
                    b * specs["Bravo"]["hours"]
                    + c * specs["Charlie"]["hours"]
                    + d * specs["Delta"]["hours"]
                )
                if hrs < requested:
                    continue

                cost = (
                    b * specs["Bravo"]["cost"]
                    + c * specs["Charlie"]["cost"]
                    + d * specs["Delta"]["cost"]
                )
                excess = hrs - requested
                unique_types = sum(1 for x in (b, c, d) if x > 0)

                cand = AllocationResult(
                    bravo=b, charlie=c, delta=d,
                    total_hours=hrs, total_cost=cost, is_valid=True
                )
                meta = {"excess": excess, "types": unique_types}

                if best is None:
                    best = cand
                    best_meta = meta
                    logger.debug(
                        "Initial candidate: B=%d,C=%d,D=%d, hrs=%d, cost=$%.2f, excess=%d",
                        b, c, d, hrs, cost, excess
                    )
                    continue

                if objective == "hours":
                    # L1: Minimise excess, tie-break by maximising category diversity
                    if (
                        excess < best_meta["excess"]
                        or (excess == best_meta["excess"] and unique_types > best_meta["types"])
                    ):
                        logger.debug(
                            "L1 tie-break: new candidate better (excess %d→%d, types %d→%d)",
                            best_meta["excess"], excess, best_meta["types"], unique_types
                        )
                        best = cand
                        best_meta = meta
                else:
                    # L2/L3/L4: Minimise cost, tie-break by minimising excess
                    if (
                        cost < best.total_cost
                        or (cost == best.total_cost and excess < best_meta["excess"])
                    ):
                        logger.debug(
                            "L2+ tie-break: new candidate better (cost $%.2f→$%.2f, excess %d→%d)",
                            best.total_cost, cost, best_meta["excess"], excess
                        )
                        best = cand
                        best_meta = meta

    logger.debug("Solver completed: %d iterations evaluated", iterations)

    # Constraint: Impossible Allocation (exact Level 4 PDF string)
    if best is None:
        logger.warning(
            "No valid allocation found for %dh with inventory %s",
            requested, inventory
        )
        return AllocationResult(
            error="Error: Unable to allocate at least one robot from each category with the available inventory.",
            is_valid=False,
        )

    logger.info(
        "Allocation successful: B=%d,C=%d,D=%d, hrs=%d, cost=$%.2f",
        best.bravo, best.charlie, best.delta,
        best.total_hours, best.total_cost
    )
    return best


def format_allocation(res: AllocationResult) -> str:
    """
    Format an AllocationResult as a human-readable string.
    Omits robot types with zero count. Returns "None" if no robots assigned.
    Args:
        res: AllocationResult instance (valid or invalid)
    Returns:
        Comma-separated string like "Bravo: 2, Delta: 1" or "None"
    Example:
        >>> res = AllocationResult(bravo=2, charlie=0, delta=1)
        >>> format_allocation(res)
        'Bravo: 2, Delta: 1'
    """
    if not res.is_valid:
        return ""
    parts = []
    if res.bravo > 0:
        parts.append(f"Bravo: {res.bravo}")
    if res.charlie > 0:
        parts.append(f"Charlie: {res.charlie}")
    if res.delta > 0:
        parts.append(f"Delta: {res.delta}")
    return ", ".join(parts) if parts else "None"
