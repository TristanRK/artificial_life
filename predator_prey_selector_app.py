import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
from true_predator_prey_simulation import TruePredatorPreySimulation, FunctionalResponseType

# Configure Streamlit page
st.set_page_config(
    page_title="Predator-Prey Functional Response Selector",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🦁 Predator-Prey Functional Response Demonstrations")
st.markdown("""
Select a **functional response type** to observe how different predator hunting strategies affect population dynamics.
- **🔴 Red circles**: Predators
- **🔵 Blue circles**: Prey
""")

# Initialize session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = None
if 'running' not in st.session_state:
    st.session_state.running = False
if 'population_history' not in st.session_state:
    st.session_state.population_history = []
if 'step_count' not in st.session_state:
    st.session_state.step_count = 0

# Sidebar controls
st.sidebar.header("🎛️ Simulation Controls")

# Functional response type selector
response_type = st.sidebar.selectbox(
    "Select Functional Response Type",
    options=[
        FunctionalResponseType.TYPE_I,
        FunctionalResponseType.TYPE_II,
        FunctionalResponseType.TYPE_III,
        FunctionalResponseType.TYPE_IV
    ],
    format_func=lambda x: x.value,
    index=1  # Default to Type II
)

st.sidebar.markdown("---")

# Population settings
st.sidebar.subheader("Population Settings")
num_predators = st.sidebar.slider("Number of Predators", 5, 30, 15, 2)
num_prey = st.sidebar.slider("Number of Prey", 30, 100, 60, 5)

st.sidebar.markdown("---")

# Simulation speed
simulation_speed = st.sidebar.slider("Simulation Speed", 0.01, 0.2, 0.05, 0.01)

# Display information about selected type
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ About Selected Type")

if response_type == FunctionalResponseType.TYPE_I:
    st.sidebar.markdown("""
    **Type I - Linear Response**
    - Linear increase in attack success
    - Reaches satiation threshold
    - Example: Filter feeders
    - Constant hunting efficiency until full
    """)
elif response_type == FunctionalResponseType.TYPE_II:
    st.sidebar.markdown("""
    **Type II - Hyperbolic Response**
    - Most common in nature
    - Limited by handling time
    - Can't attack while digesting
    - Example: Wolves, hawks, spiders
    """)
elif response_type == FunctionalResponseType.TYPE_III:
    st.sidebar.markdown("""
    **Type III - Sigmoidal Response**
    - Poor at low prey densities
    - Learning/switching behavior
    - Creates prey refuges
    - Example: Specialized predators
    """)
elif response_type == FunctionalResponseType.TYPE_IV:
    st.sidebar.markdown("""
    **Type IV - Dome-shaped Response**
    - Peaks at optimal prey density
    - Interference at high densities
    - Example: Dangerous prey interactions
    - Efficiency drops when crowded
    """)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Simulation display
    st.subheader(f"🎬 Live Simulation - {response_type.value}")
    simulation_placeholder = st.empty()
    
    # Control buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        start_btn = st.button("🚀 Start Simulation", key="start")
    with col_btn2:
        pause_btn = st.button("⏸️ Pause", key="pause")
    with col_btn3:
        reset_btn = st.button("🔄 Reset", key="reset")

with col2:
    # Population statistics
    st.subheader("📊 Population Stats")
    stats_placeholder = st.empty()
    
    # Current simulation info
    st.subheader("⚙️ Current Settings")
    info_placeholder = st.empty()

# Population chart (full width)
st.subheader("📈 Population Dynamics Over Time")
population_chart_placeholder = st.empty()

def create_population_chart(history):
    """Create population dynamics chart"""
    if not history:
        return go.Figure()
    
    df = pd.DataFrame(history)
    fig = go.Figure()
    
    if 'predators' in df.columns:
        fig.add_trace(go.Scatter(
            x=list(range(len(df))),
            y=df['predators'],
            name='🔴 Predators',
            line=dict(color='red', width=3),
            mode='lines'
        ))
    
    if 'prey' in df.columns:
        fig.add_trace(go.Scatter(
            x=list(range(len(df))),
            y=df['prey'],
            name='🔵 Prey',
            line=dict(color='blue', width=3),
            mode='lines'
        ))
    
    fig.update_layout(
        title=f"Population Dynamics - {response_type.value}",
        xaxis_title="Time Steps",
        yaxis_title="Population Count",
        height=300,
        showlegend=True
    )
    
    return fig

def display_stats(stats):
    """Display current population statistics"""
    with stats_placeholder.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔴 Predators", stats['predators'])
        with col2:
            st.metric("🔵 Prey", stats['prey'])
        with col3:
            ratio = stats['prey'] / max(stats['predators'], 1)
            st.metric("Prey:Predator Ratio", f"{ratio:.1f}:1")

def display_simulation_info():
    """Display current simulation information"""
    with info_placeholder.container():
        st.write(f"**Response Type:** {response_type.value}")
        st.write(f"**Initial Predators:** {num_predators}")
        st.write(f"**Initial Prey:** {num_prey}")
        st.write(f"**Steps Run:** {st.session_state.step_count}")

# Handle button clicks
if start_btn:
    # Initialize new simulation
    st.session_state.simulation = TruePredatorPreySimulation(
        width=600, height=400, response_type=response_type
    )
    st.session_state.simulation.initialize_population(num_predators, num_prey)
    st.session_state.population_history = []
    st.session_state.step_count = 0
    st.session_state.running = True

if pause_btn:
    st.session_state.running = False

if reset_btn:
    st.session_state.simulation = None
    st.session_state.running = False
    st.session_state.population_history = []
    st.session_state.step_count = 0
    simulation_placeholder.empty()
    population_chart_placeholder.empty()
    stats_placeholder.empty()

# Display current info
display_simulation_info()

# Run simulation loop
if st.session_state.running and st.session_state.simulation:
    progress_bar = st.progress(0)
    max_steps = 500
    
    for step in range(max_steps):
        if not st.session_state.running:
            break
        
        # Run simulation step
        img = st.session_state.simulation.run_step()
        simulation_placeholder.image(img, channels="RGB", use_column_width=True)
        
        # Get and display statistics
        stats = st.session_state.simulation.get_population_stats()
        display_stats(stats)
        
        # Record population history every 5 steps
        if st.session_state.step_count % 5 == 0:
            st.session_state.population_history.append(stats)
            
            # Update population chart
            if len(st.session_state.population_history) > 1:
                pop_chart = create_population_chart(st.session_state.population_history)
                population_chart_placeholder.plotly_chart(pop_chart, use_container_width=True)
        
        # Update progress
        progress = (step + 1) / max_steps
        progress_bar.progress(progress)
        
        st.session_state.step_count += 1
        
        # Check for extinction
        if stats['total'] == 0:
            st.error("🚨 All populations extinct! Click Reset to try again.")
            st.session_state.running = False
            break
        
        if stats['predators'] == 0:
            st.success("🎉 Prey survived! All predators are extinct.")
            st.session_state.running = False
            break
            
        if stats['prey'] == 0:
            st.warning("⚰️ All prey consumed! Predators will starve soon.")
        
        # Control simulation speed
        time.sleep(simulation_speed)
    
    progress_bar.empty()
    
    if st.session_state.running:
        st.info("🏁 Simulation completed. Click Reset to run again.")
        st.session_state.running = False

# Information panel at bottom
st.markdown("---")
st.subheader("🔬 Understanding the Differences")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🔴 Type I (Linear)**
    - Steady hunting rate
    - Clear satiation point
    - Predictable predation pressure
    
    **🟢 Type II (Hyperbolic)**
    - Most realistic
    - Handling time creates delays
    - Natural predator-prey cycles
    """)

with col2:
    st.markdown("""
    **🔵 Type III (Sigmoidal)**
    - Prey refuges at low density
    - Can create boom-bust cycles
    - Switching behavior effects
    
    **🟡 Type IV (Dome-shaped)**
    - Interference competition
    - Crowding reduces efficiency
    - Complex dynamics possible
    """)

st.markdown("""
**🎮 Experiment Tips:**
- Try different starting populations to see how they affect dynamics
- Notice how predator behavior changes with prey density
- Observe the different population cycle patterns
- Compare extinction risks between response types
""")