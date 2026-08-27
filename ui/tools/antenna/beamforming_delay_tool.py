# -*- coding: utf-8 -*-
"""
相控阵移相与时延工具 UI
Phased Array Beamforming Phase & Delay Configuration Tool UI

版本: v1.0.0
功能:
- 支持一维均匀线阵 (ULA) 与二维均匀面阵 (UPA) 模式自由切换
- 支持射频频率输入及物理间距 (mm) 与电长度 (d/λ) 的双向无缝联动
- 提供相邻通道相位差/时延差、全阵列最大时延、移相器 RMS 量化误差等大盘指标
- 提供通道逐点明细表格 (Channel Config Table) 及 CSV 配置文件一键导出
- 提供通道相位/时延分布阶梯图/热力图及宽带波束斜视 (Beam Squint) 分析图表
- 深度注入四维微波工程知识科普 (直观比喻、严谨推导、工程避坑、发展史)
"""

import math
import csv
from typing import Optional, Dict, Any

import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QComboBox, QPushButton,
    QFrame, QGroupBox, QDoubleSpinBox, QSpinBox,
    QLineEdit, QRadioButton, QButtonGroup, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QDoubleValidator

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

# 设置 Matplotlib 中文字体与负号支持
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False

from ui.base.tool_base import ToolBase
from core.antenna.beamforming_delay import (
    BeamformingDelayCalculator,
    BeamformingDelayParams,
    BeamformingDelayResult,
    ArrayGeometry
)
from core.constants import SPEED_OF_LIGHT


class BeamformingDelayTool(ToolBase):
    """相控阵移相与时延配置计算工具"""

    tool_name = "相控阵移相与时延"
    tool_icon = "🧭"
    tool_category = "antenna"
    tool_description = "相控阵天线通道级相位差、真时延配置、移相器量化与宽带波束斜视评估。"

    def __init__(self, parent: Optional[QWidget] = None):
        self.calculator = BeamformingDelayCalculator()
        self._is_updating = False  # 防止双向联动死循环
        self._last_result: Optional[BeamformingDelayResult] = None
        super().__init__(parent)
        
        # 初始化触发首次计算
        self._update_calculation()

    # ==================== 1. 左侧输入面板 ====================

    def create_input_panel(self) -> QWidget:
        """创建左侧参数控制面板 (舒展优雅布局，层级分明，呼吸感良好)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(6)

        # 1. 快速上手区 (2x2 网格，清晰完备)
        preset_group = QGroupBox("⚡ 快速预设 (小白推荐)")
        preset_layout = QGridLayout()
        preset_layout.setContentsMargins(8, 6, 8, 6)
        preset_layout.setSpacing(5)

        btn_preset1 = QPushButton("X波段 8元线阵")
        btn_preset2 = QPushButton("Ku波段 16元线阵")
        btn_preset3 = QPushButton("Ka波段 8x8面阵")
        btn_preset4 = QPushButton("5G 64通道面阵")

        for b in [btn_preset1, btn_preset2, btn_preset3, btn_preset4]:
            b.setStyleSheet("padding: 3px 6px; font-size: 11.5px;")

        btn_preset1.clicked.connect(lambda: self._apply_preset("x_band_ula"))
        btn_preset2.clicked.connect(lambda: self._apply_preset("ku_band_ula"))
        btn_preset3.clicked.connect(lambda: self._apply_preset("ka_band_upa"))
        btn_preset4.clicked.connect(lambda: self._apply_preset("5g_n78_upa"))

        preset_layout.addWidget(btn_preset1, 0, 0)
        preset_layout.addWidget(btn_preset2, 0, 1)
        preset_layout.addWidget(btn_preset3, 1, 0)
        preset_layout.addWidget(btn_preset4, 1, 1)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # 2. 阵列拓扑与硬件规模
        geom_group = QGroupBox("📐 阵列拓扑与硬件规模")
        geom_layout = QGridLayout()
        geom_layout.setContentsMargins(8, 6, 8, 6)
        geom_layout.setSpacing(5)

        self.radio_ula = QRadioButton("一维线阵 (ULA)")
        self.radio_upa = QRadioButton("二维面阵 (UPA)")
        self.radio_ula.setChecked(True)

        self.geom_btn_group = QButtonGroup(self)
        self.geom_btn_group.addButton(self.radio_ula, 0)
        self.geom_btn_group.addButton(self.radio_upa, 1)
        self.geom_btn_group.idClicked.connect(self._on_geometry_changed)

        geom_mode_layout = QHBoxLayout()
        geom_mode_layout.addWidget(self.radio_ula)
        geom_mode_layout.addWidget(self.radio_upa)
        geom_layout.addLayout(geom_mode_layout, 0, 0, 1, 4)

        # Nx 与 Ny 并排
        self.lbl_nx = QLabel("Nx (阵元数):")
        self.spin_nx = QSpinBox()
        self.spin_nx.setRange(1, 256)
        self.spin_nx.setValue(8)
        self.spin_nx.valueChanged.connect(self._update_calculation)

        self.lbl_ny = QLabel("Ny (阵元数):")
        self.spin_ny = QSpinBox()
        self.spin_ny.setRange(1, 256)
        self.spin_ny.setValue(8)
        self.spin_ny.setEnabled(False)  # 初始 ULA 禁用
        self.spin_ny.valueChanged.connect(self._update_calculation)

        geom_layout.addWidget(self.lbl_nx, 1, 0)
        geom_layout.addWidget(self.spin_nx, 1, 1)
        geom_layout.addWidget(self.lbl_ny, 1, 2)
        geom_layout.addWidget(self.spin_ny, 1, 3)

        geom_group.setLayout(geom_layout)
        layout.addWidget(geom_group)

        # 3. 频段波长与阵元间距 (一体化物理参数关联)
        spacing_group = QGroupBox("📡 频段波长与阵元间距")
        spacing_layout = QGridLayout()
        spacing_layout.setContentsMargins(8, 6, 8, 6)
        spacing_layout.setSpacing(5)

        # 频率与波长同行
        self.input_freq = QLineEdit("10.0")
        self.input_freq.setValidator(QDoubleValidator(0.001, 1000.0, 4))
        self.input_freq.setFixedWidth(65)
        self.input_freq.textChanged.connect(self._on_frequency_changed)

        self.combo_freq_unit = QComboBox()
        self.combo_freq_unit.addItems(["GHz", "MHz"])
        self.combo_freq_unit.setFixedWidth(62)
        self.combo_freq_unit.currentIndexChanged.connect(self._on_frequency_changed)

        self.lbl_wavelength = QLabel("λ: 29.98 mm")
        self.lbl_wavelength.setStyleSheet("color: #2B6CB0; font-weight: bold; font-family: Consolas; font-size: 12px;")

        freq_row = QHBoxLayout()
        freq_row.addWidget(QLabel("工作频率:"))
        freq_row.addWidget(self.input_freq)
        freq_row.addWidget(self.combo_freq_unit)
        freq_row.addSpacing(8)
        freq_row.addWidget(self.lbl_wavelength)
        freq_row.addStretch()
        spacing_layout.addLayout(freq_row, 0, 0, 1, 3)

        # X轴间距 (dx)
        self.spin_dx_mm = QDoubleSpinBox()
        self.spin_dx_mm.setRange(0.1, 5000.0)
        self.spin_dx_mm.setDecimals(3)
        self.spin_dx_mm.setValue(14.990)
        self.spin_dx_mm.setSuffix(" mm")
        self.spin_dx_mm.valueChanged.connect(self._on_dx_mm_changed)

        self.spin_dx_lambda = QDoubleSpinBox()
        self.spin_dx_lambda.setRange(0.01, 10.0)
        self.spin_dx_lambda.setDecimals(3)
        self.spin_dx_lambda.setSingleStep(0.05)
        self.spin_dx_lambda.setValue(0.500)
        self.spin_dx_lambda.setSuffix(" λ")
        self.spin_dx_lambda.valueChanged.connect(self._on_dx_lambda_changed)

        spacing_layout.addWidget(QLabel("X轴间距:"), 1, 0)
        spacing_layout.addWidget(self.spin_dx_mm, 1, 1)
        spacing_layout.addWidget(self.spin_dx_lambda, 1, 2)

        # Y轴间距 (dy)
        self.lbl_dy_mm = QLabel("Y轴间距:")
        self.spin_dy_mm = QDoubleSpinBox()
        self.spin_dy_mm.setRange(0.1, 5000.0)
        self.spin_dy_mm.setDecimals(3)
        self.spin_dy_mm.setValue(14.990)
        self.spin_dy_mm.setSuffix(" mm")
        self.spin_dy_mm.setEnabled(False)
        self.spin_dy_mm.valueChanged.connect(self._on_dy_mm_changed)

        self.lbl_dy_lambda = self.lbl_dy_mm  # 保持属性兼容
        self.spin_dy_lambda = QDoubleSpinBox()
        self.spin_dy_lambda.setRange(0.01, 10.0)
        self.spin_dy_lambda.setDecimals(3)
        self.spin_dy_lambda.setSingleStep(0.05)
        self.spin_dy_lambda.setValue(0.500)
        self.spin_dy_lambda.setSuffix(" λ")
        self.spin_dy_lambda.setEnabled(False)
        self.spin_dy_lambda.valueChanged.connect(self._on_dy_lambda_changed)

        spacing_layout.addWidget(self.lbl_dy_mm, 2, 0)
        spacing_layout.addWidget(self.spin_dy_mm, 2, 1)
        spacing_layout.addWidget(self.spin_dy_lambda, 2, 2)

        spacing_group.setLayout(spacing_layout)
        layout.addWidget(spacing_group)

        # 4. 波束扫描指向 (Beam Steering)
        scan_group = QGroupBox("🎯 目标波束指向 (Beam Steering)")
        scan_layout = QVBoxLayout()
        scan_layout.setContentsMargins(8, 6, 8, 6)
        scan_layout.setSpacing(5)

        # Theta 俯仰角 / 偏离角
        theta_header = QHBoxLayout()
        self.lbl_theta_title = QLabel("扫描角 (θ Theta):")
        self.lbl_theta_title.setStyleSheet("font-weight: 500;")

        self.spin_theta = QDoubleSpinBox()
        self.spin_theta.setRange(-90.0, 90.0)
        self.spin_theta.setDecimals(1)
        self.spin_theta.setSingleStep(1.0)
        self.spin_theta.setValue(30.0)
        self.spin_theta.setSuffix("°")
        self.spin_theta.setFixedWidth(95)
        self.spin_theta.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spin_theta.setStyleSheet("""
            QDoubleSpinBox {
                font-weight: bold;
                color: #2B6CB0;
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-size: 13px;
                padding: 2px 22px 2px 6px;
                border: 1px solid #CBD5E0;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QDoubleSpinBox:focus {
                border-color: #3182CE;
                background-color: #F7FAFC;
            }
        """)
        self.spin_theta.valueChanged.connect(self._on_theta_spin_changed)

        theta_header.addWidget(self.lbl_theta_title)
        theta_header.addStretch()
        theta_header.addWidget(self.spin_theta)

        self.slider_theta = QSlider(Qt.Orientation.Horizontal)
        self.slider_theta.setRange(-900, 900)
        self.slider_theta.setValue(300)
        self.slider_theta.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_theta.setTickInterval(150)
        self.slider_theta.valueChanged.connect(self._on_theta_slider_changed)

        scan_layout.addLayout(theta_header)
        scan_layout.addWidget(self.slider_theta)

        # Phi 方位角 (仅 UPA)
        self.phi_container = QWidget()
        phi_layout = QVBoxLayout(self.phi_container)
        phi_layout.setContentsMargins(0, 0, 0, 0)
        phi_layout.setSpacing(5)

        phi_header = QHBoxLayout()
        self.lbl_phi_title = QLabel("方位角 (φ Phi):")
        self.lbl_phi_title.setStyleSheet("font-weight: 500;")

        self.spin_phi = QDoubleSpinBox()
        self.spin_phi.setRange(0.0, 360.0)
        self.spin_phi.setDecimals(1)
        self.spin_phi.setSingleStep(1.0)
        self.spin_phi.setValue(0.0)
        self.spin_phi.setSuffix("°")
        self.spin_phi.setFixedWidth(95)
        self.spin_phi.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spin_phi.setStyleSheet("""
            QDoubleSpinBox {
                font-weight: bold;
                color: #2B6CB0;
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-size: 13px;
                padding: 2px 22px 2px 6px;
                border: 1px solid #CBD5E0;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QDoubleSpinBox:focus {
                border-color: #3182CE;
                background-color: #F7FAFC;
            }
        """)
        self.spin_phi.valueChanged.connect(self._on_phi_spin_changed)

        phi_header.addWidget(self.lbl_phi_title)
        phi_header.addStretch()
        phi_header.addWidget(self.spin_phi)

        self.slider_phi = QSlider(Qt.Orientation.Horizontal)
        self.slider_phi.setRange(0, 3600)
        self.slider_phi.setValue(0)
        self.slider_phi.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_phi.setTickInterval(450)
        self.slider_phi.valueChanged.connect(self._on_phi_slider_changed)

        phi_layout.addLayout(phi_header)
        phi_layout.addWidget(self.slider_phi)
        self.phi_container.setVisible(False)  # 默认 ULA 模式隐藏 Phi 方位角

        scan_layout.addWidget(self.phi_container)
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        # 5. 移相器量化与波束斜视配置
        adv_group = QGroupBox("⚙️ 移相器量化与斜视分析")
        adv_layout = QGridLayout()
        adv_layout.setContentsMargins(8, 6, 8, 6)
        adv_layout.setSpacing(5)

        self.combo_bits = QComboBox()
        self.combo_bits.addItem("连续 (无量化)", 0)
        self.combo_bits.addItem("4-bit (22.5°)", 4)
        self.combo_bits.addItem("5-bit (11.25°)", 5)
        self.combo_bits.addItem("6-bit (5.625°)", 6)
        self.combo_bits.addItem("7-bit (2.8125°)", 7)
        self.combo_bits.addItem("8-bit (1.40625°)", 8)
        self.combo_bits.setCurrentIndex(3)  # 默认 6-bit
        self.combo_bits.currentIndexChanged.connect(self._update_calculation)

        self.input_bw = QLineEdit("2.0")
        self.input_bw.setValidator(QDoubleValidator(0.01, 100.0, 3))
        self.input_bw.setFixedWidth(55)
        self.input_bw.textChanged.connect(self._update_calculation)

        self.combo_bw_unit = QComboBox()
        self.combo_bw_unit.addItems(["GHz", "MHz", "% 带宽"])
        self.combo_bw_unit.setFixedWidth(70)
        self.combo_bw_unit.currentIndexChanged.connect(self._update_calculation)

        bw_row = QHBoxLayout()
        bw_row.addWidget(self.input_bw)
        bw_row.addWidget(self.combo_bw_unit)

        adv_layout.addWidget(QLabel("移相位数:"), 0, 0)
        adv_layout.addWidget(self.combo_bits, 0, 1)
        adv_layout.addWidget(QLabel("斜视带宽:"), 0, 2)
        adv_layout.addLayout(bw_row, 0, 3)

        adv_group.setLayout(adv_layout)
        layout.addWidget(adv_group)

        layout.addStretch()
        return panel

    # ==================== 2. 右侧结果与可视化面板 ====================

    def create_result_panel(self) -> QWidget:
        """创建右侧指标看板、通道表格与可视化面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 0, 4, 4)
        layout.setSpacing(10)

        # 1. 顶部核心指标大盘
        dashboard_group = QGroupBox("📊 相控阵通道核心指标大盘")
        dashboard_layout = QGridLayout()
        dashboard_layout.setSpacing(10)

        self.lbl_delta_phase = self._make_metric_label()
        self.lbl_delta_delay = self._make_metric_label()
        self.lbl_max_delay = self._make_metric_label()
        self.lbl_rms_error = self._make_metric_label(color="#D69E2E")

        dashboard_layout.addWidget(QLabel("相邻阵元相位差 (ΔΦ):"), 0, 0)
        dashboard_layout.addWidget(self.lbl_delta_phase, 0, 1)

        dashboard_layout.addWidget(QLabel("相邻阵元真时延 (Δτ):"), 0, 2)
        dashboard_layout.addWidget(self.lbl_delta_delay, 0, 3)

        dashboard_layout.addWidget(QLabel("全阵最大时延跨度:"), 1, 0)
        dashboard_layout.addWidget(self.lbl_max_delay, 1, 1)

        dashboard_layout.addWidget(QLabel("移相器量化 RMS 误差:"), 1, 2)
        dashboard_layout.addWidget(self.lbl_rms_error, 1, 3)

        dashboard_group.setLayout(dashboard_layout)
        layout.addWidget(dashboard_group)

        # 2. 中部多功能 Tab 选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Tab 1: 通道配置明细表
        tab_table = QWidget()
        tab_table_layout = QVBoxLayout(tab_table)
        tab_table_layout.setContentsMargins(6, 6, 6, 6)
        tab_table_layout.setSpacing(6)

        # 表格工具栏
        table_bar = QHBoxLayout()
        self.lbl_table_info = QLabel("共计 8 个通道")
        self.lbl_table_info.setStyleSheet("color: #4A5568; font-size: 12px; font-weight: 500;")

        self.btn_export_csv = QPushButton("📥 导出通道配置表 (CSV)")
        self.btn_export_csv.setStyleSheet(
            "background-color: #3182CE; color: white; padding: 5px 12px; font-weight: bold; border-radius: 4px;"
        )
        self.btn_export_csv.clicked.connect(self._export_to_csv)

        table_bar.addWidget(self.lbl_table_info)
        table_bar.addStretch()
        table_bar.addWidget(self.btn_export_csv)
        tab_table_layout.addLayout(table_bar)

        # 表格组件 (高度适中 300px，支持完整呈现更多数据行，开启常驻水平滑动条)
        self.table_channels = QTableWidget()
        self.table_channels.setColumnCount(10)
        self.table_channels.setHorizontalHeaderLabels([
            "通道编号", "网格位置", "X坐标(mm)", "Y坐标(mm)",
            "连续相位(°)", "模360相位(°)", "量化相位(°)",
            "量化码字(Hex/Dec)", "量化误差(°)", "真时延(ps)"
        ])
        self.table_channels.setFixedHeight(300)
        self.table_channels.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table_channels.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_channels.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_channels.horizontalHeader().setStretchLastSection(False)
        self.table_channels.setAlternatingRowColors(True)
        self.table_channels.setStyleSheet("""
            QTableWidget {
                gridline-color: #E2E8F0;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                background-color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #EDF2F7;
                font-weight: bold;
                padding: 4px 8px;
                border: 1px solid #CBD5E0;
            }
            QScrollBar:horizontal {
                background-color: #EDF2F7;
                height: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #A0AEC0;
                border-radius: 5px;
                min-width: 40px;
                margin: 1px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #718096;
            }
        """)
        tab_table_layout.addWidget(self.table_channels)
        self.tab_widget.addTab(tab_table, "📋 通道配置明细表")

        # Tab 2: 通道相位与时延分布可视化 (高度 350px，双子图清晰舒展不扁平)
        tab_dist = QWidget()
        tab_dist_layout = QVBoxLayout(tab_dist)
        tab_dist_layout.setContentsMargins(2, 2, 2, 2)

        self.fig_dist = Figure(figsize=(3.8, 3.4), dpi=100)
        self.canvas_dist = FigureCanvas(self.fig_dist)
        self.canvas_dist.setFixedHeight(350)
        self.canvas_dist.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tab_dist_layout.addWidget(self.canvas_dist)
        self.tab_widget.addTab(tab_dist, "📈 相位/时延分布图")

        # Tab 3: 宽带波束斜视 (Beam Squint) 分析 (高度 330px，比例均衡适度)
        tab_squint = QWidget()
        tab_squint_layout = QVBoxLayout(tab_squint)
        tab_squint_layout.setContentsMargins(2, 2, 2, 2)

        self.fig_squint = Figure(figsize=(3.8, 3.2), dpi=100)
        self.canvas_squint = FigureCanvas(self.fig_squint)
        self.canvas_squint.setFixedHeight(330)
        self.canvas_squint.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tab_squint_layout.addWidget(self.canvas_squint)
        self.tab_widget.addTab(tab_squint, "🌪️ 宽带波束斜视分析")

        # 切换 Tab 时按需重绘
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tab_widget)
        return panel

    def _make_metric_label(self, color: str = "#2B6CB0") -> QLabel:
        lbl = QLabel("-")
        lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color}; font-family: 'Consolas', monospace;")
        return lbl

    def _on_tab_changed(self, index: int):
        """切换 Tab 选项卡时按需触发对应图表的自适应重绘"""
        if not self._last_result:
            return
        if index == 1:
            self._draw_distribution_plot(self._last_result)
        elif index == 2:
            self._draw_squint_plot(self._last_result)

    # ==================== 3. 交互事件与双向联动 ====================

    def _apply_preset(self, preset_key: str):
        """应用快速预设"""
        self._is_updating = True
        try:
            if preset_key == "x_band_ula":
                self.radio_ula.setChecked(True)
                self.spin_nx.setValue(8)
                self.input_freq.setText("10.0")
                self.combo_freq_unit.setCurrentText("GHz")
                self.spin_dx_lambda.setValue(0.5)
                self.spin_theta.setValue(30.0)
                self.slider_theta.setValue(300)
                self.combo_bits.setCurrentIndex(3)  # 6-bit
                self.input_bw.setText("2.0")
                self.combo_bw_unit.setCurrentText("GHz")
            elif preset_key == "ku_band_ula":
                self.radio_ula.setChecked(True)
                self.spin_nx.setValue(16)
                self.input_freq.setText("15.0")
                self.combo_freq_unit.setCurrentText("GHz")
                self.spin_dx_lambda.setValue(0.5)
                self.spin_theta.setValue(45.0)
                self.slider_theta.setValue(450)
                self.combo_bits.setCurrentIndex(3)  # 6-bit
                self.input_bw.setText("3.0")
                self.combo_bw_unit.setCurrentText("GHz")
            elif preset_key == "ka_band_upa":
                self.radio_upa.setChecked(True)
                self.spin_nx.setValue(8)
                self.spin_ny.setValue(8)
                self.input_freq.setText("28.0")
                self.combo_freq_unit.setCurrentText("GHz")
                self.spin_dx_lambda.setValue(0.5)
                self.spin_dy_lambda.setValue(0.5)
                self.spin_theta.setValue(30.0)
                self.slider_theta.setValue(300)
                self.spin_phi.setValue(45.0)
                self.slider_phi.setValue(450)
                self.combo_bits.setCurrentIndex(3)  # 6-bit
                self.input_bw.setText("2.0")
                self.combo_bw_unit.setCurrentText("GHz")
            elif preset_key == "5g_n78_upa":
                self.radio_upa.setChecked(True)
                self.spin_nx.setValue(8)
                self.spin_ny.setValue(8)
                self.input_freq.setText("3.5")
                self.combo_freq_unit.setCurrentText("GHz")
                self.spin_dx_lambda.setValue(0.5)
                self.spin_dy_lambda.setValue(0.5)
                self.spin_theta.setValue(20.0)
                self.slider_theta.setValue(200)
                self.spin_phi.setValue(30.0)
                self.slider_phi.setValue(300)
                self.combo_bits.setCurrentIndex(3)  # 6-bit
                self.input_bw.setText("200.0")
                self.combo_bw_unit.setCurrentText("MHz")

            self._update_geometry_ui_state()
            self._sync_physical_spacings()
        finally:
            self._is_updating = False

        self._update_calculation()

    def _on_geometry_changed(self, mode_id: int):
        """阵列拓扑模式切换 (ULA vs UPA)"""
        self._update_geometry_ui_state()
        self._update_calculation()

    def _update_geometry_ui_state(self):
        """根据当前拓扑更新控件可编辑与可见状态 (ULA 智能精简，UPA 全功能展开)"""
        is_upa = self.radio_upa.isChecked()
        self.spin_ny.setEnabled(is_upa)
        self.lbl_ny.setEnabled(is_upa)
        self.lbl_dy_mm.setEnabled(is_upa)
        self.spin_dy_mm.setEnabled(is_upa)
        self.lbl_dy_lambda.setEnabled(is_upa)
        self.spin_dy_lambda.setEnabled(is_upa)
        self.phi_container.setVisible(is_upa)

        if not is_upa:
            # ULA 模式下，Theta 滑块允许 -90.0° ~ +90.0°
            self.spin_theta.setRange(-90.0, 90.0)
            self.slider_theta.setRange(-900, 900)
            self.lbl_theta_title.setText("扫描角 (θ Theta):")
        else:
            # UPA 模式下，Theta 为俯仰偏角 0.0° ~ 90.0°
            if self.spin_theta.value() < 0:
                self.spin_theta.setValue(abs(self.spin_theta.value()))
            self.spin_theta.setRange(0.0, 90.0)
            self.slider_theta.setRange(0, 900)
            self.lbl_theta_title.setText("俯仰角 (θ Theta):")

    def _get_frequency_hz(self) -> float:
        """获取当前输入的频率 (Hz)"""
        try:
            val = float(self.input_freq.text())
            if val <= 0:
                return 10.0e9
            unit = self.combo_freq_unit.currentText()
            return val * 1e9 if unit == "GHz" else val * 1e6
        except ValueError:
            return 10.0e9

    def _on_frequency_changed(self):
        """
        频率改变时联动更新波长显示与电间距。
        物理原理：天线硬件物理阵元间距 (mm) 制造后保持固定不变，
        因此锁定物理间距不变，根据新波长动态更新电间距 d/λ，真时延 Δτ 保持物理恒定！
        """
        if self._is_updating:
            return
        self._is_updating = True
        try:
            freq_hz = self._get_frequency_hz()
            wl_mm = (SPEED_OF_LIGHT / freq_hz) * 1000.0
            self.lbl_wavelength.setText(f"波长 λ: {wl_mm:.2f} mm")
            
            # 保持物理间距 mm 不变，联动更新电间距 λ 倍数
            dx_mm = self.spin_dx_mm.value()
            self.spin_dx_lambda.setValue(dx_mm / wl_mm)
            
            dy_mm = self.spin_dy_mm.value()
            self.spin_dy_lambda.setValue(dy_mm / wl_mm)
        finally:
            self._is_updating = False

        self._update_calculation()

    def _sync_physical_spacings(self):
        """根据当前电间距同步计算物理间距 (仅在快速预设初始化时使用)"""
        freq_hz = self._get_frequency_hz()
        wl_mm = (SPEED_OF_LIGHT / freq_hz) * 1000.0
        self.lbl_wavelength.setText(f"波长 λ: {wl_mm:.2f} mm")
        self.spin_dx_mm.setValue(self.spin_dx_lambda.value() * wl_mm)
        self.spin_dy_mm.setValue(self.spin_dy_lambda.value() * wl_mm)

    def _on_dx_mm_changed(self, val_mm: float):
        """X物理间距改变 -> 联动更新电间距"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            freq_hz = self._get_frequency_hz()
            wl_mm = (SPEED_OF_LIGHT / freq_hz) * 1000.0
            self.spin_dx_lambda.setValue(val_mm / wl_mm)
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_dx_lambda_changed(self, val_lambda: float):
        """X电间距改变 -> 联动更新物理间距"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            freq_hz = self._get_frequency_hz()
            wl_mm = (SPEED_OF_LIGHT / freq_hz) * 1000.0
            self.spin_dx_mm.setValue(val_lambda * wl_mm)
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_dy_mm_changed(self, val_mm: float):
        """Y物理间距改变 -> 联动更新电间距"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            freq_hz = self._get_frequency_hz()
            wl_mm = (SPEED_OF_LIGHT / freq_hz) * 1000.0
            self.spin_dy_lambda.setValue(val_mm / wl_mm)
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_dy_lambda_changed(self, val_lambda: float):
        """Y电间距改变 -> 联动更新物理间距"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            freq_hz = self._get_frequency_hz()
            wl_mm = (SPEED_OF_LIGHT / freq_hz) * 1000.0
            self.spin_dy_mm.setValue(val_lambda * wl_mm)
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_theta_slider_changed(self, val: int):
        """Theta 滑块拖动 -> 联动更新 SpinBox 并触发计算"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            self.spin_theta.setValue(val / 10.0)
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_theta_spin_changed(self, val: float):
        """Theta 数值框直接输入 -> 联动更新滑块并触发计算"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            self.slider_theta.setValue(int(round(val * 10.0)))
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_phi_slider_changed(self, val: int):
        """Phi 滑块拖动 -> 联动更新 SpinBox 并触发计算"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            self.spin_phi.setValue(val / 10.0)
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_phi_spin_changed(self, val: float):
        """Phi 数值框直接输入 -> 联动更新滑块并触发计算"""
        if self._is_updating:
            return
        self._is_updating = True
        try:
            self.slider_phi.setValue(int(round(val * 10.0)))
        finally:
            self._is_updating = False
        self._update_calculation()

    def _on_tab_changed(self, index: int):
        """Tab 切换时重绘对应图表"""
        if self._last_result:
            if index == 1:
                self._draw_distribution_plot(self._last_result)
            elif index == 2:
                self._draw_squint_plot(self._last_result)

    # ==================== 4. 核心计算与 UI 刷新 ====================

    def _update_calculation(self):
        """收集所有 UI 参数并执行核心计算"""
        try:
            freq_hz = self._get_frequency_hz()
            is_upa = self.radio_upa.isChecked()
            geom = ArrayGeometry.UPA if is_upa else ArrayGeometry.ULA

            num_x = self.spin_nx.value()
            num_y = self.spin_ny.value() if is_upa else 1

            spacing_x_m = self.spin_dx_mm.value() / 1000.0
            spacing_y_m = self.spin_dy_mm.value() / 1000.0 if is_upa else spacing_x_m

            scan_theta = float(self.spin_theta.value())
            scan_phi = float(self.spin_phi.value()) if is_upa else 0.0

            quant_bits = self.combo_bits.currentData()
            if quant_bits is None:
                quant_bits = 6

            # 斜视带宽换算
            bw_val = float(self.input_bw.text()) if self.input_bw.text() else 2.0
            bw_unit = self.combo_bw_unit.currentText()
            if bw_unit == "GHz":
                squint_bw_hz = bw_val * 1e9
            elif bw_unit == "MHz":
                squint_bw_hz = bw_val * 1e6
            else:  # % 带宽
                squint_bw_hz = (bw_val / 100.0) * freq_hz

            params = BeamformingDelayParams(
                geometry=geom,
                num_x=num_x,
                num_y=num_y,
                frequency_hz=freq_hz,
                spacing_x_m=spacing_x_m,
                spacing_y_m=spacing_y_m,
                scan_theta_deg=scan_theta,
                scan_phi_deg=scan_phi,
                quant_bits=quant_bits,
                squint_bandwidth_hz=squint_bw_hz
            )

            result = self.calculator.calculate(params)
            self._last_result = result

            # 刷新大盘看板
            self._update_dashboard(result, geom)

            # 刷新表格
            self._update_table(result)

            # 刷新当前可见 Tab 的图表
            curr_tab = self.tab_widget.currentIndex()
            if curr_tab == 1:
                self._draw_distribution_plot(result)
            elif curr_tab == 2:
                self._draw_squint_plot(result)

        except Exception as e:
            print(f"[BeamformingDelayTool] 计算出错: {e}")

    def _update_dashboard(self, result: BeamformingDelayResult, geom: ArrayGeometry):
        """刷新指标看板"""
        if geom == ArrayGeometry.ULA:
            self.lbl_delta_phase.setText(f"{result.delta_phase_x_deg:+.2f}°")
            self.lbl_delta_delay.setText(f"{result.delta_delay_x_ps:+.2f} ps")
        else:
            self.lbl_delta_phase.setText(
                f"X: {result.delta_phase_x_deg:+.1f}° | Y: {result.delta_phase_y_deg:+.1f}°"
            )
            self.lbl_delta_delay.setText(
                f"X: {result.delta_delay_x_ps:+.1f}ps | Y: {result.delta_delay_y_ps:+.1f}ps"
            )

        self.lbl_max_delay.setText(
            f"{result.max_array_delay_ps:.2f} ps ({result.max_array_delay_ns:.3f} ns)"
        )

        if result.phase_lsb_deg > 0:
            self.lbl_rms_error.setText(
                f"{result.rms_phase_error_deg:.2f}° (LSB: {result.phase_lsb_deg:.2f}°)"
            )
        else:
            self.lbl_rms_error.setText("0.00° (理想连续)")

    def _update_table(self, result: BeamformingDelayResult):
        """刷新通道配置表格"""
        channels = result.channels
        self.lbl_table_info.setText(f"全阵列共 {len(channels)} 个通道配置")

        self.table_channels.setRowCount(len(channels))
        for row_idx, ch in enumerate(channels):
            items = [
                f"CH-{ch.channel_id:03d}",
                f"({ch.row_idx}, {ch.col_idx})",
                f"{ch.pos_x_mm:.2f}",
                f"{ch.pos_y_mm:.2f}",
                f"{ch.unwrapped_phase_deg:+.2f}",
                f"{ch.wrapped_phase_deg:.2f}",
                f"{ch.quantized_phase_deg:.2f}",
                f"{ch.quantized_hex} ({ch.quantized_code})",
                f"{ch.phase_error_deg:+.2f}",
                f"{ch.delay_ps:+.2f}"
            ]
            for col_idx, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col_idx in [4, 5, 6]:
                    item.setForeground(QColor("#2B6CB0"))
                elif col_idx == 7:
                    item.setForeground(QColor("#805AD5"))  # 紫色码字
                elif col_idx == 8:
                    item.setForeground(QColor("#C53030") if abs(ch.phase_error_deg) > 0.01 else QColor("#22543D"))
                self.table_channels.setItem(row_idx, col_idx, item)

        # 确保刷新数据后水平滑动条重置在最左侧（优先展示通道编号、坐标等关键前置列）
        self.table_channels.horizontalScrollBar().setValue(0)

    def _draw_distribution_plot(self, result: BeamformingDelayResult):
        """绘制通道相位与时延分布图 (Tab 2 - 饱满大图，双子图清晰舒展)"""
        self.fig_dist.clear()
        channels = result.channels
        if not channels:
            self.canvas_dist.draw()
            return

        is_upa = self.radio_upa.isChecked()
        if not is_upa:
            # 1D 线阵：双子图（上图量化与理论相位阶梯，下图通道时延）
            ax1 = self.fig_dist.add_subplot(2, 1, 1)
            ax2 = self.fig_dist.add_subplot(2, 1, 2)

            ch_ids = [ch.channel_id for ch in channels]
            wrapped_phases = [ch.wrapped_phase_deg for ch in channels]
            quant_phases = [ch.quantized_phase_deg for ch in channels]
            delays = [ch.delay_ps for ch in channels]

            x_pos = np.arange(len(ch_ids))
            width = 0.38

            ax1.bar(x_pos - width/2, wrapped_phases, width, label='模360相位', color='#4299E1', alpha=0.85)
            ax1.bar(x_pos + width/2, quant_phases, width, label='量化相位', color='#9F7AEA', alpha=0.85)
            ax1.set_ylabel('相位 (°)', fontsize=9)
            ax1.set_title('各通道相位配置对比 (Phase Profile)', fontsize=10, fontweight='bold', pad=6)
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels([f"CH{i}" for i in ch_ids], fontsize=8)
            ax1.tick_params(axis='both', labelsize=8)
            ax1.set_ylim(0, 390)
            ax1.legend(loc='upper left', fontsize=7.5, framealpha=0.85)
            ax1.grid(True, linestyle='--', alpha=0.5)

            ax2.plot(x_pos, delays, 'o-', color='#E53E3E', linewidth=2.0, markersize=5, label='理论真时延')
            ax2.set_ylabel('时延 (ps)', fontsize=9)
            ax2.set_xlabel('通道编号 (Channel ID)', fontsize=9)
            ax2.set_title('各通道时间延迟分布 (True Time Delay)', fontsize=10, fontweight='bold', pad=6)
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels([f"CH{i}" for i in ch_ids], fontsize=8)
            ax2.tick_params(axis='both', labelsize=8)
            ax2.grid(True, linestyle='--', alpha=0.5)

            ax1.set_xlim(-0.6, len(ch_ids) + 0.1)
            ax2.set_xlim(-0.6, len(ch_ids) + 0.1)

        else:
            # 2D 面阵：绘制 Nx * Ny 通道量化相位的 2D 热力图
            ax = self.fig_dist.add_subplot(1, 1, 1)
            nx = self.spin_nx.value()
            ny = self.spin_ny.value()

            phase_matrix = np.zeros((ny, nx))
            for ch in channels:
                phase_matrix[ch.row_idx - 1, ch.col_idx - 1] = ch.quantized_phase_deg

            im = ax.imshow(phase_matrix, cmap='viridis', origin='lower', aspect='auto')
            cbar = self.fig_dist.colorbar(im, ax=ax)
            cbar.set_label('量化相位 (°)', fontsize=9)
            cbar.ax.tick_params(labelsize=8)

            # 在每个格子上显示量化相位
            for r in range(ny):
                for c in range(nx):
                    val = phase_matrix[r, c]
                    ax.text(c, r, f"{val:.0f}°", ha="center", va="center", color="white" if val < 180 else "black", fontsize=8)

            ax.set_title(f'2D 平面阵通道量化相位热力图 ({nx}×{ny})', fontsize=10.5, fontweight='bold', pad=8)
            ax.set_xlabel('X 轴通道列 (Col)', fontsize=9)
            ax.set_ylabel('Y 轴通道行 (Row)', fontsize=9)
            ax.set_xticks(range(nx))
            ax.set_xticklabels(range(1, nx + 1), fontsize=8)
            ax.set_yticks(range(ny))
            ax.set_yticklabels(range(1, ny + 1), fontsize=8)

        self.fig_dist.tight_layout(pad=1.0, rect=[0.01, 0.01, 0.92, 0.98])
        self.canvas_dist.draw()

    def _draw_squint_plot(self, result: BeamformingDelayResult):
        """绘制宽带波束斜视对比曲线 (Tab 3 - 比例饱满舒展)"""
        self.fig_squint.clear()
        squint_pts = result.squint_analysis
        if not squint_pts:
            self.canvas_squint.draw()
            return

        ax = self.fig_squint.add_subplot(1, 1, 1)
        freqs_ghz = [p.frequency_ghz for p in squint_pts]
        phase_beams = [p.actual_beam_deg if p.actual_beam_deg is not None else np.nan for p in squint_pts]
        ttd_beams = [p.ttd_beam_deg for p in squint_pts]

        ax.plot(freqs_ghz, phase_beams, '-', color='#E53E3E', linewidth=2.0, label='纯移相器 (有斜视)')
        ax.plot(freqs_ghz, ttd_beams, '--', color='#38A169', linewidth=2.0, label='真时延 TTD (无斜视)')

        f0_ghz = self._get_frequency_hz() / 1e9
        target_theta = self.spin_theta.value()
        ax.axvline(f0_ghz, color='#718096', linestyle=':', label=f'中心频点 f0={f0_ghz:.2f}GHz')
        ax.scatter([f0_ghz], [target_theta], color='#3182CE', s=50, zorder=5)

        freq_min = min(freqs_ghz)
        freq_max = max(freqs_ghz)
        df = (freq_max - freq_min) * 0.05
        ax.set_xlim(freq_min - df, freq_max + df)

        ax.set_title(
            f'宽带波束斜视 (Beam Squint) 分析 (最大漂移: {result.max_squint_error_deg:.2f}°)',
            fontsize=10.5, fontweight='bold', pad=8
        )
        ax.set_xlabel('工作频率 (GHz)', fontsize=9.5, labelpad=4)
        ax.set_ylabel('实际波束指向角 θ (°)', fontsize=9.5, labelpad=4)
        ax.tick_params(axis='both', which='major', labelsize=8.5)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='lower left', fontsize=8.5, framealpha=0.85)

        if result.is_squint_cutoff:
            ax.text(
                0.5, 0.05, '⚠️ 警告: 带宽边缘波束已移出可见区 (|sin θ| > 1)',
                transform=ax.transAxes, color='#E53E3E', fontweight='bold',
                fontsize=8.5, ha='center', bbox=dict(boxstyle='round', facecolor='#FED7D7', edgecolor='#E53E3E', pad=0.3)
            )

        self.fig_squint.tight_layout(rect=[0.01, 0.01, 0.96, 0.98])
        self.canvas_squint.draw()

    # ==================== 5. CSV 导出功能 ====================

    def _export_to_csv(self):
        """导出通道配置表为 CSV 文件"""
        if not self._last_result or not self._last_result.channels:
            QMessageBox.warning(self, "提示", "当前没有可导出的通道配置数据！")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存相控阵通道配置表",
            "beamforming_channels_config.csv",
            "CSV 文件 (*.csv);;所有文件 (*.*)"
        )
        if not file_path:
            return

        try:
            res = self._last_result
            freq_hz = self._get_frequency_hz()
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # 元数据信息头
                writer.writerow(["# 相控阵通道移相与时延配置文件"])
                writer.writerow(["# 生成工具", "射频天线工具集 - 相控阵移相与时延"])
                writer.writerow(["# 阵列拓扑", "二维面阵 (UPA)" if self.radio_upa.isChecked() else "一维线阵 (ULA)"])
                writer.writerow(["# 工作频率 (GHz)", f"{freq_hz / 1e9:.4f}"])
                writer.writerow(["# 波长 (mm)", f"{res.wavelength_mm:.3f}"])
                writer.writerow(["# X轴阵元数", f"{self.spin_nx.value()}"])
                writer.writerow(["# Y轴阵元数", f"{self.spin_ny.value() if self.radio_upa.isChecked() else 1}"])
                writer.writerow(["# 目标波束指向", f"Theta = {self.spin_theta.value():.1f}°, Phi = {self.spin_phi.value():.1f}°"])
                writer.writerow(["# 移相器量化", f"{self.combo_bits.currentText()}"])
                writer.writerow(["# 相邻相位差 (度)", f"ΔΦx = {res.delta_phase_x_deg:.2f}°, ΔΦy = {res.delta_phase_y_deg:.2f}°"])
                writer.writerow(["# 相邻时延差 (ps)", f"Δτx = {res.delta_delay_x_ps:.2f} ps, Δτy = {res.delta_delay_y_ps:.2f} ps"])
                writer.writerow(["# 全阵最大时延跨度 (ps)", f"{res.max_array_delay_ps:.2f}"])
                writer.writerow([])

                # 数据表头
                headers = [
                    "通道编号", "行号(Row)", "列号(Col)", "X坐标(mm)", "Y坐标(mm)",
                    "连续理论相位(deg)", "模360寄存器相位(deg)", "对称相位(deg)",
                    "移相器量化相位(deg)", "量化十六进制码(Hex)", "量化十进制码(Dec)",
                    "量化相位误差(deg)", "理论绝对时延(ps)", "相对非负时延(ps)"
                ]
                writer.writerow(headers)

                # 通道数据
                for ch in res.channels:
                    writer.writerow([
                        f"CH-{ch.channel_id:03d}",
                        ch.row_idx,
                        ch.col_idx,
                        f"{ch.pos_x_mm:.3f}",
                        f"{ch.pos_y_mm:.3f}",
                        f"{ch.unwrapped_phase_deg:.3f}",
                        f"{ch.wrapped_phase_deg:.3f}",
                        f"{ch.sym_phase_deg:.3f}",
                        f"{ch.quantized_phase_deg:.3f}",
                        ch.quantized_hex,
                        ch.quantized_code,
                        f"{ch.phase_error_deg:.3f}",
                        f"{ch.delay_ps:.3f}",
                        f"{ch.relative_delay_ps:.3f}"
                    ])

            QMessageBox.information(self, "导出成功", f"通道配置数据已成功保存至:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"保存 CSV 时出现错误:\n{e}")

    # ==================== 6. 四维知识科普注入 ====================

    def get_intuition_content(self) -> Optional[str]:
        """直观理解 - 图解与物理本质"""
        return """
        <span style="background-color: #EBF8FF; padding: 6px 10px; border-radius: 6px; display: inline-block; margin: 4px 0;">
        <b>🎯 为什么需要通道移相与时延？—— “合唱团”与“百米赛跑”比喻</b>
        </span><br>
        • <b>百米赛跑的起跑线（波前倾斜）</b>：<br>
        想象一排运动员站在同一直线上同时向前冲，他们形成的“冲击波”（等相位面/波前）是垂直于跑道向前的。<br>
        如果想让这个冲击波<b>斜着偏转 30° 前进</b>，右边的运动员就必须比左边的运动员<b>提前起跑一段精确的时间（时间延迟 Δτ）</b>，或者让他们起跑的动作节拍错开一个固定的步调（相位差 ΔΦ）。<br><br>

        • <b>移相器（Phase Shifter）与真时延（TTD）的本质区别</b>：<br>
        1. <b>移相器（相位的魔术）</b>：只关注信号波形的“周期峰谷节拍”（0°~360°），相当于让运动员原地等半拍再动。在单一频率下完美工作，但遇到宽频带信号时，由于不同频率的波长不同，固定相位会导致高频与低频“跑偏”（波束斜视）。<br>
        2. <b>真时延器（TTD，物理的光速距离）</b>：直接在硬件通道中串联不同长度的延迟线（如微带线或光纤），真正推迟信号到达的时间。无论信号频率是多少，波束指向都纹丝不动。<br><br>

        <b>🔑 一句话直觉：</b><br>
        <i>空间波束偏转角度 θ，本质上等于空间几何光程差 ΔL = d·sin(θ)；给射频通道配置相位或时延，就是在电路内部提前把这段空间差“填平”。</i>
        """

    def get_math_model_content(self) -> Optional[str]:
        """数学模型 - 精确公式推导与展开 (HTML + Unicode 严谨排版)"""
        return """
        <b>📐 空间光程差与通道配置推导</b><br><br>

        <b>1. 一维线阵 (ULA) 核心公式:</b><br>
        当波束指向偏离天线法线 θ 角时，相邻阵元（间距 d）的空间电磁波程差为：<br>
        <div style="background-color: #F7FAFC; padding: 6px 12px; border-left: 3px solid #3182CE; font-family: 'Cambria Math', monospace; margin: 4px 0;">
        ΔL = d · sin(θ)
        </div><br>
        • <b>所需相邻真时延差 (TTD):</b><br>
        <div style="background-color: #F7FAFC; padding: 6px 12px; border-left: 3px solid #3182CE; font-family: 'Cambria Math', monospace; margin: 4px 0;">
        Δτ = ΔL / c = (d · sin(θ)) / c
        </div>
        （其中 c ≈ 2.99792458 × 10<sup>8</sup> m/s 为光速，时延与工作频率无关）<br><br>

        • <b>所需相邻电相位差 (单频 f0):</b><br>
        <div style="background-color: #F7FAFC; padding: 6px 12px; border-left: 3px solid #3182CE; font-family: 'Cambria Math', monospace; margin: 4px 0;">
        ΔΦ = (2π / λ) · ΔL = (2π · f0 / c) · d · sin(θ) = 2π · (d / λ) · sin(θ) (rad)
        </div>
        换算为角度制：<b>ΔΦ (°) = 360° · (d / λ) · sin(θ)</b><br><br>

        <b>2. 二维平面阵 (UPA) 空间指向 (θ, φ):</b><br>
        空间方向余弦分量为 u = sin(θ)cos(φ), v = sin(θ)sin(φ)，则网格通道 (m, n) 的激励相位为：<br>
        <div style="background-color: #F7FAFC; padding: 6px 12px; border-left: 3px solid #3182CE; font-family: 'Cambria Math', monospace; margin: 4px 0;">
        Φ(m, n) = - [ (m - 1) · (2π dx / λ) sin(θ)cos(φ) + (n - 1) · (2π dy / λ) sin(θ)sin(φ) ]
        </div><br>

        <b>3. 移相器位宽量化 (Quantization):</b><br>
        对于 B-bit 数字控制移相器：<br>
        • <b>最小量化步进 (LSB):</b> Δφ<sub>LSB</sub> = 360° / 2<sup>B</sup><br>
        • <b>寄存器量化码字:</b> Code = round(Φ<sub>wrapped</sub> / Δφ<sub>LSB</sub>) mod 2<sup>B</sup><br>
        • <b>量化相位:</b> Φ<sub>quant</sub> = Code · Δφ<sub>LSB</sub><br><br>

        <b>4. 宽带波束斜视 (Beam Squint) 模型:</b><br>
        若采用固定移相器，当工作频率偏离中心频点 f0 到 f 时，实际主瓣指向 θ(f) 发生色散偏转：<br>
        <div style="background-color: #F7FAFC; padding: 6px 12px; border-left: 3px solid #E53E3E; font-family: 'Cambria Math', monospace; margin: 4px 0;">
        sin[θ(f)] = (f0 / f) · sin(θ0) &nbsp;⇒&nbsp; θ(f) = arcsin [ (f0 / f) · sin(θ0) ]
        </div>
        当 f &gt; f0 时波束向法线收缩；当 f &lt; f0 时波束向大角度发散，甚至出现 |(f0/f)sin(θ0)| &gt; 1 导致波束截止。
        """

    def get_engineering_content(self) -> Optional[str]:
        """工程边界 - 选型考量与避坑指南"""
        return """
        <b>⚙️ 射频工程师必看的工程边界与权衡:</b><br><br>

        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030; font-weight: bold;">
        ❌ 移相器量化引起的“量化栅瓣 (Quantization Lobes)”
        </span><br>
        • 移相器位数直接决定了波束副瓣的理论下限。<br>
        • <b>理论峰值量化副瓣电平 (QSLL):</b><br>
        <table style="margin: 6px 0; border-collapse: collapse;">
        <tr><td style="padding: 2px 10px; border: 1px solid #CBD5E0;"><b>移相器位数 (Bits)</b></td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;"><b>LSB 步进</b></td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;"><b>量化 RMS 误差</b></td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;"><b>峰值量化副瓣 (QSLL)</b></td></tr>
        <tr><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">4-bit</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">22.5°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ 6.5°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ -24 dBc</td></tr>
        <tr><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">5-bit</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">11.25°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ 3.2°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ -30 dBc</td></tr>
        <tr><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">6-bit (工业界黄金标准)</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">5.625°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ 1.6°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ -36 dBc</td></tr>
        <tr><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">8-bit (超高精度)</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">1.406°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ 0.4°</td><td style="padding: 2px 10px; border: 1px solid #CBD5E0;">≈ -48 dBc</td></tr>
        </table><br>

        <span style="background-color: #FEFCBF; padding: 4px 8px; border-radius: 4px; color: #B7791F; font-weight: bold;">
        ⚠️ 什么时候必须上真时延 (TTD) 芯片？—— 空间色散判据
        </span><br>
        • 业界工程经验准则：当信号瞬时带宽 <b>B</b> 与阵列物理孔径 <b>D</b> 的乘积满足：<br>
        <div style="font-family: 'Cambria Math', monospace; margin: 4px 0; font-weight: bold;">
        B · (D / c) · sin(θ<sub>max</sub>) &gt; 0.1 ~ 0.2
        </div>
        此时由于波束斜视，阵列边缘通道的脉冲信号包络无法对齐，将导致<b>脉冲展宽、主瓣增益下降（&gt;3dB 塌陷）</b>。这种情况下必须采用 <b>TTD（或子阵级 TTD + 元级移相器）混合架构</b>！
        """

    def get_history_content(self) -> Optional[str]:
        """发现历史 - 趣味故事与技术演进"""
        return """
        <b>📜 从重达数吨的同轴延迟管到指甲盖大小的毫米波硅芯片</b><br><br>

        • <b>1950年代（机械与铁氧体时代）</b>：<br>
        早期相控阵雷达为了实现微秒级的波束跳变，发明了极其沉重的<b>铁氧体移相器（Ferrite Phase Shifters）</b>，靠外部线圈施加毫安级磁化电流来改变微波导模速度。功耗巨大且发热严重。<br><br>

        • <b>1970~1980年代（PIN 二极管与 GaAs MMIC 时代）</b>：<br>
        随着半导体技术进步，微波单片集成电路（MMIC）问世。工程师使用 PIN 二极管和 MESFET 开关在电路板上切换不同长度的微带延时线，实现了 4~6 bit 的数控移相器，被广泛装备于“宙斯盾” SPY-1 等军用雷达。<br><br>

        • <b>2020年代（硅基 CMOS/SiGe 与 5G/6G 革命）</b>：<br>
        如今，得益于先进纳米制程，一颗不到 5×5 mm 的硅基波束赋形芯片（Beamformer IC）就集成了 <b>4~16 个独立通道</b>的 6-bit 移相器、可变增益放大器（VGA）、功率检测和 SPI 寄存器，被数以百万计地安装在 5G 毫米波基站和低轨卫星互联网（如 Starlink 终端）上！
        """
