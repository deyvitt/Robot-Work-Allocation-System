# ~/RobotWorkAllocationSystem/strategies/level4.py

"""
Level 4: Multi-Client Allocation Strategy

Business Rule:
Process multiple client requests in descending order of hours requested,
deducting active inventory sequentially. Trigger cost-optimised standby
deployment when active capacity is exhausted. Generate a consolidated
summary with total cost and fleet utilisation metrics.

Technical Implementation:
Returns a structured dictionary containing per-client allocation details
and a summary block. All presentation logic (terminal printing or JSON
formatting) is delegated to the caller (CLI or API layer).
"""

import logging
from typing import List, Dict, Any, Optional
from models import Inventory, AllocationResult
from utils import solve_allocation, calculate_max_capacity

logger = logging.getLogger(__name__)

def run_level4(inventory: Inventory, client_requests: List[int]) -> Dict[str, Any]:
    """
    Execute Level 4 multi-client allocation strategy.
    
    Args:
        inventory: Available active robot counts (Bravo, Charlie, Delta)
        client_requests: List of client work hour requests (all must be > 0)
        
    Returns:
        Dictionary with keys:
            - allocations (list[dict]): Per-client status, assigned robots, or standby info
            - summary (dict): Total robots used, total cost, average utilisation percentage
            
    Raises:
        ValueError: If client_requests is empty or contains non-positive integers.
        TypeError: If inventory is not an Inventory instance.
        RuntimeError: If the underlying solver fails unexpectedly.
    """
    # 1. Input validation (fail fast)
    if not isinstance(inventory, Inventory):
        raise TypeError("inventory must be an Inventory instance.")
    if not client_requests or any(r <= 0 for r in client_requests):
        raise ValueError("client_requests must be a non-empty list of positive integers.")
        
    logger.info("Executing Level 4 strategy for %d client requests", len(client_requests))
    
    # 2. Execute logic with explicit error boundaries
    try:
        # Priority queue: highest hours first
        sorted_clients = sorted(client_requests, reverse=True)
        remaining = inventory.to_dict()
        total_used = {"Bravo": 0, "Charlie": 0, "Delta": 0}
        total_cost = 0.0
        allocations = []
        
        logger.debug("Sorted client requests (descending): %s", sorted_clients)
        
        for idx, req in enumerate(sorted_clients, 1):
            alloc = solve_allocation(req, remaining, objective="cost")
            
            if alloc.is_valid:
                # Deduct from active pool
                remaining["Bravo"] -= alloc.bravo
                remaining["Charlie"] -= alloc.charlie
                remaining["Delta"] -= alloc.delta
                
                # Accumulate metrics
                total_used["Bravo"] += alloc.bravo
                total_used["Charlie"] += alloc.charlie
                total_used["Delta"] += alloc.delta
                total_cost += alloc.total_cost
                
                allocations.append({
                    "client": idx,
                    "hours": req,
                    "status": "allocated",
                    "assigned": alloc
                })
                logger.debug("Client %d allocated: %d hours, cost=%.2f", idx, req, alloc.total_cost)
                
            else:
                # Check if active pool still has capacity
                remaining_capacity = calculate_max_capacity(Inventory(**remaining))
                deficit = req - remaining_capacity
                
                if deficit > 0:
                    logger.info("Client %d deficit of %d hours. Querying standby pool.", idx, deficit)
                    standby = solve_allocation(deficit, {"Bravo": 100, "Charlie": 100, "Delta": 100}, objective="cost")
                    
                    if standby.is_valid:
                        total_used["Bravo"] += standby.bravo
                        total_used["Charlie"] += standby.charlie
                        total_used["Delta"] += standby.delta
                        total_cost += standby.total_cost
                        
                        allocations.append({
                            "client": idx,
                            "hours": req,
                            "status": "standby_required",
                            "standby": standby
                        })
                    else:
                        allocations.append({
                            "client": idx,
                            "hours": req,
                            "status": "impossible",
                            "error": alloc.error
                        })
                else:
                    allocations.append({
                        "client": idx,
                        "hours": req,
                        "status": "impossible",
                        "error": alloc.error
                    })
        
        # 3. Calculate fleet utilisation metrics
        total_potential_hours = (
            total_used["Bravo"] * 3 +
            total_used["Charlie"] * 5 +
            total_used["Delta"] * 8
        )
        total_requested_hours = sum(client_requests)
        avg_utilisation = (total_requested_hours / total_potential_hours * 100) if total_potential_hours > 0 else 0.0
        
        logger.info(
            "Level 4 complete: total_cost=%.2f, avg_utilisation=%.1f%%",
            total_cost, avg_utilisation
        )
        
        return {
            "allocations": allocations,
            "summary": {
                "total_robots_used": total_used,
                "total_cost": round(total_cost, 2),
                "total_requested_hours": total_requested_hours,
                "avg_utilisation": round(avg_utilisation, 1)
            }
        }
        
    except ValueError:
        raise
    except Exception as e:
        logger.exception("Level 4 allocation failed unexpectedly")
        raise RuntimeError(f"Level 4 strategy failed: {str(e)}") from e
