import pandas as pd
import pulp

# -------------------------------
# 1. READ INPUT DATA FROM CSV
# -------------------------------

supplies_df = pd.read_csv("supplies.csv")
demands_df = pd.read_csv("demands.csv")
costs_df = pd.read_csv("costs.csv")

supplies = {row["supply"]: row["stock"] for _, row in supplies_df.iterrows()}
trucks = {row["supply"]: row["trucks"] for _, row in supplies_df.iterrows()}
demands = {row["shelter"]: row["demand"] for _, row in demands_df.iterrows()}

cost = {
    (row["supply"], row["shelter"]): row["cost"]
    for _, row in costs_df.iterrows()
}

TRUCK_CAPACITY = 20  # units per truck

# -------------------------------
# 2. DEFINE OPTIMIZATION MODEL
# -------------------------------

problem = pulp.LpProblem("Relief_Route_Optimization", pulp.LpMinimize)

x = {
    (s, d): pulp.LpVariable(f"x_{s}_{d}", lowBound=0, cat="Continuous")
    for s in supplies
    for d in demands
}

problem += pulp.lpSum(cost[(s, d)] * x[(s, d)] for s in supplies for d in demands)

for s in supplies:
    stock_limit = supplies[s]
    truck_limit = trucks[s] * TRUCK_CAPACITY
    max_outflow = min(stock_limit, truck_limit)

    problem += (
        pulp.lpSum(x[(s, d)] for d in demands) <= max_outflow,
        f"Outflow_limit_{s}"
    )

for d in demands:
    problem += (
        pulp.lpSum(x[(s, d)] for s in supplies) >= demands[d],
        f"Demand_requirement_{d}"
    )

# -------------------------------
# 3. SOLVE
# -------------------------------

solution_status = problem.solve(pulp.PULP_CBC_CMD(msg=False))

# -------------------------------
# 4. OUTPUT
# -------------------------------

print("Status:", pulp.LpStatus[solution_status])
print()

rows = []
total_cost = 0.0

for s in supplies:
    for d in demands:
        quantity = x[(s, d)].value()
        if quantity is None:
            quantity = 0.0
        if quantity > 1e-6:
            route_cost = cost[(s, d)] * quantity
            total_cost += route_cost
            rows.append({
                "from_supply": s,
                "to_shelter": d,
                "units_sent": round(quantity, 2),
                "cost_per_unit": cost[(s, d)],
                "route_cost": round(route_cost, 2),
            })

df = pd.DataFrame(rows)

print("Optimal shipment plan:")
print(df.to_string(index=False))
print()
print("Total cost:", round(total_cost, 2))

print("\nSupply utilization:")
for s in supplies:
    shipped = sum(x[(s, d)].value() for d in demands)
    print(f"  {s}: shipped {round(shipped, 2)} / stock {supplies[s]} (trucks: {trucks[s]})")

print("\nDemand coverage:")
for d in demands:
    received = sum(x[(s, d)].value() for s in supplies)
    print(f"  {d}: received {round(received, 2)} / required {demands[d]}")

