"""
Pricing Module
Handles electricity pricing models and tariff structures.
"""

import numpy as np
from typing import Tuple, Dict


class PricingManager:
    """Manage electricity pricing and tariff structures."""
    
    # Grid parameters
    GRID_SELL_PRICE = 3.0  # Feed-in tariff (₹/kWh)
    MAX_GRID_IMPORT = 50.0  # kW
    MAX_GRID_EXPORT = 10.0  # kW
    
    # Carbon intensity (kg CO2/kWh)
    GRID_CARBON_INTENSITY = 0.82  # India grid average
    SOLAR_CARBON_INTENSITY = 0.05  # Lifecycle emissions
    
    def __init__(self):
        """Initialize pricing manager."""
        pass
    
    def get_tou_pricing(self) -> np.ndarray:
        """
        Get Time-of-Use pricing.
        
        Hours:
        - 00-06: Off-peak (₹3)
        - 07-09: Peak (₹12)
        - 10-16: Mid-peak (₹5)
        - 17-20: Peak (₹12)
        - 21-23: Mid-peak (₹5)
        
        Returns:
            24-hour price array
        """
        return np.array(
            [3]*7 + [12]*3 + [5]*7 + [12]*4 + [5]*3, 
            dtype=float
        )
    
    def get_flat_pricing(self, rate: float = 5.0) -> np.ndarray:
        """
        Get flat rate pricing.
        
        Args:
            rate: Flat rate in ₹/kWh
            
        Returns:
            24-hour price array
        """
        return np.full(24, rate, dtype=float)
    
    def get_dynamic_pricing(self, 
                           base_price: float = 5.0,
                           volatility: float = 0.3) -> np.ndarray:
        """
        Generate simulated dynamic/real-time pricing.
        
        Args:
            base_price: Base price in ₹/kWh
            volatility: Price volatility factor
            
        Returns:
            24-hour price array with random variations
        """
        prices = []
        current_price = base_price
        
        for hour in range(24):
            # Random walk
            change = np.random.normal(0, volatility)
            current_price = max(2.0, current_price + change)
            
            # Peak hour multiplier
            if hour in [7, 8, 9, 17, 18, 19, 20]:
                current_price *= 1.5
            
            prices.append(current_price)
        
        return np.array(prices)
    
    def get_pricing(self, 
                   model: str = "TOU",
                   **kwargs) -> Tuple[np.ndarray, float]:
        """
        Get pricing based on model type.
        
        Args:
            model: "TOU", "Flat", or "Dynamic"
            **kwargs: Additional parameters for specific models
            
        Returns:
            Tuple of (buy_prices, sell_price)
        """
        if model == "TOU":
            prices = self.get_tou_pricing()
        elif model == "Flat":
            rate = kwargs.get('rate', 5.0)
            prices = self.get_flat_pricing(rate)
        elif model == "Dynamic":
            base = kwargs.get('base_price', 5.0)
            vol = kwargs.get('volatility', 0.3)
            prices = self.get_dynamic_pricing(base, vol)
        else:
            prices = self.get_tou_pricing()
        
        sell_price = kwargs.get('sell_price', self.GRID_SELL_PRICE)
        
        return prices, sell_price
    
    def calculate_cost(self,
                      grid_buy: np.ndarray,
                      grid_sell: np.ndarray,
                      prices: np.ndarray,
                      sell_price: float) -> np.ndarray:
        """
        Calculate hourly costs.
        
        Args:
            grid_buy: Grid import power (kW)
            grid_sell: Grid export power (kW)
            prices: Buy prices (₹/kWh)
            sell_price: Sell price (₹/kWh)
            
        Returns:
            Hourly cost array
        """
        return grid_buy * prices - grid_sell * sell_price
    
    def calculate_carbon_emissions(self,
                                   grid_buy: float,
                                   solar_gen: float) -> Dict[str, float]:
        """
        Calculate carbon emissions.
        
        Args:
            grid_buy: Total grid import (kWh)
            solar_gen: Total solar generation (kWh)
            
        Returns:
            Dict with emission metrics
        """
        grid_carbon = grid_buy * self.GRID_CARBON_INTENSITY
        solar_carbon = solar_gen * self.SOLAR_CARBON_INTENSITY
        total_carbon = grid_carbon + solar_carbon
        
        return {
            "grid_carbon": grid_carbon,
            "solar_carbon": solar_carbon,
            "total_carbon": total_carbon,
            "carbon_intensity": total_carbon / (grid_buy + solar_gen) if (grid_buy + solar_gen) > 0 else 0
        }