#ifndef I2C_HELPER
#define I2C_HELPER

#include <stdint.h>
#include "stm32f4xx_hal.h"

// Declare the function
HAL_StatusTypeDef read_register_burst_16(uint8_t addr, uint8_t reg, uint8_t words, int16_t *result,uint8_t padding);

#endif  // I2C_HELPER