#include "filter.h"
#include "FreeRTOSConfig.h"
#include "GyroData.h"
#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "MadgwickAHRS.h"

#define SWAP_ENDIAN(x) ((int16_t)(((uint16_t)x & 0xff00) >> 8) | ((uint16_t)x & 0xff))
//#define gyroDivider 131.0
//#define accelDivider 16384.0

#define ACC_RANGE_G   8.0f      // match your ACC_CONF bits 6:4
#define GYR_RANGE_DPS 2000.0f
#define DEG2RAD       0.0174533f
uint32_t lastTick;
float deltaT;

void PopulateRealValues(struct MPU6050Data *data) {
  data->accel_x_raw=data->accel_gyro_sample_16[0];
  data->accel_y_raw=data->accel_gyro_sample_16[1];
  data->accel_z_raw=data->accel_gyro_sample_16[2];
  data->gyro_x_raw=data->accel_gyro_sample_16[3];
  data->gyro_y_raw=data->accel_gyro_sample_16[4];
  data->gyro_z_raw=data->accel_gyro_sample_16[5];
  const float ka = ACC_RANGE_G   / 32768.0f;
  const float kg = GYR_RANGE_DPS / 32768.0f;
  
  data->accel_x = (int16_t)data->accel_x_raw * ka;   // g
  data->accel_y = (int16_t)data->accel_y_raw * ka;
  data->accel_z = (int16_t)data->accel_z_raw * ka;
  
  data->gyro_x  = (int16_t)data->gyro_x_raw * kg;    // dps
  data->gyro_y  = (int16_t)data->gyro_y_raw * kg;
  data->gyro_z  = (int16_t)data->gyro_z_raw * kg;
  MadgwickAHRSupdateIMU(   
    data->gyro_x,data->gyro_y,data->gyro_z,
    data->accel_x,data->accel_y,data->accel_z 
    );
  
  data->roll  = atan2f(q0*q1 + q2*q3, 0.5f - q1*q1 - q2*q2);
  data->pitch = asinf(-2.0f * (q1*q3 - q0*q2));
  data->yaw   = atan2f(q1*q2 + q0*q3, 0.5f - q2*q2 - q3*q3);
}

