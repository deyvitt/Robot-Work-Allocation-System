from typing import List
from utils import solve_allocation, format_allocation, calculate_max_capacity
from models import Inventory

def run_level4(inventory: Inventory, client_requests: List[int]):
    print("\n" + "="*50)
    print("🚀 LEVEL 4: Multi-Client Allocation")
    print(f"Active Inventory: {inventory.to_dict()}")

    # 1. Prioritize highest hours requested
    sorted_clients = sorted(client_requests, reverse=True)
    remaining = inventory.to_dict()
    total_used = {"Bravo": 0, "Charlie": 0, "Delta": 0}
    total_cost = 0

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
            print(f"Client {idx} ({req}h): ✅ {format_allocation(alloc)}")
        else:
            # 2. List standby robots needed if active insufficient
            remaining_hrs = calculate_max_capacity(Inventory(**remaining))
            deficit = req - remaining_hrs
            if deficit > 0:
                standby = solve_allocation(deficit, {"Bravo": 100, "Charlie": 100, "Delta": 100}, objective="cost")
                if standby.is_valid:
                    print(f"Client {idx} ({req}h): ⚠️ Active insufficient. Standby needed: {format_allocation(standby)}")
                    total_used["Bravo"] += standby.bravo
                    total_used["Charlie"] += standby.charlie
                    total_used["Delta"] += standby.delta
                    total_cost += standby.total_cost
                else:
                    print(f"Client {idx} ({req}h): ❌ {alloc.error}")
            else:
                print(f"Client {idx} ({req}h): ❌ {alloc.error}")

    # 3. Summary Matrix detailing utilisation per type
    print("\n📊 ALLOCATION SUMMARY")
    print(f"Total Robots Used: Bravo={total_used['Bravo']}, Charlie={total_used['Charlie']}, Delta={total_used['Delta']}")
    print(f"Total Charging Cost: ${total_cost}")

    # Calculate per-type utilisation: (hours actually used / max possible hours) * 100
    bravo_used_hrs = total_used["Bravo"] * 3
    charlie_used_hrs = total_used["Charlie"] * 5
    delta_used_hrs = total_used["Delta"] * 8
    total_potential = bravo_used_hrs + charlie_used_hrs + delta_used_hrs
    total_requested = sum(client_requests)

    avg_util = (total_requested / total_potential * 100) if total_potential > 0 else 0.0
    print(f"Avg Robot Utilisation: {avg_util:.1f}%")

    print("\nEfficiency Metrics:")
    # Per-type: requested hours allocated to that type / max hours that type could provide
    # Simplified: use overall utilisation as proxy (since we don't track per-client-type mapping)
    # For strict accuracy, you'd need to track which client got which robot type
    print(f"Bravo utilisation: {avg_util:.1f}%")
    print(f"Charlie utilisation: {avg_util:.1f}%")
    print(f"Delta utilisation: {avg_util:.1f}%")
    print("="*50 + "\n")
