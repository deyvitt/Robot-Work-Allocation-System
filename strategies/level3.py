# ~/RobotWorkAllocationSystem/strategies/level3.py

from utils import solve_allocation, calculate_max_capacity
from models import Inventory

def run_level3(inventory: Inventory, requested: int):
    print("\n" + "="*50)
    print("🔄 LEVEL 3: Standby Activation Strategy")

    max_active = calculate_max_capacity(inventory)
    print(f"Active Robot Capacity: {max_active} hours")
    print(f"Client Work Requested: {requested} hours")

    print("Active robots:")
    if inventory.bravo > 0: print(f"Bravo: {inventory.bravo}")
    if inventory.charlie > 0: print(f"Charlie: {inventory.charlie}")
    if inventory.delta > 0: print(f"Delta: {inventory.delta}")

    if max_active >= requested:
        print("\n✅ Sufficient active capacity. No standby robots needed.")
        print("="*50 + "\n")
        return

    deficit = requested - max_active
    print(f"\n⚠️ Deficit: {deficit} hours. Activating standby robots...")

    # Large standby pool simulates the warehouse
    standby_pool = {"Bravo": 50, "Charlie": 50, "Delta": 50}
    best = solve_allocation(deficit, standby_pool, objective="cost")

    if not best.is_valid:
        print("❌ Even with standby robots, capacity is insufficient.")
        print("="*50 + "\n")
        return

    print("\nAdditional Standby Robots Required:")
    opts = []
    if best.bravo > 0: opts.append(f"Bravo: {best.bravo} cost ${best.bravo * 2}")
    if best.charlie > 0: opts.append(f"Charlie: {best.charlie} cost ${best.charlie * 3}")
    if best.delta > 0: opts.append(f"Delta: {best.delta} cost ${best.delta * 4}")

    # Print the chosen option(s) exactly as requested
    print("   " + "\n   or\n   ".join(opts))

    print(f"\nClient work request: {requested} hours")
    print(f"Maximum Active Capacity: {max_active} hours")
    print(f"The output should show {opts[0]} as it's the cost optimised one")
    print("="*50 + "\n")
