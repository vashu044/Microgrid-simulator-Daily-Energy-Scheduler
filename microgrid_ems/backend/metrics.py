import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_kpis(results_df: pd.DataFrame, total_load_kwh: float, 
                   battery_metrics: Dict = None, prices: np.ndarray = None,
                   system_config: Dict = None) -> Dict[str, Any]:
    """
    Comprehensive KPI calculation for EMS performance evaluation.
    
    Args:
        results_df: Simulation results dataframe
        total_load_kwh: Total energy demand
        battery_metrics: Battery health and usage metrics
        prices: Grid pricing array
        system_config: System configuration parameters
    
    Returns:
        Dict containing all KPIs organized by category
    """
    
    # ===== ECONOMIC METRICS =====
    total_cost = results_df["cost"].sum()
    grid_import = results_df["grid_buy"].sum()
    grid_export = results_df["grid_sell"].sum()
    
    grid_cost = (results_df["grid_buy"] * prices).sum() if prices is not None else total_cost
    export_revenue = results_df["grid_sell"].sum() * 3.0  # Assuming feed-in tariff
    net_cost = grid_cost - export_revenue
    
    # Cost per kWh of load served
    cost_per_kwh = net_cost / total_load_kwh if total_load_kwh > 0 else 0
    
    # ===== ENERGY METRICS =====
    solar_generation = results_df.get("solar", pd.Series([0])).sum() if "solar" in results_df.columns else 0
    battery_charge_total = results_df["bat_charge"].sum()
    battery_discharge_total = results_df["bat_discharge"].sum()
    
    # Self-sufficiency ratio
    if total_load_kwh > 0:
        self_sufficiency = max(0, min(100, (1 - grid_import / total_load_kwh) * 100))
    else:
        self_sufficiency = 0.0
    
    # Self-consumption ratio (what % of solar is used on-site)
    if solar_generation > 0:
        solar_to_load = solar_generation - grid_export
        self_consumption = (solar_to_load / solar_generation) * 100
    else:
        self_consumption = 0.0
    
    # Load matching index
    if solar_generation > 0 and total_load_kwh > 0:
        load_matching = min(solar_generation, total_load_kwh) / max(solar_generation, total_load_kwh) * 100
    else:
        load_matching = 0.0
    
    # ===== BATTERY METRICS =====
    if battery_metrics:
        battery_efficiency = (battery_discharge_total / battery_charge_total * 100) if battery_charge_total > 0 else 0
        battery_cycles = battery_metrics.get("cycles", 0)
        battery_soh = battery_metrics.get("state_of_health", 100)
        battery_throughput = battery_metrics.get("throughput", 0)
        battery_degradation = battery_metrics.get("degradation", 0)
    else:
        battery_efficiency = 0
        battery_cycles = 0
        battery_soh = 100
        battery_throughput = battery_charge_total
        battery_degradation = 0
    
    # Battery utilization
    avg_soc = results_df["battery_soc"].mean() if "battery_soc" in results_df.columns else 0
    max_soc = results_df["battery_soc"].max() if "battery_soc" in results_df.columns else 0
    
    # ===== GRID INTERACTION METRICS =====
    peak_import = results_df["grid_buy"].max()
    peak_export = results_df["grid_sell"].max()
    
    # Grid dependency factor
    grid_dependency = (grid_import / total_load_kwh * 100) if total_load_kwh > 0 else 0
    
    # Export ratio
    export_ratio = (grid_export / solar_generation * 100) if solar_generation > 0 else 0
    
    # ===== ENVIRONMENTAL METRICS =====
    # Carbon intensity: India grid ~0.82 kg CO2/kWh, Solar ~0.05 kg CO2/kWh
    grid_carbon = grid_import * 0.82
    solar_carbon = solar_generation * 0.05
    total_carbon = grid_carbon + solar_carbon
    carbon_per_kwh = total_carbon / total_load_kwh if total_load_kwh > 0 else 0
    
    # Carbon avoided vs. pure grid scenario
    pure_grid_carbon = total_load_kwh * 0.82
    carbon_avoided = pure_grid_carbon - total_carbon
    carbon_reduction = (carbon_avoided / pure_grid_carbon * 100) if pure_grid_carbon > 0 else 0
    
    # ===== OPERATIONAL METRICS =====
    # Peak to average ratio
    peak_load = results_df.get("load", pd.Series([0])).max() if "load" in results_df.columns else 0
    avg_load = results_df.get("load", pd.Series([0])).mean() if "load" in results_df.columns else 0
    peak_to_avg_ratio = peak_load / avg_load if avg_load > 0 else 0
    
    # Load factor
    load_factor = (avg_load / peak_load * 100) if peak_load > 0 else 0
    
    # ===== RELIABILITY METRICS =====
    # Energy not served (if any curtailment happened)
    energy_not_served = 0  # Would need to track curtailment events
    reliability_index = (1 - energy_not_served / total_load_kwh) * 100 if total_load_kwh > 0 else 100
    
    # ===== FINANCIAL ANALYSIS (if system config provided) =====
    if system_config:
        battery_capex = system_config.get("battery_size", 0) * 800  # ₹/kWh
        solar_capex = system_config.get("solar_size", 0) * 40000  # ₹/kW
        total_capex = battery_capex + solar_capex
        
        # Daily savings vs. baseline
        baseline_cost = total_load_kwh * 5.0  # Assumed flat rate
        daily_savings = baseline_cost - net_cost
        annual_savings = daily_savings * 365
        
        # Simple payback period
        payback_years = total_capex / annual_savings if annual_savings > 0 else float('inf')
        
        # Return on investment (10 year horizon)
        roi_10yr = ((annual_savings * 10) - total_capex) / total_capex * 100 if total_capex > 0 else 0
    else:
        total_capex = 0
        daily_savings = 0
        annual_savings = 0
        payback_years = 0
        roi_10yr = 0
    
    # ===== ORGANIZE RESULTS =====
    kpis = {
        # Economic
        "Total Cost": round(total_cost, 2),
        "Net Cost": round(net_cost, 2),
        "Cost per kWh": round(cost_per_kwh, 3),
        "Grid Cost": round(grid_cost, 2),
        "Export Revenue": round(export_revenue, 2),
        "Daily Savings": round(daily_savings, 2),
        "Annual Savings": round(annual_savings, 2),
        "Payback Period": round(payback_years, 1),
        "ROI (10yr)": round(roi_10yr, 1),
        
        # Energy
        "Grid Import": round(grid_import, 2),
        "Grid Export": round(grid_export, 2),
        "Solar Generation": round(solar_generation, 2),
        "Battery Charge": round(battery_charge_total, 2),
        "Battery Discharge": round(battery_discharge_total, 2),
        "Total Load": round(total_load_kwh, 2),
        
        # Performance
        "Self Sufficiency": round(self_sufficiency, 1),
        "Self Consumption": round(self_consumption, 1),
        "Load Matching": round(load_matching, 1),
        "Grid Dependency": round(grid_dependency, 1),
        "Export Ratio": round(export_ratio, 1),
        
        # Battery
        "Battery Efficiency": round(battery_efficiency, 1),
        "Battery Cycles": round(battery_cycles, 2),
        "Battery SOH": round(battery_soh, 1),
        "Battery Throughput": round(battery_throughput, 2),
        "Battery Degradation": round(battery_degradation, 4),
        "Avg SOC": round(avg_soc, 2),
        "Max SOC": round(max_soc, 2),
        
        # Grid
        "Peak Import": round(peak_import, 2),
        "Peak Export": round(peak_export, 2),
        
        # Environmental
        "Total Carbon": round(total_carbon, 2),
        "Carbon per kWh": round(carbon_per_kwh, 3),
        "Carbon Avoided": round(carbon_avoided, 2),
        "Carbon Reduction": round(carbon_reduction, 1),
        
        # Operational
        "Peak Load": round(peak_load, 2),
        "Avg Load": round(avg_load, 2),
        "Load Factor": round(load_factor, 1),
        "Reliability": round(reliability_index, 1)
    }
    
    return kpis


def calculate_comparative_metrics(results_dict: Dict[str, pd.DataFrame], 
                                  strategies: list) -> pd.DataFrame:
    """
    Compare multiple strategies side-by-side.
    
    Args:
        results_dict: Dictionary of {strategy_name: results_df}
        strategies: List of strategy names
    
    Returns:
        DataFrame with comparative metrics
    """
    comparison = []
    
    for strategy in strategies:
        if strategy in results_dict:
            df = results_dict[strategy]
            kpis = calculate_kpis(df, df.get("load", pd.Series([0])).sum())
            kpis["Strategy"] = strategy
            comparison.append(kpis)
    
    return pd.DataFrame(comparison)


def check_energy_balance(df: pd.DataFrame, solar: np.ndarray = None, 
                        load: np.ndarray = None, tolerance: float = 0.01) -> Dict:
    """
    Validate energy conservation at each timestep.
    
    Returns:
        Dict with validation results and error details
    """
    # Reconstruct inputs and outputs
    if solar is not None and load is not None:
        inputs = solar + df['grid_buy'] + df['bat_discharge']
        outputs = load + df['grid_sell'] + df['bat_charge']
    else:
        # Try to infer from dataframe
        inputs = df.get('solar', 0) + df['grid_buy'] + df['bat_discharge']
        outputs = df.get('load', 0) + df['grid_sell'] + df['bat_charge']
    
    diff = inputs - outputs
    abs_diff = abs(diff)
    
    errors = df[abs_diff > tolerance].copy()
    errors['energy_imbalance'] = diff[abs_diff > tolerance]
    
    max_error = abs_diff.max()
    avg_error = abs_diff.mean()
    num_errors = len(errors)
    
    validation = {
        "passed": len(errors) == 0,
        "num_violations": num_errors,
        "max_error": max_error,
        "avg_error": avg_error,
        "error_timesteps": errors.index.tolist() if len(errors) > 0 else [],
        "total_imbalance": diff.sum()
    }
    
    return validation


class MetricsCalculator:
    """Calculator for performance metrics and KPIs."""
    
    def __init__(self):
        """Initialize metrics calculator."""
        pass
    
    def calculate_kpis(self,
                      results_df: pd.DataFrame, 
                      total_load_kwh: float, 
                      battery_metrics: Dict = None, 
                      prices: np.ndarray = None,
                      system_config: Dict = None) -> Dict[str, Any]:
        """Calculate all KPIs."""
        return calculate_kpis(results_df, total_load_kwh, battery_metrics, prices, system_config)
    
    def compare_strategies(self,
                          results_dict: Dict[str, pd.DataFrame], 
                          strategies: list) -> pd.DataFrame:
        """Compare multiple strategies."""
        return calculate_comparative_metrics(results_dict, strategies)
    
    def check_energy_balance(self,
                            df: pd.DataFrame, 
                            solar: np.ndarray = None, 
                            load: np.ndarray = None, 
                            tolerance: float = 0.01) -> Dict:
        """Check energy balance."""
        return check_energy_balance(df, solar, load, tolerance)
    
    def calculate_financial_metrics(self,
                                    kpis: Dict, 
                                    system_config: Dict, 
                                    years: int = 10, 
                                    discount_rate: float = 0.08) -> Dict:
        """
        Calculate financial metrics including NPV and LCOE.
        """
        # Extract base costs and savings
        total_capex = kpis.get("Total CAPEX", 0)
        if total_capex == 0:
            # Fallback calculation if not in KPIs
            battery_capex = system_config.get("battery_size", 0) * 800
            solar_capex = system_config.get("solar_size", 0) * 40000
            total_capex = battery_capex + solar_capex

        annual_savings = kpis.get("Annual Savings", 0)
        annual_om = total_capex * 0.02  # 2% O&M rate
        annual_cash_flow = annual_savings - annual_om
        
        # Calculate NPV
        npv = -total_capex
        for year in range(1, years + 1):
            npv += annual_cash_flow / ((1 + discount_rate) ** year)
            
        # Calculate LCOE (simplified)
        total_load_10yr = kpis.get("Total Load", 0) * 365 * years
        total_lifecycle_cost = total_capex + (annual_om * years)
        lcoe = total_lifecycle_cost / total_load_10yr if total_load_10yr > 0 else 0
        
        return {
            "Total CAPEX": total_capex,
            "Battery CAPEX": system_config.get("battery_size", 0) * 800,
            "Solar CAPEX": system_config.get("solar_size", 0) * 40000,
            "Annual Cash Flow": annual_cash_flow,
            "Annual O&M": annual_om,
            "NPV": npv,
            "LCOE": lcoe,
            "Payback Period": kpis.get("Payback Period", 0)
        }