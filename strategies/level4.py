# ~/RobotWorkAllocationSystem/strategies/level4.py

"""Level 4: Multi-Client Allocation Strategy"""
import logging
from typing import List, Dict, Any
from models import Inventory, AllocationResult
from utils import solve_allocation, calculate_max_capacity

logger = logging.getLogger(__name__)

def run_level4(inventory: Inventory, client_requests: List[int]) -> Dict[str, Any]:
    if not isinstance(inventory, Inventory):
        raise TypeError("inventory must be an Inventory instance.")
    if not client_requests or any(r <= 0 for r in client_requests):
        raise ValueError("client_requests must be a non-empty list of positive integers.")

    logger.info("Executing Level 4 strategy for %d clients", len(client_requests))
    try:
        sorted_clients = sorted(client_requests, reverse=True)
        remaining = inventory.to_dict()
        total_used = {"Bravo": 0, "Charlie": 0, "Delta": 0}
        total_cost = 0.0
        allocations = []

        for idx, req in enumerate(sorted_clients, 1):
            alloc = solve_allocation(req, remaining, objective="cost")
            if alloc.is_valid:
                remaining["Bravo"] -= alloc.bravo
                remaining["Charlie"] -= alloc.charlie
                remaining["Delta"] -= alloc.delta
                total_used["Bravo"] += alloc.bravo
                total_used["Charlie"] += alloc.charlie
                total_used["Delta"] += alloc.delta
                total_cost += alloc.total_cost
                allocations.append({"client": idx, "hours": req, "status": "allocated", "assigned": alloc})
            else:
                # Explicitly map uppercase keys to lowercase Inventory fields
                remaining_cap = calculate_max_capacity(
                    Inventory(
                        bravo=remaining["Bravo"],
                        charlie=remaining["Charlie"],
                        delta=remaining["Delta"]
                    )
                )

                deficit = req - remaining_cap
                if deficit > 0:
                    standby = solve_allocation(deficit, {"Bravo": 100, "Charlie": 100, "Delta": 100}, objective="cost")
                    if standby.is_valid:
                        total_used["Bravo"] += standby.bravo
                        total_used["Charlie"] += standby.charlie
                        total_used["Delta"] += standby.delta
                        total_cost += standby.total_cost
                        allocations.append({"client": idx, "hours": req, "status": "standby_required", "standby": standby})
                    else:
                        allocations.append({"client": idx, "hours": req, "status": "impossible", "error": alloc.error})
                else:
                    allocations.append({"client": idx, "hours": req, "status": "impossible", "error": alloc.error})

        total_potential = total_used["Bravo"]*3 + total_used["Charlie"]*5 + total_used["Delta"]*8
        total_requested = sum(client_requests)
        avg_util = (total_requested / total_potential * 100) if total_potential > 0 else 0.0

        summary = {
            "total_robots_used": total_used,
            "total_cost": round(total_cost, 2),
            "total_requested_hours": total_requested,
            "avg_utilisation": round(avg_util, 1)
        }

        inv_dict = inventory.to_dict()
        def calc_util(rt: str) -> float:
            t = inv_dict.get(rt, 0); u = total_used.get(rt, 0)
            return round((u / t) * 100, 1) if t > 0 else 0.0
        summary["efficiency_metrics"] = {"Bravo": calc_util("Bravo"), "Charlie": calc_util("Charlie"), "Delta": calc_util("Delta")}

        return {"allocations": allocations, "summary": summary}

    except ValueError:
        raise
    except Exception as e:
        logger.exception("Level 4 failed unexpectedly")
        raise RuntimeError(f"Level 4 strategy failed: {str(e)}") from e
