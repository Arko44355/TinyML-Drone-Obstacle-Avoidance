import numpy as np

def tinyml_steering_logic(sensors):
    """
    5-ToF LiDAR Array data for 2WD Autonomous Rover
    Sensors Input Order: [L90, L45, Front, R45, R90] in meters
    Output: (left_motor_speed, right_motor_speed) -> PWM Range: -255 to 255
    """
    d_L90, d_L45, d_Front, d_R45, d_R90 = sensors
    
    SAFE_DISTANCE = 0.5   # Threshold distance in meters
    BASE_SPEED = 200      # Nominal PWM driving speed
    TURN_SPEED = 180      # Differential turn speed
    
    # 1. Front obstacle detection (Front Collision Avoidance)
    if d_Front < SAFE_DISTANCE:
        # Compare available clearance on left vs right side
        left_space = d_L45 + d_L90
        right_space = d_R45 + d_R90
        
        if left_space > right_space:
            # More space on left -> Sharp Left Turn (Left reverse, Right forward)
            left_speed = -TURN_SPEED  
            right_speed = TURN_SPEED
            action = "EMERGENCY: Sharp Left Turn"
        else:
            # More space on right -> Sharp Right Turn (Left forward, Right reverse)
            left_speed = TURN_SPEED
            right_speed = -TURN_SPEED
            action = "EMERGENCY: Sharp Right Turn"
            
    # 2. Left obstacle detection (Left Wall Avoidance)
    elif d_L45 < SAFE_DISTANCE or d_L90 < SAFE_DISTANCE:
        left_speed = BASE_SPEED
        right_speed = 80  # Reduce right motor speed to steer right
        action = "Steering: Slight Right"
        
    # 3. Right obstacle detection (Right Wall Avoidance)
    elif d_R45 < SAFE_DISTANCE or d_R90 < SAFE_DISTANCE:
        left_speed = 80   # Reduce left motor speed to steer left
        right_speed = BASE_SPEED
        action = "Steering: Slight Left"
        
    # 4. Clear path ahead (Forward Drive)
    else:
        left_speed = BASE_SPEED
        right_speed = BASE_SPEED
        action = "Status: Moving Forward"
        
    return left_speed, right_speed, action


# --- Test Simulation Runs ---
if __name__ == "__main__":
    print("=== 2WD TinyML Rover Obstacle Avoidance Simulation ===\n")
    
    # Test Scenarios Data (in meters)
    test_scenarios = [
        {"name": "Clear Path Ahead", "data": [1.5, 1.2, 1.8, 1.1, 1.4]},
        {"name": "Front Obstacle Detected", "data": [1.2, 0.8, 0.3, 0.4, 0.5]},
        {"name": "Diagonal Left Obstacle", "data": [0.8, 0.3, 1.1, 1.5, 2.0]},
        {"name": "Right Wall/Obstacle", "data": [1.8, 1.5, 0.9, 0.4, 0.3]}
    ]

    for test in test_scenarios:
        sensors = np.array(test["data"])
        v_left, v_right, status = tinyml_steering_logic(sensors)
        
        print(f"Scenario: {test['name']}")
        print(f"Sensor Readings [L90, L45, Front, R45, R90]: {test['data']}")
        print(f"Decision: {status}")
        print(f"Motor Output -> Left Motor PWM: {v_left} | Right Motor PWM: {v_right}")
        print("-" * 65)