import streamlit as st
import pandas as pd
import pulp

st.set_page_config(page_title="Relief Route Optimizer", page_icon="🚚", layout="wide")

st.title("Relief Route Optimizer")
st.caption("Compute an optimal shipment plan from depots to shelters")

st.sidebar.header("Run scenario")

uploaded_supplies = st.sidebar.file_uploader("Supplies CSV", type=["csv"])
uploaded_demands = st.sidebar.file_uploader("Demands CSV", type=["csv"])
uploaded_costs = st.sidebar.file_uploader("Costs CSV", type=["csv"])

run_clicked = st.sidebar.button("Solve scenario")

if run_clicked:
    if uploaded_supplies is not None and uploaded_demands is not None and uploaded_costs is not None:
        supplies_df = pd.read_csv(uploaded_supplies)
        demands_df = pd.read_csv(uploaded_demands)
        costs_df = pd.read_csv(uploaded_costs)
    else:
        supplies_df = pd.read_csv("supplies.csv")
        demands_df = pd.read_csv("demands.csv")
        costs_df = pd.read_csv("costs.csv")

    supplies = {row["supply"]: row["stock"] for _, row in supplies_df.iterrows()}
    trucks = {row["supply"]: row["trucks"] for _, row in supplies_df.iterrows()}
    demands = {row["shelter"]: row["demand"] for _, row in demands_df.iterrows()}

    cost = {(row["supply"], row["shelter"]): row["cost"] for _, row in costs_df.iterrows()}

    TRUCK_CAPACITY = 20

    problem = pulp.LpProblem("Relief_Route_Optimization", pulp.LpMinimize)

    x = {(s, d): pulp.LpVariable(f"x_{s}_{d}", lowBound=0, cat="Continuous")
         for s in supplies for d in demands}

    problem += pulp.lpSum(cost[(s, d)] * x[(s, d)] for s in supplies for d in demands)

    for s in supplies:
        max_outflow = min(supplies[s], trucks[s] * TRUCK_CAPACITY)
        problem += (pulp.lpSum(x[(s, d)] for d in demands) <= max_outflow)

    for d in demands:
        problem += (pulp.lpSum(x[(s, d)] for s in supplies) >= demands[d])

    status = problem.solve(pulp.PULP_CBC_CMD(msg=False))
    st.write(f"Solver status: **{pulp.LpStatus[status]}**")

    rows = []
    total_cost = 0.0

    for s in supplies:
        for d in demands:
            quantity = x[(s, d)].value()
            if quantity and quantity > 1e-6:
                route_cost = quantity * cost[(s, d)]
                total_cost += route_cost
                rows.append({
                    "from_supply": s,
                    "to_shelter": d,
                    "units_sent": round(quantity, 2),
                    "cost_per_unit": cost[(s, d)],
                    "route_cost": round(route_cost, 2)
                })

    if rows:
        df = pd.DataFrame(rows)

        total_demand = sum(demands.values())
        total_shipped = df["units_sent"].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total demand", total_demand)
        c2.metric("Total shipped", int(total_shipped))
        c3.metric("Total transport cost", round(total_cost, 2))

        st.subheader("Optimal shipment plan")
        st.dataframe(df, use_container_width=True)

        shelter_summary = df.groupby("to_shelter")["units_sent"].sum().reset_index()
        shelter_summary["required"] = shelter_summary["to_shelter"].map(demands)
        shelter_summary["gap"] = shelter_summary["units_sent"] - shelter_summary["required"]

        st.subheader("Shelter coverage summary")
        st.dataframe(shelter_summary, use_container_width=True)

        if "lat" in demands_df.columns and "lon" in demands_df.columns:
            st.subheader("Shelters Map")
