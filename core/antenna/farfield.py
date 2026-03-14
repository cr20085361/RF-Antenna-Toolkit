# -*- coding: utf-8 -*-
"""
射频天线工具集 - 远场距离计算模块
RF Antenna Toolkit - Far-Field Distance Calculator

版本: v2.0.0
功能: 基于 IEEE 149-2019 / 3GPP TS 38.810 计算天线远场距离
      支持电大/电小天线自动判据切换与相控阵扫描角修正
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

from ..constants import SPEED_OF_LIGHT


class ApertureShape(Enum):
    """天线口径形状枚举"""
    DIRECT = "direct"           # 直接输入最大尺寸 D
    RECTANGULAR = "rectangular" # 矩形口径 (长×宽)
    CIRCULAR = "circular"       # 圆形口径 (直径)


class AntennaElectricalSize(Enum):
    """天线电尺寸分类"""
    ELECTRICALLY_LARGE = "electrically_large"   # 电大天线 (D/λ > 2.5)
    ELECTRICALLY_MODERATE = "electrically_moderate"  # 中等电尺寸 (1 < D/λ ≤ 2.5)
    ELECTRICALLY_SMALL = "electrically_small"   # 电小天线 (D/λ ≤ 1)


@dataclass
class FarFieldResult:
    """远场距离计算结果数据类"""

    # 核心输出
    far_field_distance_m: float       # 远场最终距离 (m), 取所有判据最大值
    reactive_near_field_m: float      # 反应性近场外边界 (m)
    radiative_near_field_m: float     # 辐射近场/菲涅尔区外边界 (= 远场起始)

    # 各分项判据值 (m)
    criterion_phase_m: float          # 相位判据: 2D²/λ
    criterion_5lambda_m: float        # 5λ 判据
    criterion_10lambda_m: float       # 10λ 判据 (保守)
    criterion_5d_m: float             # 5D 判据

    # 天线电尺寸信息
    d_over_lambda: float              # D/λ 比值
    electrical_size: AntennaElectricalSize  # 电尺寸分类
    dominant_criterion: str           # 主导判据名称

    # 输入参数回显
    frequency_hz: float               # 测试频率 (Hz)
    wavelength_m: float               # 对应波长 (m)
    aperture_d_m: float               # 天线口径 D (m)
    effective_d_m: float              # 有效口径 (含扫描角修正) (m)
    scan_angle_deg: float             # 波束扫描角 (°)

    @property
    def far_field_formatted(self) -> str:
        """格式化远场距离输出，自适应单位"""
        d = self.far_field_distance_m
        if d >= 1000:
            return f"{d / 1000:.2f} km"
        elif d >= 1:
            return f"{d:.2f} m"
        elif d >= 0.01:
            return f"{d * 100:.2f} cm"
        else:
            return f"{d * 1000:.2f} mm"

    @property
    def electrical_size_label(self) -> str:
        """电尺寸的中文标签"""
        mapping = {
            AntennaElectricalSize.ELECTRICALLY_LARGE: "电大天线 (D >> λ)",
            AntennaElectricalSize.ELECTRICALLY_MODERATE: "中等电尺寸 (D ~ λ)",
            AntennaElectricalSize.ELECTRICALLY_SMALL: "电小天线 (D ≤ λ)",
        }
        return mapping.get(self.electrical_size, "未知")


class FarFieldCalculator:
    """
    远场距离计算器

    依据标准:
    - IEEE 149-2019: Standard Test Procedures for Antennas
    - 3GPP TS 38.810: 5G NR OTA Measurement
    - CTIA OTA Test Plan

    三分区模型:
    ┌──────────────────────────────────────────────────────────────┐
    │ 反应性近场 → 辐射近场 (菲涅尔区) → 远场 (夫琅禾费区)        │
    │    0 ~ R_rn        R_rn ~ R_ff            R_ff ~ ∞          │
    │ R_rn = 0.62√(D³/λ)                R_ff = max(2D²/λ, Nλ,..) │
    └──────────────────────────────────────────────────────────────┘

    对于大型天线 (D >> λ), 相位判据 2D²/λ 占主导。
    对于小型天线 (D ~ λ 或更小), 场衰减判据 5λ/10λ 占主导。
    """

    def calculate(
        self,
        frequency_hz: float,
        aperture_d_m: float,
        scan_angle_deg: float = 0.0,
    ) -> FarFieldResult:
        """
        计算远场距离

        参数:
            frequency_hz: 测试频率 (Hz)
            aperture_d_m: 天线最大物理口径 D (m)
            scan_angle_deg: 波束扫描角 (°), 仅相控阵适用, 默认 0

        返回:
            FarFieldResult 包含完整三分区结果
        """
        # =============== 参数校验 ===============
        if frequency_hz <= 0:
            raise ValueError("频率必须为正数")
        if aperture_d_m <= 0:
            raise ValueError("天线口径 D 必须为正数")
        if not (0 <= scan_angle_deg < 90):
            raise ValueError("扫描角须在 [0, 90) 度范围内")

        # =============== 基础物理量 ===============
        wavelength_m = SPEED_OF_LIGHT / frequency_hz
        scan_angle_rad = math.radians(scan_angle_deg)

        # 有效口径修正 (相控阵波束偏转时投影面缩小)
        effective_d_m = aperture_d_m * math.cos(scan_angle_rad)

        # 电尺寸比
        d_over_lambda = effective_d_m / wavelength_m

        # 电尺寸分类
        if d_over_lambda > 2.5:
            electrical_size = AntennaElectricalSize.ELECTRICALLY_LARGE
        elif d_over_lambda > 1.0:
            electrical_size = AntennaElectricalSize.ELECTRICALLY_MODERATE
        else:
            electrical_size = AntennaElectricalSize.ELECTRICALLY_SMALL

        # =============== 各判据计算 ===============

        # 1. 相位判据 (IEEE 149 核心公式)
        #    确保 AUT 口径面上各点到观测点的路径差 < λ/16
        criterion_phase = (2.0 * effective_d_m ** 2) / wavelength_m

        # 2. 场衰减判据 (确保辐射场 >> 反应场)
        criterion_5lambda = 5.0 * wavelength_m
        criterion_10lambda = 10.0 * wavelength_m  # 保守值

        # 3. 最小绝对距离判据
        criterion_5d = 5.0 * effective_d_m

        # =============== 远场距离裁定 ===============
        # 取所有判据中的最大值 (IEEE 149 推荐的保守策略)
        candidates = {
            "相位判据 (2D²/λ)": criterion_phase,
            "场衰减判据 (5λ)": criterion_5lambda,
            "最小距离判据 (5D)": criterion_5d,
        }

        dominant_name = max(candidates, key=candidates.get)
        far_field_distance = candidates[dominant_name]

        # =============== 近场边界 ===============
        # 反应性近场外边界: 0.62√(D³/λ)
        reactive_near_field = 0.62 * math.sqrt(effective_d_m ** 3 / wavelength_m)

        # 辐射近场 (菲涅尔区) 外边界 = 远场起始
        radiative_near_field = far_field_distance

        return FarFieldResult(
            far_field_distance_m=far_field_distance,
            reactive_near_field_m=reactive_near_field,
            radiative_near_field_m=radiative_near_field,
            criterion_phase_m=criterion_phase,
            criterion_5lambda_m=criterion_5lambda,
            criterion_10lambda_m=criterion_10lambda,
            criterion_5d_m=criterion_5d,
            d_over_lambda=d_over_lambda,
            electrical_size=electrical_size,
            dominant_criterion=dominant_name,
            frequency_hz=frequency_hz,
            wavelength_m=wavelength_m,
            aperture_d_m=aperture_d_m,
            effective_d_m=effective_d_m,
            scan_angle_deg=scan_angle_deg,
        )

    @staticmethod
    def resolve_aperture(
        shape: ApertureShape,
        d_m: float = 0.0,
        length_m: float = 0.0,
        width_m: float = 0.0,
        diameter_m: float = 0.0,
    ) -> float:
        """
        根据口径形状解析出最大物理尺寸 D

        参数:
            shape: 口径形状枚举
            d_m: 直接输入的最大尺寸 (仅 DIRECT 模式)
            length_m: 矩形长边 (仅 RECTANGULAR 模式)
            width_m: 矩形短边 (仅 RECTANGULAR 模式)
            diameter_m: 圆形直径 (仅 CIRCULAR 模式)

        返回:
            天线最大物理尺寸 D (m)
        """
        if shape == ApertureShape.DIRECT:
            if d_m <= 0:
                raise ValueError("口径尺寸 D 必须为正数")
            return d_m
        elif shape == ApertureShape.RECTANGULAR:
            if length_m <= 0 or width_m <= 0:
                raise ValueError("矩形口径的长和宽必须为正数")
            return math.sqrt(length_m ** 2 + width_m ** 2)
        elif shape == ApertureShape.CIRCULAR:
            if diameter_m <= 0:
                raise ValueError("圆形口径的直径必须为正数")
            return diameter_m
        else:
            raise ValueError(f"不支持的口径形状: {shape}")

    @staticmethod
    def get_measurement_recommendation(result: FarFieldResult) -> str:
        """
        根据远场距离生成测量建议

        参数:
            result: FarFieldResult 计算结果

        返回:
            工程建议文本
        """
        d_over_lam = result.d_over_lambda
        r_ff = result.far_field_distance_m

        lines = []

        # 距离可行性评估
        if r_ff > 500:
            lines.append("⚠️ 远场距离超过 500m，建议考虑以下替代方案：")
            lines.append("• 紧缩场 (CATR) 测量系统")
            lines.append("• 近场-远场变换 (NF-FF Transformation)")
            lines.append("• 球面近场扫描 (SNF) 测量")
        elif r_ff > 100:
            lines.append("⚠️ 远场距离较大 (>100m)，室外远场测试场可满足。")
            lines.append("如需室内测试，可考虑小型紧缩场 (Mini-CATR)。")
        elif r_ff > 10:
            lines.append("✅ 远场距离适中，标准微波暗室可满足。")
        else:
            lines.append("✅ 远场距离较短，小型暗室或桌面测试台即可满足。")

        # 电尺寸提示
        if result.electrical_size == AntennaElectricalSize.ELECTRICALLY_SMALL:
            lines.append("")
            lines.append("💡 电小天线提示：")
            lines.append("• 当前为电小天线 (D/λ ≤ 1)，远场由场衰减判据主导。")
            lines.append("• 测试探头校准精度直接影响方向图质量。")
        elif result.electrical_size == AntennaElectricalSize.ELECTRICALLY_LARGE:
            if result.scan_angle_deg > 0:
                lines.append("")
                lines.append(f"📡 相控阵提示：波束偏转 {result.scan_angle_deg}° 后有效口径缩短，远场距离随之降低。")

        return "\n".join(lines)
