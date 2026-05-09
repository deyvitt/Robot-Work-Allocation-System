# ~/RobotWorkAllocationSystem/tests/test_allocation.py

"""
Test suite for the Robot Work Allocation System.
Covers:
- Core solver logic (solve_allocation)
- Input validation (parse_clients_input, parse_inventory_input)
- Strategy functions (run_level1–run_level4)
- Edge cases and PDF-compliant error messages
Run with: pytest tests/ -v --cov=robot_allocator
"""

import pytest
from utils import (
    solve_allocation,
    parse_clients_input,
    parse_inventory_input,
    calculate_max_capacity,
    format_allocation
)
from strategies.level1 import run_level1
from strategies.level2 import run_level2
from strategies.level3 import run_level3
from strategies.level4 import run_level4
from models import Inventory, AllocationResult

# =============================================================================
# Fixtures: Reusable test data
# =============================================================================
@pytest.fixture
def sample_inventory():
    """Standard test inventory: 2 Bravo, 3 Charlie, 2 Delta."""
    return Inventory(bravo=2, charlie=3, delta=2)

@pytest.fixture
def empty_inventory():
    """Zero-robot inventory for negative testing."""
    return Inventory(bravo=0, charlie=0, delta=0)


# =============================================================================
# Core Solver Tests: solve_allocation
# =============================================================================
class TestSolveAllocation:
    """Tests for the bounded brute-force allocation solver."""

    def test_l1_minimize_excess_16hrs_exact_fit(self, sample_inventory):
        """Level 1: Request exactly 16h → should find perfect fit with category diversity."""
        res = solve_allocation(16, sample_inventory.to_dict(), objective="hours")
        assert res.is_valid
        # 1×Bravo (3h) + 1×Charlie (5h) + 1×Delta (8h) = 16h, cost $9
        assert res.bravo == 1 and res.charlie == 1 and res.delta == 1
        assert res.total_hours == 16
        assert res.total_cost == 9

    def test_l2_minimize_cost_20hrs(self, sample_inventory):
        """Level 2: Request 20h → minimise cost, accept slight excess."""
        res = solve_allocation(20, sample_inventory.to_dict(), objective="cost")
        assert res.is_valid
        # Cheapest: 1×Charlie ($3) + 2×Delta ($8) = 21h, cost $11
        assert res.charlie == 1 and res.delta == 2
        assert res.total_hours == 21
        assert res.total_cost == 11

    def test_l2_exact_fit_6hrs_cheapest_option(self):
        """Level 2: Request 6h → two Bravo ($4) cheaper than one Charlie ($3) + excess."""
        inv = {"Bravo": 2, "Charlie": 2, "Delta": 3}
        res = solve_allocation(6, inv, objective="cost")
        assert res.is_valid
        # 2×Bravo = 6h, cost $4 (vs 1×Charlie = 5h + excess, cost $3 but violates exact fit preference)
        assert res.bravo == 2
        assert res.total_cost == 4

    def test_zero_inventory_returns_exact_error_string(self, empty_inventory):
        """Constraint: Zero robots → exact PDF-compliant error message."""
        res = solve_allocation(10, empty_inventory.to_dict(), objective="cost")
        assert not res.is_valid
        # Must match Everest Engineering spec exactly
        assert res.error == "Error: No robots available for assignment."

    def test_negative_hours_returns_exact_error_string(self):
        """Constraint: Invalid input (hours ≤ 0) → exact PDF-compliant error."""
        res = solve_allocation(-5, {"Bravo": 1}, objective="cost")
        assert not res.is_valid
        assert res.error == "Error: Work hours must be a positive integer."

    def test_impossible_allocation_exact_error_string(self):
        """Constraint: No valid combination → exact PDF-compliant error."""
        # Request 100h but only 1 Bravo available (max 3h)
        inv = {"Bravo": 1, "Charlie": 0, "Delta": 0}
        res = solve_allocation(100, inv, objective="cost")
        assert not res.is_valid
        assert res.error == "Error: Unable to allocate at least one robot from each category with the available inventory."

    @pytest.mark.parametrize("requested,expected_valid", [
        (1, True),      # Minimum valid request
        (1000, True),   # Large request (solver bounds should handle)
        (0, False),     # Boundary: zero
        (-1, False),    # Negative
    ])
    def test_request_boundaries(self, requested, expected_valid):
        """Parametric test: solver handles edge request values correctly."""
        inv = {"Bravo": 10, "Charlie": 10, "Delta": 10}
        res = solve_allocation(requested, inv, objective="cost")
        assert res.is_valid == expected_valid


# =============================================================================
# Input Parsing Tests
# =============================================================================
class TestInputParsing:
    """Tests for input validation helpers."""

    def test_parse_clients_input_comma_separated(self):
        """Parse comma-separated hours string."""
        assert parse_clients_input("12, 16, 17") == [12, 16, 17]

    def test_parse_clients_input_space_separated(self):
        """Parse space-separated hours string."""
        assert parse_clients_input("20 15 10") == [20, 15, 10]

    def test_parse_clients_input_mixed_delimiters(self):
        """Parse mixed comma/space delimiters."""
        assert parse_clients_input("12, 16 17, 10") == [12, 16, 17, 10]

    def test_parse_clients_input_rejects_zero_or_negative(self):
        """Reject non-positive hours with clear error."""
        with pytest.raises(ValueError, match="positive integers"):
            parse_clients_input("0, -5")

    def test_parse_clients_input_rejects_non_numeric(self):
        """Reject non-numeric input with clear error."""
        with pytest.raises(ValueError, match="Invalid input"):
            parse_clients_input("abc, 12")

    def test_parse_inventory_input_rejects_negative_counts(self):
        """Inventory validation: reject negative robot counts."""
        with pytest.raises(ValueError, match="non-negative"):
            parse_inventory_input(-1, 2, 3)


# =============================================================================
# Utility Function Tests
# =============================================================================
class TestUtilities:
    """Tests for helper functions."""

    def test_calculate_max_capacity(self):
        """Verify capacity calculation: B×3 + C×5 + D×8."""
        inv = Inventory(bravo=2, charlie=3, delta=2)
        # 2×3 + 3×5 + 2×8 = 6 + 15 + 16 = 37
        assert calculate_max_capacity(inv) == 37

    def test_format_allocation_non_zero_only(self):
        """Format only assigned robot types (skip zero counts)."""
        res = AllocationResult(bravo=2, charlie=0, delta=1)
        assert format_allocation(res) == "Bravo: 2, Delta: 1"

    def test_format_allocation_all_zero(self):
        """Format empty allocation gracefully."""
        res = AllocationResult()
        assert format_allocation(res) == "None"


# =============================================================================
# Strategy Function Tests (Integration-Level)
# =============================================================================
class TestStrategyFunctions:
    """Tests for level-specific strategy wrappers."""

    def test_run_level1_returns_valid_allocation(self, sample_inventory):
        """Level 1 strategy: returns structured AllocationResult."""
        result = run_level1(sample_inventory, 16)
        assert isinstance(result, AllocationResult)
        assert result.is_valid
        assert result.total_hours >= 16

    def test_run_level2_returns_cost_optimised_result(self, sample_inventory):
        """Level 2 strategy: cost-minimised allocation with comparison data."""
        l1 = run_level1(sample_inventory, 20)
        l2 = run_level2(sample_inventory, 20, l1_alloc=l1)
        assert l2.is_valid
        # Level 2 should be <= Level 1 cost (or equal if already optimal)
        assert l2.total_cost <= l1.total_cost

    def test_run_level3_sufficient_capacity(self, sample_inventory):
        """Level 3: request within active capacity → no standby needed."""
        result = run_level3(sample_inventory, 10)  # Capacity is 37h
        assert result["sufficient"] is True
        assert result["deficit"] == 0
        assert result["standby"] is None

    def test_run_level3_deficit_triggers_standby(self, sample_inventory):
        """Level 3: request exceeds capacity → standby allocation returned."""
        result = run_level3(sample_inventory, 100)  # Exceeds 37h capacity
        assert result["sufficient"] is False
        assert result["deficit"] > 0
        assert result["standby"] is not None
        assert result["standby"].is_valid

    def test_run_level4_processes_multiple_clients(self, sample_inventory):
        """Level 4: sequential allocation for multiple clients."""
        clients = [12, 16, 17]
        result = run_level4(sample_inventory, clients)
        assert "allocations" in result
        assert "summary" in result
        assert len(result["allocations"]) == 3
        # All clients should have a status field
        for alloc in result["allocations"]:
            assert alloc["status"] in ["allocated", "standby_required", "impossible"]


# =============================================================================
# End-to-End Integration Test
# =============================================================================
class TestEndToEnd:
    """Smoke test: full allocation flow matching PDF examples."""

    def test_pdf_example_level2_20hrs(self):
        """Reproduce Everest Engineering Level 2 example exactly."""
        inv = Inventory(bravo=2, charlie=3, delta=2)
        l1 = run_level1(inv, 20)
        l2 = run_level2(inv, 20, l1_alloc=l1)

        # Level 1: category diversity preference
        assert l1.is_valid
        assert l1.total_hours >= 20

        # Level 2: cost optimisation
        assert l2.is_valid
        assert l2.total_cost == 11  # $11 = 1×Charlie ($3) + 2×Delta ($8)
        assert l2.total_hours == 21  # 5 + 2×8

        # Comparison insight
        diff = l1.total_cost - l2.total_cost
        assert diff >= 0  # Level 2 should never cost more
