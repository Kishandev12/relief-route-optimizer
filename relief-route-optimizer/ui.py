import streamlit as st
import pandas as pd
import pulp

st.set_page_config(page_title="Relief Route Optimizer", page_icon="🚚", layout="wide")

st.title("Relief Route Optimizer")
st.caption("Compute an optimal shipment plan from depots to shelters")

run = st.sidebar.button("Solve scenario")

if run:
    supplies = {
        "Central_Warehouse": 120,
        "North_Depot": 80,
        "East_Depot": 60,
    }

    trucks = {
        "Central_Warehouse": 5,
        "North_Depot": 3,
        "East_Depot": 2,
    }

    demands = {
        "Shelter_A": 50,
        "Shelter_B": 70,
        "Shelter_C": 90,
    }

    cost = {
        ("Central_Warehouse", "Shelter_A"): 4,
        ("Central_Warehouse", "Shelter_B"): 6,
        ("Central_Warehouse", "Shelter_C"): 8,
        ("North_Depot", "Shelter_A"): 5,
        ("North_Depot", "Shelter_B"): 4,
        ("North_Depot", "Shelter_C"): 7,
        ("East_Depot", "Shelter_A"): 6,
        ("East_Depot", "Shelter_B"): 3,
        ("East_Depot", "Shelter_C"): 4,
    }

    TRUCK_CAPACITY = 20

    problem = pulp.LpProblem("Relief_Route_Optimization", pulp.LpMinimize)

    x = {
        (s, d): pulp.LpVariable(f"x_{s}_{d}", lowBound=0, cat="Continuous")
        for s in supplies
        for d in demands
    }

    problem += pulp.lpSum(cost[(s, d)] * x[(s, d)] for s in supplies for d in demands)

    for s in supplies:
        max_outflow = min(supplies[s], trucks[s] * TRUCK_CAPACITY)
        problem += pulp.lpSum(x[(s, d)] for d in demands) <= max_outflow

    for d in demands:
        problem += pulp.lpSum(x[(s, d)] for s in supplies) >= demands[d]

    status = problem.solve(pulp.PULP_CBC_CMD(msg=False))
    st.write(f"Solver status: **{pulp.LpStatus[status]}**")

    rows = []
    total_cost = 0.0

    for s in supplies:
        for d in demands:
            qty = x[(s, d)].value()
            if qty is None:
                qty = 0.0
            if qty > 1e-6:
                route_cost = qty * cost[(s, d)]
                total_cost += route_cost
                rows.append({
                    "from_supply": s,
                    "to_shelter": d,
                    "units_sent": round(qty, 2),
                    "cost_per_unit": cost[(s, d)],
                    "route_cost": round(route_cost, 2),
                })

    if rows:
        df = pd.DataFrame(rows)
        total_demand = sum(demands.values())
        total_shipped = df["units_sent"].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total demand (units)", int(total_demand))
        c2.metric("Total shipped (units)", int(total_shipped))
        c3.metric("Total transport cost", round(total_cost, 2))

        st.subheader("Optimal shipment plan")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("No feasible routes found.")
else:
    st.info("Click **Solve scenario** in the sidebar to run the optimizer.")
