# Vector Velocity

Vector Velocity is a 3D highway racing game developed in Python with PyOpenGL, GLU, and GLUT for the CSE 423 Computer Graphics course.

The project includes single-player racing, local split-screen multiplayer, AI opponents, moving highway traffic, two camera modes, configurable race settings, an endless roadside environment, day/night themes, smooth steering, collisions, laps, scoring, and a cooldown-based speed boost.

## Features

- Race and Free Roam game modes
- Single-player and local two-player split-screen racing
- Easy, Normal, and Hard AI difficulty levels
- Configurable lap count, collision mode, and steering sensitivity
- Chase and Hood cameras
- Adjustable Chase camera position
- Day and Night environments
- Procedurally arranged buildings, trees, and distant skyline objects
- Endless segmented highway with lane markings
- Moving NPC highway traffic
- Three-second countdown and drag-racing staging lights
- Lap tracking, race timer, ranking, finish order, and results
- Distance-based score system
- Cooldown-based temporary speed boost with an exhaust effect
- Menu, tutorial, HUD, pause screen, and time-selection screen

## Requirements

- Python 3
- PyOpenGL
- PyOpenGL Accelerate, recommended
- A compatible GLUT or freeglut runtime

Install the Python packages with:

```bash
python -m pip install PyOpenGL PyOpenGL_accelerate
```

## Running the game

Clone the repository and enter its directory:

```bash
git clone https://github.com/Nabilthahamid/CSE423_project-.git
cd CSE423_project-
```

Run the game:

```bash
python 'Project_Final (2).py'
```

## Controls

### Player 1

| Input | Action |
|---|---|
| `W` | Accelerate |
| `S` | Brake / reverse |
| `A` / `D` | Steer left / right |
| `E` | Activate boost |
| `Q` | Toggle Chase/Hood camera |
| Right mouse button | Toggle camera |
| `P` | Pause or resume |
| `M` | Return to the main menu |
| Arrow keys | Adjust the Chase camera |

### Player 2

| Input | Action |
|---|---|
| `I` / `K` | Accelerate / brake and reverse |
| `J` / `L` | Steer left / right |
| `O` | Activate boost |
| `Y` | Toggle camera |

### Menus

- Use `W` and `S` to move through options.
- Use `A` and `D` to change a setting.
- Press `Enter` to select or confirm.

## Score calculation

Score represents the greatest forward distance reached:

```python
score = max(score, int(car_position_z / 10))
```

Every 10 forward world units adds one score point. Reversing does not reduce the score.

## Steering sensitivity

Sensitivity controls how quickly steering moves toward the requested wheel angle:

- `1.0`: slower and heavier
- `2.0`: normal
- `4.0`: faster and more responsive

Steering uses elapsed frame time to maintain consistent behavior at different frame rates.

## Documentation

Full feature and technical documentation is available in:

- [Project documentation](Vector_Velocity_Project_Documentation.md)
- [Word documentation](Vector_Velocity_Project_Documentation.docx)

## Project structure

| File | Description |
|---|---|
| `Project_Final (2).py` | Main game source code |
| `README.md` | Repository overview and setup guide |
| `Vector_Velocity_Project_Documentation.md` | Complete Markdown documentation |
| `Vector_Velocity_Project_Documentation.docx` | Formatted Word documentation |

## Technical notes

- The game uses immediate-mode OpenGL and primitive geometry for course compliance.
- Physics is designed for responsive arcade-style driving rather than realistic simulation.
- Multiplayer is local split-screen and does not require a network connection.
- Roadside objects repeat in environment spans to create an efficient endless-highway effect.

## License

This project was created for academic and educational purposes.
