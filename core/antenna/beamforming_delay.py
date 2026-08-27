# -*- coding: utf-8 -*-
"""
核心计算逻辑 - 相控阵通道移相与时延配置计算器
Core Logic - Phased Array Beamforming Phase & Delay Calculator

版本: v1.0.0
功能:
- 支持一维线阵 (ULA) 与二维平面阵 (UPA) 的通道相位与时延配置
- 支持物理间距 (mm) 与电长度波长倍数 (d/λ) 的双向无缝换算
- 计算相邻阵元及各通道理论相位差、连续展开相位、[0, 360) 模360 寄存器相位
- 支持移相器位宽量化 (3~8 bit 及自定义)，生成寄存器量化码字 (Dec/Hex) 与量化误差评估
- 宽带波束斜视 (Beam Squint) 模型分析，对比传统移相器与真时延 (TTD) 在频偏下的波束漂移
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

from ..constants import SPEED_OF_LIGHT, DEG_TO_RAD, RAD_TO_DEG


class ArrayGeometry(Enum):
    """阵列几何拓扑"""
    ULA = "ula"  # 一维均匀线阵 (Uniform Linear Array)
    UPA = "upa"  # 二维均匀平面阵 (Uniform Planar Array)


@dataclass
class ChannelConfig:
    """单个通道的详细配置与量化数据"""
    channel_id: int                    # 通道顺序编号 (1, 2, ..., N)
    row_idx: int                       # 行索引 (1-indexed)
    col_idx: int                       # 列索引 (1-indexed)
    pos_x_mm: float                    # X轴物理坐标 (mm)
    pos_y_mm: float                    # Y轴物理坐标 (mm)
    unwrapped_phase_deg: float         # 连续展开绝对理论相位 (°)
    wrapped_phase_deg: float           # [0°, 360°) 模360寄存器相位 (°)
    sym_phase_deg: float               # [-180°, +180°] 对称相位 (°)
    quantized_phase_deg: float         # 移相器量化后相位 (°)
    quantized_code: int                # 移相器量化十进制码字 (0 ~ 2^B - 1)
    quantized_hex: str                 # 移相器十六进制码字 (如 "0x1A")
    phase_error_deg: float             # 量化相位误差 (°)
    delay_ps: float                    # 理论绝对时延 (ps)
    delay_ns: float                    # 理论绝对时延 (ns)
    relative_delay_ps: float           # 相对全阵列首元的非负相对时延 (ps)


@dataclass
class BeamSquintPoint:
    """频偏点处的波束斜视计算数据"""
    frequency_hz: float                # 计算频点 (Hz)
    frequency_ghz: float               # 计算频点 (GHz)
    offset_percent: float              # 相对中心频点的百分比偏移量 (%)
    actual_beam_deg: Optional[float]   # 移相器波束实际指向偏角 (°)，超出可见区为 None
    squint_error_deg: Optional[float]  # 移相器波束偏转误差 (°)
    ttd_beam_deg: float                # 真时延 (TTD) 波束指向 (°，恒定)


@dataclass
class BeamformingDelayParams:
    """相控阵通道移相与时延输入参数"""
    geometry: ArrayGeometry = ArrayGeometry.ULA  # 阵列拓扑 (ULA / UPA)
    num_x: int = 8                               # X轴阵元数 (ULA 模式下的总阵元数)
    num_y: int = 1                               # Y轴阵元数 (仅 UPA 模式有效，默认 1)
    frequency_hz: float = 10.0e9                 # 工作频率 (Hz)，默认 10 GHz
    spacing_x_m: float = 0.015                   # X轴阵元间距 (m)
    spacing_y_m: float = 0.015                   # Y轴阵元间距 (m)
    scan_theta_deg: float = 30.0                 # 扫描偏角/俯仰角 θ (度, ULA: -90~+90°, UPA: 0~90°)
    scan_phi_deg: float = 0.0                    # 扫描方位角 φ (度, 仅 UPA: 0~360°)
    quant_bits: int = 6                          # 移相器量化位数 (0 为理想连续无量化，常用 4, 5, 6, 8)
    squint_bandwidth_hz: float = 2.0e9           # 评估波束斜视的分析带宽 (Hz, 默认 2 GHz)
    squint_num_points: int = 51                  # 波束斜视采样点数


@dataclass
class BeamformingDelayResult:
    """相控阵移相与时延完整计算结果"""
    # 基础物理电参数
    wavelength_m: float                          # 自由空间工作波长 (m)
    wavelength_mm: float                         # 自由空间工作波长 (mm)
    spacing_x_lambda: float                      # X 轴间距 (以波长 λ 为单位)
    spacing_y_lambda: float                      # Y 轴间距 (以波长 λ 为单位)
    
    # 核心理论相位与时延差 (相邻阵元)
    delta_phase_x_deg: float                     # X 轴相邻阵元理论相位差 (°)
    delta_phase_y_deg: float                     # Y 轴相邻阵元理论相位差 (°)
    delta_delay_x_ps: float                      # X 轴相邻阵元理论时延差 (ps)
    delta_delay_y_ps: float                      # Y 轴相邻阵元理论时延差 (ps)
    
    # 阵列整体时延特性
    max_array_delay_ps: float                    # 全阵列最大相对时延跨度 (ps)
    max_array_delay_ns: float                    # 全阵列最大相对时延跨度 (ns)
    
    # 移相器量化特性
    phase_lsb_deg: float                         # 移相器量化步进 LSB (°)
    rms_phase_error_deg: float                   # 全通道均方根量化误差 (°)
    max_phase_error_deg: float                   # 全通道最大量化绝对误差 (°)
    
    # 通道明细数据表
    channels: List[ChannelConfig] = field(default_factory=list)
    
    # 宽带波束斜视 (Beam Squint) 分析
    squint_analysis: List[BeamSquintPoint] = field(default_factory=list)
    max_squint_error_deg: float = 0.0            # 在分析带宽边缘的最大斜视漂移角 (°)
    is_squint_cutoff: bool = False               # 是否在频带边缘出现波束移出可见区 (超出 ±90°)


class BeamformingDelayCalculator:
    """
    相控阵波束赋形通道移相与时延计算引擎
    """

    @staticmethod
    def calc_wavelength(frequency_hz: float) -> float:
        """根据频率计算自由空间波长 (m)"""
        if frequency_hz <= 0:
            raise ValueError("工作频率必须为正数")
        return SPEED_OF_LIGHT / frequency_hz

    @staticmethod
    def physical_to_electrical_spacing(spacing_m: float, frequency_hz: float) -> float:
        """物理间距 (m) 转为 电长度 (d/λ)"""
        wavelength = BeamformingDelayCalculator.calc_wavelength(frequency_hz)
        return spacing_m / wavelength

    @staticmethod
    def electrical_to_physical_spacing(spacing_lambda: float, frequency_hz: float) -> float:
        """电长度 (d/λ) 转为 物理间距 (m)"""
        wavelength = BeamformingDelayCalculator.calc_wavelength(frequency_hz)
        return spacing_lambda * wavelength

    @staticmethod
    def wrap_phase_360(phase_deg: float) -> float:
        """将相位规范化包装到 [0°, 360°) 区间"""
        wrapped = phase_deg % 360.0
        if wrapped < 0:
            wrapped += 360.0
        # 避免浮点数精度导致的 360.0
        if math.isclose(wrapped, 360.0, abs_tol=1e-9):
            wrapped = 0.0
        return wrapped

    @staticmethod
    def wrap_phase_180(phase_deg: float) -> float:
        """将相位规范化包装到 [-180°, +180°] 对称区间"""
        wrapped = (phase_deg + 180.0) % 360.0
        if wrapped < 0:
            wrapped += 360.0
        return wrapped - 180.0

    @classmethod
    def quantize_phase(cls, phase_deg: float, bits: int) -> Tuple[float, int, str, float]:
        """
        根据移相器位宽量化相位
        
        Args:
            phase_deg: 连续相位 (°)
            bits: 量化位数 (0 表示不量化，理想情况)
            
        Returns:
            Tuple[量化相位(°), 十进制码字(int), 十六进制码字(str), 量化误差(°)]
        """
        wrapped = cls.wrap_phase_360(phase_deg)
        if bits <= 0:
            return wrapped, 0, "0x00", 0.0
            
        num_levels = 2 ** bits
        lsb = 360.0 / num_levels
        
        # 四舍五入到最近的量化步进
        code = int(round(wrapped / lsb)) % num_levels
        quant_phase = code * lsb
        
        # 计算量化误差 (考虑 0° 与 360° 环状邻近)
        err = quant_phase - wrapped
        if err > 180.0:
            err -= 360.0
        elif err < -180.0:
            err += 360.0
            
        hex_digits = max(2, math.ceil(bits / 4))
        hex_str = f"0x{code:0{hex_digits}X}"
        
        return quant_phase, code, hex_str, err

    def calculate(self, params: BeamformingDelayParams) -> BeamformingDelayResult:
        """
        执行完整的相控阵通道移相与时延配置计算
        """
        if params.frequency_hz <= 0:
            raise ValueError("工作频率必须大于 0 Hz")
        if params.num_x <= 0:
            raise ValueError("X轴阵元数必须大于等于 1")
        if params.geometry == ArrayGeometry.UPA and params.num_y <= 0:
            raise ValueError("二维面阵 Y轴阵元数必须大于等于 1")

        wavelength_m = self.calc_wavelength(params.frequency_hz)
        wavelength_mm = wavelength_m * 1000.0
        
        spacing_x_lambda = params.spacing_x_m / wavelength_m
        spacing_y_lambda = params.spacing_y_m / wavelength_m if params.geometry == ArrayGeometry.UPA else 0.0
        
        theta_rad = params.scan_theta_deg * DEG_TO_RAD
        phi_rad = params.scan_phi_deg * DEG_TO_RAD if params.geometry == ArrayGeometry.UPA else 0.0
        
        # 1. 计算相邻阵元波程差与相邻相位差/时延差
        # 采用电磁学标准波前补偿约定:
        # 当波束向正角度 θ 扫描时，空间波程差为 d * sin(θ)
        if params.geometry == ArrayGeometry.ULA:
            # 一维线阵沿 X 轴分布
            delta_path_x = params.spacing_x_m * math.sin(theta_rad)
            delta_path_y = 0.0
            num_y_actual = 1
        else:
            # 二维面阵分布在 X-Y 平面，以 Z 轴为法向
            # 方向余弦: u = sin(θ)cos(φ), v = sin(θ)sin(φ)
            delta_path_x = params.spacing_x_m * math.sin(theta_rad) * math.cos(phi_rad)
            delta_path_y = params.spacing_y_m * math.sin(theta_rad) * math.sin(phi_rad)
            num_y_actual = params.num_y

        # 相邻通道相位差 (度): ΔΦ = (2π / λ) * ΔL
        delta_phase_x_deg = (delta_path_x / wavelength_m) * 360.0
        delta_phase_y_deg = (delta_path_y / wavelength_m) * 360.0 if params.geometry == ArrayGeometry.UPA else 0.0
        
        # 相邻通道时延差 (ps): Δτ = ΔL / c
        delta_delay_x_ps = (delta_path_x / SPEED_OF_LIGHT) * 1e12
        delta_delay_y_ps = (delta_path_y / SPEED_OF_LIGHT) * 1e12 if params.geometry == ArrayGeometry.UPA else 0.0

        # 2. 计算各通道逐点配置 (以 (1,1) 角点通道为基准)
        channels: List[ChannelConfig] = []
        phase_errors: List[float] = []
        raw_delays: List[float] = []
        
        ch_id = 1
        for row in range(1, num_y_actual + 1):
            for col in range(1, params.num_x + 1):
                # 物理坐标 (以第1个阵元为 (0,0))
                pos_x_mm = (col - 1) * params.spacing_x_m * 1000.0
                pos_y_mm = (row - 1) * params.spacing_y_m * 1000.0 if params.geometry == ArrayGeometry.UPA else 0.0
                
                # 连续展开绝对相位 (发射激励所需超前/补偿相位，随索引线性递推)
                # 为使正向扫描形成同相叠加，通道激发相位补偿量为: -( (col-1)*ΔΦx + (row-1)*ΔΦy )
                unwrapped_phase = -((col - 1) * delta_phase_x_deg + (row - 1) * delta_phase_y_deg)
                
                wrapped_phase = self.wrap_phase_360(unwrapped_phase)
                sym_phase = self.wrap_phase_180(unwrapped_phase)
                
                # 移相器量化
                quant_phase, quant_code, quant_hex, phase_err = self.quantize_phase(
                    unwrapped_phase, params.quant_bits
                )
                phase_errors.append(phase_err)
                
                # 理论时延值 (ps)
                delay_ps = ((col - 1) * delta_delay_x_ps + (row - 1) * delta_delay_y_ps)
                raw_delays.append(delay_ps)
                
                channels.append(ChannelConfig(
                    channel_id=ch_id,
                    row_idx=row,
                    col_idx=col,
                    pos_x_mm=pos_x_mm,
                    pos_y_mm=pos_y_mm,
                    unwrapped_phase_deg=unwrapped_phase,
                    wrapped_phase_deg=wrapped_phase,
                    sym_phase_deg=sym_phase,
                    quantized_phase_deg=quant_phase,
                    quantized_code=quant_code,
                    quantized_hex=quant_hex,
                    phase_error_deg=phase_err,
                    delay_ps=delay_ps,
                    delay_ns=delay_ps / 1000.0,
                    relative_delay_ps=0.0  # 待全部计算完后偏移到非负
                ))
                ch_id += 1

        # 计算全阵列非负相对时延与最大时延跨度
        min_delay_ps = min(raw_delays) if raw_delays else 0.0
        max_delay_ps = max(raw_delays) if raw_delays else 0.0
        max_array_delay_ps = max_delay_ps - min_delay_ps
        max_array_delay_ns = max_array_delay_ps / 1000.0
        
        for ch in channels:
            ch.relative_delay_ps = ch.delay_ps - min_delay_ps

        # 3. 统计移相器量化误差指标
        if params.quant_bits > 0:
            phase_lsb_deg = 360.0 / (2 ** params.quant_bits)
            rms_phase_error_deg = float(np.sqrt(np.mean(np.array(phase_errors) ** 2)))
            max_phase_error_deg = float(np.max(np.abs(np.array(phase_errors))))
        else:
            phase_lsb_deg = 0.0
            rms_phase_error_deg = 0.0
            max_phase_error_deg = 0.0

        # 4. 宽带波束斜视 (Beam Squint) 评估
        # 以一维或主平面主波束偏角为基准分析
        squint_analysis, max_squint_err, is_cutoff = self._calc_beam_squint(params)

        return BeamformingDelayResult(
            wavelength_m=wavelength_m,
            wavelength_mm=wavelength_mm,
            spacing_x_lambda=spacing_x_lambda,
            spacing_y_lambda=spacing_y_lambda,
            delta_phase_x_deg=delta_phase_x_deg,
            delta_phase_y_deg=delta_phase_y_deg,
            delta_delay_x_ps=delta_delay_x_ps,
            delta_delay_y_ps=delta_delay_y_ps,
            max_array_delay_ps=max_array_delay_ps,
            max_array_delay_ns=max_array_delay_ns,
            phase_lsb_deg=phase_lsb_deg,
            rms_phase_error_deg=rms_phase_error_deg,
            max_phase_error_deg=max_phase_error_deg,
            channels=channels,
            squint_analysis=squint_analysis,
            max_squint_error_deg=max_squint_err,
            is_squint_cutoff=is_cutoff
        )

    def _calc_beam_squint(
        self, params: BeamformingDelayParams
    ) -> Tuple[List[BeamSquintPoint], float, bool]:
        """
        计算宽带条件下的波束斜视 (Beam Squint)
        
        原理:
        对于纯移相器阵列，在中心频率 f0 配置的固定相位差 ΔΦ 在频率 f 下产生的实际偏角满足:
        sin(θ_actual) = (f0 / f) * sin(θ0)
        """
        f0 = params.frequency_hz
        theta0_deg = params.scan_theta_deg
        theta0_rad = theta0_deg * DEG_TO_RAD
        sin_theta0 = math.sin(theta0_rad)
        
        bw = max(1e6, params.squint_bandwidth_hz)
        f_min = max(1e6, f0 - bw / 2.0)
        f_max = f0 + bw / 2.0
        
        freqs = np.linspace(f_min, f_max, params.squint_num_points)
        squint_points: List[BeamSquintPoint] = []
        
        max_err = 0.0
        is_cutoff = False
        
        for f in freqs:
            offset_pct = ((f - f0) / f0) * 100.0
            sin_actual = (f0 / f) * sin_theta0
            
            if abs(sin_actual) <= 1.0:
                actual_rad = math.asin(sin_actual)
                actual_deg = actual_rad * RAD_TO_DEG
                err_deg = actual_deg - theta0_deg
                if abs(err_deg) > max_err:
                    max_err = abs(err_deg)
            else:
                actual_deg = None
                err_deg = None
                is_cutoff = True
                
            squint_points.append(BeamSquintPoint(
                frequency_hz=float(f),
                frequency_ghz=float(f / 1e9),
                offset_percent=float(offset_pct),
                actual_beam_deg=actual_deg,
                squint_error_deg=err_deg,
                ttd_beam_deg=theta0_deg
            ))
            
        return squint_points, max_err, is_cutoff
