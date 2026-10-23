"""跳频测向捕获评估界面，版本 2.3。

以固定参考通道的逐组采集为教学入口，展示同一跳内的时间预算、
逐阶段时间轴和跳速余量曲线。界面只负责单位换算，计算统一交给核心模型。
"""

import math
from dataclasses import asdict

import numpy as np
from matplotlib import rc_context
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QGroupBox, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget,
)

from core.antenna.fh_capture import CaptureParams, CaptureCalculator
from ui.base.tool_base import ToolBase


TIME_UNITS = {"ns": 1e-9, "μs": 1e-6, "ms": 1e-3}
STATUS = {
    "insufficient": ("时间不足，无法在本跳采齐整阵数据", "#B42318", "#FFF1F0"),
    "boundary": ("刚好容纳，没有时间余量", "#9A6700", "#FFF8E6"),
    "reserve_shortfall": ("可以容纳，但未达到要求的预留余量", "#9A6700", "#FFF8E6"),
    "feasible": ("满足所填时序预算", "#13765A", "#EDF9F3"),
}
STAGE_STYLES = {
    "latency": ("启动延迟", "#94A3B8"), "switch": ("切换", "#F3AE4E"),
    "settle": ("额外稳定", "#A58BD4"), "acquire": ("有效采样", "#448BDC"),
    "block": ("组间阻塞", "#C68C6C"),
}


def text_label(text: str) -> QLabel:
    """正文标签允许换行，避免中文长说明撑宽工作区。"""
    label = QLabel(text)
    label.setWordWrap(True)
    return label


def format_time(seconds: float) -> str:
    """自动选择合适的结果单位，精度只影响显示，不参与判定。"""
    magnitude = abs(seconds)
    unit, factor = ("s", 1.0) if magnitude >= 1 else ("ms", 1e-3)
    if magnitude < 1e-3:
        unit, factor = "μs", 1e-6
    if 0 < magnitude < 1e-6:
        unit, factor = "ns", 1e-9
    return f"{seconds / factor:,.7g} {unit}"


class QuantityInput(QWidget):
    """局部数值单位控件，允许科学计数法和就地校验，不静默钳制错误值。"""

    changed = pyqtSignal()

    def __init__(self, value: float, units: dict, unit: str, label: str):
        super().__init__()
        self.units = units
        self.label = label
        self._unit = unit
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.edit = QLineEdit()
        self.edit.setMinimumWidth(65)
        self.edit.setAccessibleName(label)
        self.combo = QComboBox()
        self.combo.addItems(list(units))
        self.combo.setCurrentText(unit)
        self.combo.setAccessibleName(f"{label}单位")
        self.combo.setFixedWidth(88)
        self.combo.setStyleSheet("QComboBox { min-width: 0px; padding: 7px 8px; }")
        layout.addWidget(self.edit, 1)
        layout.addWidget(self.combo)
        self.set_base_value(value)
        self.edit.textChanged.connect(self.changed.emit)
        self.combo.currentTextChanged.connect(self._change_unit)

    def base_value(self) -> float:
        """返回统一单位值，空白、溢出和非数值明确报错。"""
        try:
            value = float(self.edit.text().strip()) * self.units[self._unit]
        except ValueError as exc:
            raise ValueError(f"{self.label}请输入数值") from exc
        if not math.isfinite(value):
            raise ValueError(f"{self.label}必须是有限数值")
        return value

    def set_base_value(self, value: float) -> None:
        """保持物理量设置显示值；调用者控制是否发出重新计算事件。"""
        self.edit.blockSignals(True)
        self.edit.setText(f"{value / self.units[self._unit]:.15g}")
        self.edit.blockSignals(False)

    def _change_unit(self, unit: str) -> None:
        """用旧单位读数再换到新单位，错误文本保留待用户修正。"""
        try:
            value = self.base_value()
        except ValueError:
            value = None
        self._unit = unit
        if value is not None:
            self.set_base_value(value)
        self.changed.emit()


class ActiveInputStack(QStackedWidget):
    """只为当前输入模式预留高度，避免隐藏的采样表单撑大简单模式。"""

    def sizeHint(self):
        return self.currentWidget().sizeHint() if self.currentWidget() else super().sizeHint()

    def minimumSizeHint(self):
        return self.currentWidget().minimumSizeHint() if self.currentWidget() else super().minimumSizeHint()


class FHCaptureTool(ToolBase):
    """固定参考阵列的跳频单跳采集评估，所有数值与图表共享计算结果。"""

    tool_name = "跳频测向捕获评估"
    tool_icon = "⏱"
    tool_category = "antenna"
    tool_description = "固定参考通道 · 同一跳内整阵采集的时间预算"

    def __init__(self):
        self._initializing = True
        self._last_result = None
        self._hop_mode = 0
        self._acquisition_mode = 0
        self._plot_cache = {}
        super().__init__()
        self.setObjectName("FHCaptureTool")
        # 只调整新页面的输入密度，不影响已有工具的布局。
        self.setStyleSheet(
            "#FHCaptureTool QLineEdit, #FHCaptureTool QSpinBox { padding: 7px 8px; }"
            "#FHCaptureTool QComboBox { min-width: 0px; padding: 7px 8px; }"
        )
        self._plot_timer = QTimer(self)
        self._plot_timer.setSingleShot(True)
        self._plot_timer.setInterval(120)
        self._plot_timer.timeout.connect(self._draw_current_plot)
        # 只在此工具中启用资料链接，保留公共知识区接口。
        for label in self.findChildren(QLabel, "KnowledgeContent"):
            label.setOpenExternalLinks(True)
        self._initializing = False
        self.calculate()

    def _quantity(self, value: float, label: str, unit: str = "μs") -> QuantityInput:
        """构建时间输入并连接统一刷新入口。"""
        widget = QuantityInput(value, TIME_UNITS, unit, label)
        widget.changed.connect(self.calculate)
        return widget

    def create_input_panel(self) -> QWidget:
        """基础参数直接显示，附加净开销折叠，默认示例说明始终可见。"""
        panel = QWidget()
        panel.setMinimumWidth(330)
        panel.setMaximumWidth(440)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        self.example_note = text_label(
            "教学示例 · 默认值不是设备实测能力。\n零开销表示本次预算未计入该项。"
        )
        self.example_note.setStyleSheet("color: #756039; background: #FFF8E6; padding: 10px; border-radius: 8px;")
        layout.addWidget(self.example_note)
        group = QGroupBox("阵列与采集")
        form = QFormLayout(group)
        form.setVerticalSpacing(10)
        self.elements = QSpinBox()
        self.channels = QSpinBox()
        for spin, value in ((self.elements, 9), (self.channels, 2)):
            spin.setRange(2, 256)
            spin.setValue(value)
            spin.valueChanged.connect(self.calculate)
        form.addRow("阵元总数（含参考）", self.elements)
        form.addRow("相干通道（含参考）", self.channels)
        self.switch_time = self._quantity(500e-9, "单次切换时间", "ns")
        self.switch_time.setToolTip("从命令到切换完成；不要重复添加已包含的控制或稳定时间。")
        form.addRow("单次切换时间", self.switch_time)
        self.first_state = QComboBox()
        self.first_state.addItems(["首组也需要切换", "首组已接通且稳定"])
        self.first_state.currentIndexChanged.connect(self.calculate)
        form.addRow("首组状态", self.first_state)
        self.acquisition_mode = QComboBox()
        self.acquisition_mode.addItems(["直接填写采集时间", "采样点数 ÷ 采样率"])
        self.acquisition_mode.currentIndexChanged.connect(self._change_acquisition_mode)
        form.addRow("有效采集时间", self.acquisition_mode)
        self.acquisition_stack = ActiveInputStack()
        self.acquisition_time = self._quantity(5e-6, "每组有效采集时间")
        self.acquisition_stack.addWidget(self.acquisition_time)
        samples_panel = QWidget()
        samples_layout = QFormLayout(samples_panel)
        samples_layout.setContentsMargins(0, 0, 0, 0)
        self.samples = QSpinBox()
        self.samples.setRange(1, 1000000000)
        self.samples.setValue(50)
        self.samples.valueChanged.connect(self.calculate)
        self.sample_rate = QuantityInput(10e6, {"S/s": 1, "kS/s": 1e3, "MS/s": 1e6}, "MS/s", "有效采样率")
        self.sample_rate.changed.connect(self.calculate)
        samples_layout.addRow("每通道点数", self.samples)
        samples_layout.addRow("有效采样率", self.sample_rate)
        self.acquisition_stack.addWidget(samples_panel)
        form.addRow(self.acquisition_stack)
        self.acquisition_hint = text_label("")
        self.acquisition_hint.setStyleSheet("color: #667085; font-size: 12px;")
        form.addRow(self.acquisition_hint)
        layout.addWidget(group)

        signal_group = QGroupBox("目标跳频信号")
        signal_form = QFormLayout(signal_group)
        self.hop_mode = QComboBox()
        self.hop_mode.addItems(["按跳速输入", "按跳周期输入"])
        self.hop_mode.currentIndexChanged.connect(self._change_hop_mode)
        signal_form.addRow("输入方式", self.hop_mode)
        self.hop_stack = QStackedWidget()
        self.hop_rate = QuantityInput(10000, {"跳/秒": 1, "千跳/秒": 1000}, "跳/秒", "目标跳速")
        self.hop_rate.changed.connect(self.calculate)
        self.hop_period = self._quantity(100e-6, "跳周期")
        self.hop_stack.addWidget(self.hop_rate)
        self.hop_stack.addWidget(self.hop_period)
        signal_form.addRow(self.hop_stack)
        self.hop_hint = text_label("")
        signal_form.addRow(self.hop_hint)
        layout.addWidget(signal_group)

        self.advanced_button = QPushButton("▸ 更多时间开销")
        self.advanced_button.setCheckable(True)
        self.advanced_button.toggled.connect(self._toggle_advanced)
        layout.addWidget(self.advanced_button)
        self.advanced_panel = QGroupBox("只填写尚未计入的净开销")
        advanced_form = QFormLayout(self.advanced_panel)
        self.extra_times = {}
        fields = (
            ("unavailable_s", "每跳不可用时间", "频点过渡、空白等总时长；剩余部分须是一个连续有效窗口。"),
            ("latency_s", "启动延迟", "有效窗口开始至首条切换命令；若首组已就绪，则至开始采样。填检测、触发、调谐的净延迟。"),
            ("settling_s", "切换后额外稳定", "只计单次切换时间尚未包括的稳定过程；首组已就绪时也免除该组稳定。"),
            ("blocking_s", "组间额外阻塞", "仅计未与切换、稳定或采集重叠的数据搬运等等待。"),
            ("reserve_s", "要求预留余量", "采集完仍希望剩余的有效窗口时长。"),
            ("processing_s", "采集后处理时间", "最后采样之后的计算，仅影响结果延迟；若阻塞组间采集，应填入组间阻塞。"),
        )
        for key, label, hint in fields:
            widget = self._quantity(0, label)
            widget.setToolTip(hint)
            self.extra_times[key] = widget
            advanced_form.addRow(label, widget)
        self.advanced_panel.hide()
        layout.addWidget(self.advanced_panel)
        self.error_label = text_label("")
        self.error_label.setStyleSheet("color: #B42318;")
        layout.addWidget(self.error_label)
        layout.addStretch()
        return panel

    def _toggle_advanced(self, checked: bool) -> None:
        """折叠只影响显示，隐藏的非零参数仍参与计算。"""
        self.advanced_panel.setVisible(checked)
        self.advanced_button.setText("▾ 收起时间开销" if checked else "▸ 更多时间开销")

    def _change_hop_mode(self, index: int) -> None:
        """在跳速与周期之间切换时保留物理量，不恢复旧的隐藏值。"""
        if self._initializing:
            return
        try:
            old = self.hop_rate if self._hop_mode == 0 else self.hop_period
            value = old.base_value()
            if value <= 0 or not math.isfinite(1.0 / value):
                raise ValueError("跳速或跳周期必须为可计算的正数")
            target = self.hop_rate if index == 0 else self.hop_period
            target.set_base_value(1.0 / value)
        except ValueError as exc:
            self.hop_mode.blockSignals(True)
            self.hop_mode.setCurrentIndex(self._hop_mode)
            self.hop_mode.blockSignals(False)
            self._clear_result(str(exc))
            return
        self._hop_mode = index
        self.hop_stack.setCurrentIndex(index)
        self.calculate()

    def _change_acquisition_mode(self, index: int) -> None:
        """保留采集时长；点数模式使用当前点数反算所需有效采样率。"""
        if self._initializing:
            return
        try:
            if self._acquisition_mode == 0:
                duration = self.acquisition_time.base_value()
                if duration <= 0:
                    raise ValueError("每组有效采集时间必须大于零")
                rate = self.samples.value() / duration
                if not math.isfinite(rate):
                    raise ValueError("有效采样率超出可计算范围")
                self.sample_rate.set_base_value(rate)
            else:
                duration = CaptureCalculator.acquisition_from_samples(self.samples.value(), self.sample_rate.base_value())
                self.acquisition_time.set_base_value(duration)
        except ValueError as exc:
            self.acquisition_mode.blockSignals(True)
            self.acquisition_mode.setCurrentIndex(self._acquisition_mode)
            self.acquisition_mode.blockSignals(False)
            self._clear_result(str(exc))
            return
        self._acquisition_mode = index
        self.acquisition_stack.setCurrentIndex(index)
        self.acquisition_stack.updateGeometry()
        self.calculate()

    def create_result_panel(self) -> QWidget:
        """用结果卡呈现关键结论，次要开销保留在预算明细中。"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        self.status_label = text_label("等待计算")
        layout.addWidget(self.status_label)
        grid = QGridLayout()
        self.metrics = {}
        for i, (key, title) in enumerate((
            ("groups", "采集组数 / 切换次数"), ("scan", "整阵扫描时间"),
            ("effective", "连续有效时长"), ("margin", "实际时间余量"),
            ("max_rate", "单跳采集时序上限"), ("reserved_rate", "满足预留余量的跳速上限"),
        )):
            box = QGroupBox(title)
            box_layout = QVBoxLayout(box)
            value = text_label("—")
            value.setStyleSheet("font-size: 21px; font-weight: 600; color: #2563A6;")
            box_layout.addWidget(value)
            grid.addWidget(box, i // 2, i % 2)
            self.metrics[key] = value
        layout.addLayout(grid)
        self.budget_label = text_label("")
        self.budget_label.setTextFormat(Qt.TextFormat.RichText)
        self.budget_label.setStyleSheet("background: #F5F8FC; padding: 12px; border-radius: 8px; line-height: 150%;")
        layout.addWidget(self.budget_label)
        self.assumptions_label = text_label("")
        self.assumptions_label.setStyleSheet("color: #667085; font-size: 12px;")
        layout.addWidget(self.assumptions_label)
        layout.addStretch()
        return panel

    def create_visualization(self) -> QWidget:
        """分组表与图共用时间原点，点选表格或采集条可定位同一组。"""
        panel = QGroupBox("采集过程与跳速边界")
        layout = QVBoxLayout(panel)
        layout.addWidget(text_label("时间原点：连续有效窗口开始。选择一组查看连接和起止时间；图表工具栏支持缩放。"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["组", "同时连接的阵元", "组开始 / μs", "采样开始 / μs", "采样结束 / μs"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setFixedHeight(200)
        self.table.itemSelectionChanged.connect(self._select_group)
        layout.addWidget(self.table)
        self.group_detail = text_label("—")
        layout.addWidget(self.group_detail)
        self.tabs = QTabWidget()
        self.figures = []
        self.canvases = []
        for title in ("单跳时间轴", "跳速与设计余量"):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            figure = Figure(figsize=(9, 4), dpi=100)
            canvas = FigureCanvasQTAgg(figure)
            canvas.setMinimumHeight(370)
            tab_layout.addWidget(NavigationToolbar2QT(canvas, tab))
            tab_layout.addWidget(canvas)
            self.tabs.addTab(tab, title)
            self.figures.append(figure)
            self.canvases.append(canvas)
        self.canvases[0].mpl_connect("pick_event", self._pick_group)
        self.tabs.currentChanged.connect(self._draw_current_plot)
        layout.addWidget(self.tabs)
        return panel

    def _read_params(self) -> CaptureParams:
        """从当前输入模式读数；隐藏的另一种输入不参与预算。"""
        if self._acquisition_mode == 0:
            acquisition = self.acquisition_time.base_value()
        else:
            acquisition = CaptureCalculator.acquisition_from_samples(self.samples.value(), self.sample_rate.base_value())
        rate = self.hop_rate.base_value() if self._hop_mode == 0 else self.hop_period.base_value()
        if self._hop_mode == 1:
            if rate <= 0:
                raise ValueError("跳周期必须大于零")
            rate = 1.0 / rate
        return CaptureParams(
            elements=self.elements.value(), channels=self.channels.value(),
            switch_s=self.switch_time.base_value(), acquisition_s=acquisition,
            hop_rate_hz=rate, first_group_ready=self.first_state.currentIndex() == 1,
            **{key: widget.base_value() for key, widget in self.extra_times.items()},
        )

    def calculate(self, *_args) -> dict:
        """立即刷新数值；绘图稍作合并，避免输入过程中重复渲染。"""
        if self._initializing:
            return {}
        try:
            result = CaptureCalculator.calculate(self._read_params())
            # 界面支持纳秒换算，先检查派生时间的可显示范围，避免表格或定时绘图溢出。
            if not all(math.isfinite(value * 1e9) for value in (
                result.period_s, result.required_s, result.result_ready_s,
                result.params.unavailable_s,
            )):
                raise ValueError("时间量级过大，超出界面纳秒单位换算范围")
        except ValueError as exc:
            self._clear_result(str(exc))
            return {}
        selected = max(0, self.table.currentRow())
        self._last_result = result
        self._plot_cache.clear()
        self.error_label.clear()
        title, color, background = STATUS[result.status]
        self.status_label.setText(f"{title}\n仅判断同一跳内能否采齐数据，不代表实际捕获成功率。")
        self.status_label.setStyleSheet(f"color: {color}; background: {background}; padding: 14px; border-radius: 8px; font-weight: 600;")
        values = {
            "groups": f"{result.group_count} 组 / {result.switch_count} 次",
            "scan": format_time(result.scan_s), "effective": format_time(result.effective_s),
            "margin": format_time(result.actual_margin_s),
            "max_rate": f"{result.max_hop_rate_hz:,.7g} 跳/秒",
            "reserved_rate": f"{result.reserved_max_hop_rate_hz:,.7g} 跳/秒",
        }
        for key, value in values.items():
            self.metrics[key].setText(value)
        p = result.params
        latest = format_time(result.latest_start_s) if result.latest_start_s >= 0 else "即刻启动也无法满足预留余量"
        self.budget_label.setText(
            f"<b>预算明细</b><br>切换 {format_time(result.switch_count * p.switch_s)}"
            f" ＋ 额外稳定 {format_time(result.switch_count * p.settling_s)}"
            f" ＋ 有效采样 {format_time(result.group_count * p.acquisition_s)}"
            f" ＋ 组间阻塞 {format_time((result.group_count - 1) * p.blocking_s)}<br>"
            f"启动延迟：{format_time(p.latency_s)}；每跳不可用：{format_time(p.unavailable_s)}<br>"
            f"采集完成：{format_time(result.data_complete_s)}；要求预留：{format_time(p.reserve_s)}<br>"
            f"设计所需：{format_time(result.required_s)}；设计余量：{format_time(result.design_margin_s)}<br>"
            f"<b>最迟允许启动：</b>{latest}（相对有效窗口起点）<br>"
            f"结果就绪：{format_time(result.result_ready_s)}（包含后处理 {format_time(p.processing_s)}）"
        )
        self.assumptions_label.setText("\n".join(result.assumptions))
        self.acquisition_hint.setText(f"每组同时采集 {format_time(p.acquisition_s)}；不乘通道数。\n点数是否足够，仍取决于算法、带宽和信噪比。")
        self.hop_hint.setText(f"{p.hop_rate_hz:,.7g} 跳/秒 ↔ {format_time(result.period_s)} / 跳")
        self.table.blockSignals(True)
        self.table.setRowCount(result.group_count)
        for row, group in enumerate(result.groups):
            cells = (str(group.index), "参考1 + " + ", ".join(map(str, group.elements[1:])),
                     f"{group.start_s * 1e6:.9g}", f"{group.acquisition_start_s * 1e6:.9g}", f"{group.end_s * 1e6:.9g}")
            for column, value in enumerate(cells):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                self.table.setItem(row, column, item)
        self.table.selectRow(min(selected, result.group_count - 1))
        self.table.blockSignals(False)
        self._select_group()
        payload = asdict(result)
        self.update_result(payload)
        self._plot_timer.start()
        return payload

    def _clear_result(self, message: str) -> None:
        """失败时同步清空结果、图和已发出的状态，防止旧结论被误用。"""
        self._plot_timer.stop()
        self._last_result = None
        self._plot_cache.clear()
        self.error_label.setText(message)
        self.status_label.setText("输入无效，当前结果已清除。\n" + message)
        self.status_label.setStyleSheet("color: #B42318; background: #FFF1F0; padding: 14px; border-radius: 8px;")
        for value in self.metrics.values():
            value.setText("—")
        for label in (self.budget_label, self.assumptions_label, self.hop_hint, self.acquisition_hint):
            label.clear()
        self.table.setRowCount(0)
        self.group_detail.setText("—")
        for figure, canvas in zip(self.figures, self.canvases):
            figure.clear()
            canvas.draw_idle()
        self.update_result({})

    def _select_group(self) -> None:
        """组选择只更新说明与时间轴，不触发重复的物理计算。"""
        if self._last_result is None or self.table.currentRow() < 0:
            return
        group = self._last_result.groups[self.table.currentRow()]
        self.group_detail.setText(
            f"第 {group.index} 组：参考阵元 1 + 阵元 {', '.join(map(str, group.elements[1:]))}；"
            f"组开始 {format_time(group.start_s)} → 采样 {format_time(group.acquisition_start_s)}"
            f" 至 {format_time(group.end_s)}。"
        )
        self._plot_cache.pop(0, None)
        if not self._initializing and self.tabs.currentIndex() == 0:
            self._plot_timer.start()

    def _pick_group(self, event) -> None:
        """点击时间条选中表格中对应的采集组。"""
        group = getattr(event.artist, "capture_group", 0)
        if group and self._last_result is not None:
            self.table.selectRow(group - 1)

    def _draw_current_plot(self, *_args) -> None:
        """仅重绘当前标签，使用局部字体配置避免改变其他工具。"""
        if self._initializing or self._last_result is None:
            return
        index = self.tabs.currentIndex()
        if index in self._plot_cache:
            return
        with rc_context({"font.family": "sans-serif", "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"], "axes.unicode_minus": False}):
            figure = self.figures[index]
            figure.clear()
            ax = figure.add_subplot(111)
            try:
                if index == 0:
                    self._draw_timeline(ax)
                else:
                    self._draw_sweep(ax)
                figure.tight_layout(pad=1.5)
                self.canvases[index].draw()
            except (ValueError, OverflowError, FloatingPointError, ZeroDivisionError):
                # 极端跨度可能超出绘图库的坐标能力，显示说明而不遗留旧图或终止事件循环。
                figure.clear()
                figure.text(0.5, 0.5, "数值跨度超出绘图范围，请调整参数。\n当前数字预算仍见上方。",
                            ha="center", va="center", color="#9A6700")
                self.canvases[index].draw()
        self._plot_cache[index] = True

    def _draw_timeline(self, ax) -> None:
        """按模型的阶段绘图，越过有效窗口的条段严格分割标红。"""
        result = self._last_result
        selected = max(1, self.table.currentRow() + 1)
        first = max(1, min(selected - 5, result.group_count - 11))
        visible = list(range(first, min(result.group_count + 1, first + 12)))
        rows = {group: index + 2 for index, group in enumerate(visible)}
        rows[0] = 1
        extent = max(result.effective_s, result.required_s, result.period_s)
        factor, unit = (1e9, "ns") if extent < 1e-6 else ((1e6, "μs") if extent < 1e-3 else (1e3, "ms"))
        ax.axvspan(0, result.effective_s * factor, color="#EAF7EE", zorder=0)
        ax.barh(0, result.effective_s * factor, height=0.5, color="#83C5A6")
        ax.axvline(result.effective_s * factor, color="#B42318", linestyle="--", linewidth=1.2)
        for stage in result.stages:
            if stage.group not in rows or stage.duration_s == 0:
                continue
            start, end = stage.start_s, stage.end_s
            _, color = STAGE_STYLES[stage.kind]
            # 已经超时的阶段完全标红；跨越边界的阶段保留其窗口内颜色。
            split = min(end, max(start, result.effective_s))
            for left, right, fill in ((start, split, color), (split, end, "#E55A57")):
                if right <= left:
                    continue
                bars = ax.barh(rows[stage.group], (right - left) * factor, left=left * factor,
                               height=0.58, color=fill, edgecolor="#23354D" if stage.group == selected else "none",
                               linewidth=1, picker=True)
                for bar in bars:
                    bar.capture_group = stage.group
        if result.params.reserve_s > 0:
            ax.axvspan(result.data_complete_s * factor, result.required_s * factor,
                       facecolor="none", edgecolor="#7593A9", hatch="///", linewidth=0.7)
        ax.set_yticks([0, 1] + [rows[g] for g in visible],
                      ["有效窗口", "启动延迟"] + [f"第 {g} 组" for g in visible])
        ax.set_ylim(len(visible) + 1.8, -0.8)
        ax.set_xlim(0, extent * factor * 1.05)
        ax.set_xlabel(f"相对有效窗口起点的时间 / {unit}")
        ax.set_title(f"每跳不可用时间 {format_time(result.params.unavailable_s)} 已从周期扣除"
                     + (" · 仅显示所选组附近的12组" if result.group_count > 12 else ""), fontsize=10)
        handles = [Patch(facecolor=c, label=n) for n, c in STAGE_STYLES.values()]
        handles.append(Patch(facecolor="#E55A57", label="超出有效窗口"))
        if result.params.reserve_s > 0:
            handles.append(Patch(facecolor="none", edgecolor="#7593A9", hatch="///", label="要求预留余量"))
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.17),
                  ncol=4 if result.params.reserve_s > 0 else 6, fontsize=8)
        ax.grid(axis="x", alpha=0.18)

    def _draw_sweep(self, ax) -> None:
        """用统一计算器扫描跳速，标出当前点与满足余量的临界点。"""
        result = self._last_result
        current = result.params.hop_rate_hz
        critical = result.reserved_max_hop_rate_hz
        low, high = min(current, critical) / 4, max(current, critical) * 4
        # 对输入允许的极端有限值，避免绘图扩展边界后出现零或无穷。
        low = max(low, np.finfo(float).tiny)
        high = min(high, np.finfo(float).max / 2)
        rates = tuple(float(x) for x in np.geomspace(low, high, 120))
        sweep = CaptureCalculator.sweep(result.params, rates)
        margins = np.array([point.design_margin_s for point in sweep]) * 1e6
        ax.axhline(0, color="#667085", linewidth=1)
        ax.plot(rates, margins, color="#367CBD", linewidth=2)
        ax.fill_between(rates, margins, 0, where=margins >= 0, color="#E3F4EB")
        ax.fill_between(rates, margins, 0, where=margins < 0, color="#FFE8E5")
        ax.axvline(critical, color="#13765A", linestyle="--", label=f"预留余量临界 {critical:,.7g} 跳/秒")
        ax.scatter([current], [result.design_margin_s * 1e6], color="#DB6E2C", zorder=5,
                   label=f"当前 {current:,.7g} 跳/秒")
        ax.set_xscale("log")
        ax.set_xlabel("跳速 / 跳每秒（对数坐标）")
        ax.set_ylabel("设计余量 / μs")
        ax.set_title("净开销与启动延迟保持当前值；不代表连续处理吞吐能力", fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.18)

    def get_intuition_content(self) -> str:
        """先用换房间讲话和逐组拍照解释信号与采集窗口。"""
        return (
            "<b>信号像一个不断换房间讲话的人。</b>窄带接收机只听一间房，声音时有时无，"
            "可能只是载频跳出了接收带宽，发射机并没有停止发射。覆盖整个跳频范围的宽带接收机可能看见完整的跳动过程。<br><br>"
            "<b>跳频 FH ≠ 调频 FM：</b>跳频是在不同频点之间切换载频；调频是利用频率变化携带信息。单跳内部仍可使用 FM、FSK、PSK 等调制。<br>"
            "<b>整阵采集像分组拍合照：</b>参考阵元始终在画面里，另一个通道轮流拍其余阵元。九元双通道需要八组照片，"
            "必须在同一跳的有效时间内拍齐。首组也需调整镜头就计八次切换；已经就绪则只有七次组间切换。<br>"
            "<b>跳速越高，每跳越短：</b>10,000 跳/秒对应100 μs周期，但频率过渡、稳定或停发会缩短连续可用窗口。"
            "占空比相同但碎片化的多个短片段，不能直接拼成这里的一个连续窗口。"
        )

    def get_math_model_content(self) -> str:
        """按分组、预算、判定和反演四步解释变量与公式。"""
        return (
            "<b>① 分组：</b>N为含参考的阵元总数，C为含参考的相干通道数。一路固定参考，每组最多覆盖C−1个新阵元。<br>"
            "G = ⌈(N−1)/(C−1)⌉；首组需要切换时 S = G，已接通且稳定时 S = G−1。<br><br>"
            "<b>② 串行扫描：</b>T<sub>scan</sub> = S(t<sub>sw</sub> + t<sub>settle</sub>) + Gt<sub>acq</sub> + (G−1)t<sub>block</sub>。<br>"
            "t<sub>sw</sub>是命令到切换完成的时间；t<sub>settle</sub>仅包含尚未计入的额外稳定；"
            "t<sub>acq</sub>是每组各通道同时采样的有效时长，不乘通道数；t<sub>block</sub>是组间额外净等待。"
            "采样换算为 t<sub>acq</sub> = 每通道有效点数 / 有效采样率，50点 / 10 MS/s = 5 μs。<br><br>"
            "<b>③ 同跳判定：</b>T<sub>h</sub> = 1/R；T<sub>eff</sub> = max(0, T<sub>h</sub> − T<sub>dead</sub>)。<br>"
            "R为跳速，T<sub>dead</sub>为每跳不可用时间，剩余部分须为单个连续有效窗口。"
            "T<sub>data</sub> = L + T<sub>scan</sub>，T<sub>need</sub> = T<sub>data</sub> + M。<br>"
            "L从有效窗口开始计到首条切换命令（首组已就绪时计到采样），M为要求预留余量。"
            "实际余量 = T<sub>eff</sub> − T<sub>data</sub>；设计余量 = T<sub>eff</sub> − T<sub>need</sub>。<br><br>"
            "<b>④ 跳速上限：</b>R<sub>max</sub> = 1/(T<sub>dead</sub> + T<sub>data</sub>)；"
            "保留余量时 R<sub>max,M</sub> = 1/(T<sub>dead</sub> + T<sub>need</sub>)。<br>"
            "最迟启动 = T<sub>eff</sub> − T<sub>scan</sub> − M，相对于有效窗口起点，负值表示即刻启动仍不足。"
            "采集后处理只增加结果就绪时间，不要求信号继续存在。<br><br>"
            "<b>手算示例：</b>九元双通道、首组计切换、500 ns切换、每组5 μs采样、其他开销零："
            "8×0.5 + 8×5 = 44 μs，上限约22,727跳/秒。20,000跳/秒剩6 μs，25,000跳/秒缺4 μs。"
        )

    def get_engineering_content(self) -> str:
        """明确时序的必要条件和相干、频率、算法方面的限制。"""
        return (
            "<b>时间够只是必要条件：</b>瞬时带宽必须覆盖目标当前频点及其信号带宽；搜索、调谐等净延迟计入启动延迟。"
            "信噪比、通道校准、参考路衰落、多径和干扰都会影响结果。本工具不输出真实捕获概率或测向精度。<br>"
            "<b>相位比较需要共同参考：</b>每组同时测量目标阵元与参考路，利用 x<sub>i</sub>(t)x<sub>ref</sub><sup>*</sup>(t) "
            "消除共同源相位；接收通道仍须相干并经过校准，同一跳内传播条件与到达方向要足够稳定。"
            "宽带信号及显著路径延迟还需要适用的相关、分频或时延处理，不能把简单窄带相位解释无限推广。<br>"
            "<b>不要直接跨跳拼相位：</b>空间相位与频率有关，跳频后的波长、阵列响应和校准可能不同。频率感知的跨跳联合估计不属于本模型。<br>"
            "<b>不要重复计时：</b>500 ns若已包含控制响应或幅相稳定，就不再另加相同部分。重叠处理填写实测净开销。"
            "末次采样后的离线处理单列；若处理阻塞下一组采集，将那部分填入组间阻塞。<br>"
            "<b>最佳情况不是保证：</b>启动延迟为零只评估刚好赶上有效窗口起点的情况；异步发现信号时须计入已损失的有效时间。"
            "每组采样时间需由带宽、算法、信噪比及精度要求确定，不能由开关速度推断。<br>"
            "<b>单跳完成不等于每跳连续测向：</b>缓存、流水处理、复位、搜索与吞吐量还需另行评估。"
            "不规则跳频应按最短连续有效窗口及保守净开销核算，不能只使用平均跳速。"
        )

    def get_history_content(self) -> str:
        """给出技术背景与可追溯的一手资料，不将预算公式冒充设备指标。"""
        return (
            "<b>从相位比较到数字测向：</b>干涉仪用阵元间的相位关系推断到达方向，相关干涉仪还会与校准响应比较。"
            "宽带数字接收可同时观察更多频点，但有限通道阵列仍需核算切换与采样窗口。"
            "ITU-R的测向测试方法把最短信号持续时间作为系统实测指标；简单预算不能替代这样的验证。<br><br>"
            "<b>资料：</b>"
            '<a href="https://www.rohde-schwarz.com/us/knowledge-center/technology-fundamentals/hopper-signals/hopper-signals_256050.html">R&amp;S：跳频基础</a> · '
            '<a href="https://helpfiles.keysight.com/csg/89600B/Webhelp/Subsystems/pulse/content/metric_all_frequency_hopping.htm">Keysight：跳频时间定义</a> · '
            '<a href="https://cdn.rohde-schwarz.com/am/us/campaigns_2/a_d/Intro-to-direction-finding-methodologies.pdf">R&amp;S：测向方法</a> · '
            '<a href="https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-SM.2125-1-2011-PDF-E.pdf">ITU-R SM.2125-1 §3.3.3</a><br>'
            "本页公式是针对固定参考、单个连续窗口和串行净开销建立的工程预算，不是上述资料给出的设备性能保证。"
        )
