# -*- coding: utf-8 -*-
"""
射频天线工具集 - 级联驻波计算模块
RF Antenna Toolkit - Cascaded VSWR Calculator

版本: v1.0.0
功能: 计算多个射频组件级联后的总驻波比范围
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class CascadeResult:
    """级联驻波计算结果"""
    
    # 输入参数
    vswr_list: List[float]          # 各级VSWR值
    gamma_list: List[float]         # 各级反射系数
    
    # 计算结果
    gamma_min: float                # 最小合成反射系数
    gamma_max: float                # 最大合成反射系数
    vswr_min: float                 # 最小合成VSWR
    vswr_max: float                 # 最大合成VSWR
    
    # 最佳/最差情况
    return_loss_best: float         # 最佳回波损耗 (dB)
    return_loss_worst: float        # 最差回波损耗 (dB)


class CascadeCalculator:
    """
    级联驻波计算器
    
    原理说明:
    当两个或多个射频组件级联时，由于各组件之间的相位关系未知，
    合成的反射系数会在一定范围内变化：
    
    - 最差情况 (同相叠加): |Γ_max| = |Γ1| + |Γ2| + ... 
    - 最佳情况 (反相抵消): |Γ_min| = ||Γ1| - |Γ2|| (两级)
    
    对于多级级联，最小反射系数需要考虑各级的抵消组合。
    
    适用场景:
    - 同轴转波导 + 喇叭天线
    - 功分器 + 天线阵列
    - 馈电网络 + 天线单元
    - 任何多个射频组件的级联
    """
    
    @staticmethod
    def vswr_to_gamma(vswr: float) -> float:
        """VSWR转反射系数"""
        if vswr < 1:
            raise ValueError("VSWR必须≥1")
        return (vswr - 1) / (vswr + 1)
    
    @staticmethod
    def gamma_to_vswr(gamma: float) -> float:
        """反射系数转VSWR"""
        if gamma < 0:
            gamma = abs(gamma)
        if gamma >= 1:
            return float('inf')  # 全反射
        return (1 + gamma) / (1 - gamma)
    
    @staticmethod
    def gamma_to_return_loss(gamma: float) -> float:
        """反射系数转回波损耗 (dB)"""
        if gamma <= 0:
            return float('inf')  # 完美匹配
        return -20 * math.log10(gamma)
    
    def calculate_cascade(
        self,
        vswr_values: List[float]
    ) -> CascadeResult:
        """
        计算多级级联后的驻波范围
        
        参数:
            vswr_values: 各级组件的VSWR值列表
        
        返回:
            CascadeResult: 包含最大/最小驻波等信息
        
        说明:
            由于各级之间的电长度和相位未知，只能给出驻波的范围。
            工程上通常关注最差情况 (VSWR_max)。
        """
        if not vswr_values:
            raise ValueError("至少需要一个VSWR值")
        
        if len(vswr_values) == 1:
            # 单级情况
            vswr = vswr_values[0]
            gamma = self.vswr_to_gamma(vswr)
            return CascadeResult(
                vswr_list=vswr_values,
                gamma_list=[gamma],
                gamma_min=gamma,
                gamma_max=gamma,
                vswr_min=vswr,
                vswr_max=vswr,
                return_loss_best=self.gamma_to_return_loss(gamma),
                return_loss_worst=self.gamma_to_return_loss(gamma)
            )
        
        # 转换为反射系数
        gamma_list = [self.vswr_to_gamma(v) for v in vswr_values]
        
        # 最差情况：所有反射同相叠加
        gamma_max = sum(gamma_list)
        # 限制最大为0.999 (避免无穷大VSWR)
        gamma_max = min(gamma_max, 0.999)
        
        # 最佳情况：反射相互抵消
        # 对于两级：|Γ1 - Γ2|
        # 对于多级：最佳情况是部分抵消，这里采用保守估计
        if len(gamma_list) == 2:
            gamma_min = abs(gamma_list[0] - gamma_list[1])
        else:
            # 多级情况：最佳抵消估计
            # 将gamma按大小排序后，大的尝试与小的抵消
            sorted_gamma = sorted(gamma_list, reverse=True)
            remaining = sorted_gamma[0]
            for g in sorted_gamma[1:]:
                remaining = abs(remaining - g)
            gamma_min = remaining
        
        # 转换为VSWR
        vswr_min = self.gamma_to_vswr(gamma_min)
        vswr_max = self.gamma_to_vswr(gamma_max)
        
        return CascadeResult(
            vswr_list=vswr_values,
            gamma_list=gamma_list,
            gamma_min=gamma_min,
            gamma_max=gamma_max,
            vswr_min=vswr_min,
            vswr_max=vswr_max,
            return_loss_best=self.gamma_to_return_loss(gamma_min) if gamma_min > 0 else 999,
            return_loss_worst=self.gamma_to_return_loss(gamma_max)
        )
    
    def calculate_from_return_loss(
        self,
        return_loss_values: List[float]
    ) -> CascadeResult:
        """
        从回波损耗计算级联驻波范围
        
        参数:
            return_loss_values: 各级组件的回波损耗值列表 (dB, 正值)
        """
        # 回波损耗转VSWR
        vswr_values = []
        for rl in return_loss_values:
            gamma = 10 ** (-rl / 20)
            vswr = self.gamma_to_vswr(gamma)
            vswr_values.append(vswr)
        
        return self.calculate_cascade(vswr_values)
    
    @staticmethod
    def get_quality_assessment(vswr_max: float) -> str:
        """
        评估级联后的匹配质量
        
        参数:
            vswr_max: 最差情况VSWR
        """
        if vswr_max < 1.2:
            return "🟢 优秀 (VSWR < 1.2)"
        elif vswr_max < 1.5:
            return "🟢 良好 (VSWR < 1.5)"
        elif vswr_max < 2.0:
            return "🟡 可接受 (VSWR < 2.0)"
        elif vswr_max < 3.0:
            return "🟠 需注意 (VSWR < 3.0)"
        else:
            return "🔴 较差 (VSWR ≥ 3.0)"
    
    @staticmethod
    def get_mismatch_loss(vswr: float) -> float:
        """
        计算失配损耗 (dB)
        
        失配损耗 = -10 × log10(1 - Γ²)
        """
        gamma = (vswr - 1) / (vswr + 1)
        if gamma >= 1:
            return float('inf')
        return -10 * math.log10(1 - gamma ** 2)
