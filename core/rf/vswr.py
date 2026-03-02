# -*- coding: utf-8 -*-
"""
射频天线工具集 - 驻波(VSWR)计算模块
RF Antenna Toolkit - VSWR Calculator

版本: v1.0.0
功能: 提供驻波比与反射系数、回波损耗、失配损耗等指标的相互转换
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class VSWRResult:
    """驻波计算结果数据类
    
    v1.1: 新增S11属性
    """
    
    # 输入参数
    vswr: float                      # 驻波比 (无量纲, ≥1)
    
    # 计算结果
    reflection_coefficient: float    # 反射系数 |Γ| (0~1)
    return_loss_db: float            # 回波损耗 (dB, 正值)
    mismatch_loss_db: float          # 失配损耗 (dB)
    transmitted_power_ratio: float   # 传输功率比 (0~1)
    reflected_power_ratio: float     # 反射功率比 (0~1)
    
    @property
    def s11_db(self) -> float:
        """
        S11参数 (dB)
        S11 = 20*log10(|Γ|) = -Return Loss
        网分仪常用格式，负值表示反射衰减
        """
        if self.reflection_coefficient > 0:
            return 20 * math.log10(self.reflection_coefficient)
        else:
            return float('-inf')  # 完美匹配
    
    @property
    def reflection_coefficient_percent(self) -> float:
        """反射系数百分比"""
        return self.reflection_coefficient * 100
    
    @property
    def transmitted_power_percent(self) -> float:
        """传输功率百分比"""
        return self.transmitted_power_ratio * 100
    
    @property
    def reflected_power_percent(self) -> float:
        """反射功率百分比"""
        return self.reflected_power_ratio * 100


class VSWRCalculator:
    """
    驻波比(VSWR)计算器
    
    提供驻波比与其他射频参数之间的转换:
    - 反射系数 |Γ|
    - 回波损耗 (Return Loss)
    - 失配损耗 (Mismatch Loss)
    - 传输/反射功率比
    """
    
    def calculate_from_vswr(self, vswr: float) -> VSWRResult:
        """
        根据驻波比计算相关参数
        
        参数:
            vswr: 驻波比 (≥1)
        
        返回:
            VSWRResult: 计算结果
        
        异常:
            ValueError: 当VSWR < 1时抛出
        """
        # 参数验证
        if vswr < 1.0:
            raise ValueError("驻波比必须 ≥ 1")
        
        # 计算反射系数 |Γ| = (VSWR - 1) / (VSWR + 1)
        reflection_coeff = (vswr - 1) / (vswr + 1)
        
        # 计算回波损耗 RL = -20 * log10(|Γ|)
        if reflection_coeff > 0:
            return_loss = -20 * math.log10(reflection_coeff)
        else:
            return_loss = float('inf')  # 完美匹配
        
        # 计算反射功率比 = |Γ|²
        reflected_power = reflection_coeff ** 2
        
        # 计算传输功率比 = 1 - |Γ|²
        transmitted_power = 1 - reflected_power
        
        # 计算失配损耗 ML = -10 * log10(1 - |Γ|²)
        if transmitted_power > 0:
            mismatch_loss = -10 * math.log10(transmitted_power)
        else:
            mismatch_loss = float('inf')
        
        return VSWRResult(
            vswr=vswr,
            reflection_coefficient=reflection_coeff,
            return_loss_db=return_loss,
            mismatch_loss_db=mismatch_loss,
            transmitted_power_ratio=transmitted_power,
            reflected_power_ratio=reflected_power,
        )
    
    def calculate_from_reflection_coefficient(self, gamma: float) -> VSWRResult:
        """
        根据反射系数计算VSWR和其他参数
        
        参数:
            gamma: 反射系数模值 |Γ| (0~1)
        
        返回:
            VSWRResult: 计算结果
        """
        if gamma < 0 or gamma >= 1:
            raise ValueError("反射系数必须在 [0, 1) 范围内")
        
        # 计算VSWR = (1 + |Γ|) / (1 - |Γ|)
        vswr = (1 + gamma) / (1 - gamma)
        
        return self.calculate_from_vswr(vswr)
    
    def calculate_from_return_loss(self, return_loss_db: float) -> VSWRResult:
        """
        根据回波损耗计算VSWR和其他参数
        
        参数:
            return_loss_db: 回波损耗 (dB, 正值)
        
        返回:
            VSWRResult: 计算结果
        """
        if return_loss_db <= 0:
            raise ValueError("回波损耗必须为正值 (dB)")
        
        # 计算反射系数 |Γ| = 10^(-RL/20)
        gamma = 10 ** (-return_loss_db / 20)
        
        return self.calculate_from_reflection_coefficient(gamma)
    
    @staticmethod
    def get_vswr_quality(vswr: float) -> str:
        """
        根据VSWR值评估匹配质量
        
        参数:
            vswr: 驻波比
        
        返回:
            质量评估字符串
        """
        if vswr < 1.1:
            return "🟢 极佳 (专业级)"
        elif vswr < 1.3:
            return "🟢 优秀"
        elif vswr < 1.5:
            return "🟡 良好"
        elif vswr < 2.0:
            return "🟡 可接受"
        elif vswr < 3.0:
            return "🟠 较差"
        else:
            return "🔴 严重失配"
    
    @staticmethod
    def calculate_load_impedance(
        gamma: float, 
        z0: float = 50.0,
        gamma_phase_deg: float = 0.0
    ) -> complex:
        """
        根据反射系数计算负载阻抗
        
        参数:
            gamma: 反射系数模值 |Γ|
            z0: 特性阻抗 (欧姆), 默认50Ω
            gamma_phase_deg: 反射系数相位角 (度), 默认0
        
        返回:
            负载阻抗 Z_L (复数)
        
        公式:
            Z_L = Z0 * (1 + Γ) / (1 - Γ)
        """
        # 将模值和相位转换为复数形式
        gamma_phase_rad = math.radians(gamma_phase_deg)
        gamma_complex = gamma * (math.cos(gamma_phase_rad) + 1j * math.sin(gamma_phase_rad))
        
        # Z_L = Z0 * (1 + Γ) / (1 - Γ)
        if abs(1 - gamma_complex) < 1e-10:
            return complex(float('inf'), 0)  # 开路
        
        z_load = z0 * (1 + gamma_complex) / (1 - gamma_complex)
        return z_load
    
    @staticmethod
    def calculate_max_voltage(
        input_power_w: float,
        z0: float = 50.0,
        vswr: float = 1.0
    ) -> tuple:
        """
        计算传输线上的最大电压和电流
        
        参数:
            input_power_w: 输入功率 (W)
            z0: 特性阻抗 (欧姆)
            vswr: 驻波比
        
        返回:
            (V_max, V_min, I_max, I_min) 元组
        
        公式:
            V_rms = sqrt(P * Z0)  # 行波电压
            V_max = V_rms * sqrt(VSWR)  # 最大电压 (VSWR >1 时)
            V_min = V_rms / sqrt(VSWR)  # 最小电压
        """
        if input_power_w <= 0 or z0 <= 0 or vswr < 1:
            return (0, 0, 0, 0)
        
        # 行波电压 RMS
        v_rms = math.sqrt(input_power_w * z0)
        i_rms = math.sqrt(input_power_w / z0)
        
        # 驻波导致的最大/最小值
        sqrt_vswr = math.sqrt(vswr)
        v_max = v_rms * sqrt_vswr
        v_min = v_rms / sqrt_vswr
        i_max = i_rms * sqrt_vswr
        i_min = i_rms / sqrt_vswr
        
        return (v_max, v_min, i_max, i_min)
