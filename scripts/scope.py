#!/usr/bin/env python3
"""Live plot of CSV floats from STM32 over USB CDC.

Line format: 0.154480,0.492643,0.010992
Usage: python plot_serial.py [port] [baud]
Deps:  pip install pyserial matplotlib
"""
import sys
import time
from collections import deque

import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
WINDOW = 500                        # samples kept on screen
LABELS = ["pitch", "roll", "yaw"]   # same order as snprintf in firmware
DEBUG = True                        # print raw lines seen; set False when working
N = len(LABELS)

ser = serial.Serial(PORT, BAUD, timeout=0.01)
ser.reset_input_buffer()

t0 = time.time()
ts = deque(maxlen=WINDOW)
data = [deque(maxlen=WINDOW) for _ in range(N)]
buf = b""


def read_lines():
    """Pull all bytes waiting, yield complete lines."""
    global buf
    buf += ser.read_all()
    buf = buf.replace(b"\r", b"\n")   # handle \r\n, \r, \n
    while b"\n" in buf:
        line, buf = buf.split(b"\n", 1)
        line = line.decode(errors="ignore").strip()
        if line:
            if DEBUG:
                print(repr(line))
            yield line


def parse(line):
    parts = line.split(",")
    if len(parts) != N:
        return None
    try:
        return [float(p) for p in parts]
    except ValueError:
        return None   # half line or garbage, skip


fig, ax = plt.subplots()
lines = [ax.plot([], [], label=name)[0] for name in LABELS]
ax.set_xlabel("time (s)")
ax.set_ylabel("value")
ax.grid(True)
ax.legend(loc="upper left")


def update(_):
    for line in read_lines():
        vals = parse(line)
        if vals is None:
            continue
        ts.append(time.time() - t0)
        for i, v in enumerate(vals):
            data[i].append(v)
    if ts:
        for ln, d in zip(lines, data):
            ln.set_data(ts, d)
        ax.set_xlim(ts[0], max(ts[-1], ts[0] + 1))
        lo = min(min(d) for d in data)
        hi = max(max(d) for d in data)
        pad = (hi - lo) * 0.1 or 0.1
        ax.set_ylim(lo - pad, hi + pad)
    return lines


ani = FuncAnimation(fig, update, interval=30, blit=False, cache_frame_data=False)
try:
    plt.show()
finally:
    ser.close()
