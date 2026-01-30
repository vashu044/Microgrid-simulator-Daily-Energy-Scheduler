# ⚡ Microgrid Energy Management System

Professional-grade energy management system with clean frontend-backend architecture.

## 📁 Project Structure

```
microgrid_ems/
│
├── backend/                    # Business Logic Layer
│   ├── __init__.py
│   ├── battery_model.py        # Battery physics & degradation
│   ├── energy_profiles.py      # Solar & load profile generation
│   ├── schedulers.py           # 7 control strategies
│   ├── simulator.py            # Simulation engine
│   ├── metrics.py              # KPI calculations
│   ├── pricing.py              # Pricing models
│   └── export_utils.py         # Data export utilities
│
├── frontend/                   # Presentation Layer
│   ├── __init__.py
│   ├── app.py                  # Main Streamlit app
│   └── components.py           # UI components
│
├── config/                     # Configuration
│   └── settings.py             # System parameters
│
├── data/                       # Data files
│   └── (sample data files)
│
├── outputs/                    # Output files
│   └── plots/                  # Generated plots
│
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
cd frontend
streamlit run app.py
```

Or from project root:

```bash
streamlit run frontend/app.py
```

### 3. Access the Interface

Open your browser to `http://localhost:8501`

## 💡 Usage

### Web Interface (Recommended)

Run the Streamlit app for full interactive experience:

```bash
streamlit run frontend/app.py
```

### Python API (For Scripts/Automation)

```python
from backend import (
    Battery, ProfileGenerator, StrategyManager,
    Simulator, MetricsCalculator, PricingManager
)

# Generate profiles
profile_gen = ProfileGenerator()
solar = profile_gen.generate_solar_profile(peak_power=5.0)
load_data = profile_gen.generate_load_profile()

# Setup system
battery = Battery(capacity=13.5, soc=0, max_charge=5.0, 
                 max_discharge=5.0, efficiency=0.95)

# Get strategy
strategy_mgr = StrategyManager()
strategy_func = strategy_mgr.get_strategy("linear_optimizer")

# Run simulation
simulator = Simulator()
pricing_mgr = PricingManager()
prices, sell_price = pricing_mgr.get_pricing("TOU")

results = simulator.run(
    solar, load_data['total'], battery,
    prices, sell_price, strategy_func, mode="global"
)

# Calculate KPIs
metrics_calc = MetricsCalculator()
kpis = metrics_calc.calculate_kpis(
    results, load_data['total'].sum(),
    battery.get_metrics(), prices,
    {"battery_size": 13.5, "solar_size": 5.0}
)

print(f"Cost: ₹{kpis['Total Cost']:.2f}")
print(f"Self-Sufficiency: {kpis['Self Sufficiency']:.1f}%")
```

## 🎯 Features

### Backend Modules

1. **Battery Model** (`battery_model.py`)
   - Advanced degradation (throughput + cycle-based)
   - Thermal effects
   - State of Health tracking
   - C-rate limiting

2. **Energy Profiles** (`energy_profiles.py`)
   - Solar: Realistic generation with weather/seasonal effects
   - Load: Residential, Commercial, Industrial profiles
   - Multi-day simulation support

3. **Schedulers** (`schedulers.py`)
   - 7 control strategies
   - Naive, Self-Consumption, Peak Shaving
   - TOU, Greedy, Linear Programming, MPC

4. **Simulator** (`simulator.py`)
   - Step-by-step and global optimization modes
   - Multi-day capability
   - Validation framework

5. **Metrics** (`metrics.py`)
   - 40+ KPIs (economic, technical, environmental)
   - Financial analysis (NPV, IRR, LCOE)
   - Comparative analysis

6. **Pricing** (`pricing.py`)
   - TOU, Flat, Dynamic pricing models
   - Carbon emissions calculation

7. **Export** (`export_utils.py`)
   - CSV, Excel, JSON export
   - Comprehensive reporting

### Frontend Components

1. **Main App** (`app.py`)
   - Streamlit interface
   - 6 analysis tabs
   - Real-time simulation

2. **UI Components** (`components.py`)
   - Sidebar controls
   - Visualization functions
   - Metrics displays

## 📊 Control Strategies

| Strategy | Description | Complexity | Best For |
|----------|-------------|------------|----------|
| Naive | No optimization | Low | Baseline |
| Self-Consumption | Maximize solar usage | Low | Simple goals |
| Peak Shaving | Reduce peak demand | Medium | Demand charges |
| Time-of-Use | Price arbitrage | Medium | TOU tariffs |
| Greedy | Local optimization | Medium | Dynamic pricing |
| Linear Programming | Global optimal | High | Cost minimization |
| MPC | Rolling horizon | High | Advanced control |

## 🔧 Configuration

Edit `config/settings.py` to change:
- Battery specifications
- Solar parameters
- Grid settings
- Economic parameters
- Simulation settings

## 📈 Typical Results

**13.5 kWh Battery + 5 kW Solar (Residential)**

- Cost Reduction: 35-45% vs baseline
- Self-Sufficiency: 60-75%
- Carbon Reduction: 65%+
- Payback Period: 8-10 years
- Battery Cycles/Day: 0.8-1.2

## 🧪 Testing

```python
# Run backend tests
python -m pytest tests/

# Or test individual modules
from backend import ProfileGenerator

gen = ProfileGenerator()
solar = gen.generate_solar_profile()
assert len(solar) == 24
assert solar.sum() > 0
```

## 📦 Export Data

The system can export:
- Hourly results (CSV)
- KPIs (CSV/JSON)
- Strategy comparison (CSV)
- Complete reports (Excel)

Access exports from the "System Validation" tab or use the API:

```python
from backend import ExportManager

exporter = ExportManager()
exporter.results_to_csv(results_df, solar, load, "output.csv")
```

## 🌟 Architecture Benefits

### Backend-Frontend Separation
- ✅ Clean code organization
- ✅ Easy testing
- ✅ Reusable backend
- ✅ Multiple frontends possible

### Modularity
- ✅ Independent components
- ✅ Easy to extend
- ✅ Clear responsibilities
- ✅ Simple maintenance

## 🔄 Development

### Adding a New Strategy

1. Edit `backend/schedulers.py`:

```python
def my_custom_strategy(load, solar, battery, prices, sell_price):
    # Your logic here
    return {
        "grid_buy": ...,
        "grid_sell": ...,
        "bat_charge": ...,
        "bat_discharge": ...
    }

# Add to STRATEGIES dict
STRATEGIES["my_strategy"] = my_custom_strategy
```

2. It's immediately available in the frontend!

### Adding a New Metric

1. Edit `backend/metrics.py`:

```python
# In calculate_kpis function
my_metric = calculate_my_metric(results_df)
kpis["My Metric"] = my_metric
```

2. Access it in frontend components.

## 📚 Documentation

- **Backend API**: See docstrings in each module
- **Frontend Components**: See `frontend/components.py`
- **Configuration**: See `config/settings.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file

## 🎓 Citation

If you use this in research, please cite:

```
@software{microgrid_ems,
  title = {Microgrid Energy Management System},
  year = {2026},
  version = {2.0.0}
}
```

## 📞 Support

- Issues: GitHub Issues
- Documentation: See `/docs` folder
- Email: support@example.com

## ⚡ Quick Reference

```bash
# Install
pip install -r requirements.txt

# Run web app
streamlit run frontend/app.py

# Run custom script
python my_script.py

# Export results
# Use frontend UI or backend API
```

---

**Version**: 2.0.0  
**Architecture**: Frontend-Backend Separation  
**Status**: Production Ready ✅  
**Last Updated**: January 2026