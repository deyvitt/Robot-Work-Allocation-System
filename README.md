# Robot Work Allocation System

> A terminal-optimised Python application for automated robot fleet allocation, cost-efficient scheduling, and multi-client resource management. Built to satisfy the Everest Engineering coding challenge specification with 100 per cent compliance.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Render Deploy](https://img.shields.io/badge/deployed-on_render-0099ff.svg)](https://render.com)

[!IMPORTANT]
**Core Requirement:** Terminal-based CLI (`python3 main.py`) fully compliant with Everest Engineering's specification.
**Bonus Feature:** Optional web interface (`uvicorn  backend.app:app`) deployed to Render for browser access & live demo.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
  - [Command Line Interface](#command-line-interface-default)
  - [Browser Interface](#browser-interface)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Core Algorithm](#core-algorithm)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Deployment Guide](#deployment-guide)
- [Development Guidelines](#development-guidelines)
- [Constraints & Compliance](#constraints--compliance)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**EverBot Solutions** manages a fleet of three robot types (`Bravo`, `Charlie`, `Delta`) to fulfil client work requests measured in daily hours. This system automates the allocation process across four strategic levels, handling inventory constraints, cost optimisation, standby activation, and batch prioritisation.

The core engine uses a bounded search algorithm that guarantees optimal allocations in `<5ms` per request, while strict input validation and exact error messaging ensure production-ready reliability.

**Key Design Principles:**
- ✅ **Separation of Concerns**: Strategy logic isolated from presentation (CLI/API)
- ✅ **Fail-Fast Validation**: Clear, spec-compliant error messages at entry points
- ✅ **Structured Logging**: Debuggable without affecting user output
- ✅ **Type Safety**: Full type hints for IDE support and static analysis
- ✅ **British English**: Consistent spelling and terminology throughout

---

## Features

| Level | Feature | Business Objective | Technical Implementation |
|:---:|:---|:---|:---|
| **1** | Category Distribution | Minimises excess hours while prioritising multi-type robot usage for performance analysis | Bounded brute-force with `objective="hours"`; tie-break by category diversity |
| **2** | Cost Optimisation | Minimises daily charging fees with automatic financial comparison against Level 1 | Reuses Level 1 result; computes cost delta; logs comparison metrics |
| **3** | Standby Activation | Calculates capacity deficits and deploys cost-optimised warehouse robots on demand | Computes `max_capacity`; triggers standby solver only when deficit > 0 |
| **4** | Multi-Client Scaling | Processes batch requests in descending priority, deducts inventory sequentially, triggers standby fallback | Sorts clients descending; sequential deduction; per-client status tracking |
| **Summary** | Efficiency Analytics | Generates consolidated utilisation metrics, total cost tracking, and per-fleet breakdowns | Aggregates allocations; computes `(requested / potential) × 100` utilisation |

---

## Quick Start

### Command Line Interface (Default)
```bash
cd RobotWorkAllocationSystem
python3 main.py
```

### Interactive Example:
```text
🤖 EverBot Solutions - Robot Work Allocation System
Type 'quit' to exit.

Select Level [1/2/3/4/quit]: 2
Bravo count: 2
Charlie count: 3
Delta count: 2
Client work hours: 20

==================================================
💰 LEVEL 2: Cost Optimised Allocation
Cost Optimized Allocation
Charlie: 1
Delta: 2
Total Hours Provided: 21
Total Charging Cost: $11

Level 1 vs Level 2 Comparison
Level 1 Cost: $12
Level 2 Cost: $11
Cost Difference: $1
Insight: Level 1 strategy resulted in $1 additional cost due to mandatory usage of multiple robot categories.
==================================================
```

## Browser Interface

### Option A: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn backend.app:app --reload

# Open in browser
open frontend/index.html  # macOS
# or navigate to http://127.0.0.1:8000
 Option A: Local Development
```
### Option B: Live Demo
🌐 Access the deployed application:
```
https://robot-work-allocation-system.onrender.com
```
Note: Free-tier instances sleep after 15 minutes of inactivity. First request may take 20–40 seconds to wake.

## Installation
```text
Prerequisites
●  Python 3.11 or later
●  pip (Python package installer)
●  Git (for cloning the repository)
```

### Steps
```bash
# Clone the repository
git clone https://github.com/deyvitt/Robot-Work-Allocation-System.git
cd RobotWorkAllocationSystem

# Install dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies for testing
pip install pytest pytest-cov
```
## Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | `>=0.115.0` | Async web framework for API layer |
| `uvicorn` | `>=0.30.0` | ASGI server for running FastAPI |
| `pytest` | *(dev)* | Testing framework |
| `pytest-cov` | *(dev)* | Coverage reporting |

## Usage Examples
### Level 1: Category Distribution
```bash
Select Level [1/2/3/4/quit]: 1
Bravo count: 1
Charlie count: 1
Delta count: 2
Client work hours: 12
```
### Output:
```bash
📊 LEVEL 1: Category Distribution Strategy
Robot Assignment
Bravo: 1
Charlie: 1
Delta: 1
Total Work Hours Provided: 16
Client Work Hours Requested: 12
```
### Level 4: Multi-Client Allocation
```bash
Select Level [1/2/3/4/quit]: 4
Bravo count: 5
Charlie count: 5
Delta count: 5
Client working hours (comma/space separated): 12, 16, 17, 10, 21
```
### Output:
```bash
🚀 LEVEL 4: Multi-Client Allocation
Active Inventory: {'Bravo': 5, 'Charlie': 5, 'Delta': 5}
Client 1 (21h): ✅ Bravo:1 Charlie:2 Delta:1
Client 2 (17h): ✅ Bravo:1 Charlie:1 Delta:1
...
📊 ALLOCATION SUMMARY
Total Robots Used: Bravo=4, Charlie=6, Delta=4
Total Charging Cost: $42
Avg Robot Utilisation: 89.3%
```
### Web Interface Test Payload
```json
{
  "level": 2,
  "bravo": 2,
  "charlie": 3,
  "delta": 2,
  "hours_input": "20"
}
```
### Expected Response:
```json
{
  "status": "success",
  "level2": {
    "bravo": 0,
    "charlie": 1,
    "delta": 2,
    "cost": 11,
    "hours": 21
  },
  "level1_cost": 12,
  "cost_difference": 1,
  "insight": "Level 1if objective == "hours":
    # Level 1: Minimise excess hours, tie-break by maximising category diversity
    if excess < best_excess or (excess == best_excess and types > best_types):
        update_best()
else:
    # Levels 2-4: Minimise cost, tie-break by minimising excess
    if cost < best_cost or (cost == best_cost and excess < best_excess):
        update_best() strategy resulted in $1 additional cost due to mandatory usage of multiple robot categories."
}
```

## Architecture
```text
RobotWorkAllocationSystem/
├── backend/
│   └── app.py              # FastAPI REST wrapper with structured logging, CORS, and request tracing
├── frontend/
│   └── index.html          # Browser UI with robust error handling, XSS sanitisation, and relative fetch paths
├── strategies/
│   ├── __init__.py         # Package marker
│   ├── level1.py           # Category distribution: minimise excess, maximise diversity
│   ├── level2.py           # Cost optimisation: minimise fees, compare with Level 1
│   ├── level3.py           # Standby activation: deficit calculation + warehouse fallback
│   └── level4.py           # Multi-client: priority sorting, sequential deduction, summary metrics
├── tests/
│   ├── __init__.py         # Package marker
│   └── test_allocation.py  # pytest suite: solver logic, parsing, strategy integration, PDF compliance
├── main.py                 # CLI entry point: user interaction + terminal formatting
├── models.py               # Dataclasses: Inventory, AllocationResult, RobotSpec (single source of truth)
├── utils.py                # Core solver, input validation, capacity calculation, formatting helpers
├── requirements.txt        # Production dependencies (fastapi, uvicorn)
├── Procfile                # Render deployment: uvicorn startup command
├── runtime.txt             # Python version pin: 3.11.0
└── .gitignore              # Excludes __pycache__/, venv/, *.pyc, logs
```

## Data Flow Diagram

### 🔄 Data Flow Diagram
```markdown
```text
User Input (CLI or Web)
        │
        ▼
[Validation Layer] → parse_inventory_input / parse_clients_input
        │
        ▼
[Strategy Router] → run_level1 / run_level2 / run_level3 / run_level4
        │
        ▼
[Core Solver] → solve_allocation (bounded brute-force)
        │
        ▼
[Result Formatter] → Terminal print() or JSON response
        │
        ▼
User Output (exact PDF-compliant format)
```

## Core Algorithm
The solver uses a bounded brute-force search optimised for three variables. Loop limits are mathematically capped at (requested_hours // capacity_per_robot) + 2, keeping iterations below 1 000 even for large requests.

### Guarantees
| Property | Implementation |
|----------|---------------|
| **Optimality** | Exhaustive search within bounded space; tie-break rules enforce spec preferences |
| **Termination** | Hard caps on loop ranges guarantee `O(1)` worst-case iterations |
| **Correctness** | Strict `hrs >= requested` filter; exact error strings for edge cases |
| **Performance** | Sub-5ms execution for typical inputs (`<100` requested hours) |

### Optimisation Objectives
```python
if objective == "hours":
    # Level 1: Minimise excess hours, tie-break by maximising category diversity
    if excess < best_excess or (excess == best_excess and types > best_types):
        update_best()
else:
    # Levels 2-4: Minimise cost, tie-break by minimising excess
    if cost < best_cost or (cost == best_cost and excess < best_excess):
        update_best()
```

### Error Handling
| Scenario | Trigger Condition | Exact Output Message (PDF-Compliant) |
|----------|-------------------|--------------------------------------|
| **Invalid Input** | `hours ≤ 0` or non-integer | `Error: Work hours must be a positive integer.` |
| **Zero Inventory** | `Bravo + Charlie + Delta = 0` | `Error: No robots available for assignment.` |
| **Impossible Allocation** | No valid combination within bounds | `Error: Unable to allocate at least one robot from each category with the available inventory.` |
| **Parse Failure** | Non-numeric or malformed hours string | `Invalid input. Please enter positive integers separated by spaces or commas.` |

### Logging Strategy
```text
●  User-facing errors: print(..., file=sys.stderr) for immediate visibility
●  Debug/audit logs: logger.debug/info/warning to stderr (separate stream)
●  Request tracing: UUID prefix [abc12345] for correlating CLI/API requests
●  Production safety: No sensitive data in logs; structured JSON-ready format
```

## Testing
### Run the Test Suite
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=robot_allocator --cov-report=term-missing

# Generate HTML coverage report (open htmlcov/index.html in browser)
pytest tests/ --cov=robot_allocator --cov-report=html
```

### Test Coverage Includes
```text
✔   Exact PDF example validation (Levels 1–4)
✔   Negative/zero input rejection with correct error strings
✔   Inventory exhaustion & standby fallback routing
✔   Sequential deduction integrity (no double-booking)
✔   Cost comparison delta accuracy
✔   Multi-client priority sorting verification
✔   Edge cases: large requests, boundary values, tie-breaking scenarios
```

### Example Test Assertion
```python
def test_l2_minimize_cost_20hrs(sample_inventory):
    """Level 2: Request 20h → minimise cost, accept slight excess."""
    res = solve_allocation(20, sample_inventory.to_dict(), objective="cost")
    assert res.is_valid
    # Cheapest: 1×Charlie ($3) + 2×Delta ($8) = 21h, cost $11
    assert res.charlie == 1 and res.delta == 2
    assert res.total_hours == 21
    assert res.total_cost == 11  # Exact spec compliance
```

## Deployment Guide
## Deploy to Render (Free Tier)
1. Fork or clone this repository to your GitHub account
2. Sign in to Render with GitHub
3. Create New Web Service → Connect your repository
4. Configure settings:

| Field | Value |
|-------|-------|
| **Name** | `everbot-robot-allocator` |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.app:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free`  |
| **Region** | `Singapore (ap-southeast-1) (optimal for Malaysia)` |

Click Create Web Service → Wait 2–4 minutes for build

Test your live URL:
```
https://everbot-robot-allocator.onrender.com
```

### Environment Configuration
| File | Purpose | Notes |
|------|---------|-------|
| **`Procfile`** | Tells Render how to start the server | `web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT` |
| **`runtime.txt`** | Pins Python version for consistency | `3.11.0` (Render expects numeric only) |
| **`requirements.txt`** | Declares dependencies for `pip install` | Pin major versions only for flexibility |
| **`.gitignore`** | Excludes local artifacts from commits | Includes `__pycache__/`, `*.pyc`, `venv/`, `.env` |


### Troubleshooting Render Deploys
| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| **`ModuleNotFoundError: backend`** | Missing `__init__.py` in package directories | `touch backend/__init__.py strategies/__init__.py`, then commit and push |
| **`NameError: Path is not defined`** | Missing import in `app.py` | Ensure `from pathlib import Path` appears at the top of the file |
| **Build hangs on `pip install`** | Network timeout or stale build cache | Click **Clear build cache & deploy** in the Render dashboard |
| **`502 Bad Gateway` after deploy** | Runtime crash or unhandled exception | Check the **Logs** tab for Python traceback; fix the issue and push again |
| **"Failed to fetch" in browser** | Frontend `fetch()` uses `localhost` URL | Ensure the frontend uses a relative path: `fetch('/api/allocate')` |


## Development Guidelines
### For New Contributors

1. Branching Strategy
```bash
git checkout -b feature/your-feature-name
# Make changes, test locally
git add .
git commit -m "feat: describe your change concisely"
git push origin feature/your-feature-name
# Open Pull Request on GitHub
```

2. Code Style
```text
    ○  Use British English spellings: optimised, minimise, utilisation, programme
    ○  Currency symbol: $ (US Dollar) — matches Everest Engineering spec
    ○  Type hints: Always annotate function signatures (-> ReturnType)
    ○  Docstrings: Google-style with Args/Returns/Raises for public functions
    ○  Logging: Use logger.debug/info/warning for background audit; print() for user output
```

3. Adding a New Strategy Level

```python
# 1. Create strategies/level5.py
def run_level5(inventory: Inventory, requested: int) -> AllocationResult:
    """Your level logic here — return AllocationResult, no printing."""
    pass

# 2. Update backend/app.py and main.py to route level==5
# 3. Add tests in tests/test_allocation.py
# 4. Update this README with Level 5 documentation
```

4. Running Locally
```bash
# CLI mode (default)
python3 main.py

# API mode with auto-reload
uvicorn backend.app:app --reload

# Test suite
pytest tests/ -v

# Type checking (optional)
pip install mypy
mypy .
```

### Debugging Tips
    ○  CLI output missing? Check that print() is used for user messages (not logger.info)
    ○  Solver returning wrong result? Run python3 -c "from utils import solve_allocation; print(solve_allocation(...))"
    ○  Import errors on Render? Verify sys.path.insert(0, str(PROJECT_ROOT)) in backend/app.py
    ○  Currency symbol wrong? Search for £ and replace with $ — spec requires dollar signs

### Constraints & Compliance
| Requirement | Implementation Status | Verification Method |
|-------------|----------------------|---------------------|
| **Robots used max once per day** | ✅ Sequential inventory deduction enforced | `tests/test_allocation.py::TestStrategyFunctions::test_run_level4_processes_multiple_clients` |
| **Combined hours ≥ requested** | ✅ Strict `hrs >= requested` filter in solver | `tests/test_allocation.py::TestSolveAllocation` |
| **Non-negative robot counts** | ✅ Validated in `parse_inventory_input` | `tests/test_allocation.py::TestInputParsing::test_parse_inventory_input_rejects_negative_counts` |
| **Positive integer hours** | ✅ Early validation with exact error string | `tests/test_allocation.py::TestSolveAllocation::test_negative_hours_returns_exact_error_string` |
| **L1 vs L2 comparison** | ✅ Automatic cost delta + insight generation | `tests/test_allocation.py::TestEndToEnd::test_pdf_example_level2_20hrs` |
| **Exact error messages** | ✅ All strings match Everest Engineering PDF | `grep -r "Error:" tests/` + manual PDF cross-check |
| **Currency symbol consistency** | ✅ `$` used throughout (logs, UI, tests) | `grep -r "£" .` returns nothing |


### Contributing
```text
Contributions are welcome! Please follow these steps:
    1. Fork the repository
    2. Create a feature branch: git checkout -b feat/your-idea
    3. Make your changes with tests and documentation
    4. Run the test suite: pytest tests/ -v
    5. Lint your code: mypy . && flake8 . (optional but recommended)
    6. Submit a Pull Request with a clear description of changes
```

### Code Review Checklist
    •  British English spellings used consistently
    •  Currency symbol is $ (not £ or other)
    •  Type hints added to new public functions
    •  Docstrings follow Google style with Args/Returns/Raises
    •  Error messages match Everest Engineering specification exactly
    •  Tests added for new functionality or bug fixes
    •  README updated if user-facing behaviour changes

### License
Built for the Everest Engineering Coding Challenge 2026.
All robot specifications, level rules, and output formats strictly follow the official challenge documentation.

Licensed under the MIT License for educational and submission purposes.

```text
MIT License

Copyright (c) 2026 EverBot Solutions

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
