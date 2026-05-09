# ~/RobotWorkAllocationSystem/strategies/level1.py

from models import Inventory, AllocationResult

def run_level1(inventory: Inventory, requested: int) -> AllocationResult:
    print("\n" + "="*50)
    print("📊 LEVEL 1: Category Distribution Strategy")
    alloc = solve_allocation(requested, inventory.to_dict(), objective="hours")
    if alloc.is_valid:
        print("Robot Assignment")
        if alloc.bravo > 0: print(f"Bravo: {alloc.bravo}")
        if alloc.charlie > 0: print(f"Charlie: {alloc.charlie}")
        if alloc.delta > 0: print(f"Delta: {alloc.delta}")
        print(f"Total Work Hours Provided: {alloc.total_hours}")
        print(f"Client Work Hours Requested: {requested}")
    else:
        print(alloc.error)
    print("="*50 + "\n")
    return alloc
