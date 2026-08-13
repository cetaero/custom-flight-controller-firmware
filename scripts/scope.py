import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
window_size = 100
data_queue = deque(maxlen=window_size)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

def update(frame):
    # Read ONE line if available
    try:
        line = ser.readline().decode(errors="replace").strip()
        
        if not line:
            # No data yet, don't redraw
            return
        
        # Parse line
        if ',' not in line:
            print(f"Skipped: no commas in '{line}'")
            return
        
        parts = line.split(',')
        
        if len(parts) != 6:
            print(f"Skipped: expected 6 values, got {len(parts)}  recive string is {line}")
            return
        
        try:
            vals = list(map(int, parts))
        except ValueError as e:
            print(f"Parse error: {e}")
            return
        
        if not all(abs(v) <= 90000 for v in vals):
            print(f"Skipped: value out of range {vals}")
            return
        
        # Data good, add to queue
        data_queue.append(vals)
        print(f"Got: {vals}")
        
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Only plot if we have data
    if len(data_queue) < 2:
        return
    
    # Plot
    data = np.array(list(data_queue))
    
    ax1.clear()
    ax1.plot(data[:, 0:3], linewidth=1)
    ax1.legend(['ax', 'ay', 'az'], loc='upper right')
    ax_min, ax_max = data[:, 0:3].min(), data[:, 0:3].max()
    margin = max(abs(ax_min), abs(ax_max)) * 0.2 + 100
    ax1.set_ylim(ax_min - margin, ax_max + margin)
    ax1.set_ylabel('Accel')
    
    ax2.clear()
    ax2.plot(data[:, 3:6], linewidth=1)
    ax2.legend(['gx', 'gy', 'gz'], loc='upper right')
    gy_min, gy_max = data[:, 3:6].min(), data[:, 3:6].max()
    margin = max(abs(gy_min), abs(gy_max)) * 0.2 + 100
    ax2.set_ylim(gy_min - margin, gy_max + margin)
    ax2.set_ylabel('Gyro')

# Fast update rate (50ms) so responsive to incoming data
ani = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
plt.tight_layout()
plt.show()
