# -*- coding: utf-8 -*-
"""
全局滚轮事件过滤器单元测试
Unit Tests for Global Wheel Event Filter
"""

import sys
import pytest
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QScrollArea,
    QSpinBox, QDoubleSpinBox, QComboBox, QSlider, QScrollBar, QLineEdit
)
from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QWheelEvent

from ui.widgets.wheel_filter import GlobalWheelEventFilter


@pytest.fixture(scope="session")
def qapp():
    """获取或创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def create_mock_wheel_event(delta_y: int = -120) -> QWheelEvent:
    """构造滚轮测试事件"""
    return QWheelEvent(
        QPointF(10, 10), QPointF(10, 10),
        QPoint(0, 0), QPoint(0, delta_y),
        Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase, False
    )


def test_wheel_filter_blocks_spinboxes(qapp):
    """测试全局过滤器阻止 SpinBox 与 DoubleSpinBox 响应滚轮改值"""
    filter_obj = GlobalWheelEventFilter(qapp)
    qapp.installEventFilter(filter_obj)

    try:
        # 1. QDoubleSpinBox
        dspin = QDoubleSpinBox()
        dspin.setRange(0.0, 500.0)
        dspin.setValue(100.0)
        wheel_ev = create_mock_wheel_event(-120)
        qapp.sendEvent(dspin, wheel_ev)
        assert dspin.value() == 100.0, "QDoubleSpinBox should not change on wheel event"

        # 测试在其内部子部件 QLineEdit 上滚动
        inner_line = dspin.findChild(QLineEdit)
        if inner_line:
            qapp.sendEvent(inner_line, wheel_ev)
            assert dspin.value() == 100.0, "Inner QLineEdit wheel event should be blocked"

        # 2. QSpinBox
        spin = QSpinBox()
        spin.setRange(0, 500)
        spin.setValue(50)
        qapp.sendEvent(spin, wheel_ev)
        assert spin.value() == 50, "QSpinBox should not change on wheel event"
    finally:
        qapp.removeEventFilter(filter_obj)


def test_wheel_filter_blocks_combobox_and_slider(qapp):
    """测试全局过滤器阻止 QComboBox 与 QSlider 响应滚轮改值"""
    filter_obj = GlobalWheelEventFilter(qapp)
    qapp.installEventFilter(filter_obj)

    try:
        # 1. QComboBox (未展开时)
        combo = QComboBox()
        combo.addItems(["Item 0", "Item 1", "Item 2"])
        combo.setCurrentIndex(1)
        wheel_ev = create_mock_wheel_event(120)
        qapp.sendEvent(combo, wheel_ev)
        assert combo.currentIndex() == 1, "QComboBox should not change index on wheel event"

        # 2. QSlider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 1000)
        slider.setValue(300)
        qapp.sendEvent(slider, wheel_ev)
        assert slider.value() == 300, "QSlider should not change value on wheel event"
    finally:
        qapp.removeEventFilter(filter_obj)


def test_wheel_filter_passes_scrollbar_and_scroll_area(qapp):
    """测试 QScrollBar 放行正常滚动，且在子控件上滚动时能够透传给 QScrollArea"""
    filter_obj = GlobalWheelEventFilter(qapp)
    qapp.installEventFilter(filter_obj)

    try:
        # 1. 独立 QScrollBar 能够正常接收滚轮
        scrollbar = QScrollBar(Qt.Orientation.Vertical)
        scrollbar.setRange(0, 100)
        scrollbar.setValue(0)
        wheel_ev = create_mock_wheel_event(-120)
        # ScrollBar 自身不应被拦截过滤
        is_filtered = filter_obj.eventFilter(scrollbar, wheel_ev)
        assert is_filtered is False, "QScrollBar itself must not be filtered"

        # 2. QScrollArea 视口透传
        scroll = QScrollArea()
        scroll.resize(300, 200)
        content = QWidget()
        layout = QVBoxLayout(content)
        spin = QDoubleSpinBox()
        spin.setRange(0, 1000.0)
        spin.setValue(50.0)
        layout.addWidget(spin)
        for i in range(100):
            from PyQt6.QtWidgets import QLabel
            layout.addWidget(QLabel(f"Line {i}"))
        scroll.setWidget(content)
        scroll.show()
        qapp.processEvents()

        init_scroll = scroll.verticalScrollBar().value()
        qapp.sendEvent(spin, create_mock_wheel_event(-120))
        qapp.processEvents()

        assert spin.value() == 50.0, "Spinbox value must remain 50.0"
        assert scroll.verticalScrollBar().value() > init_scroll, "Scroll area should scroll on wheel event over spinbox"
    finally:
        qapp.removeEventFilter(filter_obj)
