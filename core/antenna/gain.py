# -*- coding: utf-8 -*-
"""
射频天线工具集 - 天线增益计算模块
RF Antenna Toolkit - Antenna Gain Calculator

版本: v2.0.0
功能: 提供多种天线增益计算方法
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

from ..constants import SPEED_OF_LIGHT


class GainUnit(Enum):
    """增益单位枚举"""
    DBI = "dBi"  # 相对于各向同性天线
    DBD = "dBd"  # 相对于半波偶极子


@dataclass
class GainResult:
    """增益计算结果数据类"""
    
    # 增益值
    gain_dbi: float          # 增益 (dBi)
    gain_dbd: float          # 增益 (dBd)
    gain_linear: float       # 增益 (线性值)
    
    # 输入参数记录
    method: str              # 计算方法
    
    @property
    def gain_dbi_formatted(self) -> str:
        """格式化dBi输出"""
        return f"{self.gain_dbi:.2f} dBi"
    
    @property
    def gain_dbd_formatted(self) -> str:
        """格式化dBd输出"""
        return f"{self.gain_dbd:.2f} dBd"


class GainCalculator:
    """
    天线增益计算器
    
    支持多种主流增益计算方法:
    1. 波束宽度法 - 根据E面/H面半功率角估算
    2. 口径效率法 - 根据天线物理口径计算
    3. 单位转换 - dBi/dBd/线性值互转
    4. EIRP计算 - 等效各向同性辐射功率
    """
    
    # dBi与dBd的转换常数 (半波偶极子增益 ≈ 2.15 dBi)
    DBI_DBD_OFFSET = 2.15
    
    # 波束宽度公式常数 (不同来源略有差异)
    # 32400常数适用于电场分布均匀的口径天线
    # 41253常数更保守，适用于一般天线
    BEAMWIDTH_CONST_CONSERVATIVE = 41253
    BEAMWIDTH_CONST_UNIFORM = 32400
    BEAMWIDTH_CONST_TYPICAL = 26000  # 典型值，考虑实际效率
    
    def calculate_from_beamwidth(
        self,
        theta_e_deg: float,
        theta_h_deg: float,
        constant: float = None
    ) -> GainResult:
        """
        根据波束宽度计算增益 (最常用方法)
        
        公式: G ≈ K / (θ_E × θ_H)
        
        参数:
            theta_e_deg: E面半功率波束宽度 (度)
            theta_h_deg: H面半功率波束宽度 (度)
            constant: 公式常数K (默认使用41253)
        
        返回:
            GainResult: 计算结果
        
        常用常数K参考:
        - 41253: 保守估计 (IEEE标准)
        - 32400: 均匀口径分布
        - 26000: 考虑实际效率的典型值
        """
        if theta_e_deg <= 0 or theta_h_deg <= 0:
            raise ValueError("波束宽度必须为正值")
        if theta_e_deg > 180 or theta_h_deg > 180:
            raise ValueError("波束宽度不能超过180度")
        
        if constant is None:
            constant = self.BEAMWIDTH_CONST_CONSERVATIVE
        
        # 计算增益 (线性值)
        gain_linear = constant / (theta_e_deg * theta_h_deg)
        
        # 转换为dB
        gain_dbi = 10 * math.log10(gain_linear)
        gain_dbd = gain_dbi - self.DBI_DBD_OFFSET
        
        return GainResult(
            gain_dbi=gain_dbi,
            gain_dbd=gain_dbd,
            gain_linear=gain_linear,
            method="波束宽度法"
        )
    
    def calculate_from_aperture(
        self,
        aperture_area_m2: float,
        frequency_hz: float,
        efficiency: float = 0.55
    ) -> GainResult:
        """
        根据天线口径计算增益 (适用于口径天线)
        
        公式: G = η × (4π/λ²) × A = η × 4πA/λ²
        
        参数:
            aperture_area_m2: 天线口径面积 (m²)
            frequency_hz: 工作频率 (Hz)
            efficiency: 口径效率 (0~1, 默认0.55)
        
        返回:
            GainResult: 计算结果
        
        典型口径效率参考:
        - 0.50~0.60: 抛物面天线
        - 0.60~0.70: 喇叭天线
        - 0.80~0.90: 馈电优化的高效天线
        """
        if aperture_area_m2 <= 0:
            raise ValueError("口径面积必须为正值")
        if frequency_hz <= 0:
            raise ValueError("频率必须为正值")
        if efficiency <= 0 or efficiency > 1:
            raise ValueError("口径效率必须在 (0, 1] 范围内")
        
        # 计算波长 (使用统一常量)
        wavelength = SPEED_OF_LIGHT / frequency_hz
        
        # 计算增益
        gain_linear = efficiency * (4 * math.pi * aperture_area_m2) / (wavelength ** 2)
        
        # 转换为dB
        gain_dbi = 10 * math.log10(gain_linear)
        gain_dbd = gain_dbi - self.DBI_DBD_OFFSET
        
        return GainResult(
            gain_dbi=gain_dbi,
            gain_dbd=gain_dbd,
            gain_linear=gain_linear,
            method="口径效率法"
        )
    
    def calculate_from_diameter(
        self,
        diameter_m: float,
        frequency_hz: float,
        efficiency: float = 0.55
    ) -> GainResult:
        """
        根据圆形口径直径计算增益
        
        公式: G = η × (πD/λ)²
        
        参数:
            diameter_m: 口径直径 (m)
            frequency_hz: 工作频率 (Hz)
            efficiency: 口径效率 (0~1)
        """
        if diameter_m <= 0:
            raise ValueError("直径必须为正值")
        
        # 计算圆形口径面积
        area = math.pi * (diameter_m / 2) ** 2
        
        result = self.calculate_from_aperture(area, frequency_hz, efficiency)
        result.method = "口径效率法 (圆形)"
        return result
    
    def calculate_from_rectangle(
        self,
        width_m: float,
        height_m: float,
        frequency_hz: float,
        efficiency: float = 0.60
    ) -> GainResult:
        """
        根据矩形口径尺寸计算增益 (适用于喇叭天线等)
        
        公式: G = η × (4πA/λ²), A = width × height
        
        参数:
            width_m: 口径宽度 (m), 通常对应H面
            height_m: 口径高度 (m), 通常对应E面
            frequency_hz: 工作频率 (Hz)
            efficiency: 口径效率 (0~1), 矩形喇叭典型0.5~0.65
        
        返回:
            GainResult: 计算结果
        
        典型口径效率参考 (矩形喇叭):
        - 0.50~0.55: 简单矩形喇叭
        - 0.55~0.65: 优化设计喇叭
        - 0.65~0.75: 波纹喇叭等高效设计
        """
        if width_m <= 0:
            raise ValueError("口径宽度必须为正值")
        if height_m <= 0:
            raise ValueError("口径高度必须为正值")
        
        # 计算矩形口径面积
        area = width_m * height_m
        
        result = self.calculate_from_aperture(area, frequency_hz, efficiency)
        result.method = "口径效率法 (矩形)"
        return result
    
    def convert_gain(
        self,
        gain_value: float,
        from_unit: str,
        to_unit: str
    ) -> float:
        """
        增益单位转换
        
        参数:
            gain_value: 原始增益值
            from_unit: 原始单位 ("dBi", "dBd", "linear")
            to_unit: 目标单位 ("dBi", "dBd", "linear")
        
        返回:
            转换后的增益值
        """
        # 先转换到dBi
        if from_unit == "dBi":
            gain_dbi = gain_value
        elif from_unit == "dBd":
            gain_dbi = gain_value + self.DBI_DBD_OFFSET
        elif from_unit == "linear":
            if gain_value <= 0:
                raise ValueError("线性增益必须为正值")
            gain_dbi = 10 * math.log10(gain_value)
        else:
            raise ValueError(f"不支持的单位: {from_unit}")
        
        # 从dBi转换到目标单位
        if to_unit == "dBi":
            return gain_dbi
        elif to_unit == "dBd":
            return gain_dbi - self.DBI_DBD_OFFSET
        elif to_unit == "linear":
            return 10 ** (gain_dbi / 10)
        else:
            raise ValueError(f"不支持的单位: {to_unit}")
    
    def calculate_eirp(
        self,
        tx_power_dbm: float,
        gain_dbi: float,
        cable_loss_db: float = 0
    ) -> dict:
        """
        计算等效各向同性辐射功率 (EIRP)
        
        公式: EIRP = P_tx + G - L_cable
        
        参数:
            tx_power_dbm: 发射功率 (dBm)
            gain_dbi: 天线增益 (dBi)
            cable_loss_db: 馈线损耗 (dB, 默认0)
        
        返回:
            包含EIRP相关参数的字典
        """
        eirp_dbm = tx_power_dbm + gain_dbi - cable_loss_db
        eirp_dbw = eirp_dbm - 30
        
        # 转换为瓦特
        eirp_w = 10 ** (eirp_dbw / 10)
        
        return {
            "eirp_dbm": eirp_dbm,
            "eirp_dbw": eirp_dbw,
            "eirp_w": eirp_w,
            "tx_power_dbm": tx_power_dbm,
            "gain_dbi": gain_dbi,
            "cable_loss_db": cable_loss_db
        }
    
    @staticmethod
    def get_gain_quality(gain_dbi: float) -> str:
        """
        根据增益值评估天线类型
        
        参数:
            gain_dbi: 增益 (dBi)
        
        返回:
            天线类型评估字符串
        """
        if gain_dbi < 0:
            return "🔴 低效天线 (负增益)"
        elif gain_dbi < 3:
            return "🔵 全向型 (如偶极子)"
        elif gain_dbi < 8:
            return "🟢 低增益定向"
        elif gain_dbi < 15:
            return "🟢 中等增益定向"
        elif gain_dbi < 25:
            return "🟡 高增益天线"
        else:
            return "🟠 极高增益 (如抛物面)"
    
    @staticmethod
    def estimate_beamwidth_from_gain(gain_dbi: float) -> Tuple[float, float]:
        """
        从增益估算对称波束宽度 (反向估算)
        
        参数:
            gain_dbi: 增益 (dBi)
        
        返回:
            (theta_estimate, None) 估算的对称波束宽度
        """
        gain_linear = 10 ** (gain_dbi / 10)
        # 假设对称波束 θ_E = θ_H
        # G = 41253 / θ² => θ = sqrt(41253 / G)
        theta = math.sqrt(41253 / gain_linear) if gain_linear > 0 else 180
        return (min(theta, 180), min(theta, 180))
