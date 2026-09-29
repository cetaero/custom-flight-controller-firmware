#!/usr/bin/env python3
"""3D digital twin of the board orientation.

Input line formats (CSV, one per line):
  4 values: w,x,y,z         quaternion (q0,q1,q2,q3)   <- preferred
  3 values: pitch,roll,yaw  radians (order set below)

Usage:  python twin.py [port] [baud]
        python twin.py --demo        (no hardware, spinning box)
Keys:   z = zero yaw (6-axis yaw drifts), r = reset yaw zero, q = quit
Deps:   pip install pyserial matplotlib numpy
"""
import sys
import math
import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

DEMO = "--demo" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
PORT = args[0] if len(args) > 0 else "/dev/ttyACM1"
BAUD = int(args[1]) if len(args) > 1 else 115200

EULER_ORDER = ("pitch", "roll", "yaw")   # order of the 3 values in firmware print
BOX = np.array([1.0, 0.6, 0.1])          # half sizes: X forward, Y left, Z up
DEBUG = False

# ---------------------------------------------------------------- math
def quat_to_R(q):
    """Body -> earth rotation matrix. Same convention as Madgwick output."""
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z) or 1.0
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ])


def euler_to_quat(roll, pitch, yaw):
    """ZYX (yaw-pitch-roll), radians."""
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy)


def qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)


def quat_to_euler(q):
    w, x, y, z = q
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    s = max(-1.0, min(1.0, 2 * (w * y - x * z)))
    pitch = math.asin(s)
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return roll, pitch, yaw


# ---------------------------------------------------------------- input
latest_q = (1.0, 0.0, 0.0, 0.0)
yaw_zero = 0.0
buf = b""
ser = None

if not DEMO:
    import serial
    ser = serial.Serial(PORT, BAUD, timeout=0.01)
    ser.reset_input_buffer()


def parse(line):
    try:
        v = [float(p) for p in line.split(",")]
    except ValueError:
        return None
    if len(v) == 4:
        return tuple(v)
    if len(v) == 3:
        d = dict(zip(EULER_ORDER, v))
        return euler_to_quat(d["roll"], d["pitch"], d["yaw"])
    return None


def poll():
    global buf, latest_q
    if DEMO:
        t = time.time()
        latest_q = euler_to_quat(0.6 * math.sin(t), 0.5 * math.sin(0.7 * t), 0.8 * t)
        return
    buf += ser.read_all()
    buf = buf.replace(b"\r", b"\n")
    parts = buf.split(b"\n")
    buf = parts[-1]                      # keep incomplete tail
    for raw in parts[:-1]:
        line = raw.decode(errors="ignore").strip()
        if not line:
            continue
        if DEBUG:
            print(repr(line))
        q = parse(line)
        if q is not None and all(math.isfinite(c) for c in q):
            latest_q = q                 # only newest sample matters for display


def display_q():
    c, s = math.cos(-yaw_zero / 2), math.sin(-yaw_zero / 2)
    return qmul((c, 0.0, 0.0, s), latest_q)


# ---------------------------------------------------------------- scene
corners = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]) * BOX
FACES = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
FACE_COLORS = ["#888888", "#cccccc", "#888888", "#888888", "#888888", "#aa3333"]  # red = +X face? see below

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(-1.6, 1.6)
ax.set_ylim(-1.6, 1.6)
ax.set_zlim(-1.6, 1.6)
ax.set_box_aspect((1, 1, 1))
ax.set_xlabel("earth X")
ax.set_ylabel("earth Y")
ax.set_zlabel("earth Z (up)")

poly = Poly3DCollection([corners[f] for f in FACES], alpha=0.85, edgecolor="k")
poly.set_facecolor(["#7a7a7a", "#b0b0b0", "#7a7a7a", "#7a7a7a", "#7a7a7a", "#c04040"])
ax.add_collection3d(poly)

body_axes = np.eye(3) * 1.5
axlines = [ax.plot([0, 0], [0, 0], [0, 0], c=col, lw=3, label=f"body {n}")[0]
           for col, n in zip(("r", "g", "b"), "XYZ")]
ax.legend(loc="upper left")
# fixed earth reference: faint axes
for v, c in zip(np.eye(3) * 1.6, ("#ffaaaa", "#aaffaa", "#aaaaff")):
    ax.plot([0, v[0]], [0, v[1]], [0, v[2]], c=c, lw=1, ls="--")


def on_key(e):
    global yaw_zero
    if e.key == "z":
        yaw_zero = quat_to_euler(latest_q)[2]
    elif e.key == "r":
        yaw_zero = 0.0
    elif e.key == "q":
        plt.close(fig)


fig.canvas.mpl_connect("key_press_event", on_key)


def update(_):
    poll()
    q = display_q()
    R = quat_to_R(q)
    v = corners @ R.T
    poly.set_verts([v[f] for f in FACES])
    for ln, a in zip(axlines, body_axes):
        p = R @ a
        ln.set_data_3d([0, p[0]], [0, p[1]], [0, p[2]])
    r, p, y = (math.degrees(a) for a in quat_to_euler(q))
    ax.set_title(f"roll {r:7.1f}   pitch {p:7.1f}   yaw {y:7.1f}  (deg)   [z: zero yaw]")
    return []


ani = FuncAnimation(fig, update, interval=30, blit=False, cache_frame_data=False)
try:
    plt.show()
finally:
    if ser:
        ser.close()
