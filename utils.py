from typing import Dict, List
from models import Inventory, AllocationResult

def parse_inventory_input(b: int, c: int, d: int) -> Inventory:
    if b < 0 or c < 0 or d < 0:
        raise ValueError("Robot counts must be non-negative integers.")
    return Inventory(bravo=b, charlie=c, delta=d)

def parse_clients_input(raw: str) -> List[int]:
    try:
        clients = [int(x.strip()) for x in raw.replace(",", " ").split() if x.strip()]
        if not clients:
            raise ValueError
        if any(h <= 0 for h in clients):
            raise ValueError("Client work hours must be positive integers.")
        return clients
    except ValueError:
        raise ValueError("Invalid input. Please enter positive integers separated by spaces or commas.")

def calculate_max_capacity(inv: Inventory) -> int:
    return (inv.bravo * 3) + (inv.charlie * 5) + (inv.delta * 8)

def solve_allocation(requested: int, inventory: Dict[str, int], objective: str = "cost") -> AllocationResult:
    """
    Core bounded-brute-force solver. Optimized for 3 variables.
    objective: 'hours' (Level 1) or 'cost' (Levels 2-4)
    """
    # Constraint 2: Invalid Input
    if requested <= 0:
        return AllocationResult(error="Error: Work hours must be a positive integer.", is_valid=False)

    # Constraint: Zero Robots
    if sum(inventory.values()) == 0:
        return AllocationResult(error="Error: No robots available for assignment.", is_valid=False)

    # Tight bounds to keep iterations < 1000 even for large requests
    max_b = min(inventory.get("Bravo", 0), (requested // 3) + 2)
    max_c = min(inventory.get("Charlie", 0), (requested // 5) + 2)
    max_d = min(inventory.get("Delta", 0), (requested // 8) + 2)

    best = None
    best_meta = None

    for b in range(max_b + 1):
        for c in range(max_c + 1):
            for d in range(max_d + 1):
                if b == 0 and c == 0 and d == 0:
                    continue

                hrs = b * 3 + c * 5 + d * 8
                if hrs < requested:
                    continue

                cost = b * 2 + c * 3 + d * 4
                excess = hrs - requested
                unique_types = sum(1 for x in (b, c, d) if x > 0)

                cand = AllocationResult(b, c, d, hrs, cost, True)
                meta = {"excess": excess, "types": unique_types}

                if best is None:
                    best = cand
                    best_meta = meta
                    continue

                if objective == "hours":
                    # L1: Minimize excess, tie-break by maximizing category diversity
                    if excess < best_meta["excess"] or \
                       (excess == best_meta["excess"] and unique_types > best_meta["types"]):
                        best = cand
                        best_meta = meta
                else:
                    # L2/L3/L4: Minimize cost, tie-break by minimizing excess
                    if cost < best.total_cost or \
                       (cost == best.total_cost and excess < best_meta["excess"]):
                        best = cand
                        best_meta = meta

    # Constraint: Impossible Allocation (Exact Level 4 PDF string)
    if best is None:
        return AllocationResult(
            error="Error: Unable to allocate at least one robot from each category with the available inventory.",
            is_valid=False
        )
    return best

def format_allocation(res: AllocationResult) -> str:
    parts = []
    if res.bravo > 0: parts.append(f"Bravo: {res.bravo}")
    if res.charlie > 0: parts.append(f"Charlie: {res.charlie}")
    if res.delta > 0: parts.append(f"Delta: {res.delta}")
    return ", ".join(parts) if parts else "None"
