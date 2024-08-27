import streamlit as st
from simulation import run_simulation
from ui import sidebar_controls, main_controls

# Streamlit UI setup
st.title("Modularized Particle Simulation App")

# Sidebar for controls
num_particles, num_types, dt, r, friction_factor, beta = sidebar_controls()

# Main area controls
run_simulation_btn, quit_simulation_btn = main_controls()

# Session state initialization
if 'run_simulation' not in st.session_state:
    st.session_state['run_simulation'] = False
if 'stop_simulation' not in st.session_state:
    st.session_state['stop_simulation'] = False

# Image placeholder
image_placeholder = st.empty()

if run_simulation_btn:
    st.session_state['run_simulation'] = True
    st.session_state['stop_simulation'] = False
    run_simulation(num_particles, num_types, dt, r, friction_factor, beta, image_placeholder)

if quit_simulation_btn:
    st.session_state['run_simulation'] = False
    st.session_state['stop_simulation'] = True
    cv2.destroyAllWindows()
