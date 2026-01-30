"""
Energy Profiles Module
Handles solar generation and load demand profile generation.
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class ProfileGenerator:
    """Generate realistic solar and load profiles."""
    
    def __init__(self):
        """Initialize the profile generator."""
        self.weather_factors = {
            "sunny": 1.0,
            "cloudy": 0.5,
            "rainy": 0.2,
            "mixed": 0.7,
            "partly_cloudy": 0.75
        }
    
    def generate_solar_profile(self, 
                              peak_power: float = 5.0,
                              noise_level: float = 0.0,
                              weather: str = "sunny",
                              day_of_year: int = 180) -> np.ndarray:
        """
        Generate solar generation profile.
        
        Args:
            peak_power: Maximum solar output in kW
            noise_level: Forecast uncertainty (0-1)
            weather: Weather condition
            day_of_year: Day number (1-365) for seasonal adjustment
            
        Returns:
            24-hour solar generation profile
        """
        solar = np.zeros(24)
        
        # Weather-based irradiance factor
        weather_factor = self.weather_factors.get(weather, 1.0)
        
        # Seasonal adjustment (cosine wave, peak at summer solstice ~day 172)
        seasonal_factor = 0.8 + 0.4 * np.cos(2 * np.pi * (day_of_year - 172) / 365)
        
        # Solar generation window (6 AM to 6 PM)
        sunrise = 6
        sunset = 18
        
        for t in range(sunrise, sunset):
            # Gaussian-like distribution centered at noon
            hours_from_noon = t - 12
            base = peak_power * np.exp(-(hours_from_noon**2) / 18)
            
            # Apply weather and seasonal factors
            adjusted = base * weather_factor * seasonal_factor
            
            # Add intermittency for cloudy weather
            if weather in ["cloudy", "mixed", "partly_cloudy"] and noise_level > 0:
                cloud_noise = np.random.uniform(-0.3, 0.3) * adjusted
                adjusted = max(0, adjusted + cloud_noise)
            
            # Add forecast uncertainty
            if noise_level > 0:
                forecast_error = np.random.normal(0, noise_level * adjusted)
                solar[t] = max(0, adjusted + forecast_error)
            else:
                solar[t] = adjusted
        
        return solar
    
    def generate_load_profile(self,
                             profile_type: str = "residential",
                             noise_level: float = 0.0,
                             day_type: str = "weekday") -> Dict[str, np.ndarray]:
        """
        Generate load demand profile.
        
        Args:
            profile_type: "residential", "commercial", or "industrial"
            noise_level: Load uncertainty (0-1)
            day_type: "weekday" or "weekend"
            
        Returns:
            Dict with 'critical', 'flexible', 'total', and 'details'
        """
        if profile_type == "residential":
            critical, flexible = self._residential_profile(day_type)
        elif profile_type == "commercial":
            critical, flexible = self._commercial_profile(day_type)
        elif profile_type == "industrial":
            critical, flexible = self._industrial_profile(day_type)
        else:
            critical, flexible = self._residential_profile(day_type)
        
        # Add noise
        if noise_level > 0:
            critical_noise = np.random.normal(0, noise_level * 0.3, 24)
            critical = np.maximum(0.1, critical + critical_noise)
            
            flexible_noise = np.random.normal(0, noise_level * 0.5, 24)
            flexible = np.maximum(0, flexible + flexible_noise)
        
        total = critical + flexible
        
        details = {
            "peak_load": np.max(total),
            "avg_load": np.mean(total),
            "min_load": np.min(total),
            "total_energy": np.sum(total),
            "load_factor": np.mean(total) / np.max(total) if np.max(total) > 0 else 0
        }
        
        return {
            "critical": critical,
            "flexible": flexible,
            "total": total,
            "details": details
        }
    
    def _residential_profile(self, day_type: str = "weekday") -> Tuple[np.ndarray, np.ndarray]:
        """Generate residential load profile."""
        if day_type == "weekday":
            critical = np.array([
                0.5, 0.5, 0.5, 0.5, 0.5, 0.8,  # 00-05: Night
                1.5, 2.5, 2.8, 2.0, 1.2, 1.0,  # 06-11: Morning peak
                1.0, 1.0, 1.2, 1.5, 2.0, 3.0,  # 12-17: Afternoon
                4.2, 4.5, 4.0, 3.0, 2.0, 1.2   # 18-23: Evening peak
            ], dtype=float)
            
            flexible = np.zeros(24)
            flexible[13] = 2.5  # Washing machine
            flexible[14] = 2.0
            flexible[22] = 3.0  # EV charging
            flexible[23] = 3.0
        else:  # Weekend
            critical = np.array([
                0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # 00-05: Night
                0.8, 1.0, 2.0, 2.5, 2.8, 3.0,  # 06-11: Late morning
                3.2, 3.0, 2.8, 2.5, 2.5, 3.5,  # 12-17: Active day
                4.0, 4.2, 3.8, 3.0, 2.0, 1.0   # 18-23: Evening
            ], dtype=float)
            
            flexible = np.zeros(24)
            flexible[10] = 2.5
            flexible[11] = 2.0
            flexible[14] = 1.5
            flexible[15] = 1.5
        
        return critical, flexible
    
    def _commercial_profile(self, day_type: str = "weekday") -> Tuple[np.ndarray, np.ndarray]:
        """Generate commercial/office load profile."""
        if day_type == "weekday":
            critical = np.array([
                0.5, 0.5, 0.5, 0.5, 0.5, 1.0,  # 00-05: Minimal
                2.0, 4.0, 6.0, 7.5, 8.0, 8.5,  # 06-11: Ramp up
                9.0, 9.0, 8.5, 8.5, 8.0, 7.0,  # 12-17: Peak hours
                5.0, 3.0, 2.0, 1.5, 1.0, 0.8   # 18-23: Wind down
            ], dtype=float)
            
            flexible = np.zeros(24)
            flexible[12] = 2.0  # HVAC boost
            flexible[13] = 2.0
        else:  # Weekend
            critical = np.full(24, 1.0, dtype=float)
            flexible = np.zeros(24)
        
        return critical, flexible
    
    def _industrial_profile(self, day_type: str = "weekday") -> Tuple[np.ndarray, np.ndarray]:
        """Generate industrial load profile (24/7 operation)."""
        base_load = 15.0
        
        critical = np.full(24, base_load, dtype=float)
        critical[2:6] = base_load * 0.7  # Maintenance window
        critical[10:16] = base_load * 1.2  # Peak production
        
        flexible = np.zeros(24)
        flexible[3] = 2.0  # Heavy equipment off-peak
        flexible[4] = 2.0
        
        return critical, flexible
    
    def generate_multi_day_profiles(self,
                                   days: int = 7,
                                   profile_type: str = "residential",
                                   weather_pattern: str = "mixed") -> Dict[str, np.ndarray]:
        """
        Generate multi-day profiles.
        
        Args:
            days: Number of days
            profile_type: Load profile type
            weather_pattern: Weather pattern for period
            
        Returns:
            Dict with extended solar, load, and weather arrays
        """
        solar_full = []
        load_full = []
        weather_full = []
        
        weather_options = ["sunny", "cloudy", "partly_cloudy"]
        
        for day in range(days):
            day_type = "weekend" if day % 7 in [5, 6] else "weekday"
            
            if weather_pattern == "mixed":
                weather = np.random.choice(weather_options)
            else:
                weather = weather_pattern
            
            solar = self.generate_solar_profile(weather=weather, day_of_year=180+day)
            load_data = self.generate_load_profile(profile_type=profile_type, day_type=day_type)
            
            solar_full.extend(solar)
            load_full.extend(load_data["total"])
            weather_full.extend([weather] * 24)
        
        return {
            "solar": np.array(solar_full),
            "load": np.array(load_full),
            "weather": weather_full,
            "hours": days * 24
        }