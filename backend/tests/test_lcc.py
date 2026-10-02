import unittest
from dataclasses import replace
from backend.app.calculations.lcc import (
    area_m2,
    discount_factor,
    present_value,
    escalate,
    energy_cost,
    water_cost,
    maintenance_cost,
    indexed_cost,
    Scenario,
    Component,
    Assumptions,
    calculate,
    compare,
    sensitivity,
)


class FinancialTests(unittest.TestCase):
    def setUp(self):
        self.c = Scenario(1000, 100, 10, 20, 0.3, 1, 2, 100)
        self.a = Assumptions(2, 0.1, 0, 0, 0, 0, 0)

    def test_units(self):
        self.assertAlmostEqual(area_m2(100, "ft²"), 9.2903)

    def test_discount_and_pv(self):
        self.assertAlmostEqual(discount_factor(0.1, 2), 1 / 1.21)
        self.assertAlmostEqual(present_value(121, 0.1, 2), 100)

    def test_escalation(self):
        self.assertAlmostEqual(escalate(100, 0.1, 2), 121)

    def test_energy(self):
        self.assertEqual(energy_cost(100, 0.3, 1), 395)

    def test_water_fixed_not_reduced(self):
        self.assertEqual(water_cost(10 * 0.6, 2, 100), 112)

    def test_maintenance(self):
        self.assertEqual(maintenance_cost(1000, None, 0.02), 20)
        self.assertEqual(maintenance_cost(1000, 0, 0.02), 0)

    def test_manual_example(self):
        # Manually: C0=1000; E=395, W=120, M=20 => 535 at t1 and t2.
        expected = 1000 + 535 / 1.1 + 535 / 1.21
        self.assertAlmostEqual(calculate(self.c, self.a)["total_lcc"], expected)

    def test_replacements(self):
        s = replace(self.c, replacements=(Component("HVAC", 2, 100, 0),))
        rows = calculate(s, replace(self.a, years=6))["cashflows"]
        self.assertEqual([r["year"] for r in rows if r["replacement"]], [2, 4])

    def test_terminal(self):
        s = replace(self.c, disposal=200, residual=50)
        difference = calculate(s, self.a)["total_lcc"] - calculate(self.c, self.a)["total_lcc"]
        self.assertAlmostEqual(difference, 150 / 1.21)

    def test_savings(self):
        s = replace(self.c, capital=900)
        result = compare(self.c, s, self.a)
        self.assertAlmostEqual(result["savings_aud"], 100)
        self.assertAlmostEqual(result["savings_percent"], 100 / result["conventional"]["total_lcc"] * 100)
        self.assertEqual(result["break_even_year"], 0)

    def test_break_even(self):
        s = replace(self.c, capital=1010, maintenance=0)
        self.assertEqual(compare(self.c, s, self.a)["break_even_year"], 1)

    def test_no_break_even(self):
        self.assertIsNone(compare(self.c, replace(self.c, capital=2000), self.a)["break_even_year"])

    def test_horizons(self):
        for n in (30, 40, 50):
            rows = calculate(self.c, replace(self.a, years=n))["cashflows"]
            self.assertEqual(len(rows), n + 1)
            self.assertEqual(rows[-1]["year"], n)

    def test_sensitivity(self):
        cells = sensitivity(self.c, self.c, self.a)
        self.assertEqual(len(cells), 48)
        self.assertEqual(len({(c["years"], c["discount"], c["energy_escalation"]) for c in cells}), 48)
        self.assertTrue(all(c["savings_aud"] == 0 for c in cells))

    def test_index_ratio(self):
        self.assertEqual(indexed_cost(100000, 100, 150), 150000)


if __name__ == "__main__":
    unittest.main()
