#!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import re

# Config
SERIAL_PORT = "/dev/ttyUSB0"  # Change to COM3, COM4 etc on Windows
BAUD_RATE = 115200
MAX_POINTS = 500  # Scrolling window

# Data buffers
data_pitch = deque(maxlen=MAX_POINTS)
data_roll = deque(maxlen=MAX_POINTS)
data_yaw = deque(maxlen=MAX_POINTS)
timestamps = deque(maxlen=MAX_POINTS)
point_counter = [0]

# Serial init
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.5)
    print(f"Connected to {SERIAL_PORT} @ {BAUD_RATE} baud")
except Exception as e:
    print(f"Serial error: {e}. Check port.")
    exit(1)

# Parse line: "Pitch:12.34,Roll:-5.67,Yaw:180.0"
def parse_mpu_line(line):
    try:
        match = re.search(r"Pitch:([-\d.]+),Roll:([-\d.]+),Yaw:([-\d.]+)", line)
        if match:
            return float(match.group(1)), float(match.group(2)), float(match.group(3))
    except:
        pass
    return None

# Update plot
def update_plot(frame):
    global ser
    
    # Read available serial data
    while ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            
            vals = parse_mpu_line(line)
            if vals:
                pitch, roll, yaw = vals
                data_pitch.append(pitch)
                data_roll.append(roll)
                data_yaw.append(yaw)
                timestamps.append(point_counter[0])
                point_counter[0] += 1
        except Exception as e:
            print(f"Parse error: {e}")
    
    # Clear & redraw
    ax1.clear()
    ax2.clear()
    ax3.clear()
    
    if timestamps:
        # Plot 1: Pitch
        ax1.plot(list(timestamps), list(data_pitch), 'b-', linewidth=1.5, label='Pitch')
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax1.set_ylabel('Pitch (°)', fontsize=10)
        ax1.set_ylim(-90, 90)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        
        # Plot 2: Roll
        ax2.plot(list(timestamps), list(data_roll), 'r-', linewidth=1.5, label='Roll')
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax2.set_ylabel('Roll (°)', fontsize=10)
        ax2.set_ylim(-90, 90)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper left')
        
        # Plot 3: Yaw
        ax3.plot(list(timestamps), list(data_yaw), 'g-', linewidth=1.5, label='Yaw')
        ax3.set_ylabel('Yaw (°)', fontsize=10)
        ax3.set_xlabel('Sample #', fontsize=10)
        ax3.set_ylim(-360, 360)
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper left')

# Setup figure
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
fig.suptitle('MPU6050 Real-Time Attitude', fontsize=12, fontweight='bold')

# Animate
ani = FuncAnimation(fig, update_plot, interval=50, blit=False)  # Update every 50ms
plt.tight_layout()
plt.show()

ser.close()