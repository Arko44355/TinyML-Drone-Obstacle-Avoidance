import numpy as np
import pandas as pd

np.random.seed(42)
NUM_SAMPLES = 10000

distances = np.random.uniform(0.2, 5.0, size=(NUM_SAMPLES, 5))
actions = []

for dist in distances:
    d_left90, d_left45, d_front, d_right45, d_right90 = dist
    
    if d_front < 1.0:
        left_clearance = min(d_left90, d_left45)
        right_clearance = min(d_right90, d_right45)
        
        if left_clearance > right_clearance:
            actions.append(1)
        else:
            actions.append(2)
    elif d_left45 < 0.8:
        actions.append(2)
    elif d_right45 < 0.8:
        actions.append(1)
    else:
        actions.append(0)

columns = ['sensor_left90', 'sensor_left45', 'sensor_front', 'sensor_right45', 'sensor_right90']
df = pd.DataFrame(distances, columns=columns)
df['action'] = actions

df.to_csv('drone_sensor_dataset.csv', index=False)
print(f"Success! Generated 'drone_sensor_dataset.csv' with {NUM_SAMPLES} samples.")
