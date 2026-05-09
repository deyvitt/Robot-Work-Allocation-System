from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models import Inventory
from utils import parse_inventory_input, parse_clients_input, solve_allocation, calculate_max_capacity
from strategies.level1 import run_level1
from strategies.level2 import run_level2
from strategies.level3 import run_level3
from strategies.level4 import run_level4

app = FastAPI(title="Robot Work Allocation System")

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Static Files & Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(frontend_path, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

# 3. Request Schema (Data Validation Only)
class AllocationRequest(BaseModel):
    level: int
    bravo: int
    charlie: int
    delta: int
    hours_input: str  # Accepts "20" or "12, 16, 21"

# 4. API Route (Business Logic)
@app.post("/api/allocate")
def allocate(req: AllocationRequest):
    try:
        inv = parse_inventory_input(req.bravo, req.charlie, req.delta)
        clients = parse_clients_input(req.hours_input)

        if req.level == 1:
            l1 = run_level1(inv, clients[0])
            return {
                "status": "success",
                "allocation": {
                    "bravo": l1.bravo, "charlie": l1.charlie, "delta": l1.delta,
                    "total_hours": l1.total_hours, "requested": clients[0],
                    "valid": l1.is_valid, "error": l1.error
                }
            }

        elif req.level == 2:
            l1 = run_level1(inv, clients[0])
            l2 = run_level2(inv, clients[0], l1_alloc=l1)
            diff = l1.total_cost - l2.total_cost if l1.is_valid and l2.is_valid else 0
            return {
                "status": "success",
                "level2": {"bravo": l2.bravo, "charlie": l2.charlie, "delta": l2.delta, "cost": l2.total_cost, "hours": l2.total_hours},
                "level1_cost": l1.total_cost if l1.is_valid else 0,
                "cost_difference": diff,
                "insight": f"Level 1 strategy resulted in ${diff} additional cost due to mandatory usage of multiple robot categories." if diff > 0 else None
            }

        elif req.level == 3:
            max_active = calculate_max_capacity(inv)
            deficit = max(0, clients[0] - max_active)
            standby = None
            if deficit > 0:
                standby = solve_allocation(deficit, {"Bravo": 50, "Charlie": 50, "Delta": 50}, "cost")
            return {
                "status": "success",
                "active_capacity": max_active,
                "requested": clients[0],
                "deficit": deficit,
                "standby": {"bravo": standby.bravo, "charlie": standby.charlie, "delta": standby.delta, "cost": standby.total_cost} if standby and standby.is_valid else None
            }

        elif req.level == 4:
            sorted_clients = sorted(clients, reverse=True)
            remaining = inv.to_dict()
            total_used = {"Bravo": 0, "Charlie": 0, "Delta": 0}
            total_cost = 0
            allocations = []

            for idx, hrs in enumerate(sorted_clients, 1):
                alloc = solve_allocation(hrs, remaining, "cost")
                if alloc.is_valid:
                    remaining["Bravo"] -= alloc.bravo
                    remaining["Charlie"] -= alloc.charlie
                    remaining["Delta"] -= alloc.delta
                    total_used["Bravo"] += alloc.bravo
                    total_used["Charlie"] += alloc.charlie
                    total_used["Delta"] += alloc.delta
                    total_cost += alloc.total_cost
                    allocations.append({"client": idx, "hours": hrs, "assigned": f"Bravo:{alloc.bravo} Charlie:{alloc.charlie} Delta:{alloc.delta}", "status": "allocated"})
                else:
                    remaining_hrs = calculate_max_capacity(Inventory(**remaining))
                    deficit = hrs - remaining_hrs
                    if deficit > 0:
                        standby = solve_allocation(deficit, {"Bravo": 100, "Charlie": 100, "Delta": 100}, "cost")
                        if standby.is_valid:
                            allocations.append({"client": idx, "hours": hrs, "standby": f"Bravo:{standby.bravo} Charlie:{standby.charlie} Delta:{standby.delta}", "status": "standby_required"})
                        else:
                            allocations.append({"client": idx, "hours": hrs, "status": "impossible"})

            total_potential = (total_used["Bravo"]*3) + (total_used["Charlie"]*5) + (total_used["Delta"]*8)
            avg_util = (sum(clients) / total_potential * 100) if total_potential > 0 else 0.0

            return {
                "status": "success",
                "allocations": allocations,
                "summary": {
                    "total_robots_used": total_used,
                    "total_cost": total_cost,
                    "avg_utilisation": round(avg_util, 1)
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid level. Choose 1, 2, 3, or 4.")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
