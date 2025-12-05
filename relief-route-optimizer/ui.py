import streamlit as st
import pandas as pd
import pulp

st.set_page_config(page_title="Relief Route Optimizer", page_icon="🚚", layout="wide")

st.title("Relief Route Optimizer")
st.caption("Compute an optimal shipment plan from depots to shelters")

st.sidebar.header("Run scenario")

if st.sidebar.button("Solve current CSV scenario"):
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

    TRUCK_CAPACITY = 20

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

    status = problem.solve(pulp.PULP_CBC_CMD(msg=False))
    st.write(f"Solver status: **{pulp.LpStatus[status]}**")

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

    if rows:
        df = pd.DataFrame(rows)
        st.subheader("Optimal shipment plan")
        st.dataframe(df, use_container_width=True)
        st.metric("Total transport cost", round(total_cost, 2))
    else:
        st.error("No feasible solution found. Check CSV inputs.")
else:
    st.info("Click 'Solve current CSV scenario' in the sidebar to run the optimizer.")
