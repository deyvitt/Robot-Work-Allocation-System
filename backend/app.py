# ~/RobotWorkAllocationSystem/backend/app.py

import os
import sys
import uuid
import logging
from pathlib import Path
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request

# Configure logging for Render + local development
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Robust path resolution
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import application logic
from models import Inventory, AllocationResult
from utils import (
    parse_inventory_input,
    parse_clients_input,
    format_allocation
)
from strategies.level1 import run_level1
from strategies.level2 import run_level2
from strategies.level3 import run_level3
from strategies.level4 import run_level4

app = FastAPI(
    title="Robot Work Allocation System",
    description="EverBot Solutions allocation engine — compliant with Everest Engineering challenge specification",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend
FRONTEND_DIR = PROJECT_ROOT / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface."""
    html_path = FRONTEND_DIR / "index.html"
    if not html_path.exists():
        logger.error("frontend/index.html not found at %s", html_path)
        return {"error": "Frontend not found. Please ensure frontend/index.html exists."}
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health_check():
    """Lightweight endpoint for uptime monitoring."""
    return {"status": "healthy", "service": "robot-allocator"}

@app.post("/api/allocate")
async def allocate(request: Request):
    """
    Main allocation endpoint.

    Expects JSON payload:
    {
        "level": 1|2|3|4,
        "bravo": int,
        "charlie": int,
        "delta": int,
        "hours_input": str  # e.g. "20" or "12, 16, 21"
    }

    Returns JSON allocation result or error.
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info("[%s] Received allocation request", request_id)

    try:
        data = await request.json()

        # Validate required fields
        required = ["level", "bravo", "charlie", "delta", "hours_input"]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        level = data["level"]
        bravo = data["bravo"]
        charlie = data["charlie"]
        delta = data["delta"]
        hours_input = data["hours_input"]

        # Type validation
        if not all(isinstance(x, int) for x in [level, bravo, charlie, delta]):
            raise ValueError("Robot counts and level must be integers")
        if not isinstance(hours_input, str):
            raise ValueError("hours_input must be a string")
        if level not in [1, 2, 3, 4]:
            raise ValueError("Level must be 1, 2, 3, or 4")

        logger.debug("[%s] Parsed input: level=%d, inventory=(B:%d,C:%d,D:%d), hours='%s'",
                    request_id, level, bravo, charlie, delta, hours_input)

        # Parse and validate domain inputs
        inv = parse_inventory_input(bravo, charlie, delta)
        clients = parse_clients_input(hours_input)

        # Route to appropriate strategy — all now use refactored functions
        if level == 1:
            logger.info("[%s] Running Level 1: Category Distribution", request_id)
            result = run_level1(inv, clients[0])
            response = {
                "status": "success",
                "allocation": {
                    "bravo": result.bravo, "charlie": result.charlie, "delta": result.delta,
                    "total_hours": result.total_hours, "requested": clients[0],
                    "valid": result.is_valid, "error": result.error
                }
            }

        elif level == 2:
            logger.info("[%s] Running Level 2: Cost Optimisation", request_id)
            l1 = run_level1(inv, clients[0])
            l2 = run_level2(inv, clients[0], l1_alloc=l1)
            diff = l1.total_cost - l2.total_cost if l1.is_valid and l2.is_valid else 0
            response = {
                "status": "success",
                "level2": {
                    "bravo": l2.bravo, "charlie": l2.charlie, "delta": l2.delta,
                    "cost": l2.total_cost, "hours": l2.total_hours, "valid": l2.is_valid
                },
                "level1_cost": l1.total_cost if l1.is_valid else 0,
                "cost_difference": diff,
                "insight": f"Level 1 strategy resulted in ${diff} additional cost due to mandatory usage of multiple robot categories." if diff > 0 else None
            }

        elif level == 3:
            logger.info("[%s] Running Level 3: Standby Activation", request_id)
            result = run_level3(inv, clients[0])
            standby_data = None
            if result["standby"] and result["standby"].is_valid:
                s = result["standby"]
                standby_data = {
                    "bravo": s.bravo, "charlie": s.charlie, "delta": s.delta,
                    "cost": s.total_cost, "valid": s.is_valid
                }
            response = {
                "status": "success",
                "active_capacity": result["max_active"],
                "requested": clients[0],
                "deficit": result["deficit"],
                "sufficient": result["sufficient"],
                "standby": standby_data
            }

        elif level == 4:
            logger.info("[%s] Running Level 4: Multi-Client Allocation for %d clients", request_id, len(clients))
            result = run_level4(inv, clients)
            formatted_allocs = []
            for c in result["allocations"]:
                entry = {"client": c["client"], "hours": c["hours"], "status": c["status"]}
                if c["status"] == "allocated" and c.get("assigned"):
                    a = c["assigned"]
                    entry["assigned"] = f"Bravo:{a.bravo} Charlie:{a.charlie} Delta:{a.delta}"
                    entry["valid"] = a.is_valid
                elif c["status"] == "standby_required" and c.get("standby"):
                    s = c["standby"]
                    entry["standby"] = f"Bravo:{s.bravo} Charlie:{s.charlie} Delta:{s.delta}"
            response = {"status": "success", "allocations": formatted_allocs, "summary": result["summary"]}

            }

        else:
            raise ValueError(f"Unsupported level: {level}")

        logger.info("[%s] Allocation completed successfully", request_id)
        return response

    except ValueError as e:
        logger.warning("[%s] Validation error: %s", request_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("[%s] Unexpected server error", request_id)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
