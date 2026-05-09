# ~/RobotWorkAllocationSystem/strategies/level1.py

"""
Level 1: Category Distribution Strategy

Business Rule:
Minimise excess hours while meeting the requested work hours, prioritising
allocations that use multiple robot categories. This supports fleet performance
analysis and balanced utilisation reporting.

Technical Implementation:
Delegates to the core bounded-brute-force solver with objective='hours'.
Returns a structured AllocationResult for downstream formatting.
"""

import logging
from utils import solve_allocation
from models import Inventory, AllocationResult

logger = logging.getLogger(__name__)

def run_level1(inventory: Inventory, requested: int) -> AllocationResult:
    """
    Execute Level 1 allocation strategy.
    Args:
        inventory: Available robot counts (Bravo, Charlie, Delta)
        requested: Client work hours required (must be > 0)
    Returns:
        AllocationResult containing the optimal assignment, or an error state
        if allocation is impossible.
        
    Raises:
        ValueError: If requested hours are non-positive.
        TypeError: If inventory is not an Inventory instance.
        RuntimeError: If the underlying solver fails unexpectedly.
    """
    # 1. Input validation (fail fast)
    if requested <= 0:
        raise ValueError("Requested work hours must be a positive integer.")
    if not isinstance(inventory, Inventory):
        raise TypeError("inventory must be an Inventory instance.")
        
    logger.info("Executing Level 1 strategy for %d requested hours", requested)
    
    # 2. Execute solver with explicit error boundaries
    try:
        result = solve_allocation(requested, inventory.to_dict(), objective="hours")
        logger.debug(
            "Level 1 solver completed: valid=%s, excess_hours=%d",
            result.is_valid,
            result.total_hours - requested
        )
        return result
        
    except ValueError:
        # Re-raise validation errors from solver as-is
        raise
    except Exception as e:
        logger.exception("Level 1 allocation failed unexpectedly")
        raise RuntimeError(f"Level 1 solver failed: {str(e)}") from e
