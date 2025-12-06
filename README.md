# Relief Route Optimizer

Relief Route Optimizer is a logistics decision engine designed for disaster response control rooms. It calculates optimal shipment plans from supply depots to relief shelters with the objective of minimizing transport cost while ensuring demand coverage under real operational constraints.

This tool is built to simulate situations where every minute and every truck matters. Relief allocation is traditionally done through intuition and fragmented spreadsheets. That results in wasted capacity, delayed response, and supply imbalance across shelters. The model assigns shipments across the complete depot-to-shelter network using linear programming to deliver the most efficient allocation possible.

---

## Core Value Proposition

Real-time routing engine that:
• Allocates supplies from available depots to multiple shelters
• Respects depot stock limits and truck availability
• Enforces realistic truck capacity constraints
• Meets or exceeds shelter demand
• Minimizes total transport cost across the network

This mirrors real disaster logistics operations where relief agencies determine how many vehicles to send from each warehouse and where to prioritize shipments.

---

## How It Works

Inputs
• Supplies available at depots
• Trucks at each depot
• Demand values for each relief shelter
• Transport cost per unit for each route

Optimization Objective
• Minimize total transport cost

Constraints
• Quantity shipped from each depot cannot exceed the minimum of available stock or total fleet capacity
• Quantity received at each shelter must satisfy or exceed demand

Output
• Optimal shipment matrix (depot → shelter)
• Scenario-wide KPIs
• Cost and payload metrics
• Ranked insights on route importance and priority shelters

---

## Technology Stack

• Python  
• Streamlit dashboard  
• PuLP linear programming engine  
• Pandas for data handling  

The application runs locally using:
streamlit run ui.py


---

## Included Scenarios

Baseline
• Typical supply distribution scenario to demonstrate basic efficiency

Earthquake In Metro City
• Demand surge and skewed distribution requiring high-capacity depot reliance

Flooded River District
• Balanced supply with fragmented access and increased transport constraints

More scenarios can be introduced for simulation by modifying the embedded dictionaries in `ui.py`.

---

## Outputs and Interpretation

Shipment Table
• Lists every active route, quantity, unit cost, and route-level cost

KPIs
• Total demand vs total shipped
• Status of solver performance
• Overall operation cost

Insights Panel
• Highlights highest-volume route
• Identifies priority shelter
• Notes strategic implications for adding trucks or capacity

This enables decision makers to immediately evaluate tradeoffs and adjust strategy.

---

## Problem Statement

Disaster response suffers from inefficient resource movement:
• Large depots oversupply low-priority shelters
• High-priority shelters remain undersupplied
• Fuel and manpower are wasted on non-optimal routing
• Decision making is delayed by manual spreadsheets

The Relief Route Optimizer replaces guesswork with data-driven allocation in real time. It gives agencies the capability to run multiple scenarios and rapidly deploy resources with measurable efficiency.

---

## Why This Matters

During disaster operations, logistics failures directly cost lives. The first 24 hours determine survival rates, and the difference between strategic allocation and random distribution is measurable. This model provides a tactical planning interface specifically designed to convert raw warehouse and shelter data into actionable operational routes.

---

## Future Roadmap

• Integration with real map routing APIs for travel time and geodesic distance
• Support for road blockages and network failures
• Severity-weighted prioritization
• GPS tracking and real-time status updates
• API endpoints for integration with NDMA, State DCRs, and NDRF control systems
• PDF and CSV export
• Deployment to cloud infrastructure for remote access

---

## Usage

Clone repository:
git clone https://github.com/Kishandev12/relief-route-optimizer
cd relief-route-optimizer



Create and activate environment:
python3 -m venv venv
source venv/bin/activate



Install requirements:
pip install -r requirements.txt



Run app:
streamlit run ui.py




---

## Current Status

MVP complete and functional locally.  
Core optimization validated.  
Scenario-based UI operational.  

Next stage: production deployment, map visualization, and government-grade field integration.

