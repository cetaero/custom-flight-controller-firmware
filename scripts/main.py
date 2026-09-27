import time
import struct
from machine import I2C

# Initialize Hardware I2C1 (Hardcoded pins: PB6 = SCL, PB7 = SDA)
i2c = I2C(1, freq=100000)
BMI323_ADDR = 0x68

def write_reg16(reg, value):
    """Write 16-bit register value in little-endian format."""
    payload = bytearray([reg]) + struct.pack('<H', value)
    i2c.writeto(BMI323_ADDR, payload)

def read_reg16_burst(reg, num_words):
    """
    Read 16-bit registers in burst mode.
    Discards the 2 leading dummy bytes returned by BMI323 I2C protocol.
    """
    total_bytes = 2 + (num_words * 2)
    i2c.writeto(BMI323_ADDR, bytes([reg]))
    raw = i2c.readfrom(BMI323_ADDR, total_bytes)
    return raw[2:]

# 1. Verify Chip ID (Register 0x00)
chip_id_raw = read_reg16_burst(0x00, 1)
chip_id = struct.unpack('<H', chip_id_raw)[0] & 0xFF
print(f"Chip ID: 0x{chip_id:02X}")

# 2. Configure Sensor (Normal Mode)
write_reg16(0x20, 0x4027)  # ACC_CONF: Normal mode, +/-8g, 50Hz
write_reg16(0x21, 0x404B)  # GYR_CONF: Normal mode, +/-2000dps, 800Hz
time.sleep_ms(50)

# 3. Read Stream Loop
while True:
    raw_data = read_reg16_burst(0x03, 6)
    acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z = struct.unpack('<hhhhhh', raw_data)

    # Unit Conversion
    acc_x_g = acc_x / 4096.0
    acc_y_g = acc_y / 4096.0
    acc_z_g = acc_z / 4096.0

    gyr_x_dps = gyr_x / 16.384
    gyr_y_dps = gyr_y / 16.384
    gyr_z_dps = gyr_z / 16.384

    print(f"Accel (g):  X={acc_x_g:6.3f} | Y={acc_y_g:6.3f} | Z={acc_z_g:6.3f}")
    print(f"Gyro (dps): X={gyr_x_dps:6.2f} | Y={gyr_y_dps:6.2f} | Z={gyr_z_dps:6.2f}")
    print("-" * 50)

    time.sleep_ms(200)
