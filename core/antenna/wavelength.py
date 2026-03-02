# -*- coding: utf-8 -*-
"""
射频天线工具集 - 波长频率计算模块
RF Antenna Toolkit - Wavelength/Frequency Calculator

版本: v1.0.0
功能: 提供频率与波长之间的转换计算，支持不同介质
"""

import math
from dataclasses import dataclass
from typing import Optional

from ..constants import (
    SPEED_OF_LIGHT,
    DIELECTRIC_CONSTANTS,
    GHZ_TO_HZ,
    MHZ_TO_HZ,
    M_TO_MM,
)


@dataclass
class WavelengthResult:
    """波长计算结果数据类"""
    
    # 输入参数
    frequency_hz: float          # 频率 (Hz)
    epsilon_r: float             # 相对介电常数
    material_name: str           # 材料名称
    
    # 计算结果
    wavelength_free_space_m: float   # 自由空间波长 (m)
    wavelength_medium_m: float       # 介质中波长 (m)
    quarter_wave_m: float            # 四分之一波长 (m)
    half_wave_m: float               # 二分之一波长 (m)
    
    @property
    def wavelength_free_space_mm(self) -> float:
        """自由空间波长 (mm)"""
        return self.wavelength_free_space_m * M_TO_MM
    
    @property
    def wavelength_medium_mm(self) -> float:
        """介质中波长 (mm)"""
        return self.wavelength_medium_m * M_TO_MM
    
    @property
    def quarter_wave_mm(self) -> float:
        """四分之一波长 (mm)"""
        return self.quarter_wave_m * M_TO_MM
    
    @property
    def half_wave_mm(self) -> float:
        """二分之一波长 (mm)"""
        return self.half_wave_m * M_TO_MM
    
    @property
    def frequency_ghz(self) -> float:
        """频率 (GHz)"""
        return self.frequency_hz / GHZ_TO_HZ
    
    @property
    def frequency_mhz(self) -> float:
        """频率 (MHz)"""
        return self.frequency_hz / MHZ_TO_HZ


class WavelengthCalculator:
    """
    波长频率计算器
    
    提供频率与波长之间的相互转换，支持:
    - 自由空间波长计算
    - 介质中波长计算
    - 常用分数波长 (λ/4, λ/2)
    """
    
    def __init__(self):
        """初始化计算器"""
        self.available_materials = list(DIELECTRIC_CONSTANTS.keys())
    
    def calculate_from_frequency(
        self,
        frequency_hz: float,
        epsilon_r: float = 1.0,
        material_name: str = "真空/空气"
    ) -> WavelengthResult:
        """
        根据频率计算波长
        
        参数:
            frequency_hz: 频率 (Hz)
            epsilon_r: 相对介电常数
            material_name: 材料名称
        
        返回:
            WavelengthResult: 计算结果
        
        异常:
            ValueError: 当输入参数无效时抛出
        """
        # 参数验证
        if frequency_hz <= 0:
            raise ValueError("频率必须为正数")
        if epsilon_r <= 0:
            raise ValueError("介电常数必须为正数")
        
        # 计算自由空间波长
        wavelength_free_space = SPEED_OF_LIGHT / frequency_hz
        
        # 计算介质中波长 (考虑介电常数)
        wavelength_medium = wavelength_free_space / math.sqrt(epsilon_r)
        
        # 计算分数波长 (基于介质波长)
        quarter_wave = wavelength_medium / 4.0
        half_wave = wavelength_medium / 2.0
        
        return WavelengthResult(
            frequency_hz=frequency_hz,
            epsilon_r=epsilon_r,
            material_name=material_name,
            wavelength_free_space_m=wavelength_free_space,
            wavelength_medium_m=wavelength_medium,
            quarter_wave_m=quarter_wave,
            half_wave_m=half_wave,
        )
    
    def calculate_from_wavelength(
        self,
        wavelength_m: float,
        epsilon_r: float = 1.0,
        material_name: str = "真空/空气"
    ) -> WavelengthResult:
        """
        根据波长计算频率和其他参数
        
        参数:
            wavelength_m: 波长 (m)，假设为自由空间波长
            epsilon_r: 相对介电常数
            material_name: 材料名称
        
        返回:
            WavelengthResult: 计算结果
        """
        if wavelength_m <= 0:
            raise ValueError("波长必须为正数")
        
        # 从自由空间波长计算频率
        frequency_hz = SPEED_OF_LIGHT / wavelength_m
        
        # 使用频率计算完整结果
        return self.calculate_from_frequency(frequency_hz, epsilon_r, material_name)
    
    def get_material_epsilon(self, material_name: str) -> Optional[float]:
        """
        获取材料的相对介电常数
        
        参数:
            material_name: 材料名称
        
        返回:
            相对介电常数，如果材料不存在则返回None
        """
        return DIELECTRIC_CONSTANTS.get(material_name)
