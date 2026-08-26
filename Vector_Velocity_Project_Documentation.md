# Vector Velocity

## Project Documentation

**Project type:** 3D OpenGL racing game  
**Course:** CSE 423 Computer Graphics  
**Technology:** Python, PyOpenGL, GLU, and GLUT  
**Source file:** `Project_Final (2).py`

---

## 1. Project overview

Vector Velocity is an interactive 3D highway racing game. It combines vehicle physics, computer-controlled racers, highway traffic, local two-player support, multiple cameras, day and night environments, procedural roadside scenery, and a menu-driven interface.

The game demonstrates the complete real-time graphics loop:

- Read keyboard and mouse input.
- Update vehicle physics and artificial intelligence.
- Detect vehicle collisions and lap completion.
- Position one or two cameras.
- Draw the 3D environment and vehicles.
- Draw a two-dimensional HUD and menus.
- Repeat the process through the GLUT main loop.

The visual objects are constructed from basic OpenGL primitives and transformations. Cars, buildings, trees, roads, staging lights, and interface elements use cubes, spheres, cylinders, colored polygons, translations, rotations, scaling, and bitmap text.

## 2. Technology

| Component | Purpose |
|---|---|
| Python | Game logic, state management, physics, input handling, and timing |
| PyOpenGL / OpenGL | Geometry, colors, transformations, depth testing, and viewports |
| GLU | Perspective projection, camera positioning, spheres, and cylinders |
| GLUT | Window creation, solid cubes, bitmap text, input callbacks, and main loop |

## 3. Game modes

### 3.1 Race mode

Race mode places one or two human players against AI racers. A three-second starting sequence freezes vehicle movement before the race starts. Racers drive along the highway, cross lap lines, and compete until the selected number of laps is completed.

During a race, the game tracks:

- Current race time
- Current lap
- Forward-distance score
- Current race position
- Boost status
- Finish order
- Final position and completion time

### 3.2 Free Roam

Free Roam provides open-ended driving without formal race progression or a finish condition. It allows the player to explore the highway, practice steering, use both cameras, activate boost, and interact with highway traffic.

### 3.3 Local two-player race

When the Players setting is set to 2, the game uses a vertical split-screen layout. Each player receives an independent:

- Car
- Control scheme
- Camera
- HUD
- Boost timer
- Score
- Lap counter

Player-to-player collisions use a shared calculation so that neither player receives an unfair advantage.

## 4. Game states

The program uses explicit states to decide what should be updated and displayed.

| State | Purpose |
|---|---|
| Main Menu | Starts a game and changes gameplay settings |
| Tutorial | Displays the controls and gameplay instructions |
| Time Selection | Selects Day or Night before starting the chosen mode |
| Race | Runs timed laps, AI competition, ranking, collisions, and results |
| Free Roam | Runs open-ended driving without race completion |
| Paused | Freezes active play and displays resume/menu options |

## 5. Controls

### 5.1 Player 1

| Input | Action |
|---|---|
| `W` | Accelerate |
| `S` | Brake; when nearly stopped, move in reverse |
| `A` / `D` | Steer left / right |
| `E` | Activate boost when it is ready |
| `Q` | Toggle Chase and Hood cameras |
| Right mouse button | Alternative camera toggle |
| `P` | Pause or resume |
| `M` | Return to the main menu from supported screens |
| Arrow Up / Down | Raise or lower the Chase camera |
| Arrow Left / Right | Swing the Chase camera horizontally |

The arrow keys control the camera. Vehicle steering uses `A` and `D`.

### 5.2 Player 2

| Input | Action |
|---|---|
| `I` / `K` | Accelerate / brake and reverse |
| `J` / `L` | Steer left / right |
| `O` | Activate Player 2 boost |
| `Y` | Toggle Player 2 camera |

### 5.3 Menu controls

- Use `W` and `S` to move the highlighted selection.
- Use `A` and `D` to change the selected setting.
- Press `Enter` to choose an action or confirm Day/Night selection.
- Press `M` to leave the tutorial.

Keyboard-down and keyboard-up callbacks maintain held-key state. Steering remains active until the player releases the corresponding key.

## 6. Configurable settings

| Setting | Behavior |
|---|---|
| Players | Selects one-player or two-player racing |
| Laps | Sets the race length from 1 to 10 laps |
| Difficulty | Selects Easy, Normal, or Hard AI behavior |
| Collisions | Enables or disables vehicle collision responses |
| Sensitivity | Controls how quickly steering responds, from 1.0 to 4.0 |
| Time of Day | Selects the Day or Night visual theme |

### 6.1 Steering sensitivity

Sensitivity controls how quickly the front wheels approach the requested steering angle. It does not change the maximum steering angle.

The maximum wheel angle is 30 degrees. Steering uses exponential easing:

```python
steering_lag = STEERING_LAG * (sensitivity / 2.0)
ease = 1.0 - math.exp(-steering_lag * dt)
wheel_angle += (target_wheel - wheel_angle) * ease
```

- `1.0` produces slower, heavier steering.
- `2.0` is the normal default.
- `4.0` produces faster, more responsive steering.

The calculation uses real elapsed time (`dt`), making steering response independent of frame rate.

## 7. Vehicle physics

Each human car stores:

- A three-dimensional position
- A three-dimensional velocity
- A facing angle
- A current wheel angle
- Pressed-key states
- Boost state and timing

### 7.1 Acceleration

Acceleration applies thrust along the direction in which the car is facing. The facing direction is calculated from the facing angle using sine and cosine.

### 7.2 Braking and reverse

When the car is moving forward, the brake key applies a stronger opposing force. Once the car is almost stopped, holding the same key applies reverse thrust.

### 7.3 Friction

Velocity is multiplied by the friction value during every physics update. This gradually reduces speed when the player stops accelerating.

### 7.4 Maximum speed

The total horizontal speed is calculated from the X and Z velocity components. If it exceeds the permitted maximum, both components are scaled down proportionally. This preserves movement direction while limiting speed.

### 7.5 Turning

At useful speed, wheel angle changes the car facing angle. Turning direction is reversed while the car is moving backward. Strong steering also causes a small speed reduction to create an arcade-style cornering penalty.

### 7.6 Road boundaries

The car X coordinate is clamped inside the road edges, leaving enough space for the width of the car. This prevents the car center from moving outside the driveable highway.

## 8. Boost system

Boost is a cooldown-based temporary speed increase.

- Player 1 activates it with `E`.
- Player 2 activates it with `O`.
- Boost lasts for 2 seconds.
- Maximum speed becomes 1.5 times normal.
- The cooldown lasts for 8 seconds.
- Boost cannot be activated again until the cooldown finishes.

The HUD displays one of the following:

- `BOOST ACTIVE!`
- `BOOST: READY`
- Remaining cooldown time

While boost is active, pulsing cyan exhaust flames are drawn behind the car to provide clear visual feedback.

## 9. Score calculation

Score represents the greatest forward distance reached by a player.

Player 1 uses:

```python
config.score = max(config.score, int(config.car_pos[2] / 10))
```

Player 2 uses the same calculation with `player2_pos` and `player2_score`.

Examples:

| Forward Z position | Displayed score |
|---:|---:|
| 100 | 10 |
| 500 | 50 |
| 1,000 | 100 |
| 3,000 | 300 |

The use of `max()` means that reversing does not reduce the score. Although the HUD labels the value as metres, it is technically the maximum forward world-coordinate distance divided by 10.

## 10. Race timer, laps, and ranking

### 10.1 Starting countdown

Race physics remains frozen during the first three seconds. The HUD displays the numeric countdown followed by `GO!`.

### 10.2 Race timer

The displayed race timer remains at zero during the countdown. After the countdown, elapsed race time is measured relative to the moment gameplay begins. The final time is preserved once the race finishes.

### 10.3 Lap system

A checkered lap line is placed every 3,000 world units. Crossing the next required line advances the player lap. The selected lap count determines when the race is complete.

Lap markers are drawn only when they are near the active camera. This reduces unnecessary rendering work.

### 10.4 Ranking

Current race position is calculated by sorting the human and AI racers according to their forward Z coordinate. The racer with the greatest Z coordinate is first.

When the race ends, finishing positions are stored so later AI movement cannot change the result displayed to the player.

## 11. Artificial intelligence and traffic

### 11.1 AI racers

AI racers compete directly with the human players. They participate in position calculations, lap completion, and finishing order. The selected Easy, Normal, or Hard difficulty changes their racing performance.

### 11.2 NPC highway traffic

NPC cars provide moving traffic separate from the race opponents. They:

- Travel forward at individually selected speeds.
- Move gradually toward a target lane.
- Use the left, center, and right highway lanes.
- Reappear ahead of the racers after falling far behind.

Recycling traffic cars produces an endless populated highway without continuously creating new objects.

### 11.3 Collision handling

When collisions are enabled, distance checks detect cars that are too close. A collision:

- Reduces vehicle velocity.
- Pushes overlapping vehicles apart.
- Prevents cars from remaining in the same position.

Player-to-player collision uses a single shared calculation so both cars receive a balanced response. Collisions can be disabled from the main menu.

## 12. Camera system

### 12.1 Chase camera

The Chase camera follows behind and above the car. It looks toward the vehicle and provides a broad view of the road, traffic, and scenery.

Its height and horizontal swing can be adjusted with the arrow keys.

### 12.2 Hood camera

The Hood camera is positioned near the front of the vehicle and looks forward along the car facing direction. It provides a more immersive first-person-style view.

### 12.3 Split-screen cameras

In a two-player race, the window is divided into two viewports. For each viewport, the program:

1. Clears the depth buffer.
2. Selects the corresponding player position and camera.
3. Applies that camera transformation.
4. Draws the complete world.
5. Draws the correct player HUD.

The same scene is therefore rendered twice from two independent viewpoints.

## 13. Track and environment

### 13.1 Endless highway

The road is 160 world units wide. It is drawn in repeating 200-unit segments around the active camera. Lane markers use repeated quadrilaterals, and ground planes are drawn on both sides of the road.

Track segments and environmental objects are positioned relative to the player to create the illusion of an endless highway.

### 13.2 Road markings

The road includes:

- Left and right edge markings
- A yellow center line
- Dashed lane separators
- Checkered lap/start lines

### 13.3 Procedural buildings

A seeded random generator creates buildings once when the game starts. Building properties include:

- Side of the road
- Distance from the road
- Forward position
- Width and depth
- Height
- RGB color

Most buildings use moderate heights, while some use a much larger height range to create a varied skyline.

### 13.4 Distant skyline or hills

Wide, low, dark cubes are positioned farther from the road. They form a second background layer that resembles distant hills or a city silhouette without introducing a new geometry type.

### 13.5 Trees

Trees are procedurally placed along both sides of the highway. Their colors and positions vary. Like buildings, they are recycled across repeating environment spans.

### 13.6 Day mode

Day mode uses brighter:

- Grass
- Road surface
- Road markings
- Buildings
- Sky colors

A yellow sphere represents the sun.

### 13.7 Night mode

Night mode darkens the ground, road, and structures. It uses a darker sky gradient and displays a pale sphere representing the moon.

### 13.8 Staging lights

A drag-racing-inspired starting-light stack appears near the start line. It contains three amber spheres and one green sphere. The lights illuminate in sequence as the countdown approaches zero.

## 14. Vehicle rendering

The car is built hierarchically with OpenGL matrix transformations.

### 14.1 Chassis and cabin

Scaled cubes form the main body and roof. Player 1, Player 2, AI racers, and NPC vehicles use different colors.

### 14.2 Windows

Scaled and rotated cubes form the windshield, rear window, and side windows.

### 14.3 Wheels

The wheels combine:

- Cylinders for tire tread
- Flattened spheres for tire walls
- Smaller flattened spheres for hubcaps

The front wheels rotate visually according to the current wheel angle.

### 14.4 Vehicle animation

The player car receives small visual movements:

- Acceleration pitches the body backward.
- Braking pitches the body forward.
- Steering rolls the body sideways.
- Boost creates pulsing cyan exhaust flames.

These animations improve the sense of speed and vehicle response without changing the physical car geometry.

## 15. User interface and HUD

The interface is drawn in a two-dimensional orthographic projection using GLUT bitmap characters.

### 15.1 HUD information

The HUD can display:

- Player name
- Approximate speed in km/h
- Forward-distance score
- Boost state or cooldown
- Current camera mode
- Current race position
- Current lap and total laps
- Race time
- Countdown or `GO!`
- Winner and final position

### 15.2 Main menu

The main menu contains actions and configurable values. The highlighted option is visually distinguished, and the displayed text updates when a setting changes.

### 15.3 Tutorial

The How to Play screen explains Player 1 controls, Player 2 controls, boost activation, camera controls, and menu navigation.

### 15.4 Time selection

Before starting Race or Free Roam, the user chooses Day or Night. The selected value controls environment colors and the sun/moon rendering.

### 15.5 Pause menu

Pressing `P` stores the previous gameplay state and opens the pause overlay. Pressing `P` again resumes that state, while `M` returns to the main menu.

## 16. Program architecture

### 16.1 Shared game state

A `GameState` object named `config` stores settings and runtime data. It contains:

- State constants and current state
- Menu selections
- Player settings
- Camera configuration
- Player positions and velocities
- Steering and input state
- Boost timing
- Race timing and lap data
- Scores and final positions
- AI and NPC lists

### 16.2 Main subsystems

| Subsystem | Responsibilities |
|---|---|
| Initialization | Create AI racers, traffic, scenery, and clean race data |
| Physics | Apply acceleration, braking, friction, steering, boost, and position changes |
| AI and traffic | Move computer racers and recycle NPC traffic |
| Collision and race logic | Resolve overlaps, count laps, calculate ranking, and finish races |
| Rendering | Draw sky, track, environment, cars, staging lights, HUD, and menus |
| Input | Handle key down/up events, special keys, mouse input, and state changes |
| State management | Select the correct update and drawing behavior for each game state |

### 16.3 Main update sequence

During active gameplay, the `idle()` callback:

1. Measures real elapsed frame time.
2. Updates held directional keys.
3. Freezes gameplay during the race countdown.
4. Updates race time.
5. Updates boost timers.
6. Updates player physics.
7. Updates AI racers.
8. Updates NPC traffic.
9. Processes collisions and laps.
10. Requests a new frame.

### 16.4 Main rendering sequence

The `showScreen()` callback:

1. Clears the color and depth buffers.
2. Selects the screen for the current game state.
3. Configures one or two viewports during gameplay.
4. Draws the sky.
5. Applies the player camera.
6. Draws the road, environment, cars, and staging lights.
7. Draws the player HUD.
8. Draws the pause overlay when required.
9. Swaps the double buffers.

## 17. Important constants

| Constant | Current value | Purpose |
|---|---:|---|
| `ROAD_WIDTH` | 160.0 | Total road width |
| `MAX_SPEED` | 20.0 | Normal maximum car speed |
| `FRICTION` | 0.96 | Velocity retained per physics update |
| `THRUST` | 0.45 | Forward acceleration force |
| `BRAKE_FORCE` | 0.40 | Base braking force |
| `MAX_WHEEL_ANGLE` | 30.0 | Maximum steering angle in degrees |
| `STEERING_LAG` | 10.0 | Base steering response rate |
| `BOOST_SPEED_MULTIPLIER` | 1.5 | Boosted maximum-speed multiplier |
| `BOOST_DURATION` | 2.0 seconds | Active boost duration |
| `BOOST_COOLDOWN` | 8.0 seconds | Time before boost can be reused |
| Lap distance | 3,000 units | Distance between lap lines |

## 18. Running the project

### Requirements

- Python 3
- PyOpenGL
- A compatible GLUT or freeglut runtime

### Command

From the project directory, run:

```powershell
python 'Project_Final (2).py'
```

The program creates a 1000 by 800 double-buffered RGB window with depth testing.

### Starting a session

1. Use `W` and `S` to choose Race, Free Roam, Tutorial, or a setting.
2. Use `A` and `D` to adjust the selected setting.
3. Press `Enter` on Race or Free Roam.
4. Select Day or Night.
5. Press `Enter` to start.

## 19. Design characteristics and limitations

- The game intentionally uses immediate-mode OpenGL and basic primitives for course compliance and clarity.
- Physics values are tuned for arcade gameplay rather than realistic vehicle simulation.
- The score is a scaled world-coordinate distance, even though the HUD labels it as metres.
- The environment is procedurally arranged but repeats in spans to support endless travel efficiently.
- The road is straight and endless rather than using a curved track system.
- Visual objects use colors and geometry rather than texture mapping.
- Multiplayer is local split-screen, not network multiplayer.

## 20. Complete feature summary

| Category | Implemented features |
|---|---|
| Game modes | Race and Free Roam |
| Players | Single-player and local split-screen two-player racing |
| Race systems | Countdown, staging lights, laps, timing, ranking, finish order, results |
| Driving | Acceleration, braking, reverse, friction, smooth steering, boundaries, boost |
| Competition | Difficulty-based AI racers and recyclable NPC traffic |
| Collisions | Optional collision detection, slowdown, and separation |
| Cameras | Chase camera, Hood camera, adjustable Chase camera, independent multiplayer views |
| Environment | Endless road, lane markings, buildings, trees, distant skyline, Day/Night themes |
| Vehicle graphics | Hierarchical car model, animated steering, pitch, roll, wheels, boost exhaust |
| Interface | Main menu, tutorial, time selection, HUD, pause screen, race results |
| Settings | Players, laps, difficulty, collisions, sensitivity, and time of day |

---

*End of project documentation.*
