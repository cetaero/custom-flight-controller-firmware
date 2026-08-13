#include "i2c_helper.h"

extern I2C_HandleTypeDef hi2c1;  // From main.c


HAL_StatusTypeDef read_register_burst_16(uint8_t addr, uint8_t reg, uint8_t words, int16_t *result, uint8_t padding) {
    uint8_t buffer[words * 2 + padding];
    
    if (HAL_I2C_Mem_Read(&hi2c1, addr, reg, I2C_MEMADD_SIZE_8BIT, 
                         buffer, words * 2 + padding, 1000) != HAL_OK) {
        return HAL_ERROR;
    }
    
    for (int i = 0; i < words; i++) {
        result[i] = (int16_t)(buffer[padding + i*2] | (buffer[padding + i*2 + 1] << 8));
    }
    return HAL_OK;
}
