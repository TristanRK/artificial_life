import cv2
import numpy as np
import math
import random
import streamlit as st

def calc_forces(dist, force, beta):
    if dist < beta:
        return dist / beta - 1
    elif beta < dist < 1:
        return force * (1 - abs(2 * dist - 1 - beta) / (1 - beta))
    else:
        return 0

def run_simulation(num_particles, num_types, dt, r, friction_factor, beta, image_placeholder):
    # Simulation setup
    X = 1600 // 2
    Y = 2560 // 2
    window = np.zeros((X, Y, 3), dtype=np.uint8)
    colour_dict = {0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255), 3: (155, 0, 155), 4: (0, 155, 155)}

    particle_types = [random.randint(0, num_types - 1) for _ in range(num_particles)]
    particle_pos_x = [random.randint(5, X - 5) for _ in range(num_particles)]
    particle_pos_y = [random.randint(5, Y - 5) for _ in range(num_particles)]
    p_v_x = [(random.random() + 100) * 2 for _ in range(num_particles)]
    p_v_y = [(random.random() + 100) * 2 for _ in range(num_particles)]
    forces = [[(random.random() + 5) * 2 for _ in range(num_types)] for _ in range(num_types)]

    while True:
        window[:, :, :] = 0  # Clear the window

        for i in range(num_particles):
            tot_force_x = 0
            tot_force_y = 0
            for j in range(num_particles):
                if i != j:
                    dx = particle_pos_x[j] - particle_pos_x[i]
                    dy = particle_pos_y[j] - particle_pos_y[i]
                    if abs(dx) > X / 2:
                        dx = (abs(dx) - X) * (dx / abs(dx))
                    if abs(dy) > Y / 2:
                        dy = (abs(dy) - Y) * (dy / abs(dy))
                    dist = math.sqrt(dx ** 2 + dy ** 2)
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
