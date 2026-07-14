import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# -----------------------
# Serial Port
# -----------------------
PORT = "COM3"      
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

# -----------------------
# Plot Settings
# -----------------------
N = 300

roll = deque([0]*N, maxlen=N)
pitch = deque([0]*N, maxlen=N)
yaw = deque([0]*N, maxlen=N)

x = list(range(N))

fig, ax = plt.subplots(figsize=(12,6))

line_roll, = ax.plot(x, roll, label="Roll")
line_pitch, = ax.plot(x, pitch, label="Pitch")
line_yaw, = ax.plot(x, yaw, label="Yaw")

ax.set_title("STM32F411 + MPU6050 (Madgwick Filter)")
ax.set_xlabel("Samples")
ax.set_ylabel("Angle (Degrees)")
ax.set_ylim(-180, 180)
ax.grid(True)
ax.legend()

def update(frame):
    try:
        line = ser.readline().decode().strip()

        if line:
            r, p, y = map(float, line.split(','))

            roll.append(r)
            pitch.append(p)
            yaw.append(y)

            line_roll.set_ydata(roll)
            line_pitch.set_ydata(pitch)
            line_yaw.set_ydata(yaw)

    except:
        pass

    return line_roll, line_pitch, line_yaw

ani = FuncAnimation(fig, update, interval=5, blit=True)

plt.tight_layout()
plt.show()