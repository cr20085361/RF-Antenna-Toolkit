# -*- coding: utf-8 -*-
"""
核心计算逻辑 - 干扰压制计算器
Core Logic - Jamming / Interference Suppression Calculator

功能:
- 基于自由空间路径损耗(FSPL)评估干扰机对目标接收机的压制效果
- 计算到达目标的干扰功率 (Received Jamming Power, P_J)
- 计算最大有效压制距离 (Max Jamming Distance)
- 提供量化改进建议所需的数据
"""

import math
import copy
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class JammingParams:
    """干扰压制计算输入参数"""
    # 干扰机参数 (Jammer Parameters)
    freq_mhz: float = 1000.0          # 发射频率 (MHz)
    tx_power_dbm: float = 40.0        # 功放输出功率 (dBm) - 默认10W
    tx_gain_dbi: float = 10.0         # 干扰发射天线增益 (dBi)
    tx_cable_loss_db: float = 1.0     # 干扰发射端馈线损耗 (dB)
    
    # 目标参数 (Target Parameters)
    rx_gain_dbi: float = 2.0          # 目标接收天线增益 (向着干扰机方向) (dBi)
    rx_cable_loss_db: float = 0.0     # 目标接收端馈线损耗 (dB)
    rx_threshold_dbm: float = -90.0   # 目标接收门限功率 (dBm) - 比如接收机灵敏度或正常通信信号强度
    js_req_db: float = 3.0            # 要求压制干信比 (J/S) (dB)
    
    target_distance_km: float = 5.0   # 当前评估的实际目标距离 (km)


@dataclass
class JammingResult:
    """干扰压制计算结果"""
    actual_pj_dbm: float              # 当前目标距离下，到达接收机的干扰功率 (dBm)
    max_distance_km: float            # 能够满足压制条件的最大距离 (km)
    
    # 压制评估与量化建议
    is_suppressed: bool               # 当前距离下是否成功压制
    margin_db: float                  # 压制余量 (dB)，正数表示有余量，负数表示不足(即功率缺口)
    
    # 辅助建议数据
    required_tx_power_dbm: float      # 在当前距离下，为了成功压制需要的发射功率 (dBm)
    required_tx_gain_dbi: float       # 在当前距离下，为了成功压制需要的发射天线增益 (dBi)


class JammingCalculator:
    """干扰压制计算器实现类"""
    
    def __init__(self):
        # FSPL 常数: 20 * log10(4 * pi / c), 单位 km 和 MHz 时约为 32.44
        self.fspl_constant = 32.44
        
    def calculate_fspl(self, freq_mhz: float, distance_km: float) -> float:
        """计算自由空间路径损耗 (dB)"""
        if freq_mhz <= 0 or distance_km <= 0:
            return 0.0
        return self.fspl_constant + 20 * math.log10(freq_mhz) + 20 * math.log10(distance_km)
        
    def calculate_distance_from_fspl(self, freq_mhz: float, fspl_db: float) -> float:
        """根据路径损耗反推距离 (km)"""
        if freq_mhz <= 0:
            return 0.0
        # FSPL = 32.44 + 20*log10(f) + 20*log10(d)
        # 20*log10(d) = FSPL - 32.44 - 20*log10(f)
        log_d = (fspl_db - self.fspl_constant - 20 * math.log10(freq_mhz)) / 20.0
        return 10 ** log_d

    def calculate(self, params: JammingParams) -> JammingResult:
        """执行干扰计算"""
        # 计算系统要求到达的最低干扰功率 (Required P_J)
        # 成功压制条件: P_J >= P_threshold + J/S_req
        required_pj_dbm = params.rx_threshold_dbm + params.js_req_db
        
        # ----------------------------------------------------
        # 1. 计算当前目标距离下的实际干扰功率 (Actual P_J)
        # ----------------------------------------------------
        actual_fspl = self.calculate_fspl(params.freq_mhz, params.target_distance_km)
        
        # P_J = P_tx + G_tx - L_tx_cable - FSPL + G_rx - L_rx_cable
        actual_pj_dbm = (params.tx_power_dbm + params.tx_gain_dbi - params.tx_cable_loss_db 
                         - actual_fspl 
                         + params.rx_gain_dbi - params.rx_cable_loss_db)
                         
        # 计算压制余量 (Margin) = 实际 P_J - 要求 P_J
        # 大于0表示已压制且有余量，小于0表示未压制存在缺口
        margin_db = actual_pj_dbm - required_pj_dbm
        is_suppressed = margin_db >= 0
        
        # ----------------------------------------------------
        # 2. 计算最大有效压制距离 (Max Distance)
        # ----------------------------------------------------
        # P_J_max_dist = P_tx + G_tx - L_tx_cable - FSPL_max + G_rx - L_rx_cable = required_pj_dbm
        # FSPL_max = P_tx + G_tx - L_tx_cable + G_rx - L_rx_cable - required_pj_dbm
        max_allowed_fspl = (params.tx_power_dbm + params.tx_gain_dbi - params.tx_cable_loss_db 
                            + params.rx_gain_dbi - params.rx_cable_loss_db 
                            - required_pj_dbm)
                            
        if max_allowed_fspl > 0:
            max_distance_km = self.calculate_distance_from_fspl(params.freq_mhz, max_allowed_fspl)
        else:
            # 说明甚至连 0 距离下的固定损耗都无法克服，最大距离视为 0
            max_distance_km = 0.0
            
        # ----------------------------------------------------
        # 3. 提供量化建议数据
        # ----------------------------------------------------
        # 为了在 target_distance_km 下成功压制，我们需要补齐 deficit (即 -margin_db，如果 margin < 0)
        deficit = -margin_db if margin_db < 0 else 0.0
        
        required_tx_power_dbm = params.tx_power_dbm + deficit
        required_tx_gain_dbi = params.tx_gain_dbi + deficit
        
        return JammingResult(
            actual_pj_dbm=actual_pj_dbm,
            max_distance_km=max_distance_km,
            is_suppressed=is_suppressed,
            margin_db=margin_db,
            required_tx_power_dbm=required_tx_power_dbm,
            required_tx_gain_dbi=required_tx_gain_dbi
        )

    def calculate_broadband(self, base_params: JammingParams, freq_overrides: List[Dict[str, float]]) -> Dict[float, JammingResult]:
        """批量计算宽带下的多个频点，支持每个频点独立配置发射功率和增益"""
        results = {}
        for override in freq_overrides:
            temp_params = copy.copy(base_params)
            temp_params.freq_mhz = override.get('freq_mhz', temp_params.freq_mhz)
            temp_params.tx_power_dbm = override.get('tx_power_dbm', temp_params.tx_power_dbm)
            temp_params.tx_gain_dbi = override.get('tx_gain_dbi', temp_params.tx_gain_dbi)
            temp_params.rx_gain_dbi = override.get('rx_gain_dbi', temp_params.rx_gain_dbi)
            
            results[temp_params.freq_mhz] = self.calculate(temp_params)
        return results
