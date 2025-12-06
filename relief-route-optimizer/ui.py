import streamlit as st
import pandas as pd
import pulp

st.set_page_config(page_title="Relief Route Optimizer", page_icon="🚚", layout="wide")

st.title("Relief Route Optimizer")
st.caption("Logistics decision engine for disaster relief convoys")

st.markdown(
    """
This tool simulates how a disaster control room allocates trucks from depots to relief shelters.

It takes three things as inputs:

1. Available stock and trucks at each supply point  
2. Demand at each shelter  
3. Transport cost per unit along each route  

Then it uses linear programming to compute the cheapest network wide shipment plan that still covers demand.
"""
)

st.sidebar.header("Control panel")

scenario = st.sidebar.selectbox(
    "Choose scenario",
    ["Baseline", "Earthquake in metro city", "Flooded river district"],
)

run = st.sidebar.button("Solve scenario")


def load_scenario(name: str):
    if name == "Earthquake in metro city":
        supplies = {
            "Central_Warehouse": 150,
            "North_Depot": 60,
            "East_Depot": 40,
        }
        trucks = {
            "Central_Warehouse": 7,
            "North_Depot": 3,
            "East_Depot": 2,
        }
        demands = {
            "Shelter_A": 80,
            "Shelter_B": 90,
            "Shelter_C": 60,
        }
    elif name == "Flooded river district":
        supplies = {
            "Central_Warehouse": 100,
            "North_Depot": 100,
            "East_Depot": 80,
        }
        trucks = {
            "Central_Warehouse": 4,
            "North_Depot": 4,
            "East_Depot": 3,
        }
        demands = {
            "Shelter_A": 70,
            "Shelter_B": 60,
            "Shelter_C": 80,
        }
    else:  # Baseline
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

    return supplies, trucks, demands, cost


if run:
    supplies, trucks, demands, cost = load_scenario(scenario)

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
    status_text = pulp.LpStatus[status]

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
                rows.append(
                    {
                        "from_supply": s,
                        "to_shelter": d,
                        "units_sent": round(qty, 2),
                        "cost_per_unit": cost[(s, d)],
                        "route_cost": round(route_cost, 2),
                    }
                )

    if rows:
        df = pd.DataFrame(rows)
        total_demand = sum(demands.values())
        total_shipped = df["units_sent"].sum()

        st.subheader("Scenario metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Scenario", scenario)
        c2.metric("Solver status", status_text)
        c3.metric("Total demand (units)", int(total_demand))
        c4.metric("Total shipped (units)", int(total_shipped))

        st.subheader("Optimal shipment plan")
        st.dataframe(df, use_container_width=True)

        st.subheader("Insights for control room")

        top_route = df.loc[df["units_sent"].idxmax()]
        top_shelter = (
            df.groupby("to_shelter")["units_sent"].sum().sort_values(ascending=False).index[0]
        )

        st.markdown(
            f"""
- Highest volume route: **{top_route['from_supply']} → {top_route['to_shelter']}**  
- Highest priority shelter by volume: **{top_shelter}**  
- Model automatically throttles depots once they hit combined stock plus truck capacity.  
- Any increase in trucks at a high volume depot will usually cut total transport cost for this scenario.
"""
        )
    else:
        st.error("No feasible routes found for this scenario.")
else:
    st.info("Select a scenario in the sidebar and click **Solve scenario**.")
