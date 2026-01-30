import pulp
import numpy as np
from typing import Dict, List, Tuple

def naive_scheduler(load, solar, battery, prices, sell_price):
    """
    Baseline Strategy: No optimization, simple grid-following.
    - Excess solar → Export to grid
    - Deficit → Import from grid
    - Battery unused
    """
    net_load = load - solar
    
    if net_load > 0:
        return {
            "grid_buy": net_load,
            "grid_sell": 0.0,
            "bat_charge": 0.0,
            "bat_discharge": 0.0
        }
    else:
        return {
            "grid_buy": 0.0,
            "grid_sell": abs(net_load),
            "bat_charge": 0.0,
            "bat_discharge": 0.0
        }


def self_consumption_scheduler(load, solar, battery, prices, sell_price):
    """
    Self-Consumption Strategy: Maximize on-site solar usage.
    Priority: Load > Battery > Grid Export
    """
    net_load = load - solar
    
    if net_load > 0:
        # Deficit: Try battery first, then grid
        battery_available = battery.soc
        from_battery = min(net_load, battery_available, battery.max_discharge)
        from_grid = max(0, net_load - from_battery)
        
        return {
            "grid_buy": from_grid,
            "grid_sell": 0.0,
            "bat_charge": 0.0,
            "bat_discharge": from_battery
        }
    else:
        # Surplus: Charge battery first, then export
        surplus = abs(net_load)
        battery_space = battery.capacity - battery.soc
        to_battery = min(surplus, battery_space, battery.max_charge)
        to_grid = max(0, surplus - to_battery)
        
        return {
            "grid_buy": 0.0,
            "grid_sell": to_grid,
            "bat_charge": to_battery,
            "bat_discharge": 0.0
        }


def peak_shaving_scheduler(load, solar, battery, prices, sell_price, peak_threshold=5.0):
    """
    Peak Shaving Strategy: Reduce maximum grid demand.
    Discharges battery when load exceeds threshold.
    """
    net_load = load - solar
    
    if net_load > peak_threshold:
        # High load: Use battery to reduce peak
        battery_help = min(net_load - peak_threshold, battery.soc, battery.max_discharge)
        from_grid = net_load - battery_help
        
        return {
            "grid_buy": from_grid,
            "grid_sell": 0.0,
            "bat_charge": 0.0,
            "bat_discharge": battery_help
        }
    elif net_load > 0:
        # Normal load: Grid only
        return {
            "grid_buy": net_load,
            "grid_sell": 0.0,
            "bat_charge": 0.0,
            "bat_discharge": 0.0
        }
    else:
        # Surplus: Charge battery
        surplus = abs(net_load)
        battery_space = battery.capacity - battery.soc
        to_battery = min(surplus, battery_space, battery.max_charge)
        to_grid = max(0, surplus - to_battery)
        
        return {
            "grid_buy": 0.0,
            "grid_sell": to_grid,
            "bat_charge": to_battery,
            "bat_discharge": 0.0
        }


def time_of_use_scheduler(load, solar, battery, prices, sell_price, current_hour=0):
    """
    TOU-Aware Strategy: Charge during off-peak, discharge during peak.
    Simple rule-based approach.
    """
    net_load = load - solar
    current_price = prices if isinstance(prices, (int, float)) else prices[current_hour]
    
    # Define peak hours (high price periods)
    peak_hours = [7, 8, 9, 17, 18, 19, 20]
    is_peak = current_hour in peak_hours
    
    if is_peak:
        # Peak hour: Use battery to reduce expensive grid purchases
        if net_load > 0:
            battery_help = min(net_load, battery.soc, battery.max_discharge)
            from_grid = max(0, net_load - battery_help)
            
            return {
                "grid_buy": from_grid,
                "grid_sell": 0.0,
                "bat_charge": 0.0,
                "bat_discharge": battery_help
            }
        else:
            # Surplus during peak: Export is valuable
            surplus = abs(net_load)
            return {
                "grid_buy": 0.0,
                "grid_sell": surplus,
                "bat_charge": 0.0,
                "bat_discharge": 0.0
            }
    else:
        # Off-peak: Charge battery from grid if cheap
        if net_load > 0:
            # Buy from grid (cheap)
            return {
                "grid_buy": net_load,
                "grid_sell": 0.0,
                "bat_charge": 0.0,
                "bat_discharge": 0.0
            }
        else:
            # Surplus: Charge battery
            surplus = abs(net_load)
            battery_space = battery.capacity - battery.soc
            to_battery = min(surplus, battery_space, battery.max_charge)
            to_grid = max(0, surplus - to_battery)
            
            return {
                "grid_buy": 0.0,
                "grid_sell": to_grid,
                "bat_charge": to_battery,
                "bat_discharge": 0.0
            }


def linear_optimizer(load_profile, solar_profile, battery, prices, sell_price):
    """
    Advanced Linear Programming Optimizer.
    Globally optimal solution over 24-hour horizon.
    Minimizes total cost while respecting all constraints.
    """
    hours = len(load_profile)
    
    # Create optimization problem
    prob = pulp.LpProblem("EMS_Cost_Minimization", pulp.LpMinimize)

    # Decision Variables
    grid_buy = pulp.LpVariable.dicts("GridBuy", range(hours), lowBound=0)
    grid_sell = pulp.LpVariable.dicts("GridSell", range(hours), lowBound=0)
    bat_charge = pulp.LpVariable.dicts("BatCharge", range(hours), lowBound=0, 
                                       upBound=battery.max_charge)
    bat_discharge = pulp.LpVariable.dicts("BatDischarge", range(hours), lowBound=0, 
                                          upBound=battery.max_discharge)
    soc = pulp.LpVariable.dicts("SOC", range(hours), lowBound=0, upBound=battery.capacity)

    # Objective Function: Minimize Net Cost
    prob += pulp.lpSum([
        grid_buy[t] * prices[t] - grid_sell[t] * sell_price 
        for t in range(hours)
    ]), "Total_Cost"

    # Constraints
    for t in range(hours):
        # 1. Energy Balance (Kirchhoff's Law)
        # All sources must equal all sinks at every timestep
        prob += (
            solar_profile[t] + grid_buy[t] + bat_discharge[t] == 
            load_profile[t] + grid_sell[t] + bat_charge[t]
        ), f"Energy_Balance_{t}"

        # 2. Battery State of Charge Dynamics
        if t == 0:
            prev_soc = battery.soc
        else:
            prev_soc = soc[t-1]
        
        prob += (
            soc[t] == prev_soc + bat_charge[t] * battery.efficiency - bat_discharge[t]
        ), f"SOC_Update_{t}"
        
        # 3. Prevent simultaneous charging and discharging (optional but realistic)
        # This is implicitly handled by the optimizer but can be enforced with binary variables

    # Terminal Constraint: End with reasonable SOC (optional)
    # prob += soc[hours-1] >= battery.capacity * 0.2, "Minimum_Final_SOC"

    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Extract results
    results = {
        "grid_buy": [pulp.value(grid_buy[t]) or 0.0 for t in range(hours)],
        "grid_sell": [pulp.value(grid_sell[t]) or 0.0 for t in range(hours)],
        "bat_charge": [pulp.value(bat_charge[t]) or 0.0 for t in range(hours)],
        "bat_discharge": [pulp.value(bat_discharge[t]) or 0.0 for t in range(hours)],
        "battery_soc": [pulp.value(soc[t]) or 0.0 for t in range(hours)],
        "cost": []
    }

    # Calculate costs
    for t in range(hours):
        cost = results["grid_buy"][t] * prices[t] - results["grid_sell"][t] * sell_price
        results["cost"].append(cost)

    return results


def mpc_optimizer(load_profile, solar_profile, battery, prices, sell_price, 
                  horizon=24, current_hour=0):
    """
    Model Predictive Control (MPC) Strategy.
    Solves optimization over receding horizon.
    Re-optimizes at each timestep with updated forecasts.
    
    Note: This returns a full 24h plan but in practice only the first action is executed.
    """
    # Similar to linear_optimizer but designed for rolling horizon
    # In a real implementation, this would be called at each timestep
    return linear_optimizer(load_profile, solar_profile, battery, prices, sell_price)


def greedy_scheduler(load, solar, battery, prices, sell_price, current_hour=0):
    """
    Greedy Strategy: Make locally optimal decision at each timestep.
    - Buy when price is low
    - Sell when price is high
    - Use battery to arbitrage price differences
    """
    current_price = prices if isinstance(prices, (int, float)) else prices[current_hour]
    net_load = load - solar
    
    # Price thresholds (can be adaptive)
    high_price_threshold = 10.0
    low_price_threshold = 4.0
    
    if current_price > high_price_threshold:
        # High price: Minimize grid purchase
        if net_load > 0:
            # Use battery if available
            battery_help = min(net_load, battery.soc, battery.max_discharge)
            from_grid = max(0, net_load - battery_help)
            
            return {
                "grid_buy": from_grid,
                "grid_sell": 0.0,
                "bat_charge": 0.0,
                "bat_discharge": battery_help
            }
        else:
            # Surplus: Export (high price is good)
            surplus = abs(net_load)
            return {
                "grid_buy": 0.0,
                "grid_sell": surplus,
                "bat_charge": 0.0,
                "bat_discharge": 0.0
            }
            
    elif current_price < low_price_threshold:
        # Low price: Charge battery from grid
        if net_load > 0:
            # Buy what we need plus charge battery
            battery_space = battery.capacity - battery.soc
            extra_buy = min(battery_space, battery.max_charge)
            
            return {
                "grid_buy": net_load,
                "grid_sell": 0.0,
                "bat_charge": extra_buy,
                "bat_discharge": 0.0
            }
        else:
            # Surplus: Charge battery, minimize export
            surplus = abs(net_load)
            battery_space = battery.capacity - battery.soc
            to_battery = min(surplus, battery_space, battery.max_charge)
            to_grid = max(0, surplus - to_battery)
            
            return {
                "grid_buy": 0.0,
                "grid_sell": to_grid,
                "bat_charge": to_battery,
                "bat_discharge": 0.0
            }
    else:
        # Medium price: Self-consumption mode
        return self_consumption_scheduler(load, solar, battery, prices, sell_price)


# Strategy Registry
STRATEGIES = {
    "naive": naive_scheduler,
    "self_consumption": self_consumption_scheduler,
    "peak_shaving": peak_shaving_scheduler,
    "time_of_use": time_of_use_scheduler,
    "greedy": greedy_scheduler,
    "linear_optimizer": linear_optimizer,
    "mpc": mpc_optimizer
}


def get_strategy(name: str):
    """Get scheduler by name."""
    return STRATEGIES.get(name, naive_scheduler)


class StrategyManager:
    """Manager for control strategies."""
    
    def __init__(self):
        """Initialize strategy manager."""
        self.strategies = STRATEGIES
    
    def get_strategy(self, name: str):
        """Get strategy function by name."""
        return get_strategy(name)
    
    def list_strategies(self) -> List[str]:
        """List available strategies."""
        return list(self.strategies.keys())
    
    def get_strategy_info(self, name: str) -> Dict[str, str]:
        """Get information about a strategy."""
        info = {
            "naive": {
                "description": "No optimization, direct grid connection",
                "complexity": "Low",
                "suitable_for": "Baseline comparison"
            },
            "self_consumption": {
                "description": "Maximize on-site solar usage",
                "complexity": "Low",
                "suitable_for": "Simple self-consumption goals"
            },
            "peak_shaving": {
                "description": "Reduce maximum grid demand",
                "complexity": "Medium",
                "suitable_for": "Demand charge reduction"
            },
            "time_of_use": {
                "description": "Charge off-peak, discharge on-peak",
                "complexity": "Medium",
                "suitable_for": "TOU tariffs"
            },
            "greedy": {
                "description": "Locally optimal decisions",
                "complexity": "Medium",
                "suitable_for": "Dynamic pricing"
            },
            "linear_optimizer": {
                "description": "Global LP optimization",
                "complexity": "High",
                "suitable_for": "Cost minimization (optimal)"
            },
            "mpc": {
                "description": "Model Predictive Control",
                "complexity": "High",
                "suitable_for": "Rolling horizon optimization"
            }
        }
        
        return info.get(name, {"description": "Unknown strategy"})