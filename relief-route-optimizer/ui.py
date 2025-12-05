import streamlit as st
import pandas as pd
import pulp

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Relief Route Optimizer",
    page_icon="🚚",
    layout="wide"
)

st.title("Relief Route Optimizer")
st.caption("Compute an optimal shipment plan from depots to shelters")

# -------------------------------
# SIDEBAR: SCENARIO INPUT
# -------------------------------
st.sidebar.header("Run scenario")

uploaded_supplies = st.sidebar.file_uploader("Supplies CSV", type=["csv"])
uploaded_demands = st.sidebar.file_uploader("Demands CSV", type=["csv"])
uploaded_costs = st.sidebar.file_uploader("Costs CSV", type=["csv"])

run_clicked = st.sidebar.button("Solve scenario")

if run_clicked:
    # Use uploaded files if all three are provided, else fall back to defaults
    if uploaded_supplies is not None and uploaded_demands is not None and uploaded_costs is not None:
        supplies_df = pd.read_csv(uploaded_supplies)
        demands_df = pd.read_csv(uploaded_demands)
        costs_df = pd.read_csv(uploaded_costs)
    else:
        supplies_df = pd.read_csv("supplies.csv")
        demands_df = pd.read_csv("demands.csv")
        costs_df = pd.read_csv("costs.csv")

    # -------------------------------
    # BUILD DICTS FROM DATAFRAMES
    # -------------------------------
    supplies = {row["supply"]: row["stock"] for _, row in supplies_df.iterrows()}
    trucks = {row["supply"]: row["trucks"] for _, row in supplies_df.iterrows()}
    demands = {row["shelter"]: row["demand"] for _, row in demands_df.iterrows()}

    cost = {
        (row["supply"], row["shelter"]): row["cost"]
        for _, row in costs_df.iterrows()
    }

    TRUCK_CAPACITY = 20  # units per truck

    # -------------------------------
    # OPTIMIZATION MODEL
    # -------------------------------
    problem = pulp.LpProblem("Relief_Route_Optimization", pulp.LpMinimize)

    # Decision variables
    x = {
        (s, d): pulp.LpVariable(f"x_{s}_{d}", lowBound=0, cat="Continuous")
        for s in supplies
        for d in demands
    }

    # Objective: minimize total transport cost
    problem += pulp.lpSum(cost[(s, d)] * x[(s, d)] for s in supplies for d in demands)

    # Supply + truck constraints
    for s in supplies:
        stock_limit = supplies[s]
        truck_limit = trucks[s] * TRUCK_CAPACITY
        max_outflow = min(stock_limit, truck_limit)
        problem += (
            pulp.lpSum(x[(s, d)] for d in demands) <= max_outflow,
            f"Outflow_limit_{s}"
        )

    # Demand constraints
    for d in demands:
        problem += (
            pulp.lpSum(x[(s, d)] for s in supplies) >= demands[d],
            f"Demand_requirement_{d}"
        )

    # -------------------------------
    # SOLVE
    # -------------------------------
    status = problem.solve(pulp.PULP_CBC_CMD(msg=False))
    st.write(f"Solver status: **{pulp.LpStatus[status]}**")

    # -------------------------------
    # BUILD OUTPUT TABLE
    # -------------------------------
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

        # KPIs
        total_demand = sum(demands.values())
        total_shipped = df["units_sent"].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total demand (units)", int(total_demand))
        c2.metric("Total shipped (units)", int(total_shipped))
        c3.metric("Total transport cost", round(total_cost, 2))

        st.subheader("Optimal shipment plan")
        st.dataframe(df, use_container_width=True)

        st.subheader("Shelter coverage summary")
        shelter_summary = df.groupby("to_shelter")["units_sent"].sum().reset_index()
        shelter_summary["required"] = shelter_summary["to_shelter"].map(demands)
        shelter_summary["gap"] = shelter_summary["units_sent"] - shelter_summary["required"]
        st.dataframe(shelter_summary, use_container_width=True)
    else:
        st.error("No feasible routes found. Check your input data.")
else:
    st.info("Upload CSVs if you want, then click **Solve scenario** in the sidebar.")
