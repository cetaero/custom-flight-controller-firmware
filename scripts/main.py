import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
window_size = 100
data_queue = deque(maxlen=window_size)
buffer = ""  
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

def update(frame):
    global buffer
    
    try:
        # Read available bytes
        chunk = ser.read(256).decode(errors="replace")
        
        if not chunk:
            return
        buffer += chunk
        lines = buffer.split('\r\n')
        
        buffer = lines[-1]
        
        # Process complete lines
        for line in lines[:-1]:
            line = line.strip()
            
            if not line or len(line) < 5:
                continue
            if ',' not in line:
                continue
            parts = line.split(',')
            
            # Try first 6 comma-separated values
            try:
                nums = []
                for i in range(6):
                    # Clean each part: remove non-digit/minus
                    cleaned = ''.join(c for c in parts[i] if c in '0123456789-')
                    if cleaned:
                        nums.,append(int(cleaned))
                
                if len(nums) == 6 and all(abs(v) <= 90000 for v in nums):
                    data_queue.append(nums)
                    print(f"Got: {nums}")
                
            except (ValueError, IndexError):
                pass
        
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

# Fast update rate (50ms)
ani = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
plt.tight_layout()
plt.show()