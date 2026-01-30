import pandas as pd
import numpy as np
from typing import Callable, Dict, Any
from config.settings import SIMULATION_CONFIG

def run_simulation(solar: np.ndarray, 
                   load: np.ndarray, 
                   battery, 
                   prices: np.ndarray, 
                   sell_price: float, 
                   strategy_func: Callable, 
                   mode: str = "step") -> pd.DataFrame:
    """
    Enhanced unified simulation engine supporting multiple operational modes.
    
    Args:
        solar: Solar generation profile [kW] (length HOURS)
        load: Load demand profile [kW] (length HOURS)
        battery: Battery object with charge/discharge methods
        prices: Grid purchase prices [₹/kWh] (length HOURS)
        sell_price: Grid feed-in tariff [₹/kWh]
        strategy_func: Control strategy function
        mode: "step" for sequential, "global" for optimization-based
    
    Returns:
        DataFrame with simulation results
    """
    
    hours = len(solar)
    
    if mode == "global":
        # Global optimization strategies (LP, MPC, etc.)
        # These strategies compute the entire 24h schedule at once
        results_dict = strategy_func(load, solar, battery, prices, sell_price)
        
        # Validate results structure
        required_keys = ["grid_buy", "grid_sell", "bat_charge", "bat_discharge", "battery_soc", "cost"]
        for key in required_keys:
            if key not in results_dict:
                raise ValueError(f"Strategy must return '{key}' in results")
        
        df = pd.DataFrame(results_dict)
        
        # Add additional metrics
        df['solar'] = solar
        df['load'] = load
        df['net_load'] = load - solar
        df['price'] = prices
        
    else:
        # Step-by-step simulation (greedy, rule-based, etc.)
        results = {
            "grid_buy": [],
            "grid_sell": [],
            "bat_charge": [],
            "bat_discharge": [],
            "battery_soc": [],
            "cost": [],
            "solar": [],
            "load": [],
            "net_load": [],
            "price": []
        }
        
        for t in range(hours):
            # Get control decision for this timestep
            decision = strategy_func(
                load[t], 
                solar[t], 
                battery, 
                prices[t] if isinstance(prices, np.ndarray) else prices, 
                sell_price
            )
            
            # Validate decision structure
            required_keys = ["grid_buy", "grid_sell", "bat_charge", "bat_discharge"]
            for key in required_keys:
                if key not in decision:
                    raise ValueError(f"Strategy must return '{key}' in decision")
            
            # Execute battery actions (modifies battery state)
            actual_charge = 0
            actual_discharge = 0
            
            if decision["bat_charge"] > 0:
                actual_charge = battery.charge(decision["bat_charge"])
            elif decision["bat_discharge"] > 0:
                actual_discharge = battery.discharge(decision["bat_discharge"])
            
            # Calculate cost for this timestep
            cost = (decision["grid_buy"] * prices[t] - 
                   decision["grid_sell"] * sell_price)
            
            # Record results
            results["grid_buy"].append(decision["grid_buy"])
            results["grid_sell"].append(decision["grid_sell"])
            results["bat_charge"].append(actual_charge)
            results["bat_discharge"].append(actual_discharge)
            results["battery_soc"].append(battery.soc)
            results["cost"].append(cost)
            results["solar"].append(solar[t])
            results["load"].append(load[t])
            results["net_load"].append(load[t] - solar[t])
            results["price"].append(prices[t])
        
        df = pd.DataFrame(results)
    
    # Add cumulative metrics
    df['cumulative_cost'] = df['cost'].cumsum()
    df['cumulative_import'] = df['grid_buy'].cumsum()
    df['cumulative_export'] = df['grid_sell'].cumsum()
    
    return df


def run_multi_day_simulation(solar: np.ndarray,
                             load: np.ndarray,
                             battery_config: Dict[str, float],
                             prices: np.ndarray,
                             sell_price: float,
                             strategy_func: Callable,
                             mode: str = "step") -> pd.DataFrame:
    """
    Run simulation over multiple days.
    
    Args:
        solar: Multi-day solar profile
        load: Multi-day load profile
        battery_config: Dict with battery parameters
        prices: Price array (will be tiled for multiple days)
        sell_price: Feed-in tariff
        strategy_func: Control strategy
        mode: Simulation mode
    
    Returns:
        DataFrame with multi-day results
    """
    from backend.battery_model import Battery
    
    # Initialize battery
    battery = Battery(
        capacity=battery_config.get('capacity', 13.5),
        soc=battery_config.get('initial_soc', 0),
        max_charge=battery_config.get('max_charge', 5.0),
        max_discharge=battery_config.get('max_discharge', 5.0),
        efficiency=battery_config.get('efficiency', 0.95),
        temperature=battery_config.get('temperature', 25.0)
    )
    
    # Extend prices to match profile length
    days = len(solar) // 24
    extended_prices = np.tile(prices, days)
    
    # Run simulation
    df = run_simulation(solar, load, battery, extended_prices, sell_price, 
                       strategy_func, mode)
    
    # Add day number
    df['day'] = df.index // 24
    df['hour_of_day'] = df.index % 24
    
    return df


def compare_strategies(solar: np.ndarray,
                      load: np.ndarray,
                      battery_config: Dict[str, float],
                      prices: np.ndarray,
                      sell_price: float,
                      strategies: Dict[str, Callable]) -> Dict[str, pd.DataFrame]:
    """
    Run and compare multiple strategies.
    
    Args:
        solar: Solar generation profile
        load: Load demand profile
        battery_config: Battery configuration
        prices: Grid prices
        sell_price: Feed-in tariff
        strategies: Dict of {name: strategy_function}
    
    Returns:
        Dict of {strategy_name: results_df}
    """
    from backend.battery_model import Battery
    
    results = {}
    
    for name, strategy_func in strategies.items():
        # Create fresh battery for each strategy
        battery = Battery(
            capacity=battery_config.get('capacity', 13.5),
            soc=battery_config.get('initial_soc', 0),
            max_charge=battery_config.get('max_charge', 5.0),
            max_discharge=battery_config.get('max_discharge', 5.0),
            efficiency=battery_config.get('efficiency', 0.95)
        )
        
        # Determine mode
        mode = "global" if name in ["linear_optimizer", "mpc"] else "step"
        
        # Run simulation
        df = run_simulation(solar, load, battery, prices, sell_price, 
                          strategy_func, mode)
        
        results[name] = df
    
    return results

def validate_simulation_results(df, solar, load, tolerance):
    from .metrics import check_energy_balance
    return check_energy_balance(df, solar, load, tolerance)

class Simulator:
    """Main simulator class for running energy management simulations."""
    
    def __init__(self):
        """Initialize simulator."""
        pass
    
    def run(self, 
            solar: np.ndarray, 
            load: np.ndarray, 
            battery, 
            prices: np.ndarray, 
            sell_price: float, 
            strategy_func: Callable, 
            mode: str = "step") -> pd.DataFrame:
        """Run simulation using specified strategy."""
        return run_simulation(solar, load, battery, prices, sell_price, strategy_func, mode)
    
    def run_multi_day(self,
                     solar: np.ndarray,
                     load: np.ndarray,
                     battery_config: Dict[str, float],
                     prices: np.ndarray,
                     sell_price: float,
                     strategy_func: Callable,
                     mode: str = "step") -> pd.DataFrame:
        """Run multi-day simulation."""
        return run_multi_day_simulation(solar, load, battery_config, prices, sell_price, strategy_func, mode)
    
    def compare_strategies(self,
                          solar: np.ndarray,
                          load: np.ndarray,
                          battery_config: Dict[str, float],
                          prices: np.ndarray,
                          sell_price: float,
                          strategies: Dict[str, Callable]) -> Dict[str, pd.DataFrame]:
        """Compare multiple strategies."""
        return compare_strategies(solar, load, battery_config, prices, sell_price, strategies)
    
    def validate(self, df, solar, load, tolerance=0.01):
        """Validate simulation results."""
        return validate_simulation_results(df, solar, load, tolerance)