import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from predator_prey_simulation import PredatorPreySimulation, FunctionalResponseType
import time

def sidebar_controls():
    """Create sidebar controls for the predator-prey simulation"""
    st.sidebar.header("🦁 Predator-Prey Simulation Controls")
    
    st.sidebar.subheader("Population Settings")
    particles_per_type = st.sidebar.number_input(
        "Particles per Type", 
        min_value=10, max_value=100, value=50, step=10
    )
    
    st.sidebar.subheader("Physics Parameters")
    dt = st.sidebar.slider("Time Step", min_value=0.01, max_value=0.05, value=0.02, step=0.005)
    friction = st.sidebar.slider("Friction", min_value=0.8, max_value=0.99, value=0.95, step=0.01)
    interaction_radius = st.sidebar.slider("Interaction Radius", min_value=30, max_value=120, value=60, step=10)
    
    st.sidebar.subheader("Biological Parameters")
    energy_decay = st.sidebar.slider("Energy Decay Rate", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
    reproduction_threshold = st.sidebar.slider("Reproduction Energy Threshold", min_value=100, max_value=200, value=150, step=10)
    energy_gain = st.sidebar.slider("Energy Gain from Prey", min_value=20, max_value=100, value=50, step=10)
    
    return (particles_per_type, dt, friction, interaction_radius, 
            energy_decay, reproduction_threshold, energy_gain)

def create_functional_response_plot():
    """Create a plot showing the four functional response types"""
    prey_density = list(range(0, 101, 2))
    
    # Calculate responses for each type
    type_i = [min(0.8, (x / 50) * 0.8) for x in prey_density]  # Linear until threshold
    type_ii = [(1.0 * x) / (20 + x) for x in prey_density]  # Hyperbolic
    type_iii = [1.2 / (1 + math.exp(-0.1 * (x - 30))) for x in prey_density]  # Sigmoidal
    type_iv = []  # Dome-shaped
    for x in prey_density:
        if x <= 40:
            type_iv.append((x / 40) * 0.9)
        else:
            excess = x - 40
            decline = math.exp(-0.02 * excess)
            type_iv.append(0.9 * decline)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=prey_density, y=type_i, name='Type I - Linear', 
                            line=dict(color='red', width=3)))
    fig.add_trace(go.Scatter(x=prey_density, y=type_ii, name='Type II - Hyperbolic', 
                            line=dict(color='green', width=3)))
    fig.add_trace(go.Scatter(x=prey_density, y=type_iii, name='Type III - Sigmoidal', 
                            line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(x=prey_density, y=type_iv, name='Type IV - Dome-shaped', 
                            line=dict(color='orange', width=3)))
    
    fig.update_layout(
        title="Functional Response Types",
        xaxis_title="Prey Density",
        yaxis_title="Consumption Rate",
        height=400,
        showlegend=True
    )
    
    return fig

def create_population_chart(population_history):
    """Create a real-time population chart"""
    if not population_history:
        return go.Figure()
        
    df = pd.DataFrame(population_history)
    
    fig = go.Figure()
    
    colors = ['red', 'green', 'blue', 'orange']
    names = ['Type I (Red)', 'Type II (Green)', 'Type III (Blue)', 'Type IV (Orange)']
    
    for i in range(4):
        if i in df.columns:
            fig.add_trace(go.Scatter(
                x=list(range(len(df))),
                y=df[i],
                name=names[i],
                line=dict(color=colors[i], width=2),
                mode='lines'
            ))
    
    fig.update_layout(
        title="Population Dynamics Over Time",
        xaxis_title="Time Steps",
        yaxis_title="Population Count",
        height=300,
        showlegend=True
    )
    
    return fig

def display_particle_info():
    """Display information about each particle type"""
    st.subheader("🔬 Particle Types & Functional Responses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔴 Type I (Red) - Linear Response**
        - Linear increase in consumption with prey density
        - Reaches satiation threshold
        - Example: Filter feeders
        - Simple, predictable hunting behavior
        """)
        
        st.markdown("""
        **🟢 Type II (Green) - Hyperbolic Response**
        - Rapid initial increase, then levels off
        - Limited by handling time
        - Most common in nature
        - Efficient at low prey densities
        """)
    
    with col2:
        st.markdown("""
        **🔵 Type III (Blue) - Sigmoidal Response**
        - S-shaped curve with threshold effect
        - Low consumption at low densities
        - May involve prey switching or learning
        - Can create refuge effects
        """)
        
        st.markdown("""
        **🟡 Type IV (Orange) - Dome-shaped Response**
        - Peak consumption at intermediate densities
        - Decreases at high prey densities
        - May involve dangerous or difficult prey
        - Rare but important for certain systems
        """)

def main_controls():
    """Create main control buttons"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        run_btn = st.button("🚀 Start Simulation", key="start_sim")
    with col2:
        pause_btn = st.button("⏸️ Pause", key="pause_sim")
    with col3:
        reset_btn = st.button("🔄 Reset", key="reset_sim")
    
    return run_btn, pause_btn, reset_btn

def simulation_stats_display(stats, total_particles):
    """Display current simulation statistics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    colors = ['🔴', '🟢', '🔵', '🟡']
    names = ['Type I', 'Type II', 'Type III', 'Type IV']
    
    with col1:
        st.metric("Total Population", total_particles)
    
    for i, (col, color, name) in enumerate(zip([col2, col3, col4, col5], colors, names)):
        with col:
            count = stats.get(i, 0)
            percentage = (count / max(total_particles, 1)) * 100
            st.metric(f"{color} {name}", f"{count} ({percentage:.1f}%)")

# Import math for the functional response plot
import math