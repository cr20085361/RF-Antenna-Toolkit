# -*- coding: utf-8 -*-
"""
射频天线工具集 - 系统灵敏度计算工具
RF Antenna Toolkit - System Sensitivity Calculation Tool

版本: v1.2.0
功能: 提供系统灵敏度计算，支持多频率点分析，优化布局与可视化
"""

import sys
import os
import numpy as np
from typing import Dict, Any, Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QGroupBox, QDoubleSpinBox, QAbstractItemView,
    QFrame, QGridLayout, QLineEdit, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QDoubleValidator, QPixmap

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ui.base.tool_base import ToolBase
# 确保资源路径正确
from core.i18n import tr
from core.antenna.sensitivity import SystemSensitivity


class SensitivityTool(ToolBase):
    """
    系统灵敏度计算工具
    
    功能:
    - 计算接收机灵敏度 (Rx Sensitivity)
    - 计算天线系数 (Antenna Factor)
    - 计算系统最小场强灵敏度 (Field Strength)
    - 频率 vs 灵敏度 曲线分析
    - 系统链路示意图展示
    """
    
    # 工具元信息
    tool_name = "系统灵敏度计算"
    tool_icon = "📶"
    tool_category = "antenna"
    tool_description = "计算无源天线+射频链路的总灵敏度 (场强)"
    
    def __init__(self):
        """初始化工具"""
        self._calculator = SystemSensitivity()
        
        # 存储绘图数据
        self._chart_data: List[tuple] = []
        
        self._static_labels = []
        super().__init__()
        
        # 初始化默认数据 (必须在 setup_ui 之后)
        self._init_default_data()

    def create_input_panel(self) -> QWidget:
        """创建顶部面板 (配置 + 表格)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # ==================== 1. 系统配置 ====================
        config_group = QGroupBox("系统配置")
        config_layout = QGridLayout(config_group)
        config_layout.setVerticalSpacing(8)
        
        # 第一行: 参数输入
        config_layout.addWidget(QLabel("信道带宽:"), 0, 0)
        self._bw_input = QLineEdit("1000")
        # 提高精度，允许输入 Hz 级别 (例如 0.001 kHz)
        self._bw_input.setValidator(QDoubleValidator(0.0, 1e9, 6)) 
        self._bw_input.setPlaceholderText("BW")
        self._bw_input.textChanged.connect(self._recalc_all) # 实时计算
        config_layout.addWidget(self._bw_input, 0, 1)
        
        # 带宽单位选择
        self._bw_unit_combo = QComboBox()
        self._bw_unit_combo.addItems(["Hz", "kHz", "MHz"])
        self._bw_unit_combo.setCurrentText("kHz")
        self._bw_unit_combo.currentTextChanged.connect(self._recalc_all)
        config_layout.addWidget(self._bw_unit_combo, 0, 2)
        
        config_layout.addWidget(QLabel("噪声系数:"), 0, 3)
        self._nf_input = QLineEdit("5.0")
        self._nf_input.setValidator(QDoubleValidator(0, 50, 2))
        self._nf_input.setPlaceholderText("dB")
        self._nf_input.textChanged.connect(self._recalc_all)
        config_layout.addWidget(self._nf_input, 0, 4)
        config_layout.addWidget(QLabel("dB"), 0, 5)
        
        # 第二行: 更多参数 + 单位选择
        config_layout.addWidget(QLabel("Min SNR:"), 1, 0)
        self._snr_input = QLineEdit("10.0")
        self._snr_input.setValidator(QDoubleValidator(-20, 50, 2))
        self._snr_input.setPlaceholderText("dB")
        self._snr_input.textChanged.connect(self._recalc_all)
        config_layout.addWidget(self._snr_input, 1, 1)
        config_layout.addWidget(QLabel("dB"), 1, 2)
        
        config_layout.addWidget(QLabel("场强单位:"), 1, 3)
        self._unit_combo = QComboBox()
        self._unit_combo.addItems(["dBuV/m", "uV/m"])
        self._unit_combo.currentTextChanged.connect(self._on_unit_changed)
        config_layout.addWidget(self._unit_combo, 1, 4, 1, 2)
        
        layout.addWidget(config_group)
        
        # ==================== 2. 频率计算表格 ====================
        table_group = QGroupBox("计算结果列表")
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(8, 8, 8, 8)
        
        # 操作栏
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ 添加频点")
        btn_add.clicked.connect(self._add_row)
        btn_remove = QPushButton("➖ 删除")
        btn_remove.clicked.connect(self._remove_row)
        btn_clear = QPushButton("🗑️ 清空")
        btn_clear.clicked.connect(self._clear_table)
        btn_recalc = QPushButton("🔄 全局刷新")
        btn_recalc.setObjectName("PrimaryButton")
        btn_recalc.clicked.connect(self._recalc_all)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_recalc)
        table_layout.addLayout(btn_layout)
        
        # 表格
        self._table = QTableWidget()
        # 列: Freq, Gain, Loss, RxSens, AF, E-Field
        headers = ["频率(MHz)", "增益(dBi)", "线缆损耗(dB)", "Rx灵敏度", "天线系数", "最小场强"]
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # 所有列均匀拉伸
        
        # 优化行高和编辑器样式
        self._table.verticalHeader().setDefaultSectionSize(38) # 增加行高
        # 修复编辑时显示不全的问题: 调整 QLineEdit 样式
        self._table.setStyleSheet("""
            QTableWidget { 
                selection-background-color: #E2E8F0; 
                selection-color: black;
                gridline-color: #E2E8F0;
            }
            QTableWidget::item { padding: 4px; }
            QLineEdit { 
                border: 1px solid #4299E1; 
                border-radius: 4px;
                padding: 0px 4px;
                margin: 2px;
            }
        """)
        
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.itemChanged.connect(self._on_item_changed)
        self._table.itemSelectionChanged.connect(self._update_plot_highlight)
        
        table_layout.addWidget(self._table)
        layout.addWidget(table_group)
        
        return panel

    def create_result_panel(self) -> Optional[QWidget]:
        """右侧面板 (已合并至 create_visualization)"""
        return None

    def create_visualization(self) -> Optional[QWidget]:
        """底部面板: 左图其架构，右图其曲线"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 1. 系统示意图 (左下) ====================
        diagram_group = QGroupBox("系统链路架构")
        diagram_layout = QVBoxLayout(diagram_group)
        diagram_layout.setContentsMargins(4, 16, 4, 4)
        
        self._diagram_label = QLabel()
        self._diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._diagram_label.setMinimumHeight(300)
        self._diagram_label.setScaledContents(False)
        self._diagram_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px; }")
        
        diagram_layout.addWidget(self._diagram_label)
        
        # 加载图片
        self._load_diagram_image()
        
        layout.addWidget(diagram_group, 1)
        
        # ==================== 2. 灵敏度曲线 (右下) ====================
        chart_group = QGroupBox("灵敏度曲线")
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.setContentsMargins(4, 16, 4, 4)
        
        self._fig = Figure(figsize=(5, 4), dpi=100)
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._ax = self._fig.add_subplot(111)
        
        chart_layout.addWidget(self._canvas)
        layout.addWidget(chart_group, 2)
        
        return panel

    def calculate(self) -> Dict[str, Any]:
        """接口实现"""
        return {}

    # ==================== 逻辑处理 ====================

    def _load_diagram_image(self):
        """加载示意图资源"""
        try:
            # 获取兼容 PyInstaller 的资源路径
            path = self.get_asset_path("ui/assets/sensitivity_link.png")
            
            pixmap = None
            if os.path.exists(path):
                pixmap = QPixmap(path)
            
            if pixmap and not pixmap.isNull():
                # 参考 los_tool.py 的缩放逻辑
                scaled_pixmap = pixmap.scaled(400, 280, Qt.AspectRatioMode.KeepAspectRatio, 
                                              Qt.TransformationMode.SmoothTransformation)
                self._diagram_label.setPixmap(scaled_pixmap)
            else:
                self._diagram_label.setText("示意图加载中...\n(或文件不存在)")
        except Exception as e:
            self._diagram_label.setText(f"错误: {str(e)}")

    def _init_default_data(self):
        """初始化演示数据"""
        self._add_row_data(2400, 2.0, 1.0)
        self._add_row_data(2450, 2.5, 1.0)
        self._add_row_data(2500, 2.0, 1.0)
        self._recalc_all()

    def _add_row(self):
        self._add_row_data(2400, 0.0, 0.0)
        self._recalc_row(self._table.rowCount() - 1)

    def _add_row_data(self, f: float, g: float, l: float):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.blockSignals(True)
        
        # 输入列 (可编辑)
        for c, val in enumerate([f, g, l]):
            item = QTableWidgetItem(f"{val:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, c, item)
            
        # 结果列 (只读)
        # 3: RxSens, 4: AF, 5: E-Field
        for c in range(3, 6):
            item = QTableWidgetItem("-")
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QColor("#F7FAFC"))
            
            # 颜色区分
            if c == 3: item.setForeground(QColor("#2B6CB0")) # Blue for Rx
            if c == 5: # Red for Field Strength
                item.setForeground(QColor("#C53030"))
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                
            self._table.setItem(row, c, item)
            
        self._table.blockSignals(False)

    def _remove_row(self):
        row = self._table.currentRow()
        if row >= 0:
            self._table.removeRow(row)
            self._recalc_all()

    def _clear_table(self):
        self._table.setRowCount(0)
        self._recalc_all()

    def _on_unit_changed(self, unit):
        """单位切换"""
        self._recalc_all()
        # 更新表头单位指示
        header_item = self._table.horizontalHeaderItem(5)
        if header_item:
            header_item.setText(f"最小场强 ({unit})")

    def _on_item_changed(self, item):
        if item.column() < 3: # 仅输入列变化生效
            self._recalc_row(item.row())
            self._update_plot()

    def _update_plot_highlight(self):
        """高亮选中点 (可选优化)"""
        pass 

    def _recalc_all(self):
        for r in range(self._table.rowCount()):
            self._recalc_row(r)
        self._update_plot()

    def _recalc_row(self, row: int):
        try:
            # 获取全局参数
            bw_val = float(self._bw_input.text() or 0)
            bw_unit = self._bw_unit_combo.currentText()
            
            # 统一转换为 kHz 进行计算
            if bw_unit == "Hz":
                bw_khz = bw_val / 1000.0
            elif bw_unit == "MHz":
                bw_khz = bw_val * 1000.0
            else: # kHz
                bw_khz = bw_val
            
            nf = float(self._nf_input.text() or 0)
            snr = float(self._snr_input.text() or 0)
            unit = self._unit_combo.currentText()
            
            # 获取行参数
            f_str = self._table.item(row, 0).text()
            g_str = self._table.item(row, 1).text()
            l_str = self._table.item(row, 2).text()
            
            if not f_str or not g_str or not l_str:
                return

            f = float(f_str)
            g = float(g_str)
            l = float(l_str)
            
            # 计算
            rx_sens = self._calculator.calculate_rx_sensitivity(bw_khz, nf, snr)
            af = self._calculator.calculate_antenna_factor(f, g)
            e_db = self._calculator.calculate_field_strength(f, rx_sens, g, l)
            
            # 更新UI
            self._table.blockSignals(True)
            self._table.item(row, 3).setText(f"{rx_sens:.2f} dBm")
            self._table.item(row, 4).setText(f"{af:.2f} dB/m")
            
            # 场强显示
            if unit == "dBuV/m":
                field_str = f"{e_db:.2f}"
            else: # uV/m
                e_uv = self._calculator.dbuv_to_uv(e_db)
                field_str = f"{e_uv:.2f}"
            self._table.item(row, 5).setText(field_str)
            
            # 存储原始数据供绘图
            self._table.item(row, 5).setData(Qt.ItemDataRole.UserRole, e_db) # 始终存dBuV/m用于绘图
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, f)
            
            self._table.blockSignals(False)
            
        except ValueError:
            pass

    def _update_plot(self):
        unit = self._unit_combo.currentText()
        self._chart_data = []
        
        for r in range(self._table.rowCount()):
            item_e = self._table.item(r, 5)
            item_f = self._table.item(r, 0)
            if item_e and item_f:
                e_val_db = item_e.data(Qt.ItemDataRole.UserRole) # 存储的是 dBuV/m
                f_val = item_f.data(Qt.ItemDataRole.UserRole)
                
                if e_val_db is not None and f_val is not None:
                    # 根据单位转换数值
                    if unit == "uV/m":
                        val_to_plot = self._calculator.dbuv_to_uv(e_val_db)
                    else:
                        val_to_plot = e_val_db
                        
                    self._chart_data.append((f_val, val_to_plot))
        
        self._chart_data.sort(key=lambda x: x[0])
        
        self._ax.clear()
        self._ax.set_title(f"System Sensitivity (Field Strength) vs Frequency")
        self._ax.set_xlabel("Frequency (MHz)")
        self._ax.set_ylabel(f"Min Field Strength ({unit})")
        self._ax.grid(True, linestyle='--', alpha=0.6)
        
        if self._chart_data:
            x, y = zip(*self._chart_data)
            self._ax.plot(x, y, 'o-', color='#C53030', linewidth=2, markersize=6)
            
            # 标记最优值 (无论 dBuV/m 还是 uV/m，越小越好)
            best_val = min(y)
            best_idx = y.index(best_val)
            anno_text = f"Best: {best_val:.2f}\n{unit}"
            
            self._ax.annotate(anno_text, 
                              xy=(x[best_idx], y[best_idx]), 
                              xytext=(0, 10), textcoords='offset points',
                              ha='center', color='#C53030', fontweight='bold')
        self._canvas.draw()

    # ==================== 四维度知识内容 ====================

    def get_intuition_content(self) -> Optional[str]:
        return tr("sens.intuition_content")

    def get_math_model_content(self) -> Optional[str]:
        return tr("sens.math_content")

    def get_engineering_content(self) -> Optional[str]:
        return tr("sens.engineering_content")

    def get_history_content(self) -> Optional[str]:
        return """
        <b>📜 历史背景：</b>
        <ul>
            <li><b>Harry Nyquist (1928):</b> 发现了热噪声原理，确定了 -174dBm/Hz 的物理基底。</li>
            <li><b>Claude Shannon (1948):</b> 提出了香农极限，定义了在给定带宽和信噪比下的最大信息传输速率，间接给出了灵敏度的理论边界。</li>
        </ul>
        """

    def retranslate_ui(self, lang: str = ""):
        super().retranslate_ui(lang)
        if not hasattr(self, '_static_labels'):
            return
        for widget, category, key, attr in self._static_labels:
            if attr == "text":
                widget.setText(tr(f"{category}.{key}"))
            elif attr == "title":
                widget.setTitle(tr(f"{category}.{key}"))
            elif attr == "placeholder":
                widget.setPlaceholderText(tr(f"{category}.{key}"))
            elif attr == "text_colon":
                widget.setText(tr(f"{category}.{key}") + ":")
