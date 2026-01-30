"""
Export Utilities Module
Handles data export to various formats.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import json


class ExportManager:
    """Manager for exporting simulation results."""
    
    def __init__(self):
        """Initialize export manager."""
        pass
    
    def to_csv(self, data: pd.DataFrame, filepath: str) -> None:
        """
        Export DataFrame to CSV.
        
        Args:
            data: DataFrame to export
            filepath: Output file path
        """
        data.to_csv(filepath, index=False)
    
    def to_excel(self, 
                 data_dict: Dict[str, pd.DataFrame], 
                 filepath: str) -> None:
        """
        Export multiple DataFrames to Excel with different sheets.
        
        Args:
            data_dict: Dict of sheet_name -> DataFrame
            filepath: Output file path
        """
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def to_json(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Export dictionary to JSON.
        
        Args:
            data: Dictionary to export
            filepath: Output file path
        """
        # Convert numpy types to native Python types
        cleaned_data = self._convert_numpy_types(data)
        
        with open(filepath, 'w') as f:
            json.dump(cleaned_data, f, indent=2)
    
    def results_to_csv(self, 
                      results_df: pd.DataFrame,
                      solar: np.ndarray,
                      load: np.ndarray,
                      filepath: str) -> None:
        """
        Export comprehensive results including profiles.
        
        Args:
            results_df: Simulation results
            solar: Solar profile
            load: Load profile
            filepath: Output file path
        """
        # Combine all data
        combined = results_df.copy()
        combined['solar'] = solar
        combined['load'] = load
        combined['hour'] = list(range(len(solar)))
        
        # Reorder columns for clarity
        cols = ['hour', 'solar', 'load'] + [col for col in results_df.columns]
        combined = combined[cols]
        
        combined.to_csv(filepath, index=False)
    
    def kpis_to_csv(self, kpis: Dict[str, Any], filepath: str) -> None:
        """
        Export KPIs to CSV.
        
        Args:
            kpis: KPIs dictionary
            filepath: Output file path
        """
        df = pd.DataFrame([kpis])
        df.to_csv(filepath, index=False)
    
    def comparison_to_csv(self,
                         comparison_df: pd.DataFrame,
                         filepath: str) -> None:
        """
        Export strategy comparison to CSV.
        
        Args:
            comparison_df: Comparison DataFrame
            filepath: Output file path
        """
        comparison_df.to_csv(filepath, index=False)
    
    def export_complete_report(self,
                              results_dict: Dict[str, pd.DataFrame],
                              kpis_dict: Dict[str, Dict],
                              comparison_df: pd.DataFrame,
                              solar: np.ndarray,
                              load: np.ndarray,
                              output_dir: str) -> Dict[str, str]:
        """
        Export complete report with all data.
        
        Args:
            results_dict: Dict of strategy -> results DataFrame
            kpis_dict: Dict of strategy -> KPIs
            comparison_df: Strategy comparison DataFrame
            solar: Solar profile
            load: Load profile
            output_dir: Output directory
            
        Returns:
            Dict of exported file paths
        """
        import os
        
        exported_files = {}
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Export each strategy's results
        for strategy_name, df in results_dict.items():
            filepath = os.path.join(output_dir, f"{strategy_name}_results.csv")
            self.results_to_csv(df, solar, load, filepath)
            exported_files[f"{strategy_name}_results"] = filepath
        
        # Export KPIs
        for strategy_name, kpis in kpis_dict.items():
            filepath = os.path.join(output_dir, f"{strategy_name}_kpis.csv")
            self.kpis_to_csv(kpis, filepath)
            exported_files[f"{strategy_name}_kpis"] = filepath
        
        # Export comparison
        comparison_path = os.path.join(output_dir, "strategy_comparison.csv")
        self.comparison_to_csv(comparison_df, comparison_path)
        exported_files["comparison"] = comparison_path
        
        # Export profiles
        profiles_df = pd.DataFrame({
            'hour': list(range(len(solar))),
            'solar': solar,
            'load': load
        })
        profiles_path = os.path.join(output_dir, "profiles.csv")
        profiles_df.to_csv(profiles_path, index=False)
        exported_files["profiles"] = profiles_path
        
        # Export all KPIs as JSON for easy parsing
        kpis_json_path = os.path.join(output_dir, "all_kpis.json")
        self.to_json(kpis_dict, kpis_json_path)
        exported_files["all_kpis_json"] = kpis_json_path
        
        return exported_files
    
    def _convert_numpy_types(self, obj: Any) -> Any:
        """Convert numpy types to Python native types for JSON serialization."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj