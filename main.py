import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm

# Define material properties for gamma rays (~1 MeV)
materials = {
    "Lead": {"density": 11.34, "mu": 0.5},  #mu is the linear attenuation coefficient of the materials
    "Aluminum": {"density": 2.7, "mu": 0.136},
    "Concrete": {"density": 2.4, "mu": 0.03},
    "Steel": {"density": 7.85, "mu": 0.15},
}

# Simulation parameters - Arbitrary Units
num_particles = 300
material_thickness = 10
canvas_width = 200
canvas_height = 150

# Dictionary to store transmitted particle counts
results = {material: 0 for material in materials.keys()}


# Simulation function
def run_simulation(material):
    mu = materials[material]["mu"]

    # Initialize particles
    particles = np.zeros((num_particles, 3))  # (x, y, speed)
    particles[:, 0] = np.random.uniform(0, canvas_width, size=num_particles)
    particles[:, 1] = np.full(num_particles, 0)  # Start below the barrier

    particle_states = np.zeros(num_particles, dtype=int)  # 0 = active, 1 = absorbed, 2 = transmitted

    #An arbitrary speed value provided to help visualise the particles motion
    speed = 70
    particles[:, 2] = np.full(num_particles, speed)

    angles = np.random.uniform(np.pi / 3, 2 * np.pi / 3, size=num_particles)
    particles[:, 0] += np.cos(angles) * particles[:, 2]
    particles[:, 1] += np.sin(angles) * particles[:, 2]

    # Plot setup
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, canvas_width)
    ax.set_ylim(0, canvas_height)
    ax.set_title(f"Gamma Ray Simulation - {material}")
    ax.set_xlabel("X Position (cm)")
    ax.set_ylabel("Y Position (cm)")

    # Draw material
    material_rect = plt.Rectangle((0, canvas_height // 2), canvas_width, material_thickness,
                                  color="gray", alpha=0.3, label="Material Barrier")
    ax.add_patch(material_rect)

    scatter = ax.scatter(particles[:, 0], particles[:, 1], c="blue", s=20, alpha=1)

    detection_layer_y = (canvas_height // 2) + material_thickness

    # Calculate probability once per photon using Beer Lambert's Law
    transmission_probabilities = np.exp(-mu * material_thickness)

    # Animation update function
    def update(frame):
        nonlocal particles, particle_states

        active_particles = particle_states == 0
        particles[active_particles, 0] += np.cos(angles[active_particles]) * 1
        particles[active_particles, 1] += np.sin(angles[active_particles]) * 1

        for i in range(num_particles):
            if particle_states[i] == 0:
                if canvas_height // 2 <= particles[i, 1] <= (canvas_height // 2 + material_thickness):
                    # Decide transmission ONCE when entering the material
                    if np.random.rand() < transmission_probabilities:
                        particle_states[i] = 2  # Transmitted
                    else:
                        particle_states[i] = 1  # Absorbed

        # Update scatter plot
        scatter.set_offsets(particles[:, :2])

        colors = ["blue" if state == 0 else "red" if state == 1 else "green"
                  for state in particle_states]
        scatter.set_color(colors)

        # Stop condition: when all particles are absorbed or transmitted
        if np.all(particle_states != 0):
            ani.event_source.stop()
            ax.text(0.5, 0.5, "Simulation Ended", ha='center', va='center', fontsize=20, color='red',
                    transform=ax.transAxes)

    ani = FuncAnimation(fig, update, frames=200, interval=50)
    plt.show()

    # Store final count of transmitted particles
    results[material] = np.sum(particle_states == 2)


# Run simulations
for material in materials.keys():
    run_simulation(material)

# Final Bar Chart
materials_list = list(materials.keys())
transmitted_counts = [results[material] for material in materials_list]

fig_results, ax_results = plt.subplots(figsize=(12, 8))
ax_results.bar(materials_list, transmitted_counts, color="green", alpha=0.7)
ax_results.set_title("Number of Transmitted Particles for Each Material (Gamma Rays)")
ax_results.set_xlabel("Material")
ax_results.set_ylabel("Number of Transmitted Particles")

plt.show()
