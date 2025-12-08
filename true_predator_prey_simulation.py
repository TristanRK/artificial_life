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
class Animal:
    """Represents an animal in the predator-prey simulation"""
    x: float
    y: float
    vx: float
    vy: float
    is_predator: bool  # True = predator, False = prey
    energy: float = 100.0
    age: int = 0
    reproduction_cooldown: int = 0
    last_meal_time: int = 0

class TruePredatorPreySimulation:
    def __init__(self, width=800, height=600, response_type=FunctionalResponseType.TYPE_II):
        self.width = width
        self.height = height
        self.response_type = response_type
        self.animals = []
        self.window = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Colors: Red = Predators, Blue = Prey
        self.predator_color = (255, 100, 100)  # Red
        self.prey_color = (100, 150, 255)     # Blue
        
        # Simulation parameters
        self.dt = 0.02
        self.friction = 0.98
        self.predator_speed = 2.0
        self.prey_speed = 1.8
        self.detection_radius = 80
        self.attack_radius = 25
        self.escape_radius = 100
        
        # Biological parameters
        self.predator_energy_decay = 1.0
        self.prey_energy_decay = 0.2
        self.energy_from_prey = 80
        self.predator_reproduction_threshold = 150
        self.prey_reproduction_threshold = 120
        self.predator_starvation_limit = 0
        self.prey_max_age = 1500
        self.predator_max_age = 2000
        
        # Functional response parameters based on type
        self.setup_functional_response_params()
        
        self.frame_count = 0

    def setup_functional_response_params(self):
        """Setup parameters specific to each functional response type"""
        if self.response_type == FunctionalResponseType.TYPE_I:
            self.max_consumption_rate = 0.8
            self.satiation_threshold = 3  # Number of prey that causes satiation
            self.attack_success_base = 0.6
            
        elif self.response_type == FunctionalResponseType.TYPE_II:
            self.max_consumption_rate = 1.0
            self.handling_time = 50  # Frames of handling time after catching prey
            self.attack_success_base = 0.7
            
        elif self.response_type == FunctionalResponseType.TYPE_III:
            self.max_consumption_rate = 1.2
            self.learning_threshold = 5  # Prey density where learning kicks in
            self.search_image_bonus = 0.4  # Bonus efficiency at high densities
            self.attack_success_base = 0.5
            
        elif self.response_type == FunctionalResponseType.TYPE_IV:
            self.max_consumption_rate = 0.9
            self.optimal_prey_density = 4  # Optimal number of prey nearby
            self.interference_factor = 0.1  # Reduction in efficiency at high densities
            self.attack_success_base = 0.8

    def calculate_attack_success_probability(self, predator: Animal, local_prey_count: int) -> float:
        """Calculate attack success based on functional response type and prey density"""
        base_prob = self.attack_success_base
        
        if self.response_type == FunctionalResponseType.TYPE_I:
            # Linear: constant until satiation
            if local_prey_count >= self.satiation_threshold:
                return base_prob * 0.8  # Reduced efficiency when satiated
            return base_prob
            
        elif self.response_type == FunctionalResponseType.TYPE_II:
            # Hyperbolic: reduced by handling time
            time_since_meal = self.frame_count - predator.last_meal_time
            if time_since_meal < self.handling_time:
                return 0.0  # Still handling previous prey
            return base_prob * (local_prey_count / (self.handling_time/10 + local_prey_count))
            
        elif self.response_type == FunctionalResponseType.TYPE_III:
            # Sigmoidal: low efficiency at low density, high at high density
            if local_prey_count < self.learning_threshold:
                return base_prob * 0.3  # Low efficiency
            else:
                # High efficiency with learning bonus
                learning_bonus = min(self.search_image_bonus, 
                                   (local_prey_count - self.learning_threshold) * 0.1)
                return min(1.0, base_prob + learning_bonus)
                
        elif self.response_type == FunctionalResponseType.TYPE_IV:
            # Dome-shaped: peaks at optimal density, declines at high density
            if local_prey_count == 0:
                return 0.0
            elif local_prey_count <= self.optimal_prey_density:
                # Increasing phase
                return base_prob * (local_prey_count / self.optimal_prey_density)
            else:
                # Declining phase due to interference
                excess = local_prey_count - self.optimal_prey_density
                interference = 1.0 - (self.interference_factor * excess)
                return base_prob * max(0.1, interference)
        
        return base_prob

    def count_nearby_prey(self, predator: Animal) -> int:
        """Count prey within detection radius of predator"""
        count = 0
        for animal in self.animals:
            if not animal.is_predator:
                dx = animal.x - predator.x
                dy = animal.y - predator.y
                
                # Handle toroidal boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < self.detection_radius:
                    count += 1
        return count

    def find_nearest_prey(self, predator: Animal) -> Animal:
        """Find the nearest prey to a predator"""
        nearest_prey = None
        min_distance = float('inf')
        
        for animal in self.animals:
            if not animal.is_predator:
                dx = animal.x - predator.x
                dy = animal.y - predator.y
                
                # Handle boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < min_distance and dist < self.detection_radius:
                    min_distance = dist
                    nearest_prey = animal
        
        return nearest_prey

    def find_nearest_predator(self, prey: Animal) -> Animal:
        """Find the nearest predator to a prey"""
        nearest_predator = None
        min_distance = float('inf')
        
        for animal in self.animals:
            if animal.is_predator:
                dx = animal.x - prey.x
                dy = animal.y - prey.y
                
                # Handle boundaries
                if abs(dx) > self.width / 2:
                    dx = (abs(dx) - self.width) * (dx / abs(dx))
                if abs(dy) > self.height / 2:
                    dy = (abs(dy) - self.height) * (dy / abs(dy))
                
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < min_distance and dist < self.escape_radius:
                    min_distance = dist
                    nearest_predator = animal
        
        return nearest_predator

    def update_predator(self, predator: Animal):
        """Update predator behavior based on functional response"""
        # Find nearest prey
        nearest_prey = self.find_nearest_prey(predator)
        local_prey_count = self.count_nearby_prey(predator)
        
        if nearest_prey:
            # Calculate direction to prey
            dx = nearest_prey.x - predator.x
            dy = nearest_prey.y - predator.y
            
            # Handle boundaries
            if abs(dx) > self.width / 2:
                dx = (abs(dx) - self.width) * (dx / abs(dx))
            if abs(dy) > self.height / 2:
                dy = (abs(dy) - self.height) * (dy / abs(dy))
            
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Move towards prey
                hunt_intensity = self.calculate_attack_success_probability(predator, local_prey_count)
                force = hunt_intensity * self.predator_speed * 50
                
                predator.vx += (dx / dist) * force * self.dt
                predator.vy += (dy / dist) * force * self.dt
                
                # Attempt to catch prey if close enough
                if dist < self.attack_radius:
                    attack_success = self.calculate_attack_success_probability(predator, local_prey_count)
                    if random.random() < attack_success:
                        # Successful hunt!
                        predator.energy += self.energy_from_prey
                        predator.last_meal_time = self.frame_count
                        self.animals.remove(nearest_prey)
        else:
            # No prey nearby - random movement
            predator.vx += random.uniform(-10, 10) * self.dt
            predator.vy += random.uniform(-10, 10) * self.dt

    def update_prey(self, prey: Animal):
        """Update prey behavior - flee from predators, forage"""
        # Find nearest predator
        nearest_predator = self.find_nearest_predator(prey)
        
        if nearest_predator:
            # Calculate direction away from predator
            dx = prey.x - nearest_predator.x
            dy = prey.y - nearest_predator.y
            
            # Handle boundaries
            if abs(dx) > self.width / 2:
                dx = (abs(dx) - self.width) * (dx / abs(dx))
            if abs(dy) > self.height / 2:
                dy = (abs(dy) - self.height) * (dy / abs(dy))
            
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Flee from predator
                panic_level = max(0.1, 1.0 - (dist / self.escape_radius))
                force = panic_level * self.prey_speed * 80
                
                prey.vx += (dx / dist) * force * self.dt
                prey.vy += (dy / dist) * force * self.dt
        else:
            # No predator nearby - forage (gain small energy)
            prey.energy += 0.5
            # Random foraging movement
            prey.vx += random.uniform(-5, 5) * self.dt
            prey.vy += random.uniform(-5, 5) * self.dt

    def reproduce_animal(self, parent: Animal):
        """Handle reproduction for both predators and prey"""
        if parent.reproduction_cooldown > 0:
            return
            
        threshold = (self.predator_reproduction_threshold if parent.is_predator 
                    else self.prey_reproduction_threshold)
        
        if parent.energy > threshold and len(self.animals) < 200:
            # Create offspring
            offspring = Animal(
                x=(parent.x + random.uniform(-30, 30)) % self.width,
                y=(parent.y + random.uniform(-30, 30)) % self.height,
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1, 1),
                is_predator=parent.is_predator,
                energy=threshold * 0.6
            )
            
            # Cost of reproduction
            parent.energy -= threshold * 0.4
            parent.reproduction_cooldown = 100 if parent.is_predator else 60
            
            self.animals.append(offspring)

    def update_animals(self):
        """Update all animals in the simulation"""
        animals_to_remove = []
        
        for animal in self.animals:
            # Age and energy changes
            animal.age += 1
            animal.reproduction_cooldown = max(0, animal.reproduction_cooldown - 1)
            
            if animal.is_predator:
                animal.energy -= self.predator_energy_decay
                self.update_predator(animal)
                
                # Predators die from starvation or old age
                if animal.energy <= self.predator_starvation_limit or animal.age > self.predator_max_age:
                    animals_to_remove.append(animal)
                else:
                    self.reproduce_animal(animal)
            else:
                animal.energy -= self.prey_energy_decay
                self.update_prey(animal)
                
                # Prey die from old age (they gain energy from foraging)
                if animal.age > self.prey_max_age:
                    animals_to_remove.append(animal)
                else:
                    self.reproduce_animal(animal)
            
            # Apply friction and update position
            animal.vx *= self.friction
            animal.vy *= self.friction
            
            # Limit maximum speed
            max_speed = 4.0
            speed = math.sqrt(animal.vx**2 + animal.vy**2)
            if speed > max_speed:
                animal.vx = (animal.vx / speed) * max_speed
                animal.vy = (animal.vy / speed) * max_speed
            
            # Update position with toroidal boundaries
            animal.x = (animal.x + animal.vx * self.dt) % self.width
            animal.y = (animal.y + animal.vy * self.dt) % self.height
        
        # Remove dead animals
        for animal in animals_to_remove:
            if animal in self.animals:
                self.animals.remove(animal)

    def initialize_population(self, num_predators=15, num_prey=60):
        """Initialize population with predators and prey"""
        self.animals = []
        
        # Create predators
        for _ in range(num_predators):
            predator = Animal(
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1, 1),
                is_predator=True,
                energy=random.uniform(100, 140)
            )
            self.animals.append(predator)
        
        # Create prey
        for _ in range(num_prey):
            prey = Animal(
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1, 1),
                is_predator=False,
                energy=random.uniform(80, 120)
            )
            self.animals.append(prey)

    def draw_animals(self):
        """Draw all animals on the window"""
        self.window[:, :, :] = 0  # Clear window
        
        for animal in self.animals:
            if animal.is_predator:
                # Draw predators as red circles, size based on energy
                size = max(4, min(10, int(animal.energy / 20)))
                color = self.predator_color
            else:
                # Draw prey as blue circles
                size = max(3, min(7, int(animal.energy / 30)))
                color = self.prey_color
            
            cv2.circle(self.window, 
                      (int(animal.x), int(animal.y)), 
                      size, color, -1)
            
            # Draw energy indicator
            if animal.is_predator and animal.energy < 50:
                # Low energy predators get a yellow outline
                cv2.circle(self.window, 
                          (int(animal.x), int(animal.y)), 
                          size + 2, (255, 255, 0), 1)

    def get_population_stats(self) -> dict:
        """Get current population statistics"""
        predators = sum(1 for animal in self.animals if animal.is_predator)
        prey = sum(1 for animal in self.animals if not animal.is_predator)
        
        return {
            'predators': predators,
            'prey': prey,
            'total': len(self.animals)
        }

    def run_step(self):
        """Run one simulation step"""
        self.frame_count += 1
        self.update_animals()
        self.draw_animals()
        return cv2.cvtColor(self.window, cv2.COLOR_BGR2RGB)