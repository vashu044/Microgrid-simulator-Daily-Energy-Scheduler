# Microgrid-simulator-Daily-Energy-Scheduler
## Project Overview

This project is a **time-based microgrid simulation and daily energy scheduling system** developed as a working MVP for the **DEIV Labs Hackathon / Virtual Labs theme**. The simulator models how energy is generated, stored, consumed, and exchanged with the utility grid over a 24‑hour period, and demonstrates how intelligent scheduling can reduce energy cost and grid dependency.

The system is designed with an **educational Virtual Lab mindset**, making internal decisions and energy flows transparent and easy to understand.

---

## Objectives

* Simulate a **24-hour microgrid operation** using hourly time steps
* Model **renewable generation (solar)**, **battery storage**, **load demand**, and **grid interaction**
* Implement and compare:

  * A **naïve scheduling strategy**
  * An **optimized energy scheduling strategy**
* Minimize:

  * Total grid energy cost
  * Peak grid usage
* Provide an **interactive Streamlit-based interface** for experimentation

---

## System Components

### 1. Renewable Energy Source

* Solar generation modeled using a simple time-based profile
* Peak generation during mid-day hours

### 2. Load Model

* Residential-style daily load profile
* Includes **load shifting**, where flexible loads are moved from peak-price hours to high-solar / low-price hours

### 3. Battery Energy Storage System (BESS)

* Configurable battery capacity
* State of Charge (SOC) tracking
* Charge and discharge power limits
* Charging efficiency modeled

### 4. Grid Interaction

* Energy can be:

  * Purchased from the grid during deficit
  * Sold back to the grid during surplus (grid sell-back)
* Time-of-use grid pricing supported

---

## Energy Scheduling Strategies

### Naïve Scheduler

* Does not use the battery intelligently
* Directly buys energy from the grid during deficit
* Sells excess solar energy to the grid
* Serves as a **baseline for comparison**

### Optimized Scheduler

* Prioritizes solar energy usage
* Charges the battery during surplus generation
* Discharges the battery during high grid price periods
* Sells excess energy to the grid only when allowed
* Demonstrates **cost-aware and energy-efficient decision making**

---

## Simulation Logic

The simulation runs in discrete hourly steps:

```
Solar + Grid Buy + Battery Discharge
= Load + Battery Charge + Grid Sell
```

At each hour:

1. Renewable generation and load demand are read
2. Scheduler decides battery and grid actions
3. Battery SOC is updated
4. Grid cost or revenue is calculated

---

## Outputs and Visualization

* Hour-wise plots for:

  * Grid energy bought
  * Grid energy sold
  * Battery State of Charge (SOC)
* Total daily energy cost
* Tabular view of hourly results
* CSV export of simulation data for offline analysis

---

## Interactive Virtual Lab (Streamlit)

The Streamlit interface allows users to:

* Select scheduling strategy (Naïve vs Optimized)
* Visualize energy flows in real time
* Observe cost differences
* Export simulation results as CSV

Run the app using:

```bash
streamlit run app.py
```

---

## Project Structure

```
microgrid_simulator/
│
├── app.py              # Streamlit Virtual Lab UI
├── main.py             # Optional CLI execution
├── config.py           # System parameters
├── profiles.py         # Load and solar profiles
├── battery.py          # Battery model
├── scheduler.py        # Energy scheduling logic
├── simulator.py        # Time-based simulation engine
├── metrics.py          # Cost calculations
├── visualization.py   # Plotting utilities
├── export.py           # CSV export
└── README.md
```

---

## Educational Value

This project helps learners understand:

* Microgrid energy flow and balance
* Role of storage in renewable integration
* Impact of time-of-use pricing
* Benefits of intelligent energy scheduling

---

## Conclusion

The Microgrid Simulator + Daily Energy Scheduler is a **complete, working MVP** that combines simulation, optimization, and visualization. It demonstrates practical concepts in **smart energy systems** and serves as a strong foundation for further extensions such as advanced optimization, uncertainty modeling, and real-world data integration.

---

## Author / Team

Developed as part of the **DEIV Labs Hackathon / Virtual Labs initiative**.
