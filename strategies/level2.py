from utils import solve_allocation
from models import Inventory, AllocationResult

def run_level2(inventory: Inventory, requested: int, l1_alloc: AllocationResult = None) -> AllocationResult:
    print("\n" + "="*50)
    print("💰 LEVEL 2: Cost Optimised Allocation")
    alloc = solve_allocation(requested, inventory.to_dict(), objective="cost")
    
    if alloc.is_valid:
        print("Cost Optimized Allocation")
        if alloc.bravo > 0: print(f"Bravo: {alloc.bravo}")
        if alloc.charlie > 0: print(f"Charlie: {alloc.charlie}")
        if alloc.delta > 0: print(f"Delta: {alloc.delta}")
        print(f"Total Hours Provided: {alloc.total_hours}")
        print(f"Total Charging Cost: ${alloc.total_cost}")
    else:
        print(alloc.error)

    # ✅ COMPARISON
    if alloc.is_valid and l1_alloc and l1_alloc.is_valid:
        diff = l1_alloc.total_cost - alloc.total_cost
        print("\nLevel 1 vs Level 2 Comparison")
        print(f"Level 1 Cost: ${l1_alloc.total_cost}")
        print(f"Level 2 Cost: ${alloc.total_cost}")
        print(f"Cost Difference: ${diff}")
        if diff > 0:
            print(f"Insight: Level 1 strategy resulted in ${diff} additional cost due to mandatory usage of multiple robot categories.")
    print("="*50 + "\n")
    return alloc
