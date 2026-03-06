# -*- coding: utf-8 -*-
"""
射频天线工具集 - 视距计算模块
RF Antenna Toolkit - Line-of-Sight Calculator

版本: v1.0.0
功能: 地球曲率视距、仰角计算、双站视距等
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

from ..constants import SPEED_OF_LIGHT


# 物理常数
EARTH_RADIUS_KM = 6371.0  # 地球平均半径 (km)
ATMOSPHERIC_REFRACTION_K = 4/3  # 标准大气折射系数


class AtmosphereType(Enum):
    """大气条件类型"""
    STANDARD = 4/3      # 标准大气 (k=4/3)
    DRY = 1.0           # 干燥/无折射
    HUMID = 1.5         # 高湿度
    SUPER_REFRACTION = 2.0  # 超折射


@dataclass
class HorizonResult:
    """视距计算结果"""
    radio_horizon_km: float       # 无线电视距 (km)
    optical_horizon_km: float     # 光学视距 (km)
    antenna_height_m: float       # 天线高度 (m)
    refraction_k: float           # 折射系数


@dataclass
class ElevationResult:
    """仰角计算结果"""
    geometric_angle_deg: float    # 几何仰角 (无曲率修正)
    corrected_angle_deg: float    # 修正仰角 (含曲率修正)
    earth_curvature_deg: float    # 地球曲率角
    target_distance_km: float     # 目标距离 (km)
    target_height_m: float        # 目标高度 (m)
    antenna_height_m: float       # 天线高度 (m)


@dataclass
class TwoStationResult:
    """双站视距结果"""
    max_los_distance_km: float    # 最大通视距离
    station1_horizon_km: float    # 站点1视距
    station2_horizon_km: float    # 站点2视距
    station1_height_m: float      # 站点1高度
    station2_height_m: float      # 站点2高度


@dataclass 
class FresnelResult:
    """菲涅尔区结果"""
    first_zone_radius_m: float    # 第一菲涅尔区半径
    clearance_60_percent_m: float # 60%净空要求
    frequency_mhz: float          # 工作频率
    distance_km: float            # 链路距离


class LOSCalculator:
    """
    视距计算器
    
    功能:
    1. 地球曲率视距 - 计算天线高度对应的无线电/光学视距
    2. 目标仰角 - 根据距离和高度计算仰角（反无场景）
    3. 双站视距 - 两个站点间的最大通视距离
    4. 菲涅尔区 - 无线链路的菲涅尔区半径
    """
    
    def __init__(self, refraction_k: float = ATMOSPHERIC_REFRACTION_K):
        """
        初始化视距计算器
        
        参数:
            refraction_k: 大气折射系数 (默认4/3)
        """
        self.refraction_k = refraction_k
        self.earth_radius_km = EARTH_RADIUS_KM
    
    def calculate_radio_horizon(
        self,
        antenna_height_m: float,
        refraction_k: Optional[float] = None
    ) -> HorizonResult:
        """
        计算无线电视距 (Radio Horizon)
        
        公式: d = √(2 × R × k × h)
        
        参数:
            antenna_height_m: 天线高度 (m)
            refraction_k: 折射系数 (可选, 默认使用实例值)
        
        返回:
            HorizonResult: 视距计算结果
        """
        if antenna_height_m < 0:
            raise ValueError("天线高度不能为负值")
        
        k = refraction_k if refraction_k is not None else self.refraction_k
        
        # 转换高度为km
        h_km = antenna_height_m / 1000
        
        # 无线电视距 (考虑大气折射)
        # d = √(2 × R × k × h)
        radio_horizon = math.sqrt(2 * self.earth_radius_km * k * h_km)
        
        # 光学视距 (无折射, k=1)
        optical_horizon = math.sqrt(2 * self.earth_radius_km * h_km)
        
        return HorizonResult(
            radio_horizon_km=radio_horizon,
            optical_horizon_km=optical_horizon,
            antenna_height_m=antenna_height_m,
            refraction_k=k
        )
    
    def calculate_elevation_angle(
        self,
        target_distance_km: float,
        target_height_m: float,
        antenna_height_m: float = 0
    ) -> ElevationResult:
        """
        计算目标仰角 (反无人机场景核心)
        
        参数:
            target_distance_km: 目标距离 (km)
            target_height_m: 目标高度 (m)
            antenna_height_m: 天线高度 (m), 默认0
        
        返回:
            ElevationResult: 仰角计算结果
        """
        if target_distance_km <= 0:
            raise ValueError("目标距离必须为正值")
        if target_height_m < 0:
            raise ValueError("目标高度不能为负值")
        
        # 高度差 (m)
        delta_h_m = target_height_m - antenna_height_m
        
        # 转换距离为m
        distance_m = target_distance_km * 1000
        
        # 几何仰角 (简单三角关系, 无曲率修正)
        geometric_angle_rad = math.atan2(delta_h_m, distance_m)
        geometric_angle_deg = math.degrees(geometric_angle_rad)
        
        # 地球曲率修正
        # 在距离d处, 由于地球曲率导致的高度下降 ≈ d²/(2R)
        earth_curvature_m = (target_distance_km ** 2) / (2 * self.earth_radius_km) * 1000
        
        # 曲率导致的角度变化 (rad)
        curvature_angle_rad = math.atan2(earth_curvature_m, distance_m)
        curvature_angle_deg = math.degrees(curvature_angle_rad)
        
        # 修正后的仰角 (需要额外抬升以补偿地球曲率)
        corrected_angle_deg = geometric_angle_deg + curvature_angle_deg
        
        return ElevationResult(
            geometric_angle_deg=geometric_angle_deg,
            corrected_angle_deg=corrected_angle_deg,
            earth_curvature_deg=curvature_angle_deg,
            target_distance_km=target_distance_km,
            target_height_m=target_height_m,
            antenna_height_m=antenna_height_m
        )
    
    def calculate_two_station_los(
        self,
        station1_height_m: float,
        station2_height_m: float,
        refraction_k: Optional[float] = None
    ) -> TwoStationResult:
        """
        计算双站间最大通视距离
        
        公式: d_max = √(2Rk×h₁) + √(2Rk×h₂)
        
        参数:
            station1_height_m: 站点1天线高度 (m)
            station2_height_m: 站点2天线高度 (m)
            refraction_k: 折射系数
        
        返回:
            TwoStationResult: 双站视距结果
        """
        if station1_height_m < 0 or station2_height_m < 0:
            raise ValueError("站点高度不能为负值")
        
        k = refraction_k if refraction_k is not None else self.refraction_k
        
        # 各站视距
        h1_km = station1_height_m / 1000
        h2_km = station2_height_m / 1000
        
        horizon1 = math.sqrt(2 * self.earth_radius_km * k * h1_km)
        horizon2 = math.sqrt(2 * self.earth_radius_km * k * h2_km)
        
        # 最大通视距离 = 两站视距之和
        max_los = horizon1 + horizon2
        
        return TwoStationResult(
            max_los_distance_km=max_los,
            station1_horizon_km=horizon1,
            station2_horizon_km=horizon2,
            station1_height_m=station1_height_m,
            station2_height_m=station2_height_m
        )
    
    def calculate_fresnel_zone(
        self,
        frequency_mhz: float,
        distance_km: float,
        zone_number: int = 1
    ) -> FresnelResult:
        """
        计算菲涅尔区半径
        
        公式: F = √(n×λ×d₁×d₂/(d₁+d₂))
        对于链路中点: F = √(n×λ×d/4)
        
        参数:
            frequency_mhz: 工作频率 (MHz)
            distance_km: 链路距离 (km)
            zone_number: 菲涅尔区编号 (默认1)
        
        返回:
            FresnelResult: 菲涅尔区结果
        """
        if frequency_mhz <= 0:
            raise ValueError("频率必须为正值")
        if distance_km <= 0:
            raise ValueError("距离必须为正值")
        
        # 波长 (m) - 使用统一常量
        wavelength_m = SPEED_OF_LIGHT / (frequency_mhz * 1e6)
        
        # 链路中点的菲涅尔区半径 (最大值)
        distance_m = distance_km * 1000
        # F = √(n × λ × d / 4)
        first_zone_radius = math.sqrt(zone_number * wavelength_m * distance_m / 4)
        
        # 60%净空要求 (工程常用)
        clearance_60 = first_zone_radius * 0.6
        
        return FresnelResult(
            first_zone_radius_m=first_zone_radius,
            clearance_60_percent_m=clearance_60,
            frequency_mhz=frequency_mhz,
            distance_km=distance_km
        )
    
    @staticmethod
    def get_elevation_quality(angle_deg: float) -> str:
        """
        评估仰角的探测难度
        
        参数:
            angle_deg: 仰角 (度)
        """
        if angle_deg < 0:
            return "🔴 无法探测 (目标低于水平面)"
        elif angle_deg < 1:
            return "🟠 极低仰角 (地杂波影响大)"
        elif angle_deg < 5:
            return "🟡 低仰角 (多径干扰)"
        elif angle_deg < 30:
            return "🟢 正常仰角"
        elif angle_deg < 60:
            return "🟢 高仰角"
        else:
            return "🔵 超高仰角 (接近天顶)"
    
    @staticmethod
    def format_distance(km: float) -> str:
        """格式化距离显示"""
        if km < 1:
            return f"{km * 1000:.1f} m"
        else:
            return f"{km:.2f} km"
