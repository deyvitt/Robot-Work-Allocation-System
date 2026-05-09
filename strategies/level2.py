# ~/RobotWorkAllocationSystem/strategies/level2.py

"""
Level 2: Cost Optimisation Strategy

Business Rule:
Allocate robots purely to minimise total daily charging cost, ignoring
the multi-category preference from Level 1. This maximises profit margins
while still meeting client work hour requirements.

Technical Implementation:
Delegates to the core bounded-brute-force solver with objective='cost'.
Returns the cost-optimised allocation. Comparison data is logged for
debugging and handled by the caller for terminal or web output.
"""

import logging
from utils import solve_allocation
from models import Inventory, AllocationResult

logger = logging.getLogger(__name__)

def run_level2(inventory: Inventory, requested: int, l1_alloc: AllocationResult = None) -> AllocationResult:
    """
    Execute Level 2 cost-optimisation strategy.
    
    Args:
        inventory: Available robot counts (Bravo, Charlie, Delta)
        requested: Client work hours required (must be > 0)
        l1_alloc: Optional AllocationResult from Level 1 for financial comparison
        
    Returns:
        AllocationResult containing the cost-minimised assignment, or an error
        state if allocation is impossible.
        
    Raises:
        ValueError: If requested hours are non-positive.
        TypeError: If inventory is not an Inventory instance.
    """
    # 1. Input validation (fail fast)
    if requested <= 0:
        raise ValueError("Requested work hours must be a positive integer.")
    if not isinstance(inventory, Inventory):
        raise TypeError("inventory must be an Inventory instance.")
        
    logger.info("Executing Level 2 strategy for %d requested hours", requested)
    
    # 2. Execute solver with error boundaries
    try:
        result = solve_allocation(requested, inventory.to_dict(), objective="cost")
        logger.debug(
            "Level 2 solver completed: valid=%s, cost=%.2f",
            result.is_valid, result.total_cost
        )
        
        # 3. Log comparison data (do not print; let caller handle formatting)
        if result.is_valid and l1_alloc and l1_alloc.is_valid:
            diff = l1_alloc.total_cost - result.total_cost
            logger.info(
                "L1 vs L2 comparison: L1=$%.2f, L2=$%.2f, Diff=$%.2f",
                l1_alloc.total_cost, result.total_cost, diff
            )
            
        return result
        
    except ValueError:
        raise
    except Exception as e:
        logger.exception("Level 2 allocation failed unexpectedly")
        raise RuntimeError(f"Level 2 solver failed: {str(e)}") from e
