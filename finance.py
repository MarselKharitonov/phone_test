"""Illustrative unit economics; all inputs are hypotheses, not provider pricing."""
import math

SCENARIOS = {
    "optimistic": dict(price=99, fee_rate=.04, fee_fixed=2, tax=.06, cac=10, gpu=5, p=.90, other=3, refund=.01, fixed=15000),
    "base": dict(price=99, fee_rate=.05, fee_fixed=3, tax=.06, cac=20, gpu=8, p=.80, other=4, refund=.02, fixed=15000),
    "stress": dict(price=99, fee_rate=.08, fee_fixed=5, tax=.06, cac=40, gpu=15, p=.60, other=8, refund=.05, fixed=15000),
}


def calculate(n, s):
    if n < 0 or not 0 <= s["p"] <= 1 or not 0 <= s["refund"] <= 1:
        raise ValueError("Invalid order count or probability")
    success = s["p"] * (2 - s["p"])
    attempts = 2 - s["p"]
    gross = n * s["price"]
    refunds = gross * (1 - success + success * s["refund"])
    costs_per_order = (s["price"] * (s["fee_rate"] + s["tax"]) + s["fee_fixed"]
                       + s["cac"] + s["gpu"] * attempts + s["other"])
    contribution_per_order = s["price"] * success * (1 - s["refund"]) - costs_per_order
    contribution = n * contribution_per_order
    break_even = math.ceil(s["fixed"] / contribution_per_order) if contribution_per_order > 0 else None
    return dict(gross=gross, refunds=refunds, net=gross - refunds,
                contribution=contribution, result=contribution - s["fixed"],
                break_even=break_even, success=success, attempts=attempts)


if __name__ == "__main__":
    print("Illustrative RUB scenarios; not actual quotes.")
    for name, scenario in SCENARIOS.items():
        print(f"\n{name}:")
        for orders in (100, 1000, 10000, 30000):
            r = calculate(orders, scenario)
            be = str(r["break_even"]) if r["break_even"] is not None else "none"
            print(f"{orders:>6} orders | gross {r['gross']:>10.0f} | refunds {r['refunds']:>9.0f} | net {r['net']:>10.0f} | contribution {r['contribution']:>10.0f} | after fixed {r['result']:>10.0f} | break-even {be}")
