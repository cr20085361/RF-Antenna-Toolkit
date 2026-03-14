# -*- coding: utf-8 -*-
"""
射频天线工具集 - 带宽计算模块
RF Antenna Toolkit - Bandwidth Calculator

版本: v2.0.0
功能: 提供各种带宽定义的相互转换与计算
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class BandwidthResult:
    """带宽计算结果数据类"""
    
    # 频率参数
    center_freq_hz: float       # 中心频率 (Hz)
    lower_freq_hz: float        # 下限频率 (Hz)
    upper_freq_hz: float        # 上限频率 (Hz)
    
    # 带宽指标
    absolute_bw_hz: float       # 绝对带宽 (Hz)
    fractional_bw_percent: float  # 分数带宽 / 相对带宽 (%)
    octave_bw: float            # 倍频程带宽
    q_factor: float             # Q值
    
    @property
    def absolute_bw_mhz(self) -> float:
        """绝对带宽 (MHz)"""
        return self.absolute_bw_hz / 1e6
    
    @property
    def absolute_bw_ghz(self) -> float:
        """绝对带宽 (GHz)"""
        return self.absolute_bw_hz / 1e9
    
    @property
    def center_freq_mhz(self) -> float:
        """中心频率 (MHz)"""
        return self.center_freq_hz / 1e6
    
    @property
    def center_freq_ghz(self) -> float:
        """中心频率 (GHz)"""
        return self.center_freq_hz / 1e9


class BandwidthCalculator:
    """
    带宽计算器
    
    提供多种带宽定义之间的转换:
    - 绝对带宽 (Absolute Bandwidth)
    - 分数带宽 / 相对带宽 (Fractional Bandwidth)
    - 倍频程带宽 (Octave Bandwidth)
    - Q值 (Quality Factor)
    """
    
    def calculate_from_freq_range(
        self, 
        lower_freq_hz: float, 
        upper_freq_hz: float
    ) -> BandwidthResult:
        """
        根据频率范围计算带宽指标
        
        参数:
            lower_freq_hz: 下限频率 (Hz)
            upper_freq_hz: 上限频率 (Hz)
        
        返回:
            BandwidthResult: 计算结果
        """
        if lower_freq_hz <= 0 or upper_freq_hz <= 0:
            raise ValueError("频率必须为正值")
        if lower_freq_hz >= upper_freq_hz:
            raise ValueError("上限频率必须大于下限频率")
        
        # 绝对带宽
        absolute_bw = upper_freq_hz - lower_freq_hz
        
        # 中心频率 (算术平均)
        center_freq = (lower_freq_hz + upper_freq_hz) / 2
        
        # 分数带宽 (%)
        fractional_bw = (absolute_bw / center_freq) * 100
        
        # 倍频程带宽 (对数比)
        octave_bw = math.log2(upper_freq_hz / lower_freq_hz)
        
        # Q值
        q_factor = center_freq / absolute_bw
        
        return BandwidthResult(
            center_freq_hz=center_freq,
            lower_freq_hz=lower_freq_hz,
            upper_freq_hz=upper_freq_hz,
            absolute_bw_hz=absolute_bw,
            fractional_bw_percent=fractional_bw,
            octave_bw=octave_bw,
            q_factor=q_factor
        )
    
    def calculate_from_center_and_bw(
        self,
        center_freq_hz: float,
        absolute_bw_hz: float
    ) -> BandwidthResult:
        """
        根据中心频率和绝对带宽计算
        
        参数:
            center_freq_hz: 中心频率 (Hz)
            absolute_bw_hz: 绝对带宽 (Hz)
        """
        if center_freq_hz <= 0 or absolute_bw_hz <= 0:
            raise ValueError("频率和带宽必须为正值")
        if absolute_bw_hz >= 2 * center_freq_hz:
            raise ValueError("带宽不能超过2倍中心频率")
        
        lower_freq = center_freq_hz - absolute_bw_hz / 2
        upper_freq = center_freq_hz + absolute_bw_hz / 2
        
        return self.calculate_from_freq_range(lower_freq, upper_freq)
    
    def calculate_from_center_and_fbw(
        self,
        center_freq_hz: float,
        fractional_bw_percent: float
    ) -> BandwidthResult:
        """
        根据中心频率和分数带宽计算
        
        参数:
            center_freq_hz: 中心频率 (Hz)
            fractional_bw_percent: 分数带宽 (%)
        """
        if center_freq_hz <= 0 or fractional_bw_percent <= 0:
            raise ValueError("频率和带宽必须为正值")
        if fractional_bw_percent >= 200:
            raise ValueError("分数带宽不能超过200%")
        
        # 从分数带宽计算绝对带宽
        absolute_bw = center_freq_hz * (fractional_bw_percent / 100)
        
        return self.calculate_from_center_and_bw(center_freq_hz, absolute_bw)
    
    def calculate_from_center_and_q(
        self,
        center_freq_hz: float,
        q_factor: float
    ) -> BandwidthResult:
        """
        根据中心频率和Q值计算
        
        参数:
            center_freq_hz: 中心频率 (Hz)
            q_factor: Q值
        """
        if center_freq_hz <= 0 or q_factor <= 0:
            raise ValueError("频率和Q值必须为正值")
        
        # 从Q值计算绝对带宽: BW = f_center / Q
        absolute_bw = center_freq_hz / q_factor
        
        return self.calculate_from_center_and_bw(center_freq_hz, absolute_bw)
    
    @staticmethod
    def get_bandwidth_quality(fractional_bw: float) -> str:
        """
        根据分数带宽评估天线带宽特性
        
        参数:
            fractional_bw: 分数带宽 (%)
        
        返回:
            带宽特性评估字符串
        """
        if fractional_bw < 1:
            return "🔵 极窄带 (谐振型)"
        elif fractional_bw < 5:
            return "🔵 窄带"
        elif fractional_bw < 20:
            return "🟢 中等带宽"
        elif fractional_bw < 50:
            return "🟡 宽带"
        elif fractional_bw < 100:
            return "🟠 超宽带"
        else:
            return "🔴 极宽带 (>1倍频程)"
    
    @staticmethod
    def freq_to_best_unit(freq_hz: float) -> Tuple[float, str]:
        """
        将频率转换为最合适的单位
        
        返回:
            (数值, 单位字符串) 元组
        """
        if freq_hz >= 1e9:
            return (freq_hz / 1e9, "GHz")
        elif freq_hz >= 1e6:
            return (freq_hz / 1e6, "MHz")
        elif freq_hz >= 1e3:
            return (freq_hz / 1e3, "kHz")
        else:
            return (freq_hz, "Hz")
    
    @staticmethod
    def parse_freq_with_unit(value: float, unit: str) -> float:
        """
        将带单位的频率值转换为Hz
        
        参数:
            value: 数值
            unit: 单位 (Hz, kHz, MHz, GHz)
        
        返回:
            频率 (Hz)
        """
        unit_multipliers = {
            "Hz": 1,
            "kHz": 1e3,
            "MHz": 1e6,
            "GHz": 1e9
        }
        return value * unit_multipliers.get(unit, 1)
