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

