"""
Backend Package - Microgrid Energy Management System
Contains all business logic, models, and simulation engine.
"""

from .battery_model import Battery
from .energy_profiles import ProfileGenerator
from .schedulers import StrategyManager, STRATEGIES, get_strategy
from .simulator import Simulator
from .metrics import MetricsCalculator
from .pricing import PricingManager
from .export_utils import ExportManager

__version__ = "2.0.0"
__all__ = [
    'Battery',
    'ProfileGenerator',
    'StrategyManager',
    'STRATEGIES',
    'get_strategy',
    'Simulator',
    'MetricsCalculator',
    'PricingManager',
    'ExportManager'
]