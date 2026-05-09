# ~/RobotWorkAllocationSystem/strategies/level3.py

"""
Level 3: Standby Activation Strategy

Business Rule:
Calculate active fleet capacity and deploy cost-optimised standby robots
from the warehouse pool only when active capacity is insufficient.
Minimises overflow costs while guaranteeing request fulfilment.

Technical Implementation:
Computes total active hours, determines deficit, and queries the core solver
against a simulated warehouse pool (assumed ample stock). Returns structured
data for downstream formatting in CLI or web layers.
"""

import logging
from models import Inventory, AllocationResult
from utils import solve_allocation, calculate_max_capacity

logger = logging.getLogger(__name__)

def run_level3(inventory: Inventory, requested: int) -> dict:
    """
    Execute Level 3 standby activation strategy.
    
    Args:
        inventory: Available active robot counts (Bravo, Charlie, Delta)
        requested: Client work hours required (must be > 0)
        
    Returns:
        Dictionary containing:
            - max_active (int): Total hours the active fleet can provide
            - deficit (int): Hours shortfall (0 if active capacity is sufficient)
            - standby (AllocationResult | None): Cost-optimised standby assignment
            - sufficient (bool): Whether active capacity meets the request
            
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
        
    logger.info("Executing Level 3 strategy for %d requested hours", requested)
    
    # 2. Execute logic with explicit error boundaries
    try:
        max_active = calculate_max_capacity(inventory)
        deficit = max(0, requested - max_active)
        logger.debug("Active capacity: %d hours, Deficit: %d hours", max_active, deficit)
        
        standby_alloc = None
        if deficit > 0:
            logger.info("Activating standby robots for %d hour deficit", deficit)
            # Simulated warehouse pool with ample inventory
            warehouse_pool = {"Bravo": 50, "Charlie": 50, "Delta": 50}
            standby_alloc = solve_allocation(deficit, warehouse_pool, objective="cost")
            
        return {
            "max_active": max_active,
            "deficit": deficit,
            "standby": standby_alloc,
            "sufficient": deficit == 0
        }
        
    except ValueError:
        raise
    except Exception as e:
        logger.exception("Level 3 allocation failed unexpectedly")
        raise RuntimeError(f"Level 3 strategy failed: {str(e)}") from e
