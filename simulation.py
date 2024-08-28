import cv2
import numpy as np
import math
import random
import streamlit as st

def calc_forces(dist, force, beta):
    '''
    The calculation of force is determined by the beta value which helps determine how forces are applied to the particles. 
    As two particles are within the beta distance then a negative force is applied on each other. This means that they are 
    attracted rather than repulsed. If two particles are a larger distance away from each other than beta but still less that 1 unit distance, then they 
    repulse each other as the force value is positive. 
    
    Parameters:
    ------------
    dist: distance between two particles.
    force: set force value applied on particles within range.
    beta: Threshold distance deciding attractive and repulsive forces between particles.
    '''
    if dist < beta:
        return dist / beta - 1 ## creates an attraction force because it ends up being negative and so is not pushing particles away from each other
    elif beta < dist < 1:
        return force * (1 - abs(2 * dist - 1 - beta) / (1 - beta)) ## the max force is 1 if the absolute function is 0.
    else:
        return 0
    


def run_simulation(num_particles, num_types, dt, r, friction_factor, beta, image_placeholder):
    """
    Runs a particle simulation with specified parameters and visualizes it using Streamlit.

    The simulation involves particles of different types moving within a bounded window,
    influenced by forces based on their distances and interactions with other particles.
    The particles are rendered in real-time and displayed through an image placeholder.

    Parameters:
    ----------
    num_particles : int
        The number of particles to simulate.
    num_types : int
        The number of different types of particles.
    dt : float
        The time step for the simulation.
    r : float
        The maximum interaction distance between particles.
    friction_factor : float
        The friction factor applied to particle velocities, reducing their speed over time.
    beta : float
        A parameter that controls the force calculation between particles.
    image_placeholder : Streamlit object
        A Streamlit placeholder object used to display the simulation frames.

    Returns:
    -------
    None

    The function continuously updates the simulation until a stop condition is met, at which point
    it stops and closes the OpenCV windows.
    """
    # Simulation setup
    X = 1600 // 2 
    Y = 2560 // 2
    window = np.zeros((X, Y, 3), dtype=np.uint8)
    colour_dict = {0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255), 3: (155, 0, 155), 4: (0, 155, 155)}

    particle_types = [random.randint(0, num_types - 1) for _ in range(num_particles)]
    particle_pos_x = [random.randint(5, X - 5) for _ in range(num_particles)] ## within the borders of the window
    particle_pos_y = [random.randint(5, Y - 5) for _ in range(num_particles)] ## within the borders of the window
    p_v_x = [(random.random() * 2) * 2 for _ in range(num_particles)] ## initial velocity is random between 0 and 20 and then multiplied by 2.
    p_v_y = [(random.random() * 2) * 2 for _ in range(num_particles)] ## initial velocity is random between 0 and 20 and then multiplied by 2.
    forces = [[(random.random() - 0.5) * 2 for _ in range(num_types)] for _ in range(num_types)] ## creates a 5 by 5 force matrix between particle types.

    while True:
        window[:, :, :] = 0  # Clear the window so that we don't get particle trails.

        for i in range(num_particles):
            tot_force_x = 0
            tot_force_y = 0
            for j in range(num_particles):
                if i != j: ## if it is not the same particle
                    dx = particle_pos_x[j] - particle_pos_x[i]
                    dy = particle_pos_y[j] - particle_pos_y[i]
                    if abs(dx) > X / 2:
                        dx = (abs(dx) - X) * (dx / abs(dx)) ## adjusts the distance to be accross boundary distance rather than within boundary distance.
                    if abs(dy) > Y / 2:
                        dy = (abs(dy) - Y) * (dy / abs(dy)) ## adjusts the distance to be accross boundary distance rather than straight distance.
                    dist = math.sqrt(dx ** 2 + dy ** 2) ## we have x and y distance of right angle triangle but need hypotenuse for straight distance.
                    if 0 < dist < r:
                        force = calc_forces(dist / r, forces[particle_types[i]][particle_types[j]], beta)
                        tot_force_x += dx / dist * force
                        tot_force_y += dy / dist * force

            tot_force_x *= r * 100
            tot_force_y *= r * 100
            p_v_x[i] *= friction_factor
            p_v_y[i] *= friction_factor
            p_v_x[i] += tot_force_x * dt
            p_v_y[i] += tot_force_y * dt

        for idx in range(num_particles):
            cv2.circle(window, (int(particle_pos_y[idx]), int(particle_pos_x[idx])), 3, colour_dict[particle_types[idx]], -1)
            particle_pos_x[idx] = (particle_pos_x[idx] + p_v_x[idx] * dt) % X
            particle_pos_y[idx] = (particle_pos_y[idx] + p_v_y[idx] * dt) % Y

        # Convert BGR to RGB for Streamlit
        img_rgb = cv2.cvtColor(window, cv2.COLOR_BGR2RGB)
        # Display the image in Streamlit
        image_placeholder.image(img_rgb, channels="RGB")

        # Check if the simulation should stop
        if st.session_state['stop_simulation']:
            break

    cv2.destroyAllWindows()
