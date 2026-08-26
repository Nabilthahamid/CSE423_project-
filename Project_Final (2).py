# ============================================================================
# VECTOR VELOCITY - ENDLESS HIGHWAY RACING
# CSE 423 OpenGL Project
# ============================================================================
#
# HOW TO PLAY
# -----------
# 1. Run this Python file. The game opens at the Main Menu.
# 2. Use W and S to move up and down through the menu.
# 3. Use A and D to change the selected setting.
# 4. Press ENTER on "Start Race" or "Free Roam".
# 5. Select Day or Night with W/S, then press ENTER to begin.
#
# MAIN MENU SETTINGS
# ------------------
# Players      : Select one-player or local two-player racing.
# Laps         : Select the number of laps required to finish the race.
# Difficulty   : Changes the maximum speed of the AI racers.
# Collisions   : Turns gameplay collision responses ON or OFF.
# Sensitivity  : Changes how quickly the cars steer.
#
# PLAYER 1 CONTROLS
# -----------------
# W : Accelerate
# S : Brake / Reverse
# A : Steer left
# D : Steer right
# E : Activate boost when it is ready
# Q : Toggle between Chase Camera and Hood Camera
#
# PLAYER 2 CONTROLS (TWO-PLAYER RACE MODE)
# ------------------------------------------------
# I : Accelerate
# K : Brake / Reverse
# J : Steer left
# L : Steer right
# O : Activate boost when it is ready
# Y : Toggle between Chase Camera and Hood Camera
#
# GLOBAL AND CAMERA CONTROLS
# --------------------------
# P           : Pause or resume the game
# M           : Return to the Main Menu when paused or after a race
# Arrow Up    : Raise the single-player camera
# Arrow Down  : Lower the single-player camera
# Arrow Left  : Swing the single-player camera left
# Arrow Right : Swing the single-player camera right
# Right Mouse : Toggle the Player 1 camera (kept for compatibility)
#
# GAME MODES
# ----------
# Start Race:
#   Race against two blue AI opponents. In two-player mode, Player 1 and
#   Player 2 race together using a vertical split screen. The first racer to
#   complete all selected laps wins. Yellow, purple, cyan, and orange traffic
#   cars are moving obstacles and are not included in race rankings.
#
# Free Roam:
#   Drive without race rankings or a finish requirement. The standard Player 1
#   controls and adjustable camera remain available.
#
# BOOST
# -----
# Each human player has a separate boost. A boost temporarily increases
# acceleration and maximum speed. It lasts about 2 seconds and takes about
# 8 seconds before it is ready again. The HUD displays READY, ACTIVE, or the
# remaining cooldown time.
#
# HUD INFORMATION
# ---------------
# Each player can see their speed, distance score, camera mode, boost status,
# current lap, current race position, and race time. In two-player mode, each
# side of the split screen displays information for its own player.
#
# HOW THE PROGRAM WORKS
# ---------------------
# - GameState/config stores menu settings, player state, cameras, race data,
#   AI racers, NPC traffic, boost timers, and the current screen state.
# - keyboardListener() and short key-expiration counters maintain driving input.
#   Single-press keys activate boost, camera, and pause actions.
# - idle() is the only game loop. It updates the countdown, timer, boosts,
#   both human players, AI racers, traffic, collisions, laps, and results.
# - update_player_physics() applies the same acceleration, braking, friction,
#   steering, road-boundary, and boost rules to both human players.
# - update_ai() controls the two racing opponents. update_npc() controls and
#   recycles traffic obstacles independently from race competitors.
# - check_collisions_and_laps() handles human, AI, and traffic collisions and
#   calculates independent player laps, rankings, and the race winner.
# - draw_game_world() draws one shared world. showScreen() draws it once in
#   single-player mode or twice with independent cameras in split-screen mode.
# - reset_race() clears old positions, keys, cameras, laps, results, and boost
#   timers so every new game starts from a clean state.
#
# ============================================================================
# CODING PART STARTS HERE
# ============================================================================

import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
class GameState:
    pass

config = GameState()

# State Constants
config.STATE_MENU     = 0
config.STATE_RACE     = 1
config.STATE_FREE_ROAM = 2
config.STATE_PAUSED   = 3
config.STATE_TIME_SELECT = 4
config.STATE_TUTORIAL = 5
config.current_state  = config.STATE_MENU
config.current_time_selection = 0
config.pending_game_state = config.STATE_RACE
config.setting_time_of_day = 'Day'

# Menu & Settings
config.current_menu_selection = 0
config.setting_laps        = 3
config.setting_opponents   = 2
config.setting_difficulty  = "Normal"
config.setting_collisions  = True
config.setting_sensitivity = 2.0
config.setting_players     = 1
config.window_width        = 1000
config.window_height       = 800
config.previous_state      = config.STATE_RACE

def get_menu_options():
    return [
        'How to Play',
        "Start Race",
        "Free Roam",
        f"Players: {config.setting_players}",
        f"Laps: {config.setting_laps}",
        f"Difficulty: {config.setting_difficulty}",
        f"Collisions: {'ON' if config.setting_collisions else 'OFF'}",
        f"Sensitivity: {round(config.setting_sensitivity, 1)}"
    ]

# Camera Configuration
config.CAM_CHASE        = 0
config.CAM_HOOD         = 1
config.current_camera   = config.CAM_CHASE
config.cam_height_offset = 50.0
config.cam_swing_angle  = 0.0

# Physics & Player Car
config.MAX_SPEED      = 20.0
config.FRICTION       = 0.96          
config.THRUST         = 0.45
config.BRAKE_FORCE    = 0.40
config.MAX_WHEEL_ANGLE = 30.0
config.STEERING_LAG    = 10.0

config.car_pos           = [0.0, 0.0, 0.0]
config.car_velocity      = [0.0, 0.0, 0.0]
config.car_facing_angle  = 0.0          # degrees, 0 = moving along +Z axis
config.current_wheel_angle = 0.0

config.keys_pressed = {b'w': False, b's': False, b'a': False, b'd': False}
config.key_expiry = {b'w': 0.0, b's': 0.0, b'a': 0.0, b'd': 0.0}
config.INPUT_STEER_SECONDS = 0.14

# ============================================================
# PLAYER 2 STATE
# ============================================================
config.player2_pos = [18.0, 0.0, 0.0]
config.player2_velocity = [0.0, 0.0, 0.0]
config.player2_facing_angle = 0.0
config.player2_current_wheel_angle = 0.0
config.player2_keys_pressed = {b'i': False, b'k': False, b'j': False, b'l': False}
config.player2_key_expiry = {b'i': 0.0, b'k': 0.0, b'j': 0.0, b'l': 0.0}
config.player2_current_lap = 1
config.player2_score = 0
config.player2_current_camera = config.CAM_CHASE
config.player2_cam_height_offset = 50.0
config.player2_cam_swing_angle = 0.0

# ============================================================
# BOOST SYSTEM
# ============================================================
config.BOOST_SPEED_MULTIPLIER = 1.5
config.BOOST_DURATION = 2.0
config.BOOST_COOLDOWN = 8.0
config.player1_boost_active = False
config.player1_boost_start_time = 0.0
config.player1_boost_last_used = -100.0
config.player2_boost_active = False
config.player2_boost_start_time = 0.0
config.player2_boost_last_used = -100.0
config.last_update_time = time.time()

# Race Progress
config.current_lap      = 1
config.race_start_time  = 0.0
config.current_race_time = 0.0
config.race_finished    = False
config.score            = 0            # distance-based score for endless mode
config.player_waypoint  = 0

# AI Opponents
config.ai_cars = []
config.npc_cars = []
config.finish_order = []
config.final_positions = {}

def init_ai(num_opponents, difficulty):
    config.ai_cars = []
    num_opponents = 2 # Force exactly 2 AI opponents for the race (total 3 cars)
    
    # Calculate player's TRUE top speed due to friction equilibrium
    # Formula: terminal_velocity = thrust / (1 - friction)
    player_true_top_speed = config.THRUST / (1.0 - config.FRICTION)

    if difficulty == "Easy":
        # Roughly 84% of player's actual top speed
        speed_min = player_true_top_speed * 0.82
        speed_max = player_true_top_speed * 0.84
    elif difficulty == "Hard":
        # Exact same top speed as player
        speed_min = player_true_top_speed * 0.98
        speed_max = player_true_top_speed * 1.00
    else: # Normal mode
        # Roughly 89-92% of player's actual top speed
        speed_min = player_true_top_speed * 0.89
        speed_max = player_true_top_speed * 0.92

    # Ensure AI acceleration is much lower than player acceleration 
    # (Player thrust is 0.25, we give AI 0.03 so that we can easily catch up)
    ai_acceleration = 0.03

    # Place them behind the player at the start line
    lanes = [-LANE_OFFSET, LANE_OFFSET] 
    for i in range(num_opponents):
        lane = lanes[i % 2]
        config.ai_cars.append({
            "pos": [lane, 0.0, -40.0],   # Start 40 units behind the player
            "max_speed": random.uniform(speed_min, speed_max),
            "accel": ai_acceleration,    # New variable for slower acceleration
            "lane": lane,
            "lane_change_timer": random.uniform(3.0, 7.0),
            "facing_angle": 0.0,
            "velocity_z": 0.0
        })

def init_npc():
    """Create traffic obstacles; they are never race competitors."""
    config.npc_cars = []
    lanes = [-LANE_OFFSET, 0.0, LANE_OFFSET]
    for i in range(6):
        config.npc_cars.append({
            "pos": [random.choice(lanes), 0.0, 350.0 + i * 260.0 + random.uniform(0, 100)],
            "speed": random.uniform(5.0, 8.0),
            "lane": random.choice(lanes),
            "color": random.choice([(0.9, 0.7, 0.1), (0.8, 0.3, 0.8),
                                    (0.1, 0.7, 0.8), (0.85, 0.45, 0.1)])
        })

def update_npc():
    humans = [config.car_pos[2]]
    if config.setting_players == 2 and config.current_state == config.STATE_RACE:
        humans.append(config.player2_pos[2])
    leading_z = max(humans)
    trailing_z = min(humans)
    for npc in config.npc_cars:
        npc["pos"][2] += npc["speed"]
        npc["pos"][0] += (npc["lane"] - npc["pos"][0]) * 0.03
        if npc["pos"][2] < trailing_z - 350.0:
            farthest = max([leading_z] + [n["pos"][2] for n in config.npc_cars])
            npc["pos"][2] = farthest + random.uniform(180.0, 360.0)
            npc["lane"] = random.choice([-LANE_OFFSET, 0.0, LANE_OFFSET])
            npc["speed"] = random.uniform(5.0, 8.0)

#  ENDLESS HIGHWAY TRACK & ENVIRONMENT


ROAD_WIDTH    = 160.0
LANE_OFFSET   = 35.0      
ROAD_HALF     = ROAD_WIDTH / 2.0
ROAD_SEGMENT  = 200.0      
NUM_SEGMENTS  = 12        

# Pre-built environment objects (generated once, then reused and repositioned as the player moves forward)
env_buildings = []   
env_trees     = []  

def generate_env_objects():
    global env_buildings, env_trees
    env_buildings = []
    env_trees     = []

    ENV_SPAN = NUM_SEGMENTS * ROAD_SEGMENT

    rng = random.Random(42)
    for _ in range(40):
        side = rng.choice([-1, 1])
        x    = side * (ROAD_HALF + rng.uniform(20, 130))
        z    = rng.uniform(0, ENV_SPAN)
        w    = rng.uniform(18, 45)
        h    = rng.uniform(25, 160) if rng.random() < 0.25 else rng.uniform(30, 90)
        d    = rng.uniform(18, 45)
        r    = rng.uniform(0.3, 1.0)
        g    = rng.uniform(0.3, 1.0)
        b_   = rng.uniform(0.3, 1.0)
        env_buildings.append((x, z, w, h, d, r, g, b_))

    # Wide, low cubes form a second skyline layer in the far distance.
    for _ in range(15):
        side = rng.choice([-1, 1])
        x = side * (ROAD_HALF + rng.uniform(250, 500))
        z = rng.uniform(0, ENV_SPAN)
        h = rng.uniform(40, 90)
        env_buildings.append((x, z, 120, h, 120, 0.35, 0.32, 0.30))

    for _ in range(120):
        side = rng.choice([-1, 1])
        x    = side * (ROAD_HALF + rng.uniform(8, 180))
        z    = rng.uniform(0, ENV_SPAN)
        r    = rng.uniform(0.0, 0.35)
        g    = rng.uniform(0.5, 0.9)
        b_   = rng.uniform(0.0, 0.25)
        env_trees.append((x, z, r, g, b_))


def draw_ground_plane():
    GROUND_HALF = 800.0
    reference_z = getattr(config, 'render_reference_z', config.car_pos[2])
    ROAD_Z_NEAR = reference_z - 400.0
    ROAD_Z_FAR  = reference_z + 800.0
    is_night = getattr(config, 'setting_time_of_day', 'Day') == "Night"

    grass_color = (0.05, 0.2, 0.08) if is_night else (0.18, 0.55, 0.18)

    glColor3f(*grass_color)
    glBegin(GL_QUADS)
    glVertex3f(-GROUND_HALF, 0.0, ROAD_Z_NEAR)
    glVertex3f(-ROAD_HALF,   0.0, ROAD_Z_NEAR)
    glVertex3f(-ROAD_HALF,   0.0, ROAD_Z_FAR)
    glVertex3f(-GROUND_HALF, 0.0, ROAD_Z_FAR)
    glEnd()

    glColor3f(*grass_color)
    glBegin(GL_QUADS)
    glVertex3f(ROAD_HALF,   0.0, ROAD_Z_NEAR)
    glVertex3f(GROUND_HALF, 0.0, ROAD_Z_NEAR)
    glVertex3f(GROUND_HALF, 0.0, ROAD_Z_FAR)
    glVertex3f(ROAD_HALF,   0.0, ROAD_Z_FAR)
    glEnd()


def draw_road():
    pz        = getattr(config, 'render_reference_z', config.car_pos[2])
    seg_start = math.floor(pz / ROAD_SEGMENT) -2
    white_w   = 3.0
    dash_len  = 20.0
    gap_len   = 20.0
    period    = dash_len + gap_len
    is_night  = getattr(config, 'setting_time_of_day', 'Day') == "Night"

    tarmac_color = (0.1, 0.1, 0.12) if is_night else (0.22, 0.22, 0.22)
    kerb_color   = (0.4, 0.4, 0.45) if is_night else (0.95, 0.95, 0.95)
    center_color = (0.6, 0.6, 0.0) if is_night else (1.0, 1.0, 0.0)
    dash_color   = (0.4, 0.4, 0.45) if is_night else (0.9, 0.9, 0.9)

    for s in range(seg_start, seg_start + NUM_SEGMENTS):
        z0 = s * ROAD_SEGMENT
        z1 = z0 + ROAD_SEGMENT

        glColor3f(*tarmac_color)
        glBegin(GL_QUADS)
        glVertex3f(-ROAD_HALF, 0.01, z0)
        glVertex3f( ROAD_HALF, 0.01, z0)
        glVertex3f( ROAD_HALF, 0.01, z1)
        glVertex3f(-ROAD_HALF, 0.01, z1)
        glEnd()

        glColor3f(*kerb_color)
        glBegin(GL_QUADS)
        glVertex3f(-ROAD_HALF,       0.02, z0)
        glVertex3f(-ROAD_HALF + 4.0, 0.02, z0)
        glVertex3f(-ROAD_HALF + 4.0, 0.02, z1)
        glVertex3f(-ROAD_HALF,       0.02, z1)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(ROAD_HALF - 4.0, 0.02, z0)
        glVertex3f(ROAD_HALF,       0.02, z0)
        glVertex3f(ROAD_HALF,       0.02, z1)
        glVertex3f(ROAD_HALF - 4.0, 0.02, z1)
        glEnd()

    first_dash = math.floor(pz / period) -5
    for d in range(first_dash, first_dash + 60):
        dz0 = d * period
        dz1 = dz0 + dash_len
        for lane_x in [0.0, -LANE_OFFSET, LANE_OFFSET]:
            glColor3f(*center_color) if lane_x == 0.0 else glColor3f(*dash_color)
            glBegin(GL_QUADS)
            glVertex3f(lane_x - white_w, 0.03, dz0)
            glVertex3f(lane_x + white_w, 0.03, dz0)
            glVertex3f(lane_x + white_w, 0.03, dz1)
            glVertex3f(lane_x - white_w, 0.03, dz1)
            glEnd()


def draw_environment():
    ENV_SPAN = NUM_SEGMENTS * ROAD_SEGMENT
    pz = getattr(config, 'render_reference_z', config.car_pos[2])
    base_offset = math.floor(pz / ENV_SPAN) * ENV_SPAN
    is_night = getattr(config, 'setting_time_of_day', 'Day') == "Night"

    # Application of Sun and Moon 
    # Y value lowered so it fits inside the camera's downward tilt!
    # This way we can have a visible sun/moon in both chase and hood cam views without needing to change the camera angle.

    glPushMatrix()
    celestial_z = pz + 3200.0  
    glTranslatef(300.0, 300.0, celestial_z) 
    if is_night:
        glColor3f(0.9, 0.9, 0.8) # Moon
        gluSphere(gluNewQuadric(), 150.0, 20, 20)
    else:
        glColor3f(1.0, 0.9, 0.2) # Sun
        gluSphere(gluNewQuadric(), 150.0, 20, 20)
    glPopMatrix()


    for (bx, bz, bw, bh, bd, r, g, b) in env_buildings:
        world_z = bz + base_offset
        if world_z < pz - 300 or world_z > pz + 700:
            world_z += ENV_SPAN if world_z < pz - 300 else -ENV_SPAN
        if abs(world_z - pz) > 750:
            continue

        glPushMatrix()
        glTranslatef(bx, 0.0, world_z)
        
        # Apply night darkening to building base color
        if is_night:
            glColor3f(r * 0.2, g * 0.2, b * 0.3)
        else:
            glColor3f(r, g, b)
            
        glTranslatef(0.0, bh / 2.0, 0.0)
        glScalef(bw, bh, bd)
        glutSolidCube(1.0)
        glPopMatrix()

        # Windows (Moved to the -Z face so the oncoming player sees them.)
        glPushMatrix()
        glTranslatef(bx, bh * 0.5, world_z - bd * 0.52) 
        
        if is_night:
            glColor3f(1.0, 0.9, 0.2) # Bright glowing yellow windows
        else:
            glColor3f(0.3, 0.5, 0.6) # Darker daytime glass

        rows = max(1, int(bh / 20))
        cols = max(1, int(bw / 12))
        for row in range(rows):
            for col in range(cols):
                wy = -bh * 0.4 + row * (bh * 0.8 / max(rows, 1))
                wx =  -bw * 0.35 + col * (bw * 0.7 / max(cols, 1))
                glPushMatrix()
                glTranslatef(wx, wy, 0)
                glScalef(4.0, 4.0, 0.5)
                glutSolidCube(1.0)
                glPopMatrix()
        glPopMatrix()

    for (tx, tz, r, g, b) in env_trees:
        world_z = tz + base_offset
        if world_z < pz - 300 or world_z > pz + 700:
            world_z += ENV_SPAN if world_z < pz - 300 else -ENV_SPAN
        if abs(world_z - pz) > 750:
            continue

        # Trunk is a tapered cylinder. A simple cone-shaped tree.
        glPushMatrix()
        glTranslatef(tx, 0.0, world_z)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        glTranslatef(0.0, 0.0, -7.0)
        if is_night:
            glColor3f(0.15, 0.08, 0.02)
        else:
            glColor3f(0.45, 0.27, 0.07)
        gluCylinder(gluNewQuadric(), 2.5, 1.5, 14.0, 8, 4)
        glPopMatrix()

        # Foliage is a flattened sphere. Visible foliage even in the top-down chase cam without needing to change the camera angle.
        glPushMatrix()
        glTranslatef(tx, 18.0, world_z)
        if is_night:
            glColor3f(r * 0.3, g * 0.3, b * 0.4)
        else:
            glColor3f(r, g, b)
        gluSphere(gluNewQuadric(), 12.0, 8, 8)
        glPopMatrix()


def draw_staging_lights():
    remaining = 3.0 - (time.time() - config.race_start_time)
    stages = [2.0, 1.33, 0.66, 0.0]
    colors = [(1.0, 0.6, 0.0)] * 3 + [(0.1, 1.0, 0.1)]
    for i, threshold in enumerate(stages):
        glPushMatrix()
        glTranslatef(-ROAD_HALF - 15.0, 20.0 + i * 8.0, 20.0)
        glColor3f(*colors[i]) if remaining <= threshold else glColor3f(0.15, 0.15, 0.15)
        gluSphere(gluNewQuadric(), 3.0, 8, 8)
        glPopMatrix()


def draw_sky():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(-1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    is_night = getattr(config, 'setting_time_of_day', 'Day') == "Night"

    if is_night:
        # Night sky gradient
        glBegin(GL_QUADS)
        glColor3f(0.02, 0.02, 0.08)   
        glVertex3f(-1,  1, 0)
        glVertex3f( 1,  1, 0)
        glColor3f(0.1, 0.1, 0.2)   
        glVertex3f( 1, -1, 0)
        glVertex3f(-1, -1, 0)
        glEnd()
    else:
        # Day sky gradient
        glBegin(GL_QUADS)
        glColor3f(0.1, 0.4, 0.8)   
        glVertex3f(-1,  1, 0)
        glVertex3f( 1,  1, 0)
        glColor3f(0.6, 0.8, 1.0)   
        glVertex3f( 1, -1, 0)
        glVertex3f(-1, -1, 0)
        glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def update_ai():
    for ai in config.ai_cars:
        ai["lane_change_timer"] -= 0.016
        if ai["lane_change_timer"] <= 0:
            ai["lane"] = random.choice([-LANE_OFFSET, 0.0, LANE_OFFSET])
            ai["lane_change_timer"] = random.uniform(3.0, 7.0)

        # Smoothly approach target lane X. This creates a more natural drifting motion instead of instant lane snapping.
        target_x = ai["lane"]
        dx = target_x - ai["pos"][0]
        ai["pos"][0] += dx * 0.04

        # Accelerate toward max speed using their specific, slower acceleration
        ai["velocity_z"] = min(ai["velocity_z"] + ai["accel"], ai["max_speed"])
        ai["pos"][2] += ai["velocity_z"]
        ai["facing_angle"] = 0.0   # AI always faces forward (+Z)


#  CAMERA AND VIEW

def apply_camera(car_pos=None, facing_angle=None, camera_mode=None,
                 cam_height=None, cam_swing=None, aspect=1.25):
    """Apply an independent camera for either human player."""
    if car_pos is None:
        car_pos = config.car_pos
    if facing_angle is None:
        facing_angle = config.car_facing_angle
    if camera_mode is None:
        camera_mode = config.current_camera
    if cam_height is None:
        cam_height = config.cam_height_offset
    if cam_swing is None:
        cam_swing = config.cam_swing_angle
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(80, aspect, 0.5, 4000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    rad_facing = math.radians(facing_angle)
    facing_dx  = math.sin(rad_facing)
    facing_dz  = math.cos(rad_facing)

    if camera_mode == config.CAM_CHASE:
        cam_dist   = 80.0
        swing_rad  = math.radians(cam_swing)
        cam_x = car_pos[0] - math.sin(rad_facing + swing_rad) * cam_dist
        cam_z = car_pos[2] - math.cos(rad_facing + swing_rad) * cam_dist
        cam_y = car_pos[1] + cam_height
        gluLookAt(cam_x, cam_y, cam_z,
                  car_pos[0], car_pos[1] + 5, car_pos[2],
                  0, 1, 0)
    else:  # Hood cam
        cam_x = car_pos[0] + facing_dx * 10.0
        cam_y = car_pos[1] + 15.0
        cam_z = car_pos[2] + facing_dz * 10.0
        gluLookAt(cam_x, cam_y, cam_z,
                  cam_x + facing_dx * 200.0, cam_y, cam_z + facing_dz * 200.0, 0, 1, 0)



#  CAR MODEL

def draw_car(car_type="player1", x=0, y=0, z=0, angle=0, color=None):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 1, 0)

    is_human = car_type in ("player1", "player2")
    if is_human:
        if car_type == "player2":
            wheel, velocity, keys, gas, brake = (config.player2_current_wheel_angle,
                config.player2_velocity, config.player2_keys_pressed, b'i', b'k')
        else:
            wheel, velocity, keys, gas, brake = (config.current_wheel_angle,
                config.car_velocity, config.keys_pressed, b'w', b's')
        roll = wheel * 0.3
        speed = math.sqrt(velocity[0]**2 + velocity[2]**2)
        pitch = -speed * 0.5 if keys[gas] else (speed * 0.3 if keys[brake] else 0)
        glRotatef(pitch, 1, 0, 0)
        glRotatef(roll,  0, 0, 1)

    # Body (Chassis)
    body_color = color or ((0.85, 0.1, 0.1) if car_type == "player1" else
                           (0.1, 0.75, 0.2) if car_type == "player2" else (0.1, 0.2, 0.85))
    glColor3f(*body_color)
    glPushMatrix()
    glTranslatef(0, 7, 0)
    glScalef(1.1, 0.35, 2.2) 
    glutSolidCube(20)
    glPopMatrix()

    # Cabin (roof)
    glColor3f(body_color[0] * 0.7, body_color[1] * 0.7, body_color[2] * 0.7)
    glPushMatrix()
    glTranslatef(0, 14, -2)
    glScalef(0.8, 0.35, 1.0)
    glutSolidCube(20)
    glPopMatrix()
    
    # Glass (Windshield, Rear Window, Side Windows)
    glColor3f(0.5, 0.8, 0.9) 
    
    # Windshield (Front)
    glPushMatrix()
    glTranslatef(0, 14, 8) 
    glRotatef(20, 1, 0, 0) 
    glScalef(0.78, 0.32, 0.05)
    glutSolidCube(20)
    glPopMatrix()
    
    # Rear Window
    glPushMatrix()
    glTranslatef(0, 14, -12) 
    glRotatef(-15, 1, 0, 0)
    glScalef(0.78, 0.32, 0.05)
    glutSolidCube(20)
    glPopMatrix()
    
    # Side Windows 
    glPushMatrix()
    glTranslatef(-8.1, 14, -2) 
    glScalef(0.05, 0.32, 0.95)
    glutSolidCube(20)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(8.1, 14, -2)
    glScalef(0.05, 0.32, 0.95)
    glutSolidCube(20)
    glPopMatrix()

    # Wheels (Lowered and tucked to fix the top-view glitch where the wheels would be hidden inside the body)
    wheel_positions = [(-11.0, 3.5, 12), (11.0, 3.5, 12), (-11.0, 3.5, -12), (11.0, 3.5, -12)]
    for i, (wx, wy, wz) in enumerate(wheel_positions):
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        if is_human and i < 2:
            glRotatef(wheel, 0, 1, 0)
        
        # Tire Tread (Cylinder)
        glColor3f(0.1, 0.1, 0.1) 
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        glTranslatef(0, 0, -2.5) 
        gluCylinder(gluNewQuadric(), 3.5, 3.5, 5.0, 12, 4)
        glPopMatrix()

        # Tire Wall (Flattened Sphere)
        glColor3f(0.15, 0.15, 0.15)
        glPushMatrix()
        glScalef(0.4, 1.0, 1.0) 
        gluSphere(gluNewQuadric(), 3.4, 12, 12)
        glPopMatrix()

        # Hubcap 
        glColor3f(0.7, 0.7, 0.7)
        glPushMatrix()
        side_dir = -1 if wx < 0 else 1
        glTranslatef(side_dir * 2.6, 0, 0)
        glScalef(0.3, 1.0, 1.0)
        gluSphere(gluNewQuadric(), 1.8, 10, 8)
        glPopMatrix()

        glPopMatrix()

    # Pulsing cyan exhaust makes the original boost immediately visible.
    boost_active = (config.player2_boost_active if car_type == 'player2'
                    else config.player1_boost_active) if is_human else False
    if boost_active:
        flame_length = 12.0 + abs(math.sin(time.time() * 18.0)) * 8.0
        for exhaust_x in (-6.0, 6.0):
            glPushMatrix()
            glTranslatef(exhaust_x, 5.0, -22.0)
            glRotatef(180.0, 1, 0, 0)
            glColor3f(0.1, 0.8, 1.0)
            gluCylinder(gluNewQuadric(), 2.4, 0.0, flame_length, 10, 2)
            glPopMatrix()

    glPopMatrix()



# Game PHYSICS engine

def update_boost_states():
    now = time.time()
    if config.player1_boost_active and now - config.player1_boost_start_time >= config.BOOST_DURATION:
        config.player1_boost_active = False
    if config.player2_boost_active and now - config.player2_boost_start_time >= config.BOOST_DURATION:
        config.player2_boost_active = False

def activate_boost(player_number):
    now = time.time()
    prefix = "player1" if player_number == 1 else "player2"
    if (not getattr(config, prefix + "_boost_active") and
            now - getattr(config, prefix + "_boost_last_used") >= config.BOOST_COOLDOWN):
        setattr(config, prefix + "_boost_active", True)
        setattr(config, prefix + "_boost_start_time", now)
        setattr(config, prefix + "_boost_last_used", now)

# ============================================================
# MULTIPLAYER PHYSICS
# ============================================================
def update_player_physics(pos, velocity, facing_angle, wheel_angle, keys,
                          gas_key, brake_key, left_key, right_key, boost_active, dt):
    target_wheel = config.MAX_WHEEL_ANGLE if keys[left_key] else (-config.MAX_WHEEL_ANGLE if keys[right_key] else 0.0)
    steering_lag = config.STEERING_LAG * (config.setting_sensitivity / 2.0)
    ease = 1.0 - math.exp(-steering_lag * dt)
    wheel_angle += (target_wheel - wheel_angle) * ease
    rad = math.radians(facing_angle)
    facing_dx, facing_dz = math.sin(rad), math.cos(rad)
    fwd_vel = velocity[0] * facing_dx + velocity[2] * facing_dz
    thrust = config.THRUST * (1.25 if boost_active else 1.0)
    if keys[gas_key]:
        force = config.BRAKE_FORCE * 2.0 if fwd_vel < -0.1 else thrust
        velocity[0] += facing_dx * force
        velocity[2] += facing_dz * force
    if keys[brake_key]:
        force = config.BRAKE_FORCE * 2.0 if fwd_vel > 0.1 else config.THRUST * 0.5
        velocity[0] -= facing_dx * force
        velocity[2] -= facing_dz * force
    velocity[0] *= config.FRICTION
    velocity[2] *= config.FRICTION
    speed = math.sqrt(velocity[0] ** 2 + velocity[2] ** 2)
    max_speed = config.MAX_SPEED * (config.BOOST_SPEED_MULTIPLIER if boost_active else 1.0)
    if speed > max_speed:
        ratio = max_speed / speed
        velocity[0] *= ratio
        velocity[2] *= ratio
        speed = max_speed
    if speed > 0.2:
        direction = 1.0 if fwd_vel >= 0 else -1.0
        facing_angle += wheel_angle * (speed / max_speed) * 0.18 * direction
        if abs(wheel_angle) > 5.0:
            velocity[0] *= 0.99
            velocity[2] *= 0.99
    pos[0] += velocity[0]
    pos[2] += velocity[2]
    pos[0] = max(-ROAD_HALF + 12.0, min(ROAD_HALF - 12.0, pos[0]))
    return facing_angle, wheel_angle

def update_physics(dt):
    if config.race_finished:
        return
    config.car_facing_angle, config.current_wheel_angle = update_player_physics(
        config.car_pos, config.car_velocity, config.car_facing_angle,
        config.current_wheel_angle, config.keys_pressed, b'w', b's', b'a', b'd',
        config.player1_boost_active, dt)
    config.score = max(config.score, int(config.car_pos[2] / 10))
    if config.setting_players == 2 and config.current_state == config.STATE_RACE:
        config.player2_facing_angle, config.player2_current_wheel_angle = update_player_physics(
            config.player2_pos, config.player2_velocity, config.player2_facing_angle,
            config.player2_current_wheel_angle, config.player2_keys_pressed,
            b'i', b'k', b'j', b'l', config.player2_boost_active, dt)
        config.player2_score = max(config.player2_score, int(config.player2_pos[2] / 10))

def check_collisions_and_laps():
    if config.race_finished:
        return

    def push_human(pos, velocity, other_pos, slowdown):
        dx, dz = pos[0] - other_pos[0], pos[2] - other_pos[2]
        dist = math.sqrt(dx ** 2 + dz ** 2)
        if dist < 18.0:
            if dist < 0.01:
                dx, dz, dist = 1.0, 0.0, 1.0
            velocity[0] *= slowdown
            velocity[2] *= slowdown
            pos[0] += dx / dist * 3.0
            pos[2] += dz / dist * 3.0
            return True
        return False

    def resolve_player_collision():
        """Resolve P1/P2 from one shared calculation so neither car is favored."""
        dx = config.car_pos[0] - config.player2_pos[0]
        dz = config.car_pos[2] - config.player2_pos[2]
        dist = math.sqrt(dx ** 2 + dz ** 2)
        hit_radius = 22.0
        if dist >= hit_radius:
            return

        # A fixed direction prevents division by zero if the cars overlap exactly.
        if dist < 0.01:
            dx, dz, dist = 1.0, 0.0, 1.0

        normal_x = dx / dist
        normal_z = dz / dist
        overlap = hit_radius - dist
        push_distance = overlap * 0.5 + 0.5

        config.car_pos[0] += normal_x * push_distance
        config.car_pos[2] += normal_z * push_distance
        config.player2_pos[0] -= normal_x * push_distance
        config.player2_pos[2] -= normal_z * push_distance

        # Remove the velocity component driving each car into the other car.
        relative_x = config.car_velocity[0] - config.player2_velocity[0]
        relative_z = config.car_velocity[2] - config.player2_velocity[2]
        closing_speed = relative_x * normal_x + relative_z * normal_z
        if closing_speed < 0.0:
            impulse = -closing_speed * 0.5
            config.car_velocity[0] += normal_x * impulse
            config.car_velocity[2] += normal_z * impulse
            config.player2_velocity[0] -= normal_x * impulse
            config.player2_velocity[2] -= normal_z * impulse

        config.car_velocity[0] *= 0.72
        config.car_velocity[2] *= 0.72
        config.player2_velocity[0] *= 0.72
        config.player2_velocity[2] *= 0.72

        # Keep the separation response inside the road boundaries.
        config.car_pos[0] = max(-ROAD_HALF + 12.0, min(ROAD_HALF - 12.0, config.car_pos[0]))
        config.player2_pos[0] = max(-ROAD_HALF + 12.0, min(ROAD_HALF - 12.0, config.player2_pos[0]))

    if config.setting_collisions:
        humans = [(config.car_pos, config.car_velocity)]
        if config.setting_players == 2 and config.current_state == config.STATE_RACE:
            humans.append((config.player2_pos, config.player2_velocity))
            resolve_player_collision()
        for pos, velocity in humans:
            for ai in config.ai_cars:
                push_human(pos, velocity, ai["pos"], 0.85)
            for npc in config.npc_cars:
                push_human(pos, velocity, npc["pos"], 0.55)

    # Lap / distance checkpoint for Race mode
    if config.current_state == config.STATE_RACE:
        lap_distance = 3000.0
        
        # Calculate current lap (Start at lap 1)
        config.current_lap = max(1, min(config.setting_laps, int(config.car_pos[2] / lap_distance) + 1))
        if config.setting_players == 2:
            config.player2_current_lap = max(1, min(config.setting_laps,
                int(config.player2_pos[2] / lap_distance) + 1))

        racers = [("Player 1", config.car_pos[2])]
        if config.setting_players == 2:
            racers.append(("Player 2", config.player2_pos[2]))
        racers.extend(("AI Racer " + str(i + 1), ai["pos"][2]) for i, ai in enumerate(config.ai_cars))
        finish_z = config.setting_laps * lap_distance
        winners = [r for r in racers if r[1] >= finish_z]
        if winners:
            ordered = sorted(racers, key=lambda item: item[1], reverse=True)
            config.race_finished = True
            config.winner = ordered[0][0]
            config.final_positions = {name: i + 1 for i, (name, z) in enumerate(ordered)}
            config.final_position = config.final_positions["Player 1"]



#  TEXT & UI

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_time_select_menu():
   
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    glColor3f(0.05, 0.05, 0.15)
    glVertex3f(0, 800, 0)
    glVertex3f(1000, 800, 0)
    glColor3f(0.10, 0.10, 0.35)
    glVertex3f(1000, 0, 0)
    glVertex3f(0, 0, 0)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_text(370, 550, "SELECT TIME OF DAY", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(360, 500, "W/S = navigate   ENTER = select")

    opts  = ["Day Mode", "Night Mode"]
    start_y  = 400
    for i, option in enumerate(opts):
        ypos = start_y - i * 50
        if i == getattr(config, 'current_time_selection', 0):
            draw_text(410, ypos, f">  {option}  <")
        else:
            draw_text(440, ypos, option)


def draw_main_menu():

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Sky gradient
    glBegin(GL_QUADS)
    glColor3f(0.05, 0.05, 0.15)
    glVertex3f(0, 800, 0)
    glVertex3f(1000, 800, 0)
    glColor3f(0.10, 0.10, 0.35)
    glVertex3f(1000, 0, 0)
    glVertex3f(0, 0, 0)
    glEnd()

    # Road strip at bottom. 
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0); glVertex3f(1000, 0, 0)
    glVertex3f(1000, 120, 0); glVertex3f(0, 120, 0)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_text(360, 680, "VECTOR VELOCITY", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(310, 640, "Endless Highway Racing  |  CSE 423 Group 01")
    draw_text(290, 600, "W/S = navigate menu   A/D = change value   ENTER = select")

    options  = get_menu_options()
    start_y  = 530
    for i, option in enumerate(options):
        ypos = start_y - i * 42
        if i == config.current_menu_selection:
            draw_text(370, ypos, f">  {option}  <")
            if i >= 2:
                draw_text(660, ypos, "[A / D]")
        else:
            draw_text(400, ypos, option)

    draw_text(250, 180, "PLAYER 1: W/S Gas/Brake  A/D Steer  E Boost  Q Camera")
    draw_text(250, 150, "PLAYER 2: I/K Gas/Brake  J/L Steer  O Boost  Y Camera")
    draw_text(250, 120, "GLOBAL: P Pause  M Main Menu (paused/finished)")
    draw_text(250, 90,  "Arrow Keys adjust the single-player camera")


def draw_tutorial_screen():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.04, 0.05, 0.12)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(1000, 0, 0)
    glVertex3f(1000, 800, 0)
    glVertex3f(0, 800, 0)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_text(405, 690, 'HOW TO PLAY', GLUT_BITMAP_TIMES_ROMAN_24)
    lines = [
        'W / S      Accelerate / Brake',
        'A / D      Steer',
        'E          Activate boost',
        'Q / RMB    Toggle camera',
        'P          Pause',
        'Arrow Keys Adjust camera',
        '',
        'In two-player races: I/K drive, J/L steer,',
        'O boosts, and Y toggles Player 2 camera.',
        '',
        'Press M to return to the menu.'
    ]
    y = 620
    for line in lines:
        draw_text(285, y, line)
        y -= 36


def draw_pause_menu():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    

    glColor3f(0.05, 0.05, 0.15)
    glBegin(GL_QUADS)
    glVertex3f(350, 300, 0)
    glVertex3f(650, 300, 0)
    glVertex3f(650, 500, 0)
    glVertex3f(350, 500, 0)
    glEnd()
    
    draw_text(445, 460, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(390, 410, "Press  'P'  to Resume")
    draw_text(390, 370, "Press  'M'  for Main Menu")

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def get_rank(name):
    racers = [("Player 1", config.car_pos[2])]
    if config.setting_players == 2 and config.current_state != config.STATE_FREE_ROAM:
        racers.append(("Player 2", config.player2_pos[2]))
    racers.extend(("AI Racer " + str(i + 1), ai["pos"][2]) for i, ai in enumerate(config.ai_cars))
    racers.sort(key=lambda item: item[1], reverse=True)
    return [item[0] for item in racers].index(name) + 1, len(racers)

def boost_label(player_number):
    prefix = "player1" if player_number == 1 else "player2"
    if getattr(config, prefix + "_boost_active"):
        return "BOOST ACTIVE!"
    remaining = config.BOOST_COOLDOWN - (time.time() - getattr(config, prefix + "_boost_last_used"))
    return "BOOST: READY" if remaining <= 0 else "BOOST: %.1fs" % remaining

def draw_hud(player_number=1):
    if player_number == 2:
        velocity, score, lap = config.player2_velocity, config.player2_score, config.player2_current_lap
        camera, player_name = config.player2_current_camera, "PLAYER 2"
    else:
        velocity, score, lap = config.car_velocity, config.score, config.current_lap
        camera, player_name = config.current_camera, "PLAYER 1"
    speed_val = math.sqrt(velocity[0]**2 + velocity[2]**2)
    speed_kmh = int(speed_val * 18)   # rough km/h scale
    draw_text(20, 780, player_name)
    draw_text(20, 40, f"Speed: {speed_kmh} km/h")
    draw_text(20, 70, f"Score: {score} m")
    draw_text(20, 100, boost_label(player_number))

    cam_label = "Chase Cam" if camera == config.CAM_CHASE else "Hood Cam"
    draw_text(840, 40, cam_label)

    if config.current_state == config.STATE_RACE:
        
        # POSITION CALCULATION: Determine player's current rank by comparing Z positions with AI cars.
        # Sort all cars by their Z coordinate (highest Z is 1st place)
        player_pos, total_racers = get_rank("Player " + str(player_number))
        
        # COUNTDOWN before race starts
        elapsed_total = time.time() - config.race_start_time
        if elapsed_total < 3.0:
            countdown_num = 3 - int(elapsed_total)
            draw_text(480, 450, str(countdown_num), GLUT_BITMAP_TIMES_ROMAN_24)
        elif elapsed_total < 4.0:
            draw_text(470, 450, "GO!", GLUT_BITMAP_TIMES_ROMAN_24)

        elapsed = f"{config.current_race_time:.1f}s" if config.current_race_time > 0 else "0.0s"
        
        # LAP AND POSITION DISPLAY
        draw_text(760, 780, f"Pos: {player_pos} / {total_racers}")
        draw_text(760, 750, f"Lap: {lap} / {config.setting_laps}")
        draw_text(840, 720, f"Time: {elapsed}")

        if config.race_finished:
            # Use the locked final position so it doesn't change after you stop. 
            # This way you can see your final placement even if the AI cars keep driving past you after the finish line.
            final_pos = config.final_positions.get("Player " + str(player_number), player_pos)
            
            #END MESSAGE after finishing race.
            draw_text(300, 500, "Winner: " + getattr(config, 'winner', 'Unknown'), GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(360, 470, player_name + " finished #" + str(final_pos))
                
            draw_text(390, 455, f"Final Time: {config.current_race_time:.1f}s")
            draw_text(360, 415, "Press 'M' for Main Menu")

    elif config.current_state == config.STATE_FREE_ROAM:
        draw_text(830, 750, "FREE ROAM")


#  MAIN GAME LOOP

def reset_race():
    config.last_update_time = time.time()
    config.car_pos           = [-18.0 if config.setting_players == 2 else 0.0, 0.0, 0.0]
    config.car_velocity      = [0.0, 0.0, 0.0]
    config.car_facing_angle  = 0.0
    config.current_wheel_angle = 0.0
    config.current_lap       = 1
    config.player_waypoint   = 0
    config.race_finished     = False
    config.score             = 0
    config.race_start_time   = time.time()
    config.cam_swing_angle   = 0.0
    config.cam_height_offset = 50.0
    config.current_camera    = config.CAM_CHASE
    config.player2_pos = [18.0, 0.0, 0.0]
    config.player2_velocity = [0.0, 0.0, 0.0]
    config.player2_facing_angle = 0.0
    config.player2_current_wheel_angle = 0.0
    config.player2_current_lap = 1
    config.player2_score = 0
    config.player2_current_camera = config.CAM_CHASE
    config.player2_cam_height_offset = 50.0
    config.player2_cam_swing_angle = 0.0
    config.player1_boost_active = False
    config.player2_boost_active = False
    config.player1_boost_last_used = -100.0
    config.player2_boost_last_used = -100.0
    config.final_positions = {}
    config.finish_order = []
    config.npc_cars = []
    for key in config.keys_pressed:
        config.keys_pressed[key] = False
        config.key_expiry[key] = 0.0
    for key in config.player2_keys_pressed:
        config.player2_keys_pressed[key] = False
        config.player2_key_expiry[key] = 0.0


def keyboardListener(key, x, y):
    # Safely initialize new Day/Night state variables if they don't exist
    if not hasattr(config, 'STATE_TIME_SELECT'):
        config.STATE_TIME_SELECT = 4
        config.current_time_selection = 0
        config.pending_game_state = config.STATE_RACE
        config.setting_time_of_day = "Day"

    key_lower = key.lower()

    if config.current_state == config.STATE_MENU:
        opts = get_menu_options()
        if key_lower == b'w':
            config.current_menu_selection = max(0, config.current_menu_selection - 1)
        elif key_lower == b's':
            config.current_menu_selection = min(len(opts) - 1, config.current_menu_selection + 1)
        elif key_lower in (b'a', b'd'):
            direction = -1 if key_lower == b'a' else 1
            sel = config.current_menu_selection
            
            if sel == 3:
                config.setting_players = max(1, min(2, config.setting_players + direction))
            elif sel == 4:
                config.setting_laps = max(1, min(10, config.setting_laps + direction))
            elif sel == 5:
                diffs = ["Easy", "Normal", "Hard"]
                idx = diffs.index(config.setting_difficulty)
                config.setting_difficulty = diffs[(idx + direction) % 3]
            elif sel == 6:
                config.setting_collisions = not config.setting_collisions
            elif sel == 7:
                config.setting_sensitivity = max(1.0, min(4.0, config.setting_sensitivity + direction * 0.5))
        
        elif key == b'\r':
            # Instead of starting the game directly, go to Time Selection
            if config.current_menu_selection == 0:
                config.current_state = config.STATE_TUTORIAL
            elif config.current_menu_selection == 1:
                config.pending_game_state = config.STATE_RACE
                config.current_state = config.STATE_TIME_SELECT
                config.current_time_selection = 0
            elif config.current_menu_selection == 2:
                config.pending_game_state = config.STATE_FREE_ROAM
                config.current_state = config.STATE_TIME_SELECT
                config.current_time_selection = 0

    elif config.current_state == config.STATE_TUTORIAL:
        if key_lower == b'm':
            config.current_state = config.STATE_MENU

    elif config.current_state == config.STATE_TIME_SELECT:
        if key_lower == b'w':
            config.current_time_selection = 0
        elif key_lower == b's':
            config.current_time_selection = 1
        elif key == b'\r':
            # Set the time of day and finalize the game launch
            config.setting_time_of_day = "Day" if config.current_time_selection == 0 else "Night"
            reset_race()
            config.current_state = config.pending_game_state
            if config.current_state == config.STATE_RACE:
                init_ai(config.setting_opponents, config.setting_difficulty)
                init_npc()
            else:
                config.ai_cars = []
                init_npc()

    elif config.current_state in [config.STATE_RACE, config.STATE_FREE_ROAM]:
        if key_lower in config.keys_pressed:
            now = time.time()
            if key_lower == b'w':
                config.keys_pressed[b'w'] = True
                config.keys_pressed[b's'] = False
            elif key_lower == b's':
                config.keys_pressed[b's'] = True
                config.keys_pressed[b'w'] = False
            else:
                config.keys_pressed[key_lower] = True
                config.key_expiry[key_lower] = now + config.INPUT_STEER_SECONDS
        if config.setting_players == 2 and config.current_state == config.STATE_RACE and key_lower in config.player2_keys_pressed:
            now = time.time()
            if key_lower == b'i':
                config.player2_keys_pressed[b'i'] = True
                config.player2_keys_pressed[b'k'] = False
            elif key_lower == b'k':
                config.player2_keys_pressed[b'k'] = True
                config.player2_keys_pressed[b'i'] = False
            else:
                config.player2_keys_pressed[key_lower] = True
                config.player2_key_expiry[key_lower] = now + config.INPUT_STEER_SECONDS
        if key_lower == b'e':
            activate_boost(1)
        elif key_lower == b'o' and config.setting_players == 2 and config.current_state == config.STATE_RACE:
            activate_boost(2)
        elif key_lower == b'q':
            config.current_camera = config.CAM_HOOD if config.current_camera == config.CAM_CHASE else config.CAM_CHASE
        elif key_lower == b'y' and config.setting_players == 2 and config.current_state == config.STATE_RACE:
            config.player2_current_camera = config.CAM_HOOD if config.player2_current_camera == config.CAM_CHASE else config.CAM_CHASE
        if key_lower == b'p':
            config.previous_state = config.current_state
            config.current_state = config.STATE_PAUSED
        if config.race_finished and key_lower == b'm':
            config.current_state = config.STATE_MENU

    elif config.current_state == config.STATE_PAUSED:
        if key_lower == b'p':
            config.current_state = config.previous_state
        elif key_lower == b'm':
            config.current_state = config.STATE_MENU

    glutPostRedisplay()


def update_key_states():
    # Key-up callbacks release steering; timer expiry caused held input to flicker.
    return
    """Expire steering keys after keyboard-repeat events stop arriving."""
    now = time.time()
    for key in (b'a', b'd'):
        if now >= config.key_expiry[key]:
            config.keys_pressed[key] = False
    for key in (b'j', b'l'):
        if now >= config.player2_key_expiry[key]:
            config.player2_keys_pressed[key] = False


def is_key_pressed(letter):
    """Return True while a letter key is physically held down on Windows."""
    key = letter.lower().encode('ascii')
    return config.keys_pressed.get(key, config.player2_keys_pressed.get(key, False))


def keyboardUpListener(key, x, y):
    key_lower = key.lower()
    if key_lower in config.keys_pressed:
        config.keys_pressed[key_lower] = False
    if key_lower in config.player2_keys_pressed:
        config.player2_keys_pressed[key_lower] = False


def update_direction_keys():
    """Read acceleration and brake keys without an unsupported GLUT key-up callback."""
    config.keys_pressed[b'w'] = is_key_pressed('w')
    config.keys_pressed[b's'] = is_key_pressed('s')

    if config.setting_players == 2 and config.current_state == config.STATE_RACE:
        config.player2_keys_pressed[b'i'] = is_key_pressed('i')
        config.player2_keys_pressed[b'k'] = is_key_pressed('k')
    else:
        config.player2_keys_pressed[b'i'] = False
        config.player2_keys_pressed[b'k'] = False


def specialKeyListener(key, x, y):
    if config.current_state in [config.STATE_RACE, config.STATE_FREE_ROAM]:
        if key == GLUT_KEY_UP:
            config.cam_height_offset += 3.0
        elif key == GLUT_KEY_DOWN:
            config.cam_height_offset = max(10.0, config.cam_height_offset - 3.0)
        elif key == GLUT_KEY_LEFT:
            config.cam_swing_angle += 3.0
        elif key == GLUT_KEY_RIGHT:
            config.cam_swing_angle -= 3.0
    glutPostRedisplay()


def mouseListener(button, state, x, y):
    if config.current_state in [config.STATE_RACE, config.STATE_FREE_ROAM]:
        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            config.current_camera = (config.CAM_HOOD
                                     if config.current_camera == config.CAM_CHASE
                                     else config.CAM_CHASE)
    glutPostRedisplay()


def idle():
    if config.current_state in [config.STATE_RACE, config.STATE_FREE_ROAM]:
        now = time.time()
        dt = min(0.1, max(0.0, now - config.last_update_time))
        config.last_update_time = now
        update_direction_keys()
        elapsed_total = time.time() - config.race_start_time
        
        # COUNTDOWN LOGIC: For the first 3 seconds of the race, the timer is frozen and a countdown is displayed. 
        if config.current_state == config.STATE_RACE and elapsed_total < 3.0:
            config.current_race_time = 0.0 # Race timer doesn't start yet
            glutPostRedisplay()
            return # Freeze the game logic during countdown
            
        if not config.race_finished:
            if config.current_state == config.STATE_RACE:
                config.current_race_time = elapsed_total - 3.0 # Shift timer so it starts at 0
            else:
                config.current_race_time = elapsed_total
                
        update_boost_states()
        update_physics(dt)
        update_ai()
        update_npc()
        check_collisions_and_laps()
        update_key_states()
        glutPostRedisplay()
def draw_lap_lines():
    lap_distance = 3000.0
    
    # Draw the start line and all lap finish lines
    for lap in range(config.setting_laps + 1):
        z_pos = lap * lap_distance
        
        # Only draw if it's close to the player to save rendering performance
        reference_z = getattr(config, 'render_reference_z', config.car_pos[2])
        if abs(reference_z - z_pos) < 1000:
            strip_width = 15.0
            
            # White base line. 
            glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glVertex3f(-ROAD_HALF, 0.04, z_pos)
            glVertex3f(ROAD_HALF, 0.04, z_pos)
            glVertex3f(ROAD_HALF, 0.04, z_pos + strip_width)
            glVertex3f(-ROAD_HALF, 0.04, z_pos + strip_width)
            glEnd()
            
            # Black checkered squares. 
            glBegin(GL_QUADS)
            num_squares = 12
            sq_width = (ROAD_HALF * 2) / num_squares
            for i in range(num_squares):
                sx = -ROAD_HALF + i * sq_width
                if i % 2 == 0: # Front row squares
                    glVertex3f(sx, 0.05, z_pos)
                    glVertex3f(sx + sq_width, 0.05, z_pos)
                    glVertex3f(sx + sq_width, 0.05, z_pos + strip_width/2)
                    glVertex3f(sx, 0.05, z_pos + strip_width/2)
                    
                else: # Back row squares
                    glVertex3f(sx, 0.05, z_pos + strip_width/2)
                    glVertex3f(sx + sq_width, 0.05, z_pos + strip_width/2)
                    glVertex3f(sx + sq_width, 0.05, z_pos + strip_width)
                    glVertex3f(sx, 0.05, z_pos + strip_width)
            glEnd()

def draw_game_world():
    draw_ground_plane()
    draw_road()
    draw_lap_lines()
    draw_environment()
    if config.current_state == config.STATE_RACE and time.time() - config.race_start_time < 3.2:
        draw_staging_lights()
    draw_car("player1", config.car_pos[0], config.car_pos[1], config.car_pos[2], config.car_facing_angle)
    if config.setting_players == 2 and config.current_state != config.STATE_FREE_ROAM:
        draw_car("player2", config.player2_pos[0], config.player2_pos[1],
                 config.player2_pos[2], config.player2_facing_angle)
    for ai in config.ai_cars:
        draw_car("ai", ai["pos"][0], ai["pos"][1], ai["pos"][2], ai["facing_angle"])
    for npc in config.npc_cars:
        draw_car("npc", npc["pos"][0], npc["pos"][1], npc["pos"][2], 0.0, npc["color"])

def render_player_view(player_number, viewport_x, viewport_width):
    glViewport(viewport_x, 0, viewport_width, config.window_height)
    glClear(GL_DEPTH_BUFFER_BIT)
    if player_number == 2:
        pos, angle = config.player2_pos, config.player2_facing_angle
        camera = config.player2_current_camera
        height, swing = config.player2_cam_height_offset, config.player2_cam_swing_angle
    else:
        pos, angle = config.car_pos, config.car_facing_angle
        camera = config.current_camera
        height, swing = config.cam_height_offset, config.cam_swing_angle
    config.render_reference_z = pos[2]
    draw_sky()
    apply_camera(pos, angle, camera, height, swing, viewport_width / float(config.window_height))
    draw_game_world()
    if config.current_state != config.STATE_PAUSED:
        draw_hud(player_number)

def showScreen():
   
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    STATE_TIME_SELECT = getattr(config, 'STATE_TIME_SELECT', 4)

    if config.current_state == config.STATE_MENU:
        draw_main_menu()

    elif config.current_state == config.STATE_TUTORIAL:
        draw_tutorial_screen()
        
    elif config.current_state == STATE_TIME_SELECT:
        draw_time_select_menu()

    elif config.current_state in [config.STATE_RACE,
                                   config.STATE_FREE_ROAM,
                                   config.STATE_PAUSED]:
        two_player_view = (config.setting_players == 2 and
            (config.current_state == config.STATE_RACE or
             (config.current_state == config.STATE_PAUSED and config.previous_state == config.STATE_RACE)))
        if two_player_view:
            half_width = config.window_width // 2
            render_player_view(1, 0, half_width)
            render_player_view(2, half_width, config.window_width - half_width)
        else:
            render_player_view(1, 0, config.window_width)
        glViewport(0, 0, config.window_width, config.window_height)
        if hasattr(config, 'render_reference_z'):
            del config.render_reference_z
        if config.current_state == config.STATE_PAUSED:
            draw_pause_menu()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Vector Velocity  |  CSE 423")

    generate_env_objects()

    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)

    glutMainLoop()


if __name__ == "__main__":
    main()
