import pytest
from robot_allocator.models import Inventory
from robot_allocator.utils import solve_allocation, parse_clients_input

class TestAllocationEngine:
    def test_l1_minimize_excess_16hrs(self):
        inv = {"Bravo": 2, "Charlie": 3, "Delta": 2}
        res = solve_allocation(16, inv, "hours")
        assert res.is_valid
        assert res.bravo == 1 and res.charlie == 1 and res.delta == 1
        assert res.total_hours == 16
        assert res.total_cost == 9

    def test_l2_minimize_cost_20hrs(self):
        inv = {"Bravo": 2, "Charlie": 3, "Delta": 2}
        res = solve_allocation(20, inv, "cost")
        assert res.is_valid
        assert res.charlie == 1 and res.delta == 2
        assert res.total_cost == 11  # 3 + 2*4
        assert res.total_hours == 21

    def test_l2_exact_fit_6hrs(self):
        inv = {"Bravo": 2, "Charlie": 2, "Delta": 3}
        res = solve_allocation(6, inv, "cost")
        assert res.is_valid
        assert res.bravo == 2
        assert res.total_cost == 4

    def test_insufficient_capacity(self):
        inv = {"Bravo": 0, "Charlie": 0, "Delta": 0}
        res = solve_allocation(10, inv, "cost")
        assert not res.is_valid
        assert "Insufficient" in res.error

    def test_invalid_hours(self):
        res = solve_allocation(-5, {"Bravo": 1}, "cost")
        assert not res.is_valid

    def test_client_parsing(self):
        assert parse_clients_input("12, 16, 17") == [12, 16, 17]
        assert parse_clients_input("20 15 10") == [20, 15, 10]
        with pytest.raises(ValueError):
            parse_clients_input("0, -5")
