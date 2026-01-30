"""
Configuration Settings
Central configuration for the Microgrid EMS.
"""

# Battery Specifications
BATTERY_CONFIG = {
    "default_capacity": 13.5,  # kWh (Tesla Powerwall 2)
    "default_power": 5.0,  # kW
    "efficiency": 0.95,  # Round-trip efficiency
    "degradation_rate": 0.00005,  # Capacity loss per kWh throughput
    "initial_temperature": 25.0,  # °C
}

# Solar System
SOLAR_CONFIG = {
    "default_capacity": 5.0,  # kW
    "degradation_annual": 0.005,  # 0.5% per year
    "lifetime_years": 25,
}

# Grid Parameters
GRID_CONFIG = {
    "sell_price": 3.0,  # Feed-in tariff (₹/kWh)
    "max_import": 50.0,  # kW
    "max_export": 10.0,  # kW
    "carbon_intensity": 0.82,  # kg CO2/kWh (India grid)
}

# Economic Parameters
ECONOMIC_CONFIG = {
    "battery_capex": 800.0,  # ₹/kWh
    "solar_capex": 40000.0,  # ₹/kW
    "discount_rate": 0.08,  # 8% annual
    "om_rate": 0.02,  # O&M as % of CAPEX
    "analysis_years": 10,
}

# Simulation Parameters
SIMULATION_CONFIG = {
    "hours_per_day": 24,
    "timestep_hours": 1.0,
    "energy_balance_tolerance": 0.01,  # kWh
}