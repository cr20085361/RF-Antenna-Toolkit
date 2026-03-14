# -*- coding: utf-8 -*-
"""
射频天线工具集 - 物理常数定义
RF Antenna Toolkit - Physical Constants

版本: v2.0.0
功能: 定义射频和天线计算中常用的物理常数
"""

import math

# ==================== 基本物理常数 ====================
# 真空中的光速 (m/s)
SPEED_OF_LIGHT = 299792458.0

# 自由空间阻抗 (Ω)
FREE_SPACE_IMPEDANCE = 376.730313668

# 真空介电常数 (F/m)
VACUUM_PERMITTIVITY = 8.8541878128e-12

# 真空磁导率 (H/m)
VACUUM_PERMEABILITY = 1.25663706212e-6

# 玻尔兹曼常数 (J/K)
BOLTZMANN_CONSTANT = 1.380649e-23

# ==================== 常用单位转换 ====================
# 频率单位
HZ_TO_KHZ = 1e-3
HZ_TO_MHZ = 1e-6
HZ_TO_GHZ = 1e-9
KHZ_TO_HZ = 1e3
MHZ_TO_HZ = 1e6
GHZ_TO_HZ = 1e9

# 长度单位
M_TO_MM = 1e3
M_TO_CM = 1e2
MM_TO_M = 1e-3
CM_TO_M = 1e-2

# 角度单位
DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi

# ==================== 常用介电常数参考值 ====================
# 材料相对介电常数 (εr)
DIELECTRIC_CONSTANTS = {
    "真空/空气": 1.0,
    "FR4": 4.4,
    "Rogers 4350B": 3.48,
    "Rogers 5880": 2.2,
    "聚四氟乙烯(PTFE)": 2.1,
    "陶瓷(Al2O3)": 9.8,
    "玻璃": 5.5,
    "硅(Si)": 11.9,
}

# ==================== 辅助函数 ====================
def frequency_to_wavelength(frequency_hz: float, epsilon_r: float = 1.0) -> float:
    """
    将频率转换为波长
    
    参数:
        frequency_hz: 频率 (Hz)
        epsilon_r: 相对介电常数 (默认为1，即真空/空气)
    
    返回:
        波长 (m)
    """
    if frequency_hz <= 0:
        raise ValueError("频率必须为正数")
    if epsilon_r <= 0:
        raise ValueError("介电常数必须为正数")
    
    return SPEED_OF_LIGHT / (frequency_hz * math.sqrt(epsilon_r))


def wavelength_to_frequency(wavelength_m: float, epsilon_r: float = 1.0) -> float:
    """
    将波长转换为频率
    
    参数:
        wavelength_m: 波长 (m)
        epsilon_r: 相对介电常数 (默认为1，即真空/空气)
    
    返回:
        频率 (Hz)
    """
    if wavelength_m <= 0:
        raise ValueError("波长必须为正数")
    if epsilon_r <= 0:
        raise ValueError("介电常数必须为正数")
    
    return SPEED_OF_LIGHT / (wavelength_m * math.sqrt(epsilon_r))
