import numpy as np

class Battery:
    def __init__(self, capacity, soc, max_charge, max_discharge, efficiency, 
                 degradation_rate=0.00005, temperature=25.0):
        """
        Enhanced Battery Model with thermal effects and advanced degradation.
        
        Args:
            capacity (float): Total energy capacity in kWh
            soc (float): Initial State of Charge in kWh
            max_charge (float): Maximum charge power in kW
            max_discharge (float): Maximum discharge power in kW
            efficiency (float): Round-trip efficiency (0-1)
            degradation_rate (float): Capacity loss per kWh throughput
            temperature (float): Operating temperature in °C
        """
        self.original_capacity = capacity
        self.capacity = capacity
        self.soc = soc
        self.max_charge = max_charge
        self.max_discharge = max_discharge
        self.base_efficiency = efficiency
        self.efficiency = efficiency
        
        # Degradation tracking
        self.degradation_rate = degradation_rate 
        self.total_throughput = 0.0  # kWh processed
        self.cycles = 0.0  # Full cycle equivalent
        self.state_of_health = 100.0  # Percentage
        
        # Thermal modeling
        self.temperature = temperature
        self.optimal_temp = 25.0
        
        # Advanced metrics
        self.charge_events = 0
        self.discharge_events = 0
        self.peak_power_reached = 0
        
    def get_temperature_factor(self):
        """Calculate efficiency adjustment based on temperature."""
        # Efficiency decreases at extreme temperatures
        temp_diff = abs(self.temperature - self.optimal_temp)
        if temp_diff < 10:
            return 1.0
        elif temp_diff < 20:
            return 0.98
        elif temp_diff < 30:
            return 0.95
        else:
            return 0.90
    
    def update_efficiency(self):
        """Update efficiency based on temperature and SOH."""
        temp_factor = self.get_temperature_factor()
        soh_factor = self.state_of_health / 100.0
        self.efficiency = self.base_efficiency * temp_factor * soh_factor

    def update_degradation(self, energy_processed):
        """
        Advanced degradation model considering:
        - Throughput-based degradation
        - Cycle counting
        - State of Health calculation
        """
        self.total_throughput += energy_processed
        
        # Update cycles (2 kWh throughput = 1 cycle for a 1 kWh battery)
        self.cycles = self.total_throughput / (2 * self.original_capacity)
        
        # Linear degradation from throughput
        throughput_loss = self.total_throughput * self.degradation_rate
        
        # Additional cycle-based degradation (lithium-ion typical: 80% after 3000 cycles)
        cycle_degradation_factor = 0.2 / 3000  # 20% over 3000 cycles
        cycle_loss = self.cycles * cycle_degradation_factor * self.original_capacity
        
        # Total degradation
        total_loss = throughput_loss + cycle_loss
        self.capacity = max(0, self.original_capacity - total_loss)
        
        # Update State of Health
        self.state_of_health = (self.capacity / self.original_capacity) * 100
        
        # Update efficiency based on new SOH
        self.update_efficiency()

    def charge(self, energy):
        """
        Charges the battery with thermal and degradation effects.
        Returns: Actual energy drawn from source (input side).
        """
        if energy > 0:
            self.charge_events += 1
            
        # Check physical limits
        space_available = self.capacity - self.soc
        
        # C-rate limiting (prevent charging too fast relative to capacity)
        # Typical max C-rate for Li-ion: 1C (full capacity in 1 hour)
        c_rate_limit = self.capacity * 1.0  # 1C rate
        safe_charge_rate = min(self.max_charge, c_rate_limit)
        
        # Limit by power, capacity, and C-rate
        accepted_energy = min(energy, safe_charge_rate, space_available)
        
        # Track peak power
        if accepted_energy > self.peak_power_reached:
            self.peak_power_reached = accepted_energy
        
        # Update SOC with efficiency losses
        self.soc += accepted_energy * self.efficiency
        
        # Ensure SOC doesn't exceed capacity due to rounding
        self.soc = min(self.soc, self.capacity)
        
        # Apply degradation
        self.update_degradation(accepted_energy)
        
        return accepted_energy

    def discharge(self, energy):
        """
        Discharges the battery with thermal and degradation effects.
        Returns: Actual energy provided to load (output side).
        """
        if energy > 0:
            self.discharge_events += 1
            
        # C-rate limiting for discharge
        c_rate_limit = self.capacity * 1.0  # 1C rate
        safe_discharge_rate = min(self.max_discharge, c_rate_limit)
        
        # Limit by power, stored energy, and C-rate
        supplied_energy = min(energy, safe_discharge_rate, self.soc)
        
        # Track peak power
        if supplied_energy > self.peak_power_reached:
            self.peak_power_reached = supplied_energy
        
        # Update SOC
        self.soc -= supplied_energy
        
        # Apply degradation
        self.update_degradation(supplied_energy)
        
        return supplied_energy
    
    def get_metrics(self):
        """Return comprehensive battery metrics."""
        return {
            "capacity": self.capacity,
            "soc": self.soc,
            "soc_percent": (self.soc / self.capacity * 100) if self.capacity > 0 else 0,
            "state_of_health": self.state_of_health,
            "cycles": self.cycles,
            "throughput": self.total_throughput,
            "charge_events": self.charge_events,
            "discharge_events": self.discharge_events,
            "efficiency": self.efficiency,
            "temperature": self.temperature,
            "degradation": self.original_capacity - self.capacity
        }