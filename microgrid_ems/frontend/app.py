"""
Main Streamlit Application
Web interface for Microgrid Energy Management System.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend import (
    Battery, ProfileGenerator, StrategyManager,
    Simulator, MetricsCalculator, PricingManager, ExportManager
)
from frontend.components import (
    render_sidebar, render_header,
    render_metrics_row, render_energy_dashboard,
    render_strategy_comparison, render_financial_analysis,
    render_battery_analytics, render_environmental_impact,
    render_system_validation
)

# Page configuration
st.set_page_config(
    page_title="Advanced Microgrid EMS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize backend components
@st.cache_resource
def initialize_backend():
    """Initialize backend components."""
    return {
        'profile_gen': ProfileGenerator(),
        'pricing': PricingManager(),
        'strategy_mgr': StrategyManager(),
        'simulator': Simulator(),
        'metrics': MetricsCalculator(),
        'exporter': ExportManager()
    }

backend = initialize_backend()

# Render header
render_header()

# Render sidebar and get configuration
config = render_sidebar(backend['strategy_mgr'], backend['pricing'])

# Main application logic
if config['run_simulation'] or 'simulation_completed' not in st.session_state:
    
    if config['run_simulation']:
        with st.spinner("Running simulations..."):
            # Generate profiles
            solar_profile = backend['profile_gen'].generate_solar_profile(
                peak_power=config['solar_size'],
                noise_level=config['noise_level'],
                weather=config['weather'],
                day_of_year=config['day_of_year']
            )
            
            load_profile = backend['profile_gen'].generate_load_profile(
                profile_type=config['load_type'],
                noise_level=config['noise_level'],
                day_type=config['day_type']
            )
            
            solar = solar_profile
            load = load_profile['total']
            
            # Get pricing
            prices, sell_price = backend['pricing'].get_pricing(
                model=config['pricing_model'],
                rate=config.get('flat_rate', 5.0),
                volatility=config.get('volatility', 0.3)
            )
            sell_price = config['sell_price']
            
            # Run simulations for all selected strategies
            results_dict = {}
            battery_dict = {}
            
            for strategy_name in config['strategies']:
                # Create battery
                battery = Battery(
                    capacity=config['battery_cap'],
                    soc=config['initial_soc'],
                    max_charge=config['battery_power'],
                    max_discharge=config['battery_power'],
                    efficiency=0.95,
                    temperature=25.0
                )
                
                # Get strategy function
                strategy_func = backend['strategy_mgr'].get_strategy(strategy_name)
                
                # Determine mode
                mode = "global" if strategy_name in ["linear_optimizer", "mpc"] else "step"
                
                # Run simulation
                results_df = backend['simulator'].run(
                    solar, load, battery, prices, sell_price, strategy_func, mode
                )
                
                results_dict[strategy_name] = results_df
                battery_dict[strategy_name] = battery
            
            # Calculate KPIs
            system_config = {
                "battery_size": config['battery_cap'],
                "solar_size": config['solar_size']
            }
            
            kpis_dict = {}
            for strategy_name in config['strategies']:
                df = results_dict[strategy_name]
                battery = battery_dict[strategy_name]
                battery_metrics = battery.get_metrics()
                
                kpis = backend['metrics'].calculate_kpis(
                    results_df=df,
                    total_load_kwh=load.sum(),
                    battery_metrics=battery_metrics,
                    prices=prices,
                    system_config=system_config
                )
                
                kpis_dict[strategy_name] = kpis
            
            # Cache in session state
            st.session_state.results_dict = results_dict
            st.session_state.battery_dict = battery_dict
            st.session_state.kpis_dict = kpis_dict
            st.session_state.solar = solar
            st.session_state.load = load
            st.session_state.prices = prices
            st.session_state.sell_price = sell_price
            st.session_state.strategies = config['strategies']
            st.session_state.system_config = system_config
            st.session_state.simulation_completed = True

# Display results if simulation completed
if 'simulation_completed' in st.session_state and st.session_state.simulation_completed:
    # Get cached data
    results_dict = st.session_state.results_dict
    battery_dict = st.session_state.battery_dict
    kpis_dict = st.session_state.kpis_dict
    solar = st.session_state.solar
    load = st.session_state.load
    prices = st.session_state.prices
    strategies = st.session_state.strategies
    system_config = st.session_state.system_config
    
    # Find best strategy
    best_strategy = min(kpis_dict.items(), key=lambda x: x[1]["Total Cost"])[0]
    best_kpis = kpis_dict[best_strategy]
    
    # Render top metrics
    render_metrics_row(best_strategy, best_kpis)
    
    st.divider()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Energy Dashboard",
        "⚖️ Strategy Comparison",
        "💰 Financial Analysis",
        "🔋 Battery Analytics",
        "🌍 Environmental Impact",
        "🔧 System Validation"
    ])
    
    with tab1:
        render_energy_dashboard(
            results_dict[best_strategy], 
            solar, load, prices, 
            config['battery_cap']
        )
    
    with tab2:
        comparison_df = backend['metrics'].compare_strategies(results_dict, strategies)
        render_strategy_comparison(
            kpis_dict, strategies, 
            results_dict, best_strategy,
            comparison_df
        )
    
    with tab3:
        financial_metrics = backend['metrics'].calculate_financial_metrics(
            best_kpis, system_config
        )
        render_financial_analysis(financial_metrics)
    
    with tab4:
        render_battery_analytics(
            battery_dict[best_strategy],
            results_dict[best_strategy],
            config['battery_cap']
        )
    
    with tab5:
        render_environmental_impact(best_kpis, solar, load, results_dict[best_strategy])
    
    with tab6:
        validation = backend['metrics'].check_energy_balance(
            results_dict[best_strategy], solar, load
        )
        render_system_validation(
            results_dict[best_strategy], 
            solar, load, validation,
            backend['exporter'], best_kpis,
            comparison_df, best_strategy
        )

else:
    st.info("👈 Configure your system in the sidebar and click '🚀 Run Simulation' to begin!")
    
    with st.expander("💡 Quick Start Guide"):
        st.markdown("""
        ### Getting Started
        
        1. **Configure Battery**: 13.5 kWh, 5 kW (Tesla Powerwall 2)
        2. **Configure Solar**: 5 kW, Sunny weather
        3. **Select Strategies**: Naive + Linear Optimizer
        4. **Run Simulation**: Click the button!
        
        ### Example Results
        - Cost Reduction: 35-45%
        - Self-Sufficiency: 60-75%
        - Carbon Reduction: 65%+
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Advanced Microgrid EMS</strong> | Production-Grade Architecture</p>
    <p style='font-size: 0.8rem;'>Backend-Frontend Separation | © 2026</p>
</div>
""", unsafe_allow_html=True)