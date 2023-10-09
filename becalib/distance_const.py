import math

PI = math.pi
PI_F = math.pi
RAD_IN_DEG = PI / 180.0
RAD_IN_DEG_HALF = PI / 360.0
COS_LUT_SIZE = 1024
COS_LUT_SIZE_F = 1024.0
ASIN_SQRT_LUT_SIZE = 512
METRIC_LUT_SIZE = 1024
EARTH_RADIUS = 6371007.180918475
EARTH_DIAMETER = 2 * EARTH_RADIUS

COS_LUT_SIZE = 1024
ASIN_SQRT_LUT_SIZE = 512
METRIC_LUT_SIZE = 1024

cos_lut = [0.0] * (COS_LUT_SIZE + 1)
asin_sqrt_lut = [0.0] * (ASIN_SQRT_LUT_SIZE + 1)
sphere_metric_lut = [0.0] * (METRIC_LUT_SIZE + 1)
sphere_metric_meters_lut = [0.0] * (METRIC_LUT_SIZE + 1)
wgs84_metric_meters_lut = [float(0.0)] * (2 * (METRIC_LUT_SIZE + 1))

CONFIG_INTERVAL = 60  # 60s reload all config
#MIN_ALLOWED_VEL = 0.2 # m/s
#MAX_ALLOWED_VEL = 70 # m/s