# -*- coding: utf-8 -*-
"""
相控阵移相与时延 UI 界面单元测试
Unit Tests for Phased Array Beamforming Delay Tool UI
"""

import sys
import pytest
from PyQt6.QtWidgets import QApplication

from ui.tools.antenna.beamforming_delay_tool import BeamformingDelayTool


@pytest.fixture(scope="session")
def qapp():
    """提供 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_ui_initialization_and_default_state(qapp):
    """测试 UI 正常初始化并自动完成首次计算"""
    tool = BeamformingDelayTool()
    assert tool.tool_name == "相控阵移相与时延"
    assert tool.tool_category == "antenna"
    assert tool._last_result is not None

    # 默认状态：ULA，8元，10GHz，0.5λ，θ=30.0°，6-bit
    assert tool.radio_ula.isChecked()
    assert tool.spin_nx.value() == 8
    assert tool.spin_dx_lambda.value() == 0.5
    assert tool.spin_theta.value() == 30.0
    assert tool.slider_theta.value() == 300

    # 验证指标大盘文本已渲染
    assert "°" in tool.lbl_delta_phase.text()
    assert "ps" in tool.lbl_delta_delay.text()
    assert "ps" in tool.lbl_max_delay.text()

    # 验证表格行数
    assert tool.table_channels.rowCount() == 8


def test_ui_angle_direct_input_and_slider_sync(qapp):
    """测试目标波束指向角度数值框直接输入与滑块双向无缝联动"""
    tool = BeamformingDelayTool()

    # 1. 键盘直接在 spin_theta 输入数值 45.5° -> 滑块同步到 455
    tool.spin_theta.setValue(45.5)
    assert tool.slider_theta.value() == 455
    assert tool._last_result.channels[1].delay_ps > 0

    # 2. 拖动 slider_theta 到 -200 (-20.0°) -> 数值框同步到 -20.0°
    tool.slider_theta.setValue(-200)
    assert pytest.approx(tool.spin_theta.value(), 0.01) == -20.0

    # 3. 切换至 UPA 面阵模式测试方位角 Phi
    tool.radio_upa.setChecked(True)
    tool.spin_phi.setValue(123.4)
    assert tool.slider_phi.value() == 1234

    tool.slider_phi.setValue(2700)
    assert pytest.approx(tool.spin_phi.value(), 0.01) == 270.0


def test_frequency_change_preserves_true_time_delay(qapp):
    """
    核心物理模型验证：
    在固定扫描角度与固定硬件阵元物理间距下，改变工作频率时：
    相邻阵元真时延 Δτ 必须严格保持恒定（与频率无关），电间距 d/λ 和相位差 ΔΦ 随频率自适应变化。
    """
    tool = BeamformingDelayTool()

    # 初始状态：10.0 GHz, dx_mm = 14.990 mm, theta = 30.0°
    # ΔL = 14.990 mm * sin(30°) = 7.495 mm
    # Δτ = 7.495 mm / c ≈ 25.00 ps
    # ΔΦ = (7.495 mm / 29.979 mm) * 360° ≈ 90.0°
    initial_dx_mm = tool.spin_dx_mm.value()
    initial_delay_ps = tool._last_result.delta_delay_x_ps
    initial_phase_deg = tool._last_result.delta_phase_x_deg

    assert pytest.approx(initial_delay_ps, 0.05) == 25.00
    assert pytest.approx(initial_phase_deg, 0.05) == 90.00

    # 1. 改变频率到 20.0 GHz (频率加倍，波长减半)
    tool.input_freq.setText("20.0")

    # 验证物理尺寸不变
    assert pytest.approx(tool.spin_dx_mm.value(), 0.01) == initial_dx_mm
    # 验证电间距更新为约 1.0 λ
    assert pytest.approx(tool.spin_dx_lambda.value(), 0.02) == 1.00
    # 验证真时延严格保持不变！
    assert pytest.approx(tool._last_result.delta_delay_x_ps, 1e-4) == initial_delay_ps
    # 验证相位差随频率翻倍至约 180°
    assert pytest.approx(tool._last_result.delta_phase_x_deg, 0.1) == 180.00

    # 2. 改变频率到 5.0 GHz (频率减半，波长加倍)
    tool.input_freq.setText("5.0")

    # 验证物理尺寸仍保持不变
    assert pytest.approx(tool.spin_dx_mm.value(), 0.01) == initial_dx_mm
    # 验证电间距更新为约 0.25 λ
    assert pytest.approx(tool.spin_dx_lambda.value(), 0.02) == 0.25
    # 验证真时延依旧严格保持不变！
    assert pytest.approx(tool._last_result.delta_delay_x_ps, 1e-4) == initial_delay_ps
    # 验证相位差变为约 45°
    assert pytest.approx(tool._last_result.delta_phase_x_deg, 0.1) == 45.00


def test_ui_preset_application(qapp):
    """测试预设切换与联动"""
    tool = BeamformingDelayTool()

    # 切换至 Ka 波段 8x8 面阵预设
    tool._apply_preset("ka_band_upa")
    assert tool.radio_upa.isChecked()
    assert tool.spin_nx.value() == 8
    assert tool.spin_ny.value() == 8
    assert tool.input_freq.text() == "28.0"
    assert tool.spin_theta.value() == 30.0
    assert tool.spin_phi.value() == 45.0
    assert tool.table_channels.rowCount() == 64

    # 验证 UPA 下控件已启用
    assert tool.spin_ny.isEnabled()
    assert tool.phi_container.isEnabled()


def test_ui_bidirectional_spacing_sync(qapp):
    """测试物理与电间距双向联动输入"""
    tool = BeamformingDelayTool()

    # 10 GHz 时，λ ≈ 29.979 mm
    # 设置电间距为 1.0 λ
    tool.spin_dx_lambda.setValue(1.0)
    assert pytest.approx(tool.spin_dx_mm.value(), 0.05) == 29.979

    # 修改物理间距为 14.99 mm -> 电间距应约为 0.50 λ
    tool.spin_dx_mm.setValue(14.99)
    assert pytest.approx(tool.spin_dx_lambda.value(), 0.01) == 0.50


def test_ui_knowledge_injection_methods(qapp):
    """测试四维知识注入方法均正常返回非空富文本 HTML"""
    tool = BeamformingDelayTool()

    intuition = tool.get_intuition_content()
    math_model = tool.get_math_model_content()
    engineering = tool.get_engineering_content()
    history = tool.get_history_content()

    assert intuition is not None and "百米赛跑" in intuition
    assert math_model is not None and "sin(θ)" in math_model
    assert engineering is not None and "量化栅瓣" in engineering
    assert history is not None and "铁氧体移相器" in history


def test_ui_tab_switching_and_drawing(qapp):
    """测试图表 Tab 切换与重绘"""
    tool = BeamformingDelayTool()

    # 切换到分布图 Tab
    tool.tab_widget.setCurrentIndex(1)
    # 切换到斜视分析 Tab
    tool.tab_widget.setCurrentIndex(2)
    assert tool._last_result is not None
    assert len(tool._last_result.squint_analysis) > 0
