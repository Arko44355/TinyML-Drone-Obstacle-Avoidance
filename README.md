# Autonomous Edge-AI Navigation via TinyML

## Dual-Platform Validation Architecture

embedded hardware-এ sub-microsecond obstacle avoidance decision tree পরীক্ষা করার জন্য ২টি প্ল্যাটফর্ম ব্যবহার করা হয়েছে:

1. **Physical Validation Prototype (2D Mobile Edge Rover):**
   * **MCU:** STM32F401 Black Pill (ARM Cortex-M4 @ 84MHz)
   * **Sensors:** 5x VL53L1X Time-of-Flight (ToF) LiDAR Sensors (Arc array at -90°, -45°, 0°, +45°, +90°)
   * **I2C Bus Expander:** PCA9548A / TCA9548A 8-Channel Multiplexer (Address: 0x70)
   * **Actuation:** Dual DC Motors via Differential Drive PWM (-255 to +255)

2. **Aerial Target Concept (3D F450 Quadcopter):**
   * Software-simulated flight dynamics mapping 5-directional range data into spatial Roll, Pitch, and Yaw commands.

---

## 2WD Rover Steering Logic

Embedded decision model (`tinyml_model.h`) মূলত ৫টি LiDAR দূরত্ব $[d_{L90}, d_{L45}, d_{Front}, d_{R45}, d_{R90}]$ ইনপুট হিসেবে নিয়ে মোটরের PWM স্পিড হিসাব করে:

$$\text{Clear Path} \longrightarrow (V_L = 200, V_R = 200)$$
$$\text{Front Obstacle } (d_{Front} < 0.5m) \longrightarrow \text{Sharp Turn away from blocked side}$$
$$\text{Left/Right Obstacle} \longrightarrow \text{Differential speed scaling to avoid walls}$$
