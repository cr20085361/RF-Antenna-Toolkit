# -*- coding: utf-8 -*-
"""
射频天线工具集 - 收发距离计算模块
RF Antenna Toolkit - Range Calculator Module

版本: v2.0.0
功能: 根据 Friis 传输方程计算最远收发通信距离
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class RangeParams:
    """距离计算输入参数"""
    tx_power_dbm: float        # 发射功率 (dBm)
    tx_gain_dbi: float         # 发射天线增益 (dBi)
    rx_gain_dbi: float         # 接收天线增益 (dBi)
    freq_mhz: float            # 工作频率 (MHz)
    rx_sensitivity_dbm: float  # 接收机灵敏度/底噪 (dBm)
    snr_req_db: float          # 解调信噪比 (dB)
    fade_margin_db: float      # 空间衰落余量 (dB)
    extra_loss_db: float       # 固定附加损耗 (dB)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_power_dbm": self.tx_power_dbm,
            "tx_gain_dbi": self.tx_gain_dbi,
            "rx_gain_dbi": self.rx_gain_dbi,
            "freq_mhz": self.freq_mhz,
            "rx_sensitivity_dbm": self.rx_sensitivity_dbm,
            "snr_req_db": self.snr_req_db,
            "fade_margin_db": self.fade_margin_db,
            "extra_loss_db": self.extra_loss_db
        }


@dataclass
class RangeResult:
    """距离计算输出结果"""
    max_range_km: float        # 最大距离 (km)
    fspl_db: float             # 此距离下的自由空间路损 (dB)
    eirp_dbm: float            # 等效全向辐射功率 (dBm)
    link_margin_db: float      # 链路余量 (此处通常为 0，因为算的是极限距离)

    @property
    def max_range_formatted(self) -> str:
        """格式化最大距离"""
        if self.max_range_km < 1.0:
            return f"{self.max_range_km * 1000:.2f} m"
        return f"{self.max_range_km:.2f} km"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_range_km": self.max_range_km,
            "fspl_db": self.fspl_db,
            "eirp_dbm": self.eirp_dbm,
            "link_margin_db": self.link_margin_db,
            "max_range_formatted": self.max_range_formatted
        }


class RangeCalculator:
    """
    收发距离计算器
    基于 Friis 传输方程 (自由空间路径损耗)
    """

    def calculate_max_range(self, params: RangeParams) -> RangeResult:
        """
        根据 Friis 传输方程计算最远通信距离。
        
        Friis 方程 (对数形式):
        Pr(dBm) = Pt(dBm) + Gt(dBi) + Gr(dBi) - FSPL(dB) - L_extra(dB)
        
        自由空间路损 FSPL(dB) = 20 * log10(d_km) + 20 * log10(f_MHz) + 32.44
        
        求解极限距离 d_km 使得 Pr = Rx_Sensitivity
        FSPL_max = Pt + Gt + Gr - Sensitivity - L_extra
        20 * log10(d_km) = FSPL_max - 20 * log10(f_MHz) - 32.44
        """
        # 计算 EIRP (等效全向辐射功率)
        eirp_dbm = params.tx_power_dbm + params.tx_gain_dbi

        # 实际需要的接收阈值 (灵敏度底线 + 解调信噪比 + 空间衰落余量)
        pr_req_dbm = params.rx_sensitivity_dbm + params.snr_req_db + params.fade_margin_db

        # 允许的最大自由空间路损
        fspl_max_db = eirp_dbm + params.rx_gain_dbi - pr_req_dbm - params.extra_loss_db

        # 反解距离 (km)
        # 移项: 20*log10(d) = FSPL - 20*log10(f_MHz) - 32.44
        # log10(d) = (FSPL - 20*log10(f_MHz) - 32.44) / 20
        # d = 10 ^ (...)
        power_term = (fspl_max_db - 20 * math.log10(params.freq_mhz) - 32.44) / 20.0
        max_range_km = math.pow(10, power_term)

        # 极限状态下，链路余量为 0
        link_margin_db = 0.0

        return RangeResult(
            max_range_km=max_range_km,
            fspl_db=fspl_max_db,
            eirp_dbm=eirp_dbm,
            link_margin_db=link_margin_db
        )

    def calculate_pr_at_distance(self, params: RangeParams, dist_km_array: List[float]) -> List[float]:
        """
        批量计算不同距离下的接收功率，用于绘制曲线。
        """
        pr_dbm_list = []
        eirp_dbm = params.tx_power_dbm + params.tx_gain_dbi
        
        for d in dist_km_array:
            if d <= 0:
                pr_dbm_list.append(eirp_dbm) # d=0 的奇异点处理
                continue
                
            fspl_db = 20 * math.log10(d) + 20 * math.log10(params.freq_mhz) + 32.44
            pr_dbm = eirp_dbm + params.rx_gain_dbi - fspl_db - params.extra_loss_db
            pr_dbm_list.append(pr_dbm)
            
        return pr_dbm_list
