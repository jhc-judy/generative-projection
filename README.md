# Generative Projection Studies

A series of real-time generative visual experiments exploring autonomous movement, spatial navigation, disturbance, accumulation, and changing visual behavior.

The project was developed as part of my ongoing investigation into how computational systems can behave as active components within sculptural and installation work rather than as fixed video playback.

These studies directly inform the real-time animation system used in *Memory of the Fish Jar*, particularly the movement of autonomous agents, reactions to disturbance, and gradual behavioral settling over time.

## Tools

- Python
- Pygame
- GLSL shaders
- Real-time interactive rendering

## Studies

### Path / Navigation
Moving agents respond to spatial structures, obstacles, and changing routes.

### Autonomous Movement
Independent agents move with variation in speed, direction, and behavior rather than following a fixed loop.

### Accumulation / Disturbance
Visual changes build over time, leave temporary traces, and gradually settle rather than resetting immediately.

## Project Structure

- `main.py` — main application entry point
- `shaders/` — shader-based visual studies
- `renderer/` — rendering components
- `recordings/` — video documentation of running systems
- `tests/` — development and interaction tests

## Running the Project

Install the required Python packages, then run:

```bash
python main.py
