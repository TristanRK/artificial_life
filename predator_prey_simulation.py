import cv2
import numpy as np
import math
import random
import streamlit as st
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum

class FunctionalResponseType(Enum):
    TYPE_I = "Type I - Linear"
    TYPE_II = "Type II - Hyperbolic" 
    TYPE_III = "Type III - Sigmoidal"
    TYPE_IV = "Type IV - Dome-shaped"

@dataclass
class Particle:
    """Represents a particle in the predator-prey simulation"""
    x: float
    y: float
    vx: float
    vy: float
    particle_type: int
    energy: float = 100.0
    age: int = 0
    reproduction_cooldown: int = 0

class PredatorPreySimulation:
    def __init__(self, width=1280, height=800):
        self.width = width
        self.height = height
        self.particles = []
        self.window = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Color mapping for 4 particle types
        self.colors = {
            0: (255, 100, 100),  # Red - Type I predator
            1: (100, 255, 100),  # Green - Type II predator  
            2: (100, 100, 255),  # Blue - Type III predator
            3: (255, 255, 100)   # Yellow - Type IV predator/dangerous prey
        }
        
        # Functional response parameters
        self.response_params = {
            0: {'type': FunctionalResponseType.TYPE_I, 'max_rate': 0.8, 'threshold': 50},
            1: {'type': FunctionalResponseType.TYPE_II, 'max_rate': 1.0, 'handling_time': 20},
            2: {'type': FunctionalResponseType.TYPE_III, 'max_rate': 1.2, 'inflection': 30, 'steepness': 0.1},
            3: {'type': FunctionalResponseType.TYPE_IV, 'max_rate': 0.9, 'optimal_density': 40, 'decline_rate': 0.02}
        }
        
        # Simulation parameters
        self.dt = 0.02
        self.friction = 0.95
        self.interaction_radius = 60
        self.consumption_radius = 15
        self.reproduction_threshold = 150
        self.min_reproduction_energy = 80
        self.energy_decay_rate = 0.5
        self.energy_gain_from_prey = 50

    def calculate_functional_response(self, predator_type: int, prey_density: float) -> float:
        """Calculate consumption rate based on functional response type"""
        params = self.response_params[predator_type]
        response_type = params['type']
        
        if response_type == FunctionalResponseType.TYPE_I:
            # Linear increase until satiation threshold
            max_rate = params['max_rate']
            threshold = params['threshold']
            return min(max_rate, (prey_density / threshold) * max_rate)
            
        elif response_type == FunctionalResponseType.TYPE_II:
            # Hyperbolic response with handling time
            max_rate = params['max_rate']
            handling_time = params['handling_time']
            return (max_rate * prey_density) / (handling_time + prey_density)
            
        elif response_type == FunctionalResponseType.TYPE_III:
            # Sigmoidal response
            max_rate = params['max_rate']
            inflection = params['inflection']
            steepness = params['steepness']
            return max_rate / (1 + math.exp(-steepness * (prey_density - inflection)))
            
        elif response_type == FunctionalResponseType.TYPE_IV:
            # Dome-shaped response
            max_rate = params['max_rate']
            optimal_density = params['optimal_density']
            decline_rate = params['decline_rate']
            
            if prey_density <= optimal_density:
                # Increasing phase
                return (prey_density / optimal_density) * max_rate
            else:
                # Declining phase due to danger/interference
                excess = prey_density - optimal_density
                decline_factor = math.exp(-decline_rate * excess)
                return max_rate * decline_factor
        
        return 0.0

    def calculate_local_prey_density(self, predator: Particle) -> float:
        """Calculate local prey density around a predator"""
        prey_count = 0
        for particle in self.particles:
            if particle.particle_type != predator.particle_type:  # Different type = potential prey
                dx = particle.x - predator.x
                dy = particle.y - predator.y
                
                # Handle toroidal boundary conditions
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist = math.sqrt(dx**2 + dy**2)
                if dist < self.interaction_radius:
                    prey_count += 1
                    
        return prey_count

    def move_towards_prey(self, predator: Particle, prey_density: float):
        """Move predator towards nearby prey based on functional response"""
        consumption_rate = self.calculate_functional_response(predator.particle_type, prey_density)
        
        # Find nearest prey
        nearest_prey = None
        min_distance = float('inf')
        
        for particle in self.particles:
            if particle.particle_type != predator.particle_type:
                dx = particle.x - predator.x
                dy = particle.y - predator.y
                
                # Handle boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist = math.sqrt(dx**2 + dy**2)
                if dist < min_distance and dist < self.interaction_radius:
                    min_distance = dist
                    nearest_prey = particle
        
        if nearest_prey and consumption_rate > 0.1:
            # Calculate direction to prey
            dx = nearest_prey.x - predator.x
            dy = nearest_prey.y - predator.y
            
            # Handle boundaries
            if abs(dx) > self.width / 2:
                dx = (abs(dx) - self.width) * (dx / abs(dx))
            if abs(dy) > self.height / 2:
                dy = (abs(dy) - self.height) * (dy / abs(dy))
            
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                # Apply force towards prey, scaled by consumption rate
                force_magnitude = consumption_rate * 100
                predator.vx += (dx / dist) * force_magnitude * self.dt
                predator.vy += (dy / dist) * force_magnitude * self.dt

    def attempt_consumption(self, predator: Particle) -> bool:
        """Attempt to consume nearby prey"""
        prey_density = self.calculate_local_prey_density(predator)
        consumption_rate = self.calculate_functional_response(predator.particle_type, prey_density)
        
        # Find prey within consumption radius
        for i, prey in enumerate(self.particles):
            if prey.particle_type != predator.particle_type:
                dx = prey.x - predator.x
                dy = prey.y - predator.y
                
                # Handle boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist = math.sqrt(dx**2 + dy**2)
                if dist < self.consumption_radius:
                    # Probability of successful consumption based on functional response
                    if random.random() < consumption_rate * 0.01:  # Scale down probability
                        predator.energy += self.energy_gain_from_prey
                        self.particles.remove(prey)
                        return True
        return False

    def reproduce_particle(self, parent: Particle):
        """Create offspring near parent particle"""
        if (parent.energy > self.reproduction_threshold and 
            parent.reproduction_cooldown <= 0 and
            len(self.particles) < 500):  # Population cap
            
            # Create offspring
            offspring = Particle(
                x=parent.x + random.uniform(-20, 20),
                y=parent.y + random.uniform(-20, 20),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1, 1),
                particle_type=parent.particle_type,
                energy=self.min_reproduction_energy
            )
            
            # Ensure offspring stays in bounds
            offspring.x = offspring.x % self.width
            offspring.y = offspring.y % self.height
            
            # Cost of reproduction
            parent.energy -= self.min_reproduction_energy
            parent.reproduction_cooldown = 100
            
            self.particles.append(offspring)

    def update_particles(self):
        """Update all particles in the simulation"""
        for particle in self.particles[:]:  # Use slice to avoid modification during iteration
            # Age and energy decay
            particle.age += 1
            particle.energy -= self.energy_decay_rate
            particle.reproduction_cooldown = max(0, particle.reproduction_cooldown - 1)
            
            # Remove particles that die of old age or starvation
            if particle.energy <= 0 or particle.age > 2000:
                if particle in self.particles:
                    self.particles.remove(particle)
                continue
            
            # Calculate local prey density and move towards prey
            prey_density = self.calculate_local_prey_density(particle)
            self.move_towards_prey(particle, prey_density)
            
            # Attempt consumption
            self.attempt_consumption(particle)
            
            # Attempt reproduction
            self.reproduce_particle(particle)
            
            # Apply friction
            particle.vx *= self.friction
            particle.vy *= self.friction
            
            # Update position
            particle.x = (particle.x + particle.vx * self.dt) % self.width
            particle.y = (particle.y + particle.vy * self.dt) % self.height

    def initialize_particles(self, particles_per_type=50):
        """Initialize particles of each type"""
        self.particles = []
        
        for particle_type in range(4):
            for _ in range(particles_per_type):
                particle = Particle(
                    x=random.uniform(0, self.width),
                    y=random.uniform(0, self.height),
                    vx=random.uniform(-2, 2),
                    vy=random.uniform(-2, 2),
                    particle_type=particle_type,
                    energy=random.uniform(80, 120)
                )
                self.particles.append(particle)

    def draw_particles(self):
        """Draw all particles on the window"""
        self.window[:, :, :] = 0  # Clear window
        
        for particle in self.particles:
            # Draw particle with size based on energy
            size = max(2, int(particle.energy / 25))
            color = self.colors[particle.particle_type]
            
            cv2.circle(self.window, 
                      (int(particle.x), int(particle.y)), 
                      size, color, -1)

    def get_population_stats(self) -> dict:
        """Get current population statistics"""
        stats = {i: 0 for i in range(4)}
        for particle in self.particles:
            stats[particle.particle_type] += 1
        return stats

    def run_step(self):
        """Run one simulation step"""
        self.update_particles()
        self.draw_particles()
        return cv2.cvtColor(self.window, cv2.COLOR_BGR2RGB)