#pragma once

#include "GyroData.h"

void ApplyMadgwickFilter(struct MPU6050Data* data);
void PopulateRealValues(struct MPU6050Data* data,int count);
#include <math.h>
