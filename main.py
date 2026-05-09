# ~/RobotWorkAllocationSystem/main.py

import sys
import logging
from models import Inventory
from utils import parse_inventory_input, parse_clients_input
from strategies.level1 import run_level1
from strategies.level2 import run_level2
from strategies.level3 import run_level3
from strategies.level4 import run_level4

# Configure logging: send DEBUG+ to stderr, separate from user output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
    force=True  # Override any existing config (useful in notebooks/repl)
)
logger = logging.getLogger(__name__)

def main():
    # Background log only - not shown to user
    logger.info("EverBot Solutions CLI started")
    
    # User-facing welcome (must appear in terminal)
    print("🤖 EverBot Solutions - Robot Work Allocation System")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            cmd = input("Select Level [1/2/3/4/quit]: ").strip().lower()
            if cmd == 'quit':
                print("👋 Exiting. Good luck with your submission!")
                break

            # Validate robot counts
            try:
                b = int(input("Bravo count: "))
                c = int(input("Charlie count: "))
                d = int(input("Delta count: "))
                inv = parse_inventory_input(b, c, d)
            except ValueError as e:
                print(f"❌ Invalid robot count: {e}", file=sys.stderr)
                logger.warning("Invalid robot count input: %s", e)
                continue

            if cmd == '1':
                try:
                    req = int(input("Client work hours: "))
                    if req <= 0:
                        raise ValueError
                except ValueError:
                    print("❌ Error: Work hours must be a positive integer.", file=sys.stderr)
                    logger.warning("Invalid hours input for Level 1: not a positive integer")
                    continue

                result = run_level1(inv, req)
                # Terminal formatting (exact PDF spec)
                print("\n" + "="*50)
                print("📊 LEVEL 1: Category Distribution Strategy")
                if result.is_valid:
                    print("Robot Assignment")
                    if result.bravo > 0: print(f"Bravo: {result.bravo}")
                    if result.charlie > 0: print(f"Charlie: {result.charlie}")
                    if result.delta > 0: print(f"Delta: {result.delta}")
                    print(f"Total Work Hours Provided: {result.total_hours}")
                    print(f"Client Work Hours Requested: {req}")
                else:
                    print(f"❌ {result.error}", file=sys.stderr)
                print("="*50 + "\n")
                logger.info("Level 1 completed: valid=%s", result.is_valid)

            elif cmd == '2':
                try:
                    req = int(input("Client work hours: "))
                    if req <= 0:
                        raise ValueError
                except ValueError:
                    print("❌ Error: Work hours must be a positive integer.", file=sys.stderr)
                    logger.warning("Invalid hours input for Level 2")
                    continue

                l1 = run_level1(inv, req)
                l2 = run_level2(inv, req, l1_alloc=l1)

                # Terminal formatting
                print("\n" + "="*50)
                print("💰 LEVEL 2: Cost Optimised Allocation")
                if l2.is_valid:
                    print("Cost Optimized Allocation")
                    if l2.bravo > 0: print(f"Bravo: {l2.bravo}")
                    if l2.charlie > 0: print(f"Charlie: {l2.charlie}")
                    if l2.delta > 0: print(f"Delta: {l2.delta}")
                    print(f"Total Hours Provided: {l2.total_hours}")
                    print(f"Total Charging Cost: ${l2.total_cost}")
                else:
                    print(f"❌ {l2.error}", file=sys.stderr)

                if l2.is_valid and l1.is_valid:
                    diff = l1.total_cost - l2.total_cost
                    print("\nLevel 1 vs Level 2 Comparison")
                    print(f"Level 1 Cost: ${l1.total_cost}")
                    print(f"Level 2 Cost: ${l2.total_cost}")
                    print(f"Cost Difference: ${diff}")
                    if diff > 0:
                        print(f"Insight: Level 1 strategy resulted in ${diff} additional cost due to mandatory usage of multiple robot categories.")
                print("="*50 + "\n")
                logger.info("Level 2 completed: cost_diff=$%.2f", l1.total_cost - l2.total_cost if l1.is_valid and l2.is_valid else 0)

            elif cmd == '3':
                try:
                    req = int(input("Client work hours: "))
                    if req <= 0:
                        raise ValueError
                except ValueError:
                    print("❌ Error: Work hours must be a positive integer.", file=sys.stderr)
                    logger.warning("Invalid hours input for Level 3")
                    continue

                result = run_level3(inv, req)

                # Terminal formatting
                print("\n" + "="*50)
                print("🔄 LEVEL 3: Standby Activation Strategy")
                print(f"Active Robot Capacity: {result['max_active']} hours")
                print(f"Client Work Requested: {req} hours")
                print("\nActive robots:")
                if inv.bravo > 0: print(f"Bravo: {inv.bravo}")
                if inv.charlie > 0: print(f"Charlie: {inv.charlie}")
                if inv.delta > 0: print(f"Delta: {inv.delta}")

                if result['sufficient']:
                    print("\n✅ Sufficient active capacity. No standby robots needed.")
                else:
                    print(f"\n⚠️ Deficit: {result['deficit']} hours. Activating standby robots...")
                    if result['standby'] and result['standby'].is_valid:
                        s = result['standby']
                        print("\nAdditional Standby Robots Required:")
                        opts = []
                        if s.bravo > 0: opts.append(f"Bravo: {s.bravo} cost ${s.bravo * 2}")
                        if s.charlie > 0: opts.append(f"Charlie: {s.charlie} cost ${s.charlie * 3}")
                        if s.delta > 0: opts.append(f"Delta: {s.delta} cost ${s.delta * 4}")
                        print("   " + "\n   or\n   ".join(opts))
                    else:
                        print("❌ Even with standby robots, capacity is insufficient.", file=sys.stderr)
                print("="*50 + "\n")
                logger.info("Level 3 completed: sufficient=%s, deficit=%d", result['sufficient'], result['deficit'])

            elif cmd == '4':
                raw = input("Client working hours (comma/space separated): ")
                try:
                    clients = parse_clients_input(raw)
                except ValueError as e:
                    print(f"❌ {e}", file=sys.stderr)
                    logger.warning("Invalid client hours input for Level 4: %s", e)
                    continue

                result = run_level4(inv, clients)

                # Terminal formatting
                print("\n" + "="*50)
                print("🚀 LEVEL 4: Multi-Client Allocation")
                print(f"Active Inventory: {inv.to_dict()}")

                for c in result["allocations"]:
                    if c["status"] == "allocated":
                        alloc = c["assigned"]
                        parts = []
                        if alloc.bravo > 0: parts.append(f"Bravo: {alloc.bravo}")
                        if alloc.charlie > 0: parts.append(f"Charlie: {alloc.charlie}")
                        if alloc.delta > 0: parts.append(f"Delta: {alloc.delta}")
                        print(f"Client {c['client']} ({c['hours']}h): ✅ {', '.join(parts)}")
                    elif c["status"] == "standby_required":
                        s = c["standby"]
                        parts = []
                        if s.bravo > 0: parts.append(f"Bravo: {s.bravo}")
                        if s.charlie > 0: parts.append(f"Charlie: {s.charlie}")
                        if s.delta > 0: parts.append(f"Delta: {s.delta}")
                        print(f"Client {c['client']} ({c['hours']}h): ⚠️ Active insufficient. Standby needed: {', '.join(parts)}")
                    else:
                        print(f"Client {c['client']} ({c['hours']}h): ❌ {c.get('error', 'Allocation failed')}", file=sys.stderr)

                # Summary
                s = result["summary"]
                print("\n📊 ALLOCATION SUMMARY")
                print(f"Total Robots Used: Bravo={s['total_robots_used']['Bravo']}, Charlie={s['total_robots_used']['Charlie']}, Delta={s['total_robots_used']['Delta']}")
                print(f"Total Charging Cost: ${s['total_cost']}")
                print(f"Avg Robot Utilisation: {s['avg_utilisation']}%")
                print("="*50 + "\n")
                logger.info("Level 4 completed: %d clients processed", len(clients))

            else:
                print("⚠️ Invalid option. Choose 1, 2, 3, 4, or quit.", file=sys.stderr)
                logger.warning("Invalid menu selection: %s", cmd)

        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            logger.info("CLI interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
            logger.exception("Unhandled exception in CLI main loop")
            # Do not exit - let user continue or quit gracefully

if __name__ == "__main__":
    main()
