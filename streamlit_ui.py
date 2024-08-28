import streamlit as st

def sidebar_controls():
    st.sidebar.header("Simulation Controls")
    num_particles = st.sidebar.number_input("Number of Particles", min_value=10, max_value=500, value=200, step=10)
    num_types = st.sidebar.number_input("Number of Particle Types", min_value=1, max_value=10, value=5, step=1)
    dt = st.sidebar.slider("Time Step (dt)", min_value=0.01, max_value=0.1, value=0.02, step=0.01)
    r = st.sidebar.slider("Interaction Radius (r)", min_value=10, max_value=200, value=80, step=10)
    friction_factor = st.sidebar.slider("Friction Factor", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
    beta = st.sidebar.slider("Beta (Force Calculation)", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
    return num_particles, num_types, dt, r, friction_factor, beta

def main_controls():
    run_simulation = st.button("Run Simulation", key="run_simulation_btn")
    stop_simulation = st.button("Quit Simulation", key="quit_simulation_btn")
    return run_simulation, stop_simulation
