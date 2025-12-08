import streamlit as st
import time
##from predator_prey_simulation import PredatorPreySimulation
from optimized_simulation import OptimizedPredatorPreySimulation as PredatorPreySimulation
from predator_prey_ui import (
    sidebar_controls, 
    create_functional_response_plot, 
    create_population_chart,
    display_particle_info,
    main_controls,
    simulation_stats_display
)

# Configure Streamlit page
st.set_page_config(
    page_title="Predator-Prey Functional Responses",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🦁 Predator-Prey Functional Response Simulation")
st.markdown("""
This simulation demonstrates the four types of functional responses in predator-prey interactions:
**Type I (Linear)**, **Type II (Hyperbolic)**, **Type III (Sigmoidal)**, and **Type IV (Dome-shaped)**.
Each colored particle represents a different functional response type.
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
(particles_per_type, dt, friction, interaction_radius, 
 energy_decay, reproduction_threshold, energy_gain) = sidebar_controls()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Simulation display area
    st.subheader("🎬 Live Simulation")
    simulation_placeholder = st.empty()
    
    # Control buttons
    run_btn, pause_btn, reset_btn = main_controls()
    
    # Statistics display
    stats_placeholder = st.empty()

with col2:
    # Information panel
    display_particle_info()
    
    # Functional response curves
    st.subheader("📊 Functional Response Curves")
    response_plot = create_functional_response_plot()
    st.plotly_chart(response_plot, use_container_width=True)

# Population dynamics chart (full width)
st.subheader("📈 Population Dynamics")
population_chart_placeholder = st.empty()

# Handle button clicks
if run_btn or st.session_state.running:
    if st.session_state.simulation is None or run_btn:
        # Initialize new simulation
        st.session_state.simulation = PredatorPreySimulation(width=800, height=600)
        st.session_state.simulation.dt = dt
        st.session_state.simulation.friction = friction
        st.session_state.simulation.interaction_radius = interaction_radius
        st.session_state.simulation.energy_decay_rate = energy_decay
        st.session_state.simulation.reproduction_threshold = reproduction_threshold
        st.session_state.simulation.energy_gain_from_prey = energy_gain
        
        st.session_state.simulation.initialize_particles(particles_per_type)
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

# Run simulation loop
if st.session_state.running and st.session_state.simulation:
    # Create placeholders for dynamic updates
    progress_bar = st.progress(0)
    
    # Run simulation steps
    max_steps = 1000  # Prevent infinite running
    
    for step in range(max_steps):
        if not st.session_state.running:
            break
            
        # Run one simulation step
        img = st.session_state.simulation.run_step()
        
        # Update display
        simulation_placeholder.image(img, channels="RGB", use_column_width=True)
        
        # Get population statistics
        stats = st.session_state.simulation.get_population_stats()
        total_pop = sum(stats.values())
        
        # Update statistics display
        with stats_placeholder.container():
            simulation_stats_display(stats, total_pop)
        
        # Record population history
        if st.session_state.step_count % 5 == 0:  # Record every 5 steps
            st.session_state.population_history.append(stats)
            
            # Update population chart
            if len(st.session_state.population_history) > 1:
                pop_chart = create_population_chart(st.session_state.population_history)
                population_chart_placeholder.plotly_chart(pop_chart, use_container_width=True)
        
        # Update progress
        progress = (step + 1) / max_steps
        progress_bar.progress(progress)
        
        st.session_state.step_count += 1
        
        # Add small delay to control simulation speed
        time.sleep(0.05)
        
        # Check if population is extinct
        if total_pop == 0:
            st.error("🚨 All populations have gone extinct! Click Reset to start over.")
            st.session_state.running = False
            break
    
    # Clean up progress bar
    progress_bar.empty()
    
    if st.session_state.running:
        st.info("🏁 Simulation completed 1000 steps. Click Reset to run again.")
        st.session_state.running = False

# Display final statistics if simulation exists
if st.session_state.simulation and not st.session_state.running:
    st.subheader("📊 Final Statistics")
    final_stats = st.session_state.simulation.get_population_stats()
    total_final = sum(final_stats.values())
    
    if total_final > 0:
        col1, col2, col3, col4 = st.columns(4)
        colors = ['🔴', '🟢', '🔵', '🟡']
        names = ['Type I', 'Type II', 'Type III', 'Type IV']
        
        for i, (col, color, name) in enumerate(zip([col1, col2, col3, col4], colors, names)):
            with col:
                count = final_stats.get(i, 0)
                percentage = (count / total_final) * 100
                st.metric(f"{color} {name}", f"{count} ({percentage:.1f}%)")

# Information sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ About This Simulation")
st.sidebar.markdown("""
This simulation models predator-prey interactions using four different functional response types:

- **Type I**: Linear response (red particles)
- **Type II**: Hyperbolic response (green particles)  
- **Type III**: Sigmoidal response (blue particles)
- **Type IV**: Dome-shaped response (yellow particles)

Each particle type hunts others according to its functional response, competing for resources and reproducing based on energy levels.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**🎮 Controls:**")
st.sidebar.markdown("- **Start**: Begin/restart simulation")
st.sidebar.markdown("- **Pause**: Pause current simulation") 
st.sidebar.markdown("- **Reset**: Clear and reset everything")