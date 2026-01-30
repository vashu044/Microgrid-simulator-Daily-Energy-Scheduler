# 🏗️ Complete Project Structure Guide

## 📦 Your New EMS Project Structure

```
microgrid_ems/
│
├── backend/                          # Business Logic (Pure Python)
│   ├── __init__.py                   # Package init
│   ├── battery_model.py              # Battery physics (6KB)
│   ├── energy_profiles.py            # Solar & load profiles (9KB)
│   ├── schedulers.py                 # 7 control strategies (13KB)
│   ├── simulator.py                  # Simulation engine (9KB)
│   ├── metrics.py                    # KPI calculations (11KB)
│   ├── pricing.py                    # Pricing models (5KB)
│   └── export_utils.py               # Data export (6KB)
│
├── frontend/                         # UI Layer (Streamlit)
│   ├── __init__.py                   # Package init
│   ├── app.py                        # Main Streamlit app (9KB)
│   └── components.py                 # UI components (16KB)
│
├── config/                           # Configuration
│   └── settings.py                   # System parameters
│
├── data/                             # Data files (for sample data)
│
├── outputs/                          # Output files
│   └── plots/                        # Generated plots
│
├── requirements.txt                  # Dependencies
└── README.md                         # Documentation
```

---

## 🎯 File Responsibilities

### Backend Files (No UI Code)

#### 1. `battery_model.py` (6KB)
**What it does:**
- Battery physics simulation
- Degradation tracking (throughput + cycle-based)
- Thermal effects
- State of Health (SOH) calculation
- C-rate limiting

**Main class:**
```python
Battery(capacity, soc, max_charge, max_discharge, efficiency, temperature)
```

**Key methods:**
- `charge(energy)` - Charge battery
- `discharge(energy)` - Discharge battery
- `get_metrics()` - Get comprehensive metrics

---

#### 2. `energy_profiles.py` (9KB)
**What it does:**
- Generate solar generation profiles
- Generate load demand profiles
- Support for multiple weather conditions
- Residential, commercial, industrial loads
- Multi-day simulation support

**Main class:**
```python
ProfileGenerator()
```

**Key methods:**
- `generate_solar_profile(peak_power, weather, day_of_year)`
- `generate_load_profile(profile_type, day_type)`
- `generate_multi_day_profiles(days, profile_type, weather_pattern)`

---

#### 3. `schedulers.py` (13KB)
**What it does:**
- 7 optimization strategies
- Strategy registry and management
- Strategy information

**Strategies available:**
1. `naive_scheduler` - No optimization
2. `self_consumption_scheduler` - Maximize solar usage
3. `peak_shaving_scheduler` - Reduce demand peaks
4. `time_of_use_scheduler` - Price arbitrage
5. `greedy_scheduler` - Local optimization
6. `linear_optimizer` - Global LP optimization (BEST)
7. `mpc_optimizer` - Model Predictive Control

**Main class:**
```python
StrategyManager()
```

**Key methods:**
- `get_strategy(name)` - Get strategy function
- `list_strategies()` - List all strategies
- `get_strategy_info(name)` - Get strategy details

---

#### 4. `simulator.py` (9KB)
**What it does:**
- Run simulations
- Support step-by-step and global modes
- Multi-day simulations
- Strategy comparison
- Results validation

**Main class:**
```python
Simulator()
```

**Key methods:**
- `run(solar, load, battery, prices, strategy_func, mode)`
- `run_multi_day(...)`
- `compare_strategies(...)`
- `validate(...)`

---

#### 5. `metrics.py` (11KB)
**What it does:**
- Calculate 40+ KPIs
- Financial analysis (NPV, IRR, LCOE)
- Energy balance validation
- Comparative analysis

**Main class:**
```python
MetricsCalculator()
```

**Key methods:**
- `calculate_kpis(results_df, total_load, battery_metrics, prices, system_config)`
- `compare_strategies(results_dict, strategies)`
- `check_energy_balance(df, solar, load)`
- `calculate_financial_metrics(kpis, system_config)`

---

#### 6. `pricing.py` (5KB)
**What it does:**
- TOU, Flat, Dynamic pricing models
- Grid parameters
- Carbon emissions calculation

**Main class:**
```python
PricingManager()
```

**Key methods:**
- `get_tou_pricing()` - Time-of-Use rates
- `get_flat_pricing(rate)` - Flat rate
- `get_dynamic_pricing(base, volatility)` - Dynamic rates
- `get_pricing(model, **kwargs)` - Unified interface
- `calculate_carbon_emissions(grid_buy, solar_gen)`

---

#### 7. `export_utils.py` (6KB)
**What it does:**
- Export to CSV, Excel, JSON
- Complete report generation
- Data formatting

**Main class:**
```python
ExportManager()
```

**Key methods:**
- `to_csv(data, filepath)`
- `to_excel(data_dict, filepath)`
- `results_to_csv(results, solar, load, filepath)`
- `export_complete_report(...)`

---

### Frontend Files (Only UI Code)

#### 1. `app.py` (9KB)
**What it does:**
- Main Streamlit application
- Page configuration
- Orchestrates backend calls
- Manages session state
- Renders tabs

**No business logic** - only calls backend and displays results.

---

#### 2. `components.py` (16KB)
**What it does:**
- Reusable UI components
- Chart rendering functions
- Sidebar controls
- Metrics displays

**Functions:**
- `render_header()` - App header
- `render_sidebar()` - Configuration controls
- `render_metrics_row()` - Top metrics
- `render_energy_dashboard()` - Power flow charts
- `render_strategy_comparison()` - Comparison tables
- `render_financial_analysis()` - Financial charts
- `render_battery_analytics()` - Battery metrics
- `render_environmental_impact()` - Carbon analysis
- `render_system_validation()` - Validation & export

---

## 🚀 How to Run

### Method 1: Web Interface (Recommended)

```bash
cd microgrid_ems
streamlit run frontend/app.py
```

Opens browser at `http://localhost:8501`

---

### Method 2: Python Script (Backend Only)

Create `my_analysis.py`:

```python
import sys
sys.path.append('.')  # Add current dir to path

from backend import (
    Battery, ProfileGenerator, StrategyManager,
    Simulator, MetricsCalculator, PricingManager
)

# Initialize components
profile_gen = ProfileGenerator()
pricing = PricingManager()
simulator = Simulator()
metrics_calc = MetricsCalculator()
strategy_mgr = StrategyManager()

# Generate profiles
solar = profile_gen.generate_solar_profile(peak_power=5.0, weather="sunny")
load_data = profile_gen.generate_load_profile(profile_type="residential")
load = load_data['total']

# Setup battery
battery = Battery(capacity=13.5, soc=0, max_charge=5.0, 
                 max_discharge=5.0, efficiency=0.95)

# Get pricing
prices, sell_price = pricing.get_pricing("TOU")

# Get strategy
strategy_func = strategy_mgr.get_strategy("linear_optimizer")

# Run simulation
results = simulator.run(
    solar, load, battery, prices, sell_price, 
    strategy_func, mode="global"
)

# Calculate KPIs
kpis = metrics_calc.calculate_kpis(
    results, load.sum(), battery.get_metrics(), prices,
    {"battery_size": 13.5, "solar_size": 5.0}
)

# Print results
print(f"Daily Cost: ₹{kpis['Total Cost']:.2f}")
print(f"Self-Sufficiency: {kpis['Self Sufficiency']:.1f}%")
print(f"Carbon Reduction: {kpis['Carbon Reduction']:.1f}%")
print(f"Payback Period: {kpis['Payback Period']:.1f} years")

# Export
from backend import ExportManager
exporter = ExportManager()
exporter.results_to_csv(results, solar, load, "my_results.csv")
exporter.kpis_to_csv(kpis, "my_kpis.csv")
```

Run it:
```bash
python my_analysis.py
```

---

## 📊 Import Guide

### Import from Backend

```python
# Battery model
from backend import Battery
from backend.battery_model import Battery  # Alternative

# Profiles
from backend import ProfileGenerator
from backend.energy_profiles import ProfileGenerator

# Strategies
from backend import StrategyManager, STRATEGIES, get_strategy
from backend.schedulers import naive_scheduler, linear_optimizer

# Simulation
from backend import Simulator
from backend.simulator import run_simulation

# Metrics
from backend import MetricsCalculator
from backend.metrics import calculate_kpis

# Pricing
from backend import PricingManager
from backend.pricing import PricingManager

# Export
from backend import ExportManager
from backend.export_utils import ExportManager
```

### Import from Frontend (for custom UI)

```python
from frontend.components import (
    render_sidebar,
    render_energy_dashboard,
    render_metrics_row
)
```

---

## 🔄 Data Flow

```
User Configures System
        ↓
frontend/app.py collects parameters
        ↓
Calls backend modules:
  → ProfileGenerator.generate_solar_profile()
  → ProfileGenerator.generate_load_profile()
  → PricingManager.get_pricing()
  → Battery() object creation
  → StrategyManager.get_strategy()
  → Simulator.run()
  → MetricsCalculator.calculate_kpis()
        ↓
frontend/components.py renders results
        ↓
User views visualizations
```

---

## 🎓 Example Use Cases

### Use Case 1: Compare All Strategies

```python
from backend import *

# Setup
profile_gen = ProfileGenerator()
pricing = PricingManager()
strategy_mgr = StrategyManager()
simulator = Simulator()

# Generate profiles
solar = profile_gen.generate_solar_profile(peak_power=5.0)
load = profile_gen.generate_load_profile()['total']
prices, sell_price = pricing.get_pricing("TOU")

# Compare all strategies
battery_config = {
    'capacity': 13.5,
    'initial_soc': 0,
    'max_charge': 5.0,
    'max_discharge': 5.0,
    'efficiency': 0.95
}

strategies = {
    name: strategy_mgr.get_strategy(name) 
    for name in strategy_mgr.list_strategies()
}

results = simulator.compare_strategies(
    solar, load, battery_config, prices, sell_price, strategies
)

# Analyze
for strategy_name, df in results.items():
    print(f"{strategy_name}: Cost = ₹{df['cost'].sum():.2f}")
```

### Use Case 2: Parameter Sweep

```python
import pandas as pd
from backend import *

results = []

for battery_size in [10, 13.5, 20, 27]:
    for solar_size in [3, 5, 7, 10]:
        # ... run simulation ...
        # ... collect KPIs ...
        results.append({
            'battery': battery_size,
            'solar': solar_size,
            'cost': kpis['Total Cost'],
            'payback': kpis['Payback Period']
        })

results_df = pd.DataFrame(results)
results_df.to_csv("parameter_sweep.csv")
```

### Use Case 3: Multi-Day Analysis

```python
from backend import ProfileGenerator, Simulator, Battery

gen = ProfileGenerator()

# Generate 7 days of profiles
multi_day = gen.generate_multi_day_profiles(
    days=7,
    profile_type="residential",
    weather_pattern="mixed"
)

# Run week-long simulation
# ... use multi_day['solar'] and multi_day['load'] ...
```

---

## 🔧 Adding New Features

### Add a New Strategy

1. Edit `backend/schedulers.py`:

```python
def my_strategy(load, solar, battery, prices, sell_price):
    """My custom strategy."""
    # Your logic here
    return {
        "grid_buy": ...,
        "grid_sell": ...,
        "bat_charge": ...,
        "bat_discharge": ...
    }

# Add to registry
STRATEGIES["my_strategy"] = my_strategy
```

2. It's automatically available in the frontend dropdown!

### Add a New Metric

1. Edit `backend/metrics.py` in `calculate_kpis()`:

```python
# Calculate my metric
my_metric = (total_load - grid_import) / total_load * 100

# Add to return dict
kpis["My Metric"] = round(my_metric, 2)
```

2. Access it in frontend or scripts:

```python
print(f"My Metric: {kpis['My Metric']}")
```

### Add a New UI Tab

1. Edit `frontend/app.py`:

```python
tab7 = st.tabs([..., "My Analysis"])

with tab7:
    st.subheader("My Custom Analysis")
    # Use backend data already available
    # Create visualizations
```

---

## 📁 Where Files Go

| File Type | Location | Example |
|-----------|----------|---------|
| Business logic | `backend/` | Battery model, strategies |
| UI code | `frontend/` | Streamlit components |
| Configuration | `config/` | System parameters |
| Data files | `data/` | Sample CSVs |
| Output files | `outputs/` | Generated results |
| Documentation | `README.md` | This file |

---

## ✅ Benefits of This Structure

### 1. Separation of Concerns
- **Backend**: Pure Python, no UI dependencies
- **Frontend**: Pure UI, no business logic
- **Config**: Centralized parameters

### 2. Testability
```python
# Easy to test backend without UI
def test_battery():
    from backend import Battery
    battery = Battery(10, 0, 5, 5, 0.95)
    battery.charge(3)
    assert battery.soc > 0
```

### 3. Reusability
- Use backend in:
  - Web app (Streamlit)
  - Scripts
  - Jupyter notebooks
  - APIs (Flask/FastAPI)
  - Desktop apps

### 4. Maintainability
- Change UI → Only edit `frontend/`
- Change logic → Only edit `backend/`
- No risk of breaking the other

### 5. Scalability
- Add new backends (database, API)
- Add new frontends (Dash, Gradio)
- Easy team collaboration

---

## 🎯 Quick Reference

```bash
# Project structure
microgrid_ems/
├── backend/      # Business logic (7 modules)
├── frontend/     # UI (2 files)
├── config/       # Settings
├── data/         # Input data
└── outputs/      # Results

# Run web app
streamlit run frontend/app.py

# Run custom script
python my_script.py

# Import backend
from backend import Battery, Simulator, MetricsCalculator

# Import frontend components (for custom UI)
from frontend.components import render_sidebar
```

---

**Version**: 2.0.0  
**Architecture**: Clean Backend-Frontend Separation  
**Status**: Production Ready ✅  
**Total Size**: ~60KB code + dependencies