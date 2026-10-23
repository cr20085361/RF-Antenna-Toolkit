"""跳频工具的单位转换、刷新、失效清理、绘图和导航集成验证。"""

import pytest
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QApplication

from ui.tools.antenna.fh_capture_tool import FHCaptureTool
from ui.widgets.wheel_filter import GlobalWheelEventFilter


@pytest.fixture(scope="session")
def qapp():
    """复用同一图形应用，适配无显示的测试运行。"""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def tool(qapp):
    """每个用例销毁自己的窗口并停止延迟绘图。"""
    widget = FHCaptureTool()
    yield widget
    widget._plot_timer.stop()
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def test_initialization_and_unit_roundtrip(tool):
    """单位变换不能把五百纳秒误解为五百微秒。"""
    assert tool._last_result.scan_s == pytest.approx(44e-6)
    assert tool.table.rowCount() == 8
    assert "44" in tool.metrics["scan"].text()
    for unit, display in (("μs", 0.5), ("ms", 0.0005), ("ns", 500)):
        tool.switch_time.combo.setCurrentText(unit)
        assert float(tool.switch_time.edit.text()) == pytest.approx(display)
        assert tool._last_result.scan_s == pytest.approx(44e-6)


def test_hop_mode_conversion_and_edit(tool):
    """输入跳周期可回到等效跳速，切换不恢复旧值。"""
    tool.hop_mode.setCurrentIndex(1)
    assert float(tool.hop_period.edit.text()) == pytest.approx(100)
    tool.hop_period.edit.setText("40")
    assert tool._last_result.status == "insufficient"
    tool.hop_mode.setCurrentIndex(0)
    assert tool.hop_rate.base_value() == pytest.approx(25000)
    tool.hop_rate.combo.setCurrentText("千跳/秒")
    assert float(tool.hop_rate.edit.text()) == pytest.approx(25)
    assert tool._last_result.actual_margin_s == pytest.approx(-4e-6)


def test_sample_mode_preserves_duration_and_responds_to_points(tool):
    """先改直接时间再切换采样模式，应保留时间并重新换算采样率。"""
    tool.acquisition_time.edit.setText("10")
    tool.acquisition_mode.setCurrentIndex(1)
    assert tool.sample_rate.base_value() == pytest.approx(5e6)
    tool.samples.setValue(100)
    assert tool._last_result.params.acquisition_s == pytest.approx(20e-6)
    tool.acquisition_mode.setCurrentIndex(0)
    assert tool.acquisition_time.base_value() == pytest.approx(20e-6)


def test_first_group_and_overheads_update_results(tool):
    """折叠附加输入不撤销预算，首组状态仍正确免除稳定开销。"""
    tool.advanced_button.setChecked(True)
    tool.extra_times["settling_s"].edit.setText("2")
    assert tool._last_result.scan_s == pytest.approx(60e-6)
    tool.first_state.setCurrentIndex(1)
    assert tool._last_result.scan_s == pytest.approx(57.5e-6)
    tool.advanced_button.setChecked(False)
    assert tool._last_result.params.settling_s == pytest.approx(2e-6)
    tool.extra_times["processing_s"].edit.setText("1000")
    assert tool._last_result.scan_s == pytest.approx(57.5e-6)
    assert tool._last_result.result_ready_s == pytest.approx(1057.5e-6)


@pytest.mark.parametrize("invalid", ["", "abc", "nan", "inf", "-5", "0"])
def test_invalid_input_clears_every_old_result(tool, invalid):
    """先画有效图再输入错误，数字、表格、缓存和两个图全部清空。"""
    tool._draw_current_plot()
    tool.tabs.setCurrentIndex(1)
    assert tool.figures[1].axes
    received = []
    tool.calculation_completed.connect(received.append)
    tool.acquisition_time.edit.setText(invalid)
    assert tool._last_result is None
    assert tool._result == {}
    assert tool.table.rowCount() == 0
    assert all(not figure.axes for figure in tool.figures)
    assert all(label.text() == "—" for label in tool.metrics.values())
    assert received[-1] == {}
    assert tool.error_label.text()
    tool.acquisition_time.edit.setText("5")
    assert tool._last_result.scan_s == pytest.approx(44e-6)


def test_invalid_mode_switch_does_not_restore_hidden_valid_value(tool):
    """错误输入时切换模式不能悄悄采用隐藏的旧值。"""
    tool.hop_rate.edit.setText("0")
    tool.hop_mode.setCurrentIndex(1)
    assert tool.hop_mode.currentIndex() == 0
    assert tool._last_result is None
    tool.hop_rate.edit.setText("10000")
    tool.acquisition_time.edit.setText("bad")
    tool.acquisition_mode.setCurrentIndex(1)
    assert tool.acquisition_mode.currentIndex() == 0
    assert tool._last_result is None


def test_extreme_finite_time_cannot_overflow_deferred_plot(tool):
    """有限输入仍可能在单位换算时溢出，应清空结果而不是令图形事件循环异常。"""
    tool.acquisition_time.combo.setCurrentText("ms")
    tool.acquisition_time.edit.setText("1e308")
    assert tool._last_result is None
    assert "换算范围" in tool.error_label.text()
    assert not tool._plot_timer.isActive()


def test_plot_numeric_failure_clears_old_figure_and_keeps_budget(tool, monkeypatch):
    """绘图库超出数值范围时提供明确说明，不能显示旧曲线。"""
    def outside_range(_axis):
        raise ValueError("坐标超出绘图范围")
    monkeypatch.setattr(tool, "_draw_sweep", outside_range)
    tool.tabs.setCurrentIndex(1)
    assert tool._last_result.scan_s == pytest.approx(44e-6)
    assert not tool.figures[1].axes
    assert "超出绘图范围" in tool.figures[1].texts[0].get_text()


def test_group_selection_plot_and_zero_window(tool):
    """分组点选定位正确，跨界阶段标红且零窗口仍可画出失败时间轴。"""
    tool.hop_rate.edit.setText("25000")
    tool.table.selectRow(7)
    assert "第 8 组" in tool.group_detail.text()
    tool._draw_current_plot()
    ax = tool.figures[0].axes[0]
    red = [p for p in ax.patches if p.get_facecolor()[:3] == pytest.approx((229/255, 90/255, 87/255))]
    assert red
    assert sum(p.get_width() for p in red) == pytest.approx(4)
    tool.extra_times["unavailable_s"].edit.setText("100")
    tool._draw_current_plot()
    assert tool._last_result.effective_s == 0
    tool.tabs.setCurrentIndex(1)
    ax = tool.figures[1].axes[0]
    assert ax.get_xscale() == "log"
    assert len(ax.lines[1].get_xdata()) == 120


def test_array_validation_and_large_group_selection(tool):
    """非法通道数报错；较多组时只显示所选组附近，表格保留完整数据。"""
    tool.channels.setValue(10)
    assert tool._last_result is None
    tool.elements.setValue(64)
    tool.channels.setValue(2)
    tool.table.selectRow(62)
    tool._draw_current_plot()
    assert tool.table.rowCount() == 63
    assert "第 63 组" in tool.group_detail.text()
    labels = [label.get_text() for label in tool.figures[0].axes[0].get_yticklabels()]
    assert "第 63 组" in labels
    assert len(labels) <= 14


def test_global_wheel_filter_applies_to_new_controls(tool, qapp):
    """复用现有全局策略，滚轮不改变通道、首组状态或单位。"""
    wheel_filter = GlobalWheelEventFilter(qapp)
    qapp.installEventFilter(wheel_filter)
    try:
        for control in (tool.channels, tool.first_state, tool.switch_time.combo):
            event = QWheelEvent(QPointF(5, 5), QPointF(5, 5), QPoint(), QPoint(0, -120),
                                Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
                                Qt.ScrollPhase.NoScrollPhase, False)
            qapp.sendEvent(control, event)
        assert tool.channels.value() == 2
        assert tool.first_state.currentIndex() == 0
        assert tool.switch_time.combo.currentText() == "ns"
        assert tool._last_result.scan_s == pytest.approx(44e-6)
    finally:
        qapp.removeEventFilter(wheel_filter)


def test_main_window_registers_and_opens_tool(qapp, monkeypatch):
    """真正经主窗口注册和导航进入，禁用测试期间的网络更新检查。"""
    from ui.main_window import MainWindow
    monkeypatch.setattr(MainWindow, "_check_updates", lambda *a, **k: None)
    window = MainWindow()
    try:
        window._on_tool_selected("fh_capture")
        registered = window._tools["fh_capture"]
        assert isinstance(registered, FHCaptureTool)
        assert window._tool_stack.currentWidget() is registered
        assert registered._last_result.scan_s == pytest.approx(44e-6)
        assert "v2.3" in window.windowTitle()
    finally:
        for widget in window.findChildren(FHCaptureTool):
            widget._plot_timer.stop()
        window.close()
        window.deleteLater()
        qapp.processEvents()
