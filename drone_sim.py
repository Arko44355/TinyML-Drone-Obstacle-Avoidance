import pygame
import math
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# 1. Train Lightweight Model for Real-time Control
df = pd.read_csv('drone_sensor_dataset.csv')
X = df.drop(columns=['action'])
y = df['action']
clf = DecisionTreeClassifier(max_depth=5, random_state=42)
clf.fit(X, y)

# 2. Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TinyML Autonomous Drone Obstacle Avoidance Simulation")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (15, 15, 20)
RED = (235, 64, 52)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)

# Obstacles Setup (Walls & Pillars)
obstacles = [
    pygame.Rect(150, 150, 100, 100),
    pygame.Rect(450, 100, 120, 180),
    pygame.Rect(250, 380, 200, 80),
    pygame.Rect(550, 350, 100, 120),
    pygame.Rect(50, 450, 120, 80)
]

# Drone State
drone_x, drone_y = 100.0, 100.0
drone_angle = 0.0 # in degrees
speed = 2.5
sensor_angles = [-90, -45, 0, 45, 90] # Left90, Left45, Front, Right45, Right90
MAX_SENSOR_DIST = 200.0 # pixels (~5 meters mapped)

def cast_ray(x, y, angle, obstacles):
    rad = math.radians(angle)
    dx = math.cos(rad)
    dy = math.sin(rad)
    
    for dist in range(1, int(MAX_SENSOR_DIST)):
        tx = x + dx * dist
        ty = y + dy * dist
        
        # Check boundary collision
        if tx <= 0 or tx >= WIDTH or ty <= 0 or ty >= HEIGHT:
            return dist
            
        # Check obstacle collision
        for obs in obstacles:
            if obs.collidepoint(tx, ty):
                return dist
    return MAX_SENSOR_DIST

# Simulation Loop
running = True
while running:
    clock.tick(30)
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Draw Obstacles
    for obs in obstacles:
        pygame.draw.rect(screen, RED, obs, border_radius=6)
        
    # Cast 5 Ultrasonic/LiDAR Sensors
    sensor_values = []
    for rel_angle in sensor_angles:
        abs_angle = drone_angle + rel_angle
        dist = cast_ray(drone_x, drone_y, abs_angle, obstacles)
        sensor_values.append(dist)
        
        # Draw Sensor Rays
        rad = math.radians(abs_angle)
        end_x = drone_x + math.cos(rad) * dist
        end_y = drone_y + math.sin(rad) * dist
        pygame.draw.line(screen, YELLOW, (drone_x, drone_y), (end_x, end_y), 1)

    # Normalize sensor input for TinyML Model (Map 0-200px to 0-5.0m)
    normalized_sensors = [d / 40.0 for d in sensor_values]
    
    # TinyML Real-Time Decision Making
    predicted_action = clf.predict([normalized_sensors])[0]
    
    # Execute Action
    if predicted_action == 0:   # Straight
        drone_angle += 0
    elif predicted_action == 1: # Turn Left
        drone_angle -= 5.0
    elif predicted_action == 2: # Turn Right
        drone_angle += 5.0
        
    # Move Drone Forward
    rad_dir = math.radians(drone_angle)
    drone_x += math.cos(rad_dir) * speed
    drone_y += math.sin(rad_dir) * speed
    
    # Wrap screen boundaries
    drone_x %= WIDTH
    drone_y %= HEIGHT
    
    # Draw Drone (Vehicle Body)
    pygame.draw.circle(screen, GREEN, (int(drone_x), int(drone_y)), 12)
    heading_x = drone_x + math.cos(rad_dir) * 20
    heading_y = drone_y + math.sin(rad_dir) * 20
    pygame.draw.line(screen, BLUE, (drone_x, drone_y), (heading_x, heading_y), 3)

    pygame.display.flip()

pygame.quit()
