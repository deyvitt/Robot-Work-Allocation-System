# ~/RobotWorkAllocationSystem/main.py

import sys
from models import Inventory
from utils import parse_inventory_input, parse_clients_input
from strategies import run_level1, run_level2, run_level3, run_level4

def main():
    print("🤖 EverBot Solutions - Robot Work Allocation System")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            cmd = input("Select Level [1/2/3/4/quit]: ").strip().lower()
            if cmd == 'quit':
                print("👋 Exiting. Good luck with your submission!")
                break

            # Validate robot counts first
            b = int(input("Bravo count: "))
            c = int(input("Charlie count: "))
            d = int(input("Delta count: "))
            inv = parse_inventory_input(b, c, d)

            if cmd == '1':
                try:
                    req = int(input("Client work hours: "))
                    if req <= 0:
                        print("❌ Error: Work hours must be a positive integer.")
                        continue
                except ValueError:
                    print("❌ Invalid input. Please enter a positive integer.")
                    continue
                run_level1(inv, req)

            elif cmd == '2':
                try:
                    req = int(input("Client work hours: "))
                    if req <= 0:
                        print("❌ Error: Work hours must be a positive integer.")
                        continue
                except ValueError:
                    print("❌ Invalid input. Please enter a positive integer.")
                    continue
                l1 = run_level1(inv, req)
                run_level2(inv, req, l1_alloc=l1)

            elif cmd == '3':
                try:
                    req = int(input("Client work hours: "))
                    if req <= 0:
                        print("❌ Error: Work hours must be a positive integer.")
                        continue
                except ValueError:
                    print("❌ Invalid input. Please enter a positive integer.")
                    continue
                run_level3(inv, req)

            elif cmd == '4':
                raw = input("Client working hours (comma/space separated): ")
                clients = parse_clients_input(raw)
                run_level4(inv, clients)

            else:
                print("⚠️ Invalid option. Choose 1, 2, 3, 4, or quit.")

        except ValueError as e:
            # Catches invalid robot counts
            print(f"❌ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
