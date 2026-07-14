#pragma once

#include <stdint.h>

struct MPU6050Data {
    uint8_t accel_rec_data[6];
    uint8_t gyro_rec_data[6];
    uint8_t Temp_Data[2];
    int16_t accel_x_raw;
    int16_t accel_y_raw;
    int16_t accel_z_raw;
    int16_t temp_raw;
    int16_t gyro_x_raw;
    int16_t gyro_y_raw;
    int16_t gyro_z_raw;

    float accel_x;
    float accel_y;
    float accel_z;
    float temp;
    float gyro_x;
    float gyro_y;
    float gyro_z;

    float roll;
    float pitch;
    float yaw;
  };