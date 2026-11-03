import pygame
import math
import sys

# ---------------------------------------------------------
# 1. INITIALIZATION & STYLING
# ---------------------------------------------------------
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TinyML Autonomous Drone Obstacle Avoidance Simulation")
clock = pygame.time.Clock()

COLOR_BG = (228, 233, 237)          # Light Floor Grid
COLOR_GRID = (210, 216, 222)        # Floor Tile Lines
COLOR_WALL_FILL = (85, 95, 105)     # Dark Slate Furniture
COLOR_WALL_BORDER = (40, 48, 55)   # Border
COLOR_WALL_TOP = (120, 130, 140)    # Top Highlight

COLOR_HUD_BG = (20, 24, 28)         # Dark Terminal HUD
COLOR_HUD_BORDER = (200, 205, 210)  
COLOR_RAY_BLUE = (30, 120, 225)     # Side Rays
COLOR_RAY_GREEN = (46, 204, 113)    # Front Ray
COLOR_RAY_HIT = (235, 60, 50)       # Red Hit Point

COLOR_TEXT_WHITE = (240, 245, 250)
COLOR_TEXT_GREEN = (46, 204, 113)
COLOR_TEXT_CYAN = (80, 180, 240)

font_hud = pygame.font.SysFont("Courier", 13, bold=True)
font_label = pygame.font.SysFont("Arial", 12, bold=True)

# ---------------------------------------------------------
# 2. DRONE CLASS
# ---------------------------------------------------------
class Drone:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.angle = -30.0  # Slightly facing upward to start turning smoothly
        self.speed = 1.5
        self.sensor_angles = [-90, -45, 0, 45, 90]
        self.sensor_distances = [0.0] * 5
        self.hit_points = [(0, 0)] * 5
        self.last_action = "Move Straight"
        self.action_class = 0

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        
        # Rotated Drone Body Visual
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # 4 Rotors relative offset
        offsets = [(-16, -16), (16, -16), (-16, 16), (16, 16)]
        
        # Draw Frame Cross Arms
        pygame.draw.circle(surface, (40, 45, 50), (cx, cy), 12)
        for rx, ry in offsets:
            # Rotate points based on drone angle
            rot_x = cx + int(rx * cos_a - ry * sin_a)
            rot_y = cy + int(rx * sin_a + ry * cos_a)
            
            # Draw Arm
            pygame.draw.line(surface, (30, 30, 30), (cx, cy), (rot_x, rot_y), 3)
            # Draw Rotor Blades
            pygame.draw.circle(surface, (200, 205, 210), (rot_x, rot_y), 9)
            pygame.draw.circle(surface, (30, 35, 40), (rot_x, rot_y), 9, 2)
            pygame.draw.circle(surface, (100, 100, 100), (rot_x, rot_y), 3)

        # Center Red Nose / Front Indicator
        front_x = cx + int(18 * cos_a)
        front_y = cy + int(18 * sin_a)
        pygame.draw.circle(surface, (231, 76, 60), (front_x, front_y), 4)

# ---------------------------------------------------------
# 3. MAP ENVIRONMENT (Fixed Coordinates)
# ---------------------------------------------------------
walls = [
    pygame.Rect(0, 0, WIDTH, 18),
    pygame.Rect(0, 0, 18, HEIGHT),
    pygame.Rect(0, HEIGHT - 18, WIDTH, 18),
    pygame.Rect(WIDTH - 18, 0, 18, HEIGHT),
    
    pygame.Rect(440, 90, 350, 60),
    pygame.Rect(915, 135, 200, 250),
    pygame.Rect(440, 245, 250, 40),
    pygame.Rect(190, 395, 150, 280),
    pygame.Rect(440, 395, 45, 260),
    pygame.Rect(565, 490, 300, 45),
    pygame.Rect(940, 490, 170, 160),
]

# Plant locations fixed to open floor areas (Not inside walls)
plants = [(400, 120), (380, 520), (890, 430)]

# ---------------------------------------------------------
# 4. RAYCASTING & MODEL LOGIC
# ---------------------------------------------------------
def cast_ray(drone_x, drone_y, angle, max_range=320):
    rad = math.radians(angle)
    dx = math.cos(rad)
    dy = math.sin(rad)
    
    for step in range(1, max_range):
        px = drone_x + dx * step
        py = drone_y + dy * step
        point_x, point_y = int(px), int(py)
        for wall in walls:
            if wall.collidepoint(point_x, point_y):
                distance_m = round(step / 50.0, 1)
                return distance_m, (px, py)
                
    px = drone_x + dx * max_range
    py = drone_y + dy * max_range
    return round(max_range / 50.0, 1), (px, py)

def predict_action(distances):
    dL90, dL45, dFront, dR45, dR90 = distances
    
    if dFront <= 0.9997:
        if dL45 <= 4.7937:
            if dR90 <= 4.8878:
                return "Turn Left", 1
            else:
                return "Turn Right", 2
        else:
            if dL45 <= 0.7997:
                return "Turn Right", 2
            else:
                return "Turn Left", 1
    elif dR45 <= 0.7997:
        return "Turn Left", 1
    else:
        return "Move Straight", 0

# ---------------------------------------------------------
# 5. MAIN EXECUTION
# ---------------------------------------------------------
# Spawn Drone safely in the open hallway area
drone = Drone(700, 350)

running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    sensor_names = ["dL90", "dL45", "dFront", "dR45", "dR90"]
    for i, rel_angle in enumerate(drone.sensor_angles):
        abs_angle = drone.angle + rel_angle
        dist, hit_pt = cast_ray(drone.x, drone.y, abs_angle)
        drone.sensor_distances[i] = dist
        drone.hit_points[i] = hit_pt

    # Execute Steering Logic
    drone.last_action, drone.action_class = predict_action(drone.sensor_distances)
    if drone.action_class == 1:
        drone.angle -= 2.0
    elif drone.action_class == 2:
        drone.angle += 2.0
    
    # Boundary Collision Protection (Keep moving inside room)
    next_x = drone.x + drone.speed * math.cos(math.radians(drone.angle))
    next_y = drone.y + drone.speed * math.sin(math.radians(drone.angle))
    
    # Check simple collision before advancing
    collided = False
    for wall in walls:
        if wall.collidepoint(int(next_x), int(next_y)):
            collided = True
            break
            
    if not collided:
        drone.x = next_x
        drone.y = next_y
    else:
        drone.angle += 15.0  # Recovery turn if stuck near wall

    # Render Frame
    screen.fill(COLOR_BG)

    # Tiles
    for x in range(0, WIDTH, 35):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 35):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (WIDTH, y))

    # Furniture
    for wall in walls:
        pygame.draw.rect(screen, COLOR_WALL_FILL, wall)
        pygame.draw.rect(screen, COLOR_WALL_BORDER, wall, width=3)
        pygame.draw.rect(screen, COLOR_WALL_TOP, (wall.x + 3, wall.y + 3, wall.width - 6, 4))

    # Decorative Plant Props
    for px, py in plants:
        pygame.draw.circle(screen, (34, 139, 34), (px, py), 13)
        pygame.draw.circle(screen, (0, 100, 0), (px, py), 13, 2)
        pygame.draw.circle(screen, (46, 204, 113), (px, py), 5)

    # Rays & Sensor Labels
    for i in range(5):
        hit_x, hit_y = drone.hit_points[i]
        ray_color = COLOR_RAY_GREEN if i == 2 else COLOR_RAY_BLUE
        
        pygame.draw.line(screen, ray_color, (int(drone.x), int(drone.y)), (int(hit_x), int(hit_y)), 2)
        pygame.draw.circle(screen, COLOR_RAY_HIT, (int(hit_x), int(hit_y)), 4)
        
        lbl = font_label.render(f"{sensor_names[i]}: {drone.sensor_distances[i]}m", True, (20, 20, 20))
        screen.blit(lbl, (int(hit_x) + 6, int(hit_y) - 8))

    # Render Drone ON TOP
    drone.draw(screen)

    # HUD Terminal Overlay
    hud_bg = pygame.Surface((350, 210))
    hud_bg.fill(COLOR_HUD_BG)
    screen.blit(hud_bg, (15, 15))
    pygame.draw.rect(screen, COLOR_HUD_BORDER, (15, 15, 350, 210), width=2)

    hud_text = [
        ("TinyML Drone Simulation v1.0", COLOR_TEXT_WHITE),
        ("----------------------------------", COLOR_TEXT_WHITE),
        ("Status: Navigating", COLOR_TEXT_GREEN),
        ("Active Model: `tinyml_model.h`", COLOR_TEXT_CYAN),
        (f"Prediction: [{drone.last_action}] -> [Class {drone.action_class}]", COLOR_TEXT_WHITE),
        ("Sensor Array: 5-Directional", COLOR_TEXT_WHITE),
        ("Avg Latency: 1.2µs", COLOR_TEXT_GREEN),
        ("Memory: 0.5KB Flash | 52B RAM", COLOR_TEXT_GREEN),
        ("Clock: 84MHz (STM32F401)", COLOR_TEXT_CYAN),
    ]

    for idx, (txt, col) in enumerate(hud_text):
        txt_render = font_hud.render(txt, True, col)
        screen.blit(txt_render, (25, 25 + (idx * 20)))

    pygame.display.flip()

pygame.quit()
sys.exit()