import cv2
import numpy as np
import math
import random
import streamlit as st
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum
from collections import deque

class FunctionalResponseType(Enum):
    TYPE_I = "Type I - Linear"
    TYPE_II = "Type II - Hyperbolic" 
    TYPE_III = "Type III - Sigmoidal"
    TYPE_IV = "Type IV - Dome-shaped"

@dataclass
class Particle:
    """Optimized particle with pre-calculated fields"""
    x: float
    y: float
    vx: float
    vy: float
    particle_type: int
    energy: float = 100.0
    age: int = 0
    reproduction_cooldown: int = 0
    grid_x: int = 0  # For spatial partitioning
    grid_y: int = 0

class OptimizedPredatorPreySimulation:
    def __init__(self, width=1280, height=800):
        self.width = width
        self.height = height
        self.particles = deque()  # Faster add/remove operations
        self.window = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Spatial partitioning grid
        self.grid_size = 80  # Grid cell size
        self.grid_cols = width // self.grid_size + 1
        self.grid_rows = height // self.grid_size + 1
        self.spatial_grid = {}
        
        # Color mapping
        self.colors = {
            0: (255, 100, 100),  # Red
            1: (100, 255, 100),  # Green
            2: (100, 100, 255),  # Blue
            3: (255, 255, 100)   # Yellow
        }
        
        # Pre-calculated functional response parameters
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
        
        # Performance optimization
        self.frame_count = 0
        self.update_frequency = 3  # Update expensive calculations every N frames

    def update_spatial_grid(self):
        """Update spatial partitioning grid - O(n) operation"""
        self.spatial_grid.clear()
        
        for particle in self.particles:
            # Calculate grid position
            grid_x = int(particle.x // self.grid_size)
            grid_y = int(particle.y // self.grid_size)
            particle.grid_x = grid_x
            particle.grid_y = grid_y
            
            # Add to grid
            key = (grid_x, grid_y)
            if key not in self.spatial_grid:
                self.spatial_grid[key] = []
            self.spatial_grid[key].append(particle)

    def get_nearby_particles(self, particle, radius=None):
        """Get particles in nearby grid cells - much faster than O(n²)"""
        if radius is None:
            radius = self.interaction_radius
            
        nearby = []
        grid_radius = int(radius // self.grid_size) + 1
        
        for dx in range(-grid_radius, grid_radius + 1):
            for dy in range(-grid_radius, grid_radius + 1):
                grid_x = particle.grid_x + dx
                grid_y = particle.grid_y + dy
                key = (grid_x, grid_y)
                
                if key in self.spatial_grid:
                    nearby.extend(self.spatial_grid[key])
        
        return nearby

    def calculate_functional_response_vectorized(self, predator_type: int, prey_densities):
        """Vectorized functional response calculation"""
        params = self.response_params[predator_type]
        response_type = params['type']
        
        if response_type == FunctionalResponseType.TYPE_I:
            max_rate = params['max_rate']
            threshold = params['threshold']
            return np.minimum(max_rate, (prey_densities / threshold) * max_rate)
            
        elif response_type == FunctionalResponseType.TYPE_II:
            max_rate = params['max_rate']
            handling_time = params['handling_time']
            return (max_rate * prey_densities) / (handling_time + prey_densities)
            
        elif response_type == FunctionalResponseType.TYPE_III:
            max_rate = params['max_rate']
            inflection = params['inflection']
            steepness = params['steepness']
            return max_rate / (1 + np.exp(-steepness * (prey_densities - inflection)))
            
        elif response_type == FunctionalResponseType.TYPE_IV:
            max_rate = params['max_rate']
            optimal_density = params['optimal_density']
            decline_rate = params['decline_rate']
            
            result = np.zeros_like(prey_densities)
            low_mask = prey_densities <= optimal_density
            high_mask = ~low_mask
            
            result[low_mask] = (prey_densities[low_mask] / optimal_density) * max_rate
            
            excess = prey_densities[high_mask] - optimal_density
            decline_factor = np.exp(-decline_rate * excess)
            result[high_mask] = max_rate * decline_factor
            
            return result
        
        return np.zeros_like(prey_densities)

    def calculate_local_prey_density_fast(self, predator: Particle) -> float:
        """Fast prey density calculation using spatial grid"""
        nearby_particles = self.get_nearby_particles(predator)
        
        prey_count = 0
        for particle in nearby_particles:
            if particle.particle_type != predator.particle_type and particle != predator:
                dx = particle.x - predator.x
                dy = particle.y - predator.y
                
                # Handle boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist_squared = dx*dx + dy*dy  # Avoid sqrt when possible
                if dist_squared < self.interaction_radius**2:
                    prey_count += 1
                    
        return prey_count

    def update_particles_optimized(self):
        """Optimized particle update with reduced calculations"""
        particles_to_remove = []
        particles_to_add = []
        
        # Update spatial grid
        self.update_spatial_grid()
        
        for particle in self.particles:
            # Age and energy decay
            particle.age += 1
            particle.energy -= self.energy_decay_rate
            particle.reproduction_cooldown = max(0, particle.reproduction_cooldown - 1)
            
            # Mark for removal if dead
            if particle.energy <= 0 or particle.age > 2000:
                particles_to_remove.append(particle)
                continue
            
            # Only do expensive calculations every few frames
            if self.frame_count % self.update_frequency == 0:
                # Calculate local prey density and hunting behavior
                prey_density = self.calculate_local_prey_density_fast(particle)
                self.move_towards_prey_fast(particle, prey_density)
                
                # Attempt consumption
                consumed = self.attempt_consumption_fast(particle)
                
                # Attempt reproduction
                offspring = self.reproduce_particle_fast(particle)
                if offspring:
                    particles_to_add.append(offspring)
            
            # Apply friction and update position (always)
            particle.vx *= self.friction
            particle.vy *= self.friction
            particle.x = (particle.x + particle.vx * self.dt) % self.width
            particle.y = (particle.y + particle.vy * self.dt) % self.height
        
        # Batch remove/add operations
        for particle in particles_to_remove:
            self.particles.remove(particle)
        
        for particle in particles_to_add:
            self.particles.append(particle)

    def move_towards_prey_fast(self, predator: Particle, prey_density: float):
        """Optimized movement calculation"""
        # Pre-calculate response rate
        consumption_rate = self.calculate_functional_response_vectorized(
            predator.particle_type, np.array([prey_density]))[0]
        
        if consumption_rate < 0.1:
            return
        
        # Find nearest prey using spatial grid
        nearby_particles = self.get_nearby_particles(predator)
        nearest_prey = None
        min_dist_squared = float('inf')
        
        for particle in nearby_particles:
            if particle.particle_type != predator.particle_type and particle != predator:
                dx = particle.x - predator.x
                dy = particle.y - predator.y
                
                # Handle boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist_squared = dx*dx + dy*dy
                if dist_squared < min_dist_squared and dist_squared < self.interaction_radius**2:
                    min_dist_squared = dist_squared
                    nearest_prey = particle
        
        if nearest_prey:
            dx = nearest_prey.x - predator.x
            dy = nearest_prey.y - predator.y
            
            # Handle boundaries
            if abs(dx) > self.width / 2:
                dx = (abs(dx) - self.width) * (dx / abs(dx))
            if abs(dy) > self.height / 2:
                dy = (abs(dy) - self.height) * (dy / abs(dy))
            
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                force_magnitude = consumption_rate * 100
                predator.vx += (dx / dist) * force_magnitude * self.dt
                predator.vy += (dy / dist) * force_magnitude * self.dt

    def attempt_consumption_fast(self, predator: Particle) -> bool:
        """Fast consumption attempt using spatial grid"""
        nearby_particles = self.get_nearby_particles(predator, self.consumption_radius)
        
        for prey in nearby_particles:
            if prey.particle_type != predator.particle_type and prey != predator:
                dx = prey.x - predator.x
                dy = prey.y - predator.y
                
                # Handle boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist_squared = dx*dx + dy*dy
                if dist_squared < self.consumption_radius**2:
                    # Quick consumption check
                    if random.random() < 0.05:  # 5% chance
                        predator.energy += self.energy_gain_from_prey
                        self.particles.remove(prey)
                        return True
        return False

    def reproduce_particle_fast(self, parent: Particle):
        """Fast reproduction with limits"""
        if (parent.energy > self.reproduction_threshold and 
            parent.reproduction_cooldown <= 0 and
            len(self.particles) < 400):  # Lower population cap for performance
            
            offspring = Particle(
                x=(parent.x + random.uniform(-20, 20)) % self.width,
                y=(parent.y + random.uniform(-20, 20)) % self.height,
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1, 1),
                particle_type=parent.particle_type,
                energy=self.min_reproduction_energy
            )
            
            parent.energy -= self.min_reproduction_energy
            parent.reproduction_cooldown = 100
            
            return offspring
        return None

    def initialize_particles(self, particles_per_type=40):  # Reduced default
        """Initialize with fewer particles for better performance"""
        self.particles.clear()
        
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

    def draw_particles_fast(self):
        """Optimized drawing with numpy operations"""
        self.window[:, :, :] = 0  # Clear window
        
        # Batch drawing operations
        for particle in self.particles:
            size = max(2, min(8, int(particle.energy / 25)))  # Cap size
            color = self.colors[particle.particle_type]
            
            cv2.circle(self.window, 
                      (int(particle.x), int(particle.y)), 
                      size, color, -1)

    def get_population_stats(self) -> dict:
        """Fast population counting"""
        stats = {i: 0 for i in range(4)}
        for particle in self.particles:
            stats[particle.particle_type] += 1
        return stats

    def run_step(self):
        """Optimized simulation step"""
        self.frame_count += 1
        self.update_particles_optimized()
        self.draw_particles_fast()
        return cv2.cvtColor(self.window, cv2.COLOR_BGR2RGB)