"""
UI Components Module
Reusable UI components for the Streamlit frontend.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any


def render_header():
    """Render application header."""
    st.markdown('<p class="main-header">⚡ Advanced Microgrid Energy Management System</p>', 
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Optimization & Techno-Economic Analysis Platform</p>', 
                unsafe_allow_html=True)


def render_sidebar(strategy_mgr, pricing_mgr) -> Dict[str, Any]:
    """
    Render sidebar with configuration controls.
    
    Returns:
        Dict with all configuration parameters
    """
    config = {}
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
        st.header("⚙️ System Configuration")
        
        # Battery Configuration
        with st.expander("🔋 Battery System", expanded=True):
            config['battery_cap'] = st.slider("Capacity (kWh)", 0.0, 50.0, 13.5, 0.5)
            config['battery_power'] = st.slider("Power Rating (kW)", 1.0, 20.0, 5.0, 0.5)
            initial_soc_pct = st.slider("Initial SOC (%)", 0, 100, 0, 5)
            config['initial_soc'] = config['battery_cap'] * (initial_soc_pct / 100.0)
        
        # Solar Configuration
        with st.expander("☀️ Solar PV System", expanded=True):
            config['solar_size'] = st.slider("Solar Capacity (kW)", 0.0, 20.0, 5.0, 0.5)
            config['weather'] = st.selectbox("Weather Condition", 
                                            ["sunny", "partly_cloudy", "cloudy", "rainy"])
            config['day_of_year'] = st.slider("Day of Year", 1, 365, 180)
        
        # Environment
        with st.expander("🌍 Environment & Uncertainty", expanded=False):
            config['noise_level'] = st.slider("Forecast Uncertainty (%)", 0, 30, 5) / 100.0
            config['load_type'] = st.selectbox("Load Profile", 
                                              ["residential", "commercial", "industrial"])
            config['day_type'] = st.selectbox("Day Type", ["weekday", "weekend"])
        
        # Pricing
        with st.expander("💰 Grid Pricing", expanded=False):
            config['pricing_model'] = st.selectbox("Pricing Model", ["TOU", "Flat", "Dynamic"])
            
            if config['pricing_model'] == "Flat":
                config['flat_rate'] = st.slider("Flat Rate (₹/kWh)", 2.0, 15.0, 5.0, 0.5)
            
            if config['pricing_model'] == "Dynamic":
                config['volatility'] = st.slider("Price Volatility", 0.1, 1.0, 0.3, 0.1)
            
            config['sell_price'] = st.slider("Feed-in Tariff (₹/kWh)", 1.0, 8.0, 3.0, 0.5)
        
        st.divider()
        
        # Strategy Selection
        st.header("🎯 Control Strategy")
        all_strategies = strategy_mgr.list_strategies()
        config['strategies'] = st.multiselect(
            "Select Strategies to Compare",
            all_strategies,
            default=["naive", "linear_optimizer"]
        )
        
        st.divider()
        config['run_simulation'] = st.button("🚀 Run Simulation", type="primary", 
                                             use_container_width=True)
    
    return config


def render_metrics_row(best_strategy: str, kpis: Dict[str, Any]):
    """Render top metrics row."""
    st.subheader(f"📊 Best Strategy: **{best_strategy.upper()}**")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Daily Cost", f"₹{kpis['Total Cost']:.2f}", 
                 delta=f"₹{kpis.get('Daily Savings', 0):.2f} saved",
                 delta_color="inverse")
    
    with col2:
        st.metric("Self-Sufficiency", f"{kpis['Self Sufficiency']:.1f}%")
    
    with col3:
        st.metric("Carbon Reduction", f"{kpis['Carbon Reduction']:.1f}%",
                 delta=f"{kpis['Carbon Avoided']:.1f} kg CO₂ avoided")
    
    with col4:
        st.metric("Battery SOH", f"{kpis['Battery SOH']:.1f}%",
                 delta=f"-{kpis['Battery Degradation']:.4f} kWh")
    
    with col5:
        st.metric("Payback Period", f"{kpis['Payback Period']:.1f} years")


def render_energy_dashboard(df_main: pd.DataFrame, 
                           solar: np.ndarray, 
                           load: np.ndarray,
                           prices: np.ndarray,
                           battery_cap: float):
    """Render energy dashboard tab."""
    st.subheader("Energy Flow Visualization")
    
    # Create power flow chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Power Flow", "Battery State of Charge"),
        row_heights=[0.7, 0.3],
        vertical_spacing=0.12
    )
    
    # Row 1: Power flows
    fig.add_trace(
        go.Scatter(x=list(range(24)), y=load, name="Load Demand", 
                  fill='tozeroy', line=dict(color='black', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=list(range(24)), y=solar, name="Solar Generation", 
                  line=dict(color='orange', width=2.5)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=list(range(24)), y=df_main['grid_buy'], name="Grid Import", 
              marker_color='red', opacity=0.6),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=list(range(24)), y=-df_main['grid_sell'], name="Grid Export", 
              marker_color='green', opacity=0.6),
        row=1, col=1
    )
    
    # Row 2: SOC and Price
    fig.add_trace(
        go.Scatter(x=list(range(24)), y=df_main['battery_soc'], name="SOC", 
                  line=dict(color='blue', width=3)),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=list(range(24)), y=prices, name="Grid Price", 
                  line=dict(color='red', width=2, dash='dash'), yaxis='y3'),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Hour of Day", row=2, col=1)
    fig.update_yaxes(title_text="Power (kW)", row=1, col=1)
    fig.update_yaxes(title_text="Energy (kWh)", row=2, col=1)
    
    fig.update_layout(
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Energy balance pie charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Energy Sources")
        sources = {
            "Solar": solar.sum(),
            "Grid Import": df_main['grid_buy'].sum(),
            "Battery Discharge": df_main['bat_discharge'].sum()
        }
        fig_sources = px.pie(values=list(sources.values()), names=list(sources.keys()),
                           title="Energy Sources Distribution")
        st.plotly_chart(fig_sources, use_container_width=True)
    
    with col2:
        st.subheader("Energy Sinks")
        sinks = {
            "Load": load.sum(),
            "Grid Export": df_main['grid_sell'].sum(),
            "Battery Charge": df_main['bat_charge'].sum()
        }
        fig_sinks = px.pie(values=list(sinks.values()), names=list(sinks.keys()),
                         title="Energy Sinks Distribution")
        st.plotly_chart(fig_sinks, use_container_width=True)


def render_strategy_comparison(kpis_dict: Dict[str, Dict],
                               strategies: List[str],
                               results_dict: Dict[str, pd.DataFrame],
                               best_strategy: str,
                               comparison_df: pd.DataFrame):
    """Render strategy comparison tab."""
    st.subheader("Strategy Performance Comparison")
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Visual comparison
    col1, col2 = st.columns(2)
    
    with col1:
        costs = [kpis_dict[s]['Total Cost'] for s in strategies]
        fig_cost = go.Figure(data=[
            go.Bar(x=strategies, y=costs, 
                  marker_color=['green' if s == best_strategy else 'lightblue' 
                               for s in strategies])
        ])
        fig_cost.update_layout(title="Cost Comparison", yaxis_title="Cost (₹)")
        st.plotly_chart(fig_cost, use_container_width=True)
    
    with col2:
        ss = [kpis_dict[s]['Self Sufficiency'] for s in strategies]
        fig_ss = go.Figure(data=[
            go.Bar(x=strategies, y=ss,
                  marker_color=['green' if s == best_strategy else 'lightcoral' 
                               for s in strategies])
        ])
        fig_ss.update_layout(title="Self-Sufficiency Comparison", yaxis_title="%")
        st.plotly_chart(fig_ss, use_container_width=True)


def render_financial_analysis(financial_metrics: Dict[str, float]):
    """Render financial analysis tab."""
    st.subheader("Financial Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total CAPEX", f"₹{financial_metrics['Total CAPEX']:,.0f}")
        st.metric("Battery CAPEX", f"₹{financial_metrics['Battery CAPEX']:,.0f}")
        st.metric("Solar CAPEX", f"₹{financial_metrics['Solar CAPEX']:,.0f}")
    
    with col2:
        st.metric("Annual Savings", f"₹{financial_metrics['Annual Cash Flow']:,.0f}")
        st.metric("Annual O&M", f"₹{financial_metrics['Annual O&M']:,.0f}")
        st.metric("NPV", f"₹{financial_metrics['NPV']:,.0f}")
    
    with col3:
        st.metric("LCOE", f"₹{financial_metrics['LCOE']:.3f}/kWh")
        st.metric("Payback Period", f"{financial_metrics['Payback Period']:.1f} years")
    
    # Cash flow projection
    st.subheader("10-Year Cash Flow Projection")
    years = list(range(0, 11))
    cash_flows = [-financial_metrics['Total CAPEX']]
    cumulative = [-financial_metrics['Total CAPEX']]
    
    for year in range(1, 11):
        annual_cf = financial_metrics['Annual Cash Flow']
        cash_flows.append(annual_cf)
        cumulative.append(cumulative[-1] + annual_cf)
    
    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(x=years, y=cash_flows, name="Annual Cash Flow",
                           marker_color=['red' if cf < 0 else 'green' for cf in cash_flows]))
    fig_cf.add_trace(go.Scatter(x=years, y=cumulative, name="Cumulative",
                               line=dict(color='blue', width=3), mode='lines+markers'))
    fig_cf.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_cf.update_layout(title="Cash Flow Analysis", xaxis_title="Year", yaxis_title="₹")
    st.plotly_chart(fig_cf, use_container_width=True)


def render_battery_analytics(battery, df_main: pd.DataFrame, battery_cap: float):
    """Render battery analytics tab."""
    st.subheader("Battery Performance Analytics")
    
    battery_metrics = battery.get_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("State of Health", f"{battery_metrics['state_of_health']:.1f}%")
        st.metric("Total Cycles", f"{battery_metrics['cycles']:.2f}")
    
    with col2:
        st.metric("Throughput", f"{battery_metrics['throughput']:.2f} kWh")
        st.metric("Efficiency", f"{battery_metrics['efficiency']*100:.1f}%")
    
    with col3:
        st.metric("Charge Events", f"{battery_metrics['charge_events']}")
        st.metric("Discharge Events", f"{battery_metrics['discharge_events']}")
    
    with col4:
        st.metric("Capacity Loss", f"{battery_metrics['degradation']:.4f} kWh")
        st.metric("SOC (%)", f"{battery_metrics['soc_percent']:.1f}%")
    
    # SOC chart
    st.subheader("State of Charge Profile")
    fig_soc = go.Figure()
    fig_soc.add_trace(go.Scatter(x=list(range(24)), y=df_main['battery_soc'],
                                 fill='tozeroy', name='SOC', line=dict(color='blue', width=3)))
    fig_soc.add_hline(y=battery_cap, line_dash="dash", line_color="red",
                     annotation_text="Max Capacity")
    fig_soc.update_layout(title="Battery SOC", xaxis_title="Hour", yaxis_title="kWh")
    st.plotly_chart(fig_soc, use_container_width=True)


def render_environmental_impact(kpis: Dict, solar: np.ndarray, load: np.ndarray, df_main: pd.DataFrame):
    """Render environmental impact tab."""
    st.subheader("Environmental Impact Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Carbon", f"{kpis['Total Carbon']:.2f} kg CO₂")
        st.metric("Carbon per kWh", f"{kpis['Carbon per kWh']:.3f} kg")
    
    with col2:
        st.metric("Carbon Avoided", f"{kpis['Carbon Avoided']:.2f} kg CO₂")
        st.metric("Reduction", f"{kpis['Carbon Reduction']:.1f}%")
    
    with col3:
        annual = kpis['Carbon Avoided'] * 365
        st.metric("Annual Avoided", f"{annual:.0f} kg CO₂")
        st.metric("Trees Equivalent", f"{annual/21:.0f} trees")
    
    # Carbon comparison
    st.subheader("Carbon Footprint Comparison")
    scenarios = {
        "Pure Grid": load.sum() * 0.82,
        "With Solar Only": (load.sum() - solar.sum()) * 0.82 + solar.sum() * 0.05,
        "With Solar + Battery": kpis['Total Carbon']
    }
    
    fig_carbon = px.bar(x=list(scenarios.keys()), y=list(scenarios.values()),
                      title="Daily Carbon Emissions",
                      labels={'x': 'Scenario', 'y': 'kg CO₂'})
    st.plotly_chart(fig_carbon, use_container_width=True)


def render_system_validation(df_main: pd.DataFrame, 
                            solar: np.ndarray,
                            load: np.ndarray,
                            validation: Dict,
                            exporter,
                            best_kpis: Dict,
                            comparison_df: pd.DataFrame,
                            best_strategy: str):
    """Render system validation tab."""
    st.subheader("System Validation & Diagnostics")
    
    if validation['passed']:
        st.success("✅ ENERGY BALANCE VERIFIED")
    else:
        st.error(f"❌ ENERGY BALANCE VIOLATION: {validation['num_violations']} errors")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max Imbalance", f"{validation['max_error']:.6f} kWh")
    with col2:
        st.metric("Avg Imbalance", f"{validation['avg_error']:.6f} kWh")
    with col3:
        st.metric("Total Imbalance", f"{validation['total_imbalance']:.6f} kWh")
    
    # Energy balance table
    st.subheader("Hourly Energy Balance")
    balance_df = pd.DataFrame({
        'Hour': list(range(len(solar))),
        'Solar': solar,
        'Grid Buy': df_main['grid_buy'],
        'Bat Discharge': df_main['bat_discharge'],
        'Load': load,
        'Grid Sell': df_main['grid_sell'],
        'Bat Charge': df_main['bat_charge'],
        'SOC': df_main['battery_soc'],
        'Cost': df_main['cost']
    })
    
    balance_df['Total In'] = balance_df['Solar'] + balance_df['Grid Buy'] + balance_df['Bat Discharge']
    balance_df['Total Out'] = balance_df['Load'] + balance_df['Grid Sell'] + balance_df['Bat Charge']
    balance_df['Balance'] = balance_df['Total In'] - balance_df['Total Out']
    
    st.dataframe(balance_df, use_container_width=True, height=400)
    
    # Download buttons
    st.divider()
    st.subheader("📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = balance_df.to_csv(index=False)
        st.download_button("Download Hourly Data", csv, 
                         f"ems_results_{best_strategy}.csv", "text/csv")
    
    with col2:
        kpis_df = pd.DataFrame([best_kpis])
        st.download_button("Download KPIs", kpis_df.to_csv(index=False),
                         f"ems_kpis_{best_strategy}.csv", "text/csv")
    
    with col3:
        st.download_button("Download Comparison", comparison_df.to_csv(index=False),
                         "ems_comparison.csv", "text/csv")