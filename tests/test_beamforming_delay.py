# -*- coding: utf-8 -*-
"""
相控阵移相与时延计算模块单元测试
Unit Tests for Phased Array Beamforming Delay & Phase Calculator
"""

import math
import pytest
import numpy as np

from core.antenna.beamforming_delay import (
    BeamformingDelayCalculator,
    BeamformingDelayParams,
    ArrayGeometry,
    ChannelConfig
)
from core.constants import SPEED_OF_LIGHT


class TestBeamformingDelayCalculator:
    """相控阵移相与时延算法测试套件"""

    def setup_method(self):
        self.calc = BeamformingDelayCalculator()

    def test_wavelength_and_spacing_conversion(self):
        """测试波长与电/物理间距双向转换"""
        freq_10g = 10.0e9
        wl = self.calc.calc_wavelength(freq_10g)
        expected_wl = SPEED_OF_LIGHT / 10.0e9
        assert math.isclose(wl, expected_wl, rel_tol=1e-9)

        # 0.5λ 间距
        spacing_m = 0.5 * wl
        d_lambda = self.calc.physical_to_electrical_spacing(spacing_m, freq_10g)
        assert math.isclose(d_lambda, 0.5, rel_tol=1e-9)

        recovered_spacing_m = self.calc.electrical_to_physical_spacing(0.5, freq_10g)
        assert math.isclose(recovered_spacing_m, spacing_m, rel_tol=1e-9)

    def test_phase_wrapping(self):
        """测试相位区间包装"""
        # [0, 360) 包装
        assert math.isclose(self.calc.wrap_phase_360(0.0), 0.0, abs_tol=1e-7)
        assert math.isclose(self.calc.wrap_phase_360(360.0), 0.0, abs_tol=1e-7)
        assert math.isclose(self.calc.wrap_phase_360(370.0), 10.0, abs_tol=1e-7)
        assert math.isclose(self.calc.wrap_phase_360(-90.0), 270.0, abs_tol=1e-7)

        # [-180, 180] 包装
        assert math.isclose(self.calc.wrap_phase_180(0.0), 0.0, abs_tol=1e-7)
        assert math.isclose(self.calc.wrap_phase_180(190.0), -170.0, abs_tol=1e-7)
        assert math.isclose(self.calc.wrap_phase_180(-190.0), 170.0, abs_tol=1e-7)

    def test_quantization(self):
        """测试移相器位宽量化"""
        # 6-bit 移相器: LSB = 360 / 64 = 5.625°
        quant_phase, code, hex_str, err = self.calc.quantize_phase(5.625, 6)
        assert math.isclose(quant_phase, 5.625, abs_tol=1e-7)
        assert code == 1
        assert hex_str == "0x01"
        assert math.isclose(err, 0.0, abs_tol=1e-7)

        # 理想不量化 bits=0
        q0, c0, h0, e0 = self.calc.quantize_phase(123.45, 0)
        assert math.isclose(q0, 123.45, abs_tol=1e-7)
        assert math.isclose(e0, 0.0, abs_tol=1e-7)

    def test_ula_exact_calculation(self):
        """测试一维线阵精确相位与时延配置 (θ = 30°, d = 0.5λ)"""
        f0 = 10.0e9
        wl = SPEED_OF_LIGHT / f0
        d = 0.5 * wl

        params = BeamformingDelayParams(
            geometry=ArrayGeometry.ULA,
            num_x=4,
            frequency_hz=f0,
            spacing_x_m=d,
            scan_theta_deg=30.0,
            quant_bits=0  # 理想无量化
        )

        res = self.calc.calculate(params)

        # sin(30°) = 0.5, ΔL = 0.5 * 0.5λ = 0.25λ
        # ΔΦ = 0.25 * 360° = 90°
        # Δτ = 0.25λ / c = 0.25 / 10GHz = 25.0 ps
        assert math.isclose(res.delta_phase_x_deg, 90.0, rel_tol=1e-5)
        assert math.isclose(res.delta_delay_x_ps, 25.0, rel_tol=1e-5)

        # 检查通道参数
        assert len(res.channels) == 4
        # 通道 1: (0°, 0 ps)
        assert math.isclose(res.channels[0].unwrapped_phase_deg, 0.0, abs_tol=1e-5)
        assert math.isclose(res.channels[0].wrapped_phase_deg, 0.0, abs_tol=1e-5)
        assert math.isclose(res.channels[0].delay_ps, 0.0, abs_tol=1e-5)

        # 通道 2: unwrapped = -90°, wrapped = 270°, delay = 25 ps
        assert math.isclose(res.channels[1].unwrapped_phase_deg, -90.0, abs_tol=1e-5)
        assert math.isclose(res.channels[1].wrapped_phase_deg, 270.0, abs_tol=1e-5)
        assert math.isclose(res.channels[1].delay_ps, 25.0, abs_tol=1e-5)

        # 通道 3: unwrapped = -180°, wrapped = 180°, delay = 50 ps
        assert math.isclose(res.channels[2].unwrapped_phase_deg, -180.0, abs_tol=1e-5)
        assert math.isclose(res.channels[2].wrapped_phase_deg, 180.0, abs_tol=1e-5)
        assert math.isclose(res.channels[2].delay_ps, 50.0, abs_tol=1e-5)

        # 最大跨度 (4-1)*25 = 75 ps
        assert math.isclose(res.max_array_delay_ps, 75.0, rel_tol=1e-5)

    def test_upa_plane_calculation(self):
        """测试二维面阵配置 (UPA 3x3)"""
        f0 = 10.0e9
        wl = SPEED_OF_LIGHT / f0
        d = 0.5 * wl

        params = BeamformingDelayParams(
            geometry=ArrayGeometry.UPA,
            num_x=3,
            num_y=3,
            frequency_hz=f0,
            spacing_x_m=d,
            spacing_y_m=d,
            scan_theta_deg=30.0,
            scan_phi_deg=45.0,
            quant_bits=6
        )

        res = self.calc.calculate(params)
        assert len(res.channels) == 9

        # 在 φ=45° 时，X 和 Y 方向的投影分量应完全对称
        assert math.isclose(res.delta_phase_x_deg, res.delta_phase_y_deg, rel_tol=1e-5)
        assert math.isclose(res.delta_delay_x_ps, res.delta_delay_y_ps, rel_tol=1e-5)

    def test_beam_squint_physics(self):
        """测试宽带波束斜视物理规律"""
        f0 = 10.0e9
        params = BeamformingDelayParams(
            geometry=ArrayGeometry.ULA,
            num_x=8,
            frequency_hz=f0,
            scan_theta_deg=30.0,
            squint_bandwidth_hz=4.0e9,  # 8 GHz ~ 12 GHz
            squint_num_points=3
        )

        res = self.calc.calculate(params)
        squint_pts = res.squint_analysis
        assert len(squint_pts) == 3

        # 频偏验证: sin(θ) = (f0 / f) * sin(30°) = (10 / f) * 0.5
        # 1. f = 8 GHz: sin(θ) = 10/8 * 0.5 = 0.625 -> θ = arcsin(0.625) ≈ 38.682°
        p_low = squint_pts[0]
        assert math.isclose(p_low.frequency_hz, 8.0e9, rel_tol=1e-5)
        expected_theta_low = math.degrees(math.asin(0.625))
        assert math.isclose(p_low.actual_beam_deg, expected_theta_low, rel_tol=1e-3)
        assert p_low.ttd_beam_deg == 30.0

        # 2. f = 10 GHz (中心频点): θ = 30.0°
        p_mid = squint_pts[1]
        assert math.isclose(p_mid.actual_beam_deg, 30.0, rel_tol=1e-3)
        assert math.isclose(p_mid.squint_error_deg, 0.0, abs_tol=1e-3)

        # 3. f = 12 GHz: sin(θ) = 10/12 * 0.5 = 5/12 ≈ 0.41667 -> θ = arcsin(5/12) ≈ 24.624°
        p_high = squint_pts[2]
        expected_theta_high = math.degrees(math.asin(5.0 / 12.0))
        assert math.isclose(p_high.actual_beam_deg, expected_theta_high, rel_tol=1e-3)
