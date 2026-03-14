# -*- coding: utf-8 -*-
"""
射频天线工具集 - 衰减器计算模块
RF Antenna Toolkit - Attenuator Calculator

版本: v2.0.0
功能: 计算 T 型(星型)和 π 型衰减器的电阻值，
      支持标准阻值系列匹配与偏差分析
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


# ==================== 标准阻值系列 ====================
# 每个系列存储一个 decade (1.0 ~ 10.0) 内的基准值
# 实际阻值 = 基准值 × 10^n (n 为整数)

# E12 系列 (±10%)
E12_VALUES = [
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7,
    3.3, 3.9, 4.7, 5.6, 6.8, 8.2
]

# E24 系列 (±5%)
E24_VALUES = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0,
    2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3,
    4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
]

# E48 系列 (±2%)
E48_VALUES = [
    1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40,
    1.47, 1.54, 1.62, 1.69, 1.78, 1.87, 1.96, 2.05,
    2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
    3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42,
    4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49,
    6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53
]

# E96 系列 (±1%)
E96_VALUES = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18,
    1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43,
    1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10,
    2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55,
    2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74,
    3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53,
    4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
    6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06,
    8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76
]

# 系列名称映射
SERIES_MAP: Dict[str, List[float]] = {
    "E12": E12_VALUES,
    "E24": E24_VALUES,
    "E48": E48_VALUES,
    "E96": E96_VALUES,
}

# 系列容差说明
SERIES_TOLERANCE: Dict[str, str] = {
    "E12": "±10%",
    "E24": "±5%",
    "E48": "±2%",
    "E96": "±1%",
}


@dataclass
class AttenuatorResult:
    """衰减器计算结果数据类"""

    topology: str           # 拓扑类型: "T" 或 "π"
    z0: float               # 系统阻抗 (Ω)
    target_atten_db: float  # 目标衰减值 (dB)

    # 理想电阻值
    r1_ideal: float         # R1 理想值 (Ω)
    r2_ideal: float         # R2 理想值 (Ω)
    r3_ideal: float         # R3 理想值 (Ω, T型中 R3=R1)

    # 标准阻值匹配结果
    series_name: str = ""           # 使用的阻值系列名称
    r1_std: float = 0.0             # R1 标准值 (Ω)
    r2_std: float = 0.0             # R2 标准值 (Ω)
    r3_std: float = 0.0             # R3 标准值 (Ω)
    actual_atten_db: float = 0.0    # 使用标准阻值后的实际衰减 (dB)
    deviation_db: float = 0.0       # 偏差 = 实际衰减 - 目标衰减 (dB)


def find_nearest_standard(value: float, series: List[float]) -> float:
    """
    在标准阻值系列中查找最接近的值

    参数:
        value: 目标阻值 (Ω)
        series: 标准系列基准值列表 (1.0~10.0 范围)

    返回:
        最接近的标准阻值 (Ω)
    """
    if value <= 0:
        return series[0]  # 返回最小值

    # 确定 decade: 将 value 归一化到 [1.0, 10.0) 范围
    decade = 0
    normalized = value
    while normalized >= 10.0:
        normalized /= 10.0
        decade += 1
    while normalized < 1.0:
        normalized *= 10.0
        decade -= 1

    # 在系列中查找最近值
    best = series[0]
    best_ratio = abs(math.log10(normalized / best))
    for sv in series:
        ratio = abs(math.log10(normalized / sv))
        if ratio < best_ratio:
            best = sv
            best_ratio = ratio

    # 还要检查 10.0 (即下一个 decade 的 1.0)
    ratio_10 = abs(math.log10(normalized / 10.0))
    if ratio_10 < best_ratio:
        best = 1.0
        decade += 1

    return best * (10.0 ** decade)


class AttenuatorCalculator:
    """
    衰减器电阻计算器

    支持:
    - T 型 (星型) 对称衰减器
    - π 型对称衰减器
    - 标准阻值系列匹配 (E12/E24/E48/E96)
    - 实际衰减偏差分析
    """

    def calculate_t_type(self, z0: float, atten_db: float,
                         series: Optional[str] = None) -> AttenuatorResult:
        """
        计算 T 型 (星型) 衰减器电阻值

        电路拓扑:
            ──[R1]──┬──[R3]──
                    │
                   [R2]
                    │
            ────────┴────────

        参数:
            z0: 系统阻抗 (Ω), 通常 50 或 75
            atten_db: 目标衰减量 (dB, 正值)
            series: 标准阻值系列名称 ("E12"/"E24"/"E48"/"E96"/None)

        返回:
            AttenuatorResult: 计算结果
        """
        # 参数验证
        if z0 <= 0:
            raise ValueError("系统阻抗必须 > 0")
        if atten_db <= 0:
            raise ValueError("衰减值必须 > 0 dB")

        # 计算线性比值 K = 10^(dB/20)
        K = 10 ** (atten_db / 20.0)

        # T 型公式
        # R1 = R3 = Z0 × (K-1)/(K+1)
        # R2 = Z0 × 2K/(K²-1)
        r1 = z0 * (K - 1) / (K + 1)
        r2 = z0 * 2 * K / (K * K - 1)
        r3 = r1  # 对称衰减器

        result = AttenuatorResult(
            topology="T",
            z0=z0,
            target_atten_db=atten_db,
            r1_ideal=r1,
            r2_ideal=r2,
            r3_ideal=r3,
        )

        # 标准阻值匹配
        if series and series in SERIES_MAP:
            std_values = SERIES_MAP[series]
            r1_std = find_nearest_standard(r1, std_values)
            r2_std = find_nearest_standard(r2, std_values)
            r3_std = find_nearest_standard(r3, std_values)

            # 反算实际衰减
            actual_db = self._reverse_t_atten(z0, r1_std, r2_std, r3_std)

            result.series_name = series
            result.r1_std = r1_std
            result.r2_std = r2_std
            result.r3_std = r3_std
            result.actual_atten_db = actual_db
            result.deviation_db = actual_db - atten_db

        return result

    def calculate_pi_type(self, z0: float, atten_db: float,
                          series: Optional[str] = None) -> AttenuatorResult:
        """
        计算 π 型衰减器电阻值

        电路拓扑:
            ────────┬──[R2]──┬────────
                    │        │
                   [R1]     [R3]
                    │        │
            ────────┴────────┴────────

        参数:
            z0: 系统阻抗 (Ω)
            atten_db: 目标衰减量 (dB, 正值)
            series: 标准阻值系列名称

        返回:
            AttenuatorResult: 计算结果
        """
        if z0 <= 0:
            raise ValueError("系统阻抗必须 > 0")
        if atten_db <= 0:
            raise ValueError("衰减值必须 > 0 dB")

        K = 10 ** (atten_db / 20.0)

        # π 型公式
        # R1 = R3 = Z0 × (K+1)/(K-1)
        # R2 = Z0 × (K²-1)/(2K)
        r1 = z0 * (K + 1) / (K - 1)
        r2 = z0 * (K * K - 1) / (2 * K)
        r3 = r1

        result = AttenuatorResult(
            topology="π",
            z0=z0,
            target_atten_db=atten_db,
            r1_ideal=r1,
            r2_ideal=r2,
            r3_ideal=r3,
        )

        if series and series in SERIES_MAP:
            std_values = SERIES_MAP[series]
            r1_std = find_nearest_standard(r1, std_values)
            r2_std = find_nearest_standard(r2, std_values)
            r3_std = find_nearest_standard(r3, std_values)

            actual_db = self._reverse_pi_atten(z0, r1_std, r2_std, r3_std)

            result.series_name = series
            result.r1_std = r1_std
            result.r2_std = r2_std
            result.r3_std = r3_std
            result.actual_atten_db = actual_db
            result.deviation_db = actual_db - atten_db

        return result

    @staticmethod
    def _reverse_t_atten(z0: float, r1: float, r2: float, r3: float) -> float:
        """
        根据 T 型电阻值反算衰减量 (dB)

        使用 ABCD 矩阵法:
          T 型网络的 ABCD 矩阵:
          A = 1 + R1/R2
          B = R1 + R3 + R1*R3/R2
          C = 1/R2
          D = 1 + R3/R2

          插入损耗 IL = 20*log10(|A + B/Z0 + C*Z0 + D| / 2)
        """
        try:
            A = 1 + r1 / r2
            B = r1 + r3 + r1 * r3 / r2
            C = 1.0 / r2
            D = 1 + r3 / r2
            il = abs(A + B / z0 + C * z0 + D) / 2.0
            if il <= 0:
                return 0.0
            return 20 * math.log10(il)
        except (ZeroDivisionError, ValueError):
            return 0.0

    @staticmethod
    def _reverse_pi_atten(z0: float, r1: float, r2: float, r3: float) -> float:
        """
        根据 π 型电阻值反算衰减量 (dB)

        π 型网络的 ABCD 矩阵:
          A = 1 + R2/R3
          B = R2
          C = 1/R1 + 1/R3 + R2/(R1*R3)
          D = 1 + R2/R1

          插入损耗 IL = 20*log10(|A + B/Z0 + C*Z0 + D| / 2)
        """
        try:
            A = 1 + r2 / r3
            B = r2
            C = 1.0 / r1 + 1.0 / r3 + r2 / (r1 * r3)
            D = 1 + r2 / r1
            il = abs(A + B / z0 + C * z0 + D) / 2.0
            if il <= 0:
                return 0.0
            return 20 * math.log10(il)
        except (ZeroDivisionError, ValueError):
            return 0.0

    @staticmethod
    def format_resistance(value: float) -> str:
        """
        格式化电阻值显示

        根据量级自动选择单位:
        - < 1Ω: 显示 mΩ
        - < 1000Ω: 显示 Ω
        - >= 1000Ω: 显示 kΩ
        """
        if value < 1:
            return f"{value * 1000:.1f} mΩ"
        elif value < 1000:
            if value == int(value):
                return f"{int(value)} Ω"
            return f"{value:.2f} Ω"
        else:
            return f"{value / 1000:.2f} kΩ"
