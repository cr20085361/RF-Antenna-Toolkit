# -*- coding: utf-8 -*-
"""
相控阵综合计算 UI 界面单元测试
Unit Tests for Phased Array Tool UI
"""

import sys
import pytest
from PyQt6.QtWidgets import QApplication

from ui.tools.antenna.phased_array_tool import PhasedArrayTool


@pytest.fixture(scope="session")
def qapp():
    """提供 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_phased_array_ui_initialization_and_angle_sync(qapp):
    """测试相控阵计算工具初始化与角度输入双向联动"""
    tool = PhasedArrayTool()
    assert tool.tool_name == "相控阵计算"

    # 默认状态
    assert tool.spin_theta.value() == 0.0
    assert tool.slider_theta.value() == 0
    assert tool.spin_phi.value() == 0.0
    assert tool.slider_phi.value() == 0

    # 1. 键盘直接输入 Theta 30.5° -> 滑块同步到 305
    tool.spin_theta.setValue(30.5)
    assert tool.slider_theta.value() == 305

    # 2. 拖动滑块 Theta 到 600 (60.0°) -> 数值框同步到 60.0°
    tool.slider_theta.setValue(600)
    assert pytest.approx(tool.spin_theta.value(), 0.01) == 60.0

    # 3. 键盘输入 Phi 180.5° -> 滑块同步到 1805
    tool.spin_phi.setValue(180.5)
    assert tool.slider_phi.value() == 1805

    # 4. 预设重置测试
    tool._apply_preset(4)
    assert tool.spin_nx.value() == 4
    assert tool.spin_ny.value() == 4
    assert tool.spin_theta.value() == 0.0
    assert tool.slider_theta.value() == 0
