# 🦁 Predator-Prey Functional Response Simulation

This simulation demonstrates the four types of functional responses in predator-prey ecological interactions, with each particle type representing a different functional response behavior.

## 🎯 Functional Response Types

### 🔴 Type I - Linear Response (Red Particles)
- **Behavior**: Linear increase in consumption rate with prey density until satiation
- **Real-world example**: Filter feeders like barnacles or mussels
- **Characteristics**: Simple, predictable hunting behavior with a clear maximum consumption rate

### 🟢 Type II - Hyperbolic Response (Green Particles)  
- **Behavior**: Rapid initial increase in consumption that levels off due to handling time
- **Real-world example**: Most common predator behavior (wolves, hawks, spiders)
- **Characteristics**: Limited by the time needed to catch, kill, and consume prey

### 🔵 Type III - Sigmoidal Response (Blue Particles)
- **Behavior**: S-shaped curve with low consumption at low densities, rapid increase at medium densities
- **Real-world example**: Predators that switch between prey types or learn hunting strategies
- **Characteristics**: Creates refuges for prey at low densities, may involve prey switching

### 🟡 Type IV - Dome-shaped Response (Yellow Particles)
- **Behavior**: Consumption peaks at intermediate prey densities, then decreases
- **Real-world example**: Predators facing dangerous prey (like bees with stingers)
- **Characteristics**: High prey densities become counterproductive due to interference or danger

## 🚀 How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the predator-prey simulation:**
   ```bash
   streamlit run predator_prey_app.py
   ```

3. **Use the controls:**
   - Adjust population sizes and parameters in the sidebar
   - Click "Start Simulation" to begin
   - Watch the real-time population dynamics
   - Use "Pause" and "Reset" as needed

## 🎮 Features

- **Real-time visualization** of 4 different colored particle types
- **Interactive parameter controls** for population sizes, energy dynamics, and physics
- **Live population graphs** showing dynamics over time
- **Statistical displays** of current population distributions
- **Educational information** about each functional response type

## 🔬 Simulation Mechanics

- **Energy System**: Particles gain energy by consuming others and lose energy over time
- **Reproduction**: Particles reproduce when they have sufficient energy
- **Death**: Particles die from starvation or old age
- **Movement**: Particles move according to their functional response to local prey density
- **Consumption**: Success rate depends on the specific functional response curve

## 📊 What to Observe

- **Population Oscillations**: Classic predator-prey cycles
- **Competitive Exclusion**: Some types may outcompete others
- **Stable Coexistence**: Different response types may find different niches
- **Extinction Events**: Poor parameter settings may lead to population crashes
- **Response Differences**: How each type responds to varying prey densities

## 🎛️ Key Parameters

- **Particles per Type**: Initial population of each functional response type
- **Interaction Radius**: How far particles can sense potential prey
- **Energy Decay Rate**: How quickly particles lose energy (affects lifespan)
- **Reproduction Threshold**: Energy needed to reproduce
- **Energy Gain from Prey**: How much energy predators gain from successful hunts

## 📈 Expected Behaviors

- **Type I (Red)**: Steady, predictable hunting patterns
- **Type II (Green)**: Efficient at low prey densities, most successful overall
- **Type III (Blue)**: May show boom-bust cycles, creates prey refuges
- **Type IV (Yellow)**: May struggle at high densities, complex dynamics

Experiment with different parameter combinations to see how they affect the ecological dynamics!