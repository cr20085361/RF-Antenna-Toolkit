# -*- coding: utf-8 -*-
"""
射频天线工具集 - 阻抗匹配工具界面
RF Antenna Toolkit - Impedance Matching Tool UI

版本: v2.0.0
功能: 
    - 阻抗匹配网络设计与仿真
    - 实时史密斯圆图显示
    - 支持 Touchstone 文件导入
"""

import os
import sys
import numpy as np
import skrf as rf
from typing import Optional, List, Dict

from core.i18n import tr
from ui.base.tool_base import ToolBase
from core.rf.matching import (
    MatchingCalculator, MatchingElement,
    ELEMENT_SERIES_R, ELEMENT_SERIES_L, ELEMENT_SERIES_C,
    ELEMENT_SHUNT_R, ELEMENT_SHUNT_L, ELEMENT_SHUNT_C
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QFrame, QPushButton,
    QTabWidget, QListWidget, QListWidgetItem,
    QSlider,  QDoubleSpinBox, QFileDialog, QMessageBox,
    QSplitter, QGroupBox, QScrollArea, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt,  pyqtSignal,  QTimer, QRect, QPoint, QSize
from PyQt6.QtGui import QAction,  QIcon, QPainter, QPen, QColor, QFont, QPaintEvent, QMouseEvent

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

class LadderSchematicWidget(QWidget):
    """
    梯形网络动态原理图组件
    可视化显示匹配网络拓扑，并支持点击选择元件
    """
    element_selected = pyqtSignal(int) # 发射选中元件的索引
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.elements: List[MatchingElement] = []
        self._selected_index = -1
        self._element_rects: List[QRect] = [] # 存储元件点击区域
        
        self.setMinimumHeight(180) # [FIX] 增加高度防止重叠
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 4px;")

    def set_elements(self, elements: List[MatchingElement], selected_index: int = -1):
        self.elements = elements
        self._selected_index = selected_index
        self.update()
        
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor("#FAFBFC"))
        if self.hasFocus():
             painter.drawRect(self.rect().adjusted(0,0,-1,-1))
             
        w = self.width()
        h = self.height()
        cy = 60 # [FIX] 固定中心线位置，留出底部给并联元件和文本
        
        # 定义尺寸
        seg_w = 100  # [FIX] 增加宽度
        comp_w = 40 
        comp_h = 20 
        
        # 起点
        x = 20
        
        # 绘制 Source 端口
        pen_wire = QPen(QColor("#4A5568"), 2)
        painter.setPen(pen_wire)
        painter.drawText(x, cy - 10, "Source")
        painter.drawLine(x, cy, x + 20, cy)
        x += 20
        
        self._element_rects.clear()
        
        # [FIX] 如果没有元件，绘制一条长连接线，防止 Source/Load 重叠
        if not self.elements:
            painter.drawLine(x, cy, x + 100, cy)
            x += 100
        
        # 遍历绘制元件
        for i, elem in enumerate(self.elements):
            # 记录点击区域 (整个段)
            rect = QRect(x, 10, seg_w, h - 20)
            self._element_rects.append(rect)
            
            # 选中高亮
            if i == self._selected_index:
                painter.fillRect(rect, QColor("#EBF8FF"))
                painter.setPen(QPen(QColor("#3182CE"), 1, Qt.PenStyle.DashLine))
                painter.drawRect(rect)
                painter.setPen(pen_wire)
            
            cx = x + seg_w // 2
            
            if "SERIES" in elem.type:
                # 串联: 线 -> 元件 -> 线
                painter.drawLine(x, cy, cx - comp_w//2, cy)
                painter.drawLine(cx + comp_w//2, cy, x + seg_w, cy)
                
                self._draw_component(painter, cx, cy, elem.type, comp_w, comp_h, vertical=False)
                
            elif "SHUNT" in elem.type:
                # 并联: 线 -> 节点 -> 线
                painter.drawLine(x, cy, x + seg_w, cy)
                
                # 节点向下引出
                # 线长 30
                top_y = cy + 30
                painter.drawLine(cx, cy, cx, top_y)
                
                # 绘制元件符号 (垂直)
                # !! 注意: 垂直旋转后，占用高度为 comp_w (40)，而非 comp_h (20)
                center_y = top_y + comp_w // 2 
                self._draw_component(painter, cx, center_y, elem.type, comp_w, comp_h, vertical=True)
                
                # 接地 (在元件下方 10 px)
                bottom_y = top_y + comp_w
                ground_y = bottom_y + 10
                painter.drawLine(cx, bottom_y, cx, ground_y) # 连接线
                self._draw_ground(painter, cx, ground_y)
                
                # 节点实心圆
                painter.setBrush(QColor("#4A5568"))
                painter.drawEllipse(QPoint(cx, cy), 3, 3)
                painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # 绘制信息
            painter.setPen(QColor("#2D3748"))
            font = painter.font()
            font.setPointSize(9) 
            painter.setFont(font)
            
            # 绘制编号 (Top) - 位于中心线上方
            label_text = self._get_element_label(i, elem.type)
            painter.drawText(QRect(x, cy - 35, seg_w, 20), Qt.AlignmentFlag.AlignCenter, label_text)
            
            # 绘制数值 (Bottom) - 位于最下方
            val_text = self._format_value(elem)
            # 文本要在地符号下方 (ground_y ~ cy + 80)
            text_y = cy + 95
            painter.drawText(QRect(x, text_y, seg_w, 20), Qt.AlignmentFlag.AlignCenter, val_text)
            
            painter.setPen(pen_wire)
            x += seg_w
            
        # 绘制 Load 端口
        painter.drawLine(x, cy, x + 20, cy)
        painter.drawText(x + 5, cy - 10, tr("matching.lbl_load", "Load"))
        
        # 调整自身宽度
        total_w = x + 40
        if total_w > self.width():
            self.setMinimumWidth(total_w)

    def _draw_component(self, painter, cx, cy, type_, w, h, vertical=False):
        """绘制 RLC 符号"""
        painter.save()
        painter.translate(cx, cy)
        if vertical:
            painter.rotate(90)
            
        pen = QPen(QColor("#3182CE"), 2)
        painter.setPen(pen)
        
        # 绘制符号
        # [FIX] 使用 endswith 避免 "SERIES" 包含 "R" 导致的误判
        if type_.endswith("_R"):
            # 锯齿
            painter.drawPolyline([
                QPoint(-w//2, 0), QPoint(-w//2+5, -5), QPoint(-w//2+10, 5),
                QPoint(-w//2+15, -5), QPoint(-w//2+20, 5), QPoint(-w//2+25, -5),
                QPoint(-w//2+30, 5), QPoint(w//2, 0)
            ])
        elif type_.endswith("_L"):
            # 螺旋 (简化为圆弧)
            r = w // 4
            # 调整起始位置，确保连贯
            start_x = -w//2
            for k in range(4):
                painter.drawArc(start_x + k*r, -r, r, 2*r, 0, 180*16)
        elif type_.endswith("_C"):
            # 电容 (两竖线)
            # 正常 C 符号:  -| |-
            gap = 4
            painter.drawLine(-2, -h, -2, h)
            painter.drawLine(2, -h, 2, h)
            # 引线
            painter.drawLine(-w//2, 0, -2, 0)
            painter.drawLine(2, 0, w//2, 0)
            
        painter.restore()

    def _draw_ground(self, painter, cx, cy):
        """绘制地符号"""
        painter.drawLine(cx - 10, cy, cx + 10, cy)
        painter.drawLine(cx - 6, cy + 3, cx + 6, cy + 3)
        painter.drawLine(cx - 2, cy + 6, cx + 2, cy + 6)
        # 引线
        painter.drawLine(cx, cy - 10, cx, cy)

    def _format_value(self, elem) -> str:
        if elem.type.endswith("_R"): return f"{elem.value:.1f}Ω"
        if elem.type.endswith("_L"): return f"{elem.value*1e9:.1f}nH"
        if elem.type.endswith("_C"): return f"{elem.value*1e12:.1f}pF"
        return ""
        
    def _get_element_label(self, index, type_) -> str:
        # 简易编号: L1, C1...
        # 仅根据类型前缀
        prefix = "Z"
        if type_.endswith("_R"): prefix = "R"
        elif type_.endswith("_L"): prefix = "L"
        elif type_.endswith("_C"): prefix = "C"
        return f"{prefix}{index+1}"

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.pos()
        clicked_index = -1
        for i, rect in enumerate(self._element_rects):
            if rect.contains(pos):
                clicked_index = i
                break
        
        if clicked_index != -1:
            self._selected_index = clicked_index
            self.update()
            self.element_selected.emit(clicked_index)
        else:
             # Deselect?
             pass


class SmithChartCanvas(FigureCanvasQTAgg):
    """史密斯圆图画布"""
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # 不使用 projection='smith'，直接使用默认坐标系
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal') # 保持圆形
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 初始绘制网格
        self.update_grid()

    def update_grid(self):
        """绘制史密斯圆图网格"""
        self.ax.clear()
        try:
            # 使用 skrf 专用函数绘制网格 (Attempt 3 passed)
            if hasattr(rf.plotting, 'smith'):
                rf.plotting.smith(ax=self.ax)
            else:
                # Fallback
                rf.plotting.plot_smith(np.array([[0]]), ax=self.ax, grid=False)
        except Exception as e:
            print(f"Grid Error: {e}")
            
        self.ax.set_title(tr("matching.title_smith_chart", "Smith Chart"), pad=20)
        self.draw()

    def plot_networks(self, net_orig: Optional[rf.Network], net_matched: Optional[rf.Network]):
        """绘制阻抗轨迹"""
        self.ax.clear()
        
        # 1. 绘制背景网格
        try:
            if hasattr(rf.plotting, 'smith'):
                rf.plotting.smith(ax=self.ax)
        except:
            pass

        # 2. 绘制原始阻抗
        if net_orig:
            try:
                # 传入 1D array
                s_param = net_orig.s[:, 0, 0]
                # 判断是否为单点或近似单点 (恒定阻抗扫描)
                is_single = len(s_param) == 1
                is_constant = False
                if not is_single:
                    # 检查方差或最大差值
                    spread = np.max(np.abs(s_param - s_param[0]))
                    if spread < 1e-6:
                        is_constant = True
                
                # 如果是单点或恒定点，显示 marker
                marker = 'o' if (is_single or is_constant) else None 
                # 如果是多点且非恒定，显示轨迹 (-)
                ls = '' if is_single else '-' 
                if is_constant and not is_single:
                    ls = '-' 

                self.ax.plot(s_param.real, s_param.imag, 
                             linestyle=ls, linewidth=2, color='#ED8936', alpha=0.9, label=tr("matching.lbl_original", "Original"),
                             marker=marker, markersize=6, zorder=3)
                             
            except Exception as e:
                print(f"Plot Orig Error: {e}")

        # 3. 绘制匹配后阻抗
        if net_matched:
            try:
                s_param = net_matched.s[:, 0, 0]
                is_single = len(s_param) == 1
                is_constant = False
                if not is_single:
                    spread = np.max(np.abs(s_param - s_param[0]))
                    if spread < 1e-6:
                        is_constant = True
                        
                marker = 's' if (is_single or is_constant) else None
                ls = '' if is_single else '-'
                
                self.ax.plot(s_param.real, s_param.imag, 
                             linewidth=2, linestyle=ls, color='#0070F3', label=tr("matching.lbl_matched", "Matched"),
                             marker=marker, markersize=5, zorder=4)
            except Exception as e:
                print(f"Plot Matched Error: {e}")
            
        self.ax.legend(loc='lower right', fontsize='small')
        self.draw()

class ElementControlWidget(QWidget):
    """
    元件参数控制组件
    包含滑块和数值输入框
    """
    value_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # 标签
        self._label = QLabel(tr("matching.lbl_element_value", "元件值:"))
        layout.addWidget(self._label)
        
        # 控件行
        row = QHBoxLayout()
        
        # 滑块 (对数刻度模拟)
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 1000)
        self._slider.setValue(500)
        row.addWidget(self._slider)
        
        # 输入框
        self._spin = QDoubleSpinBox()
        self._spin.setRange(0, 1e9) # 大范围
        self._spin.setDecimals(3)
        self._spin.setSingleStep(0.1)
        row.addWidget(self._spin)
        
        layout.addLayout(row)
        
        # 单位标签
        self._unit_label = QLabel("nH")
        row.addWidget(self._unit_label)
        
        # 内部逻辑: min/max value
        self._min_val = 1e-10 
        self._max_val = 1e-7
        self._is_updating = False
        
        # 连接信号
        self._slider.valueChanged.connect(self._on_slider_changed)
        self._spin.valueChanged.connect(self._on_spin_changed)
        
    def set_range(self, min_v, max_v, unit, current_v):
        """设置范围和单位"""
        self._min_val = min_v
        self._max_val = max_v
        self._unit_label.setText(unit)
        
        # 缩放因子 (适应不同单位量级)
        # 显示在 spinbox 的数值应该是带量级的? 
        # 例如 nH -> 显示 10.0 表示 10nH
        # 为了简单，SpinBox 显示实际 SI 单位? 不好读 (0.00000001)
        # 让 SpinBox 显示 缩放后的值
        
        self.blockSignals(True)
        # 确定缩放倍数
        if "pF" in unit: self._scale = 1e12
        elif "nH" in unit: self._scale = 1e9
        elif "Ω" in unit: self._scale = 1.0
        else: self._scale = 1.0
        
        self._current_si = current_v
        scaled_v = current_v * self._scale
        
        self._spin.setValue(scaled_v)
        
        # 设置 Slider 位置 (对数映射)
        # slider 0-1000 -> min-max
        # val = min * (max/min)^(slider/1000)
        if current_v <= 0: current_v = min_v
        try:
            ratio = (np.log10(current_v) - np.log10(min_v)) / (np.log10(max_v) - np.log10(min_v))
            slider_pos = int(ratio * 1000)
            self._slider.setValue(max(0, min(1000, slider_pos)))
        except:
             self._slider.setValue(0)
             
        self.blockSignals(False)
        
    def _on_slider_changed(self, val):
        """滑块改变 -> 更新 Spin -> 发射信号"""
        if self._is_updating: return
        self._is_updating = True
        
        # 对数映射计算实际值
        log_min = np.log10(self._min_val)
        log_max = np.log10(self._max_val)
        log_val = log_min + (val / 1000.0) * (log_max - log_min)
        si_val = 10 ** log_val
        
        self._spin.setValue(si_val * self._scale)
        self.value_changed.emit(si_val)
        
        self._is_updating = False
        
    def _on_spin_changed(self, val):
        """Spin改变 -> 更新 Slider -> 发射信号"""
        if self._is_updating: return
        self._is_updating = True
        
        si_val = val / self._scale
        
        # 反算 slider
        try:
            log_min = np.log10(self._min_val)
            log_max = np.log10(self._max_val)
            log_curr = np.log10(si_val) if si_val > 0 else log_min
            
            ratio = (log_curr - log_min) / (log_max - log_min)
            slider_pos = int(ratio * 1000)
            self._slider.setValue(max(0, min(1000, slider_pos)))
        except:
            pass
            
        self.value_changed.emit(si_val)
        self._is_updating = False


class MatchingTool(ToolBase):
    """阻抗匹配工具"""
    tool_name = tr("matching.tool_name", "阻抗匹配")
    tool_icon = "🔧"
    tool_category = "rf"
    tool_description = tr("matching.tool_desc", "阻抗匹配网络设计与实时调谐")
    i18n_title_key = "matching.tool_name"
    i18n_desc_key = "matching.tool_desc"

    def __init__(self, parent=None):
        self._calculator = MatchingCalculator()
        super().__init__(parent)
        
    def create_input_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ── 源阻抗设置 (Tab) ──
        self._grp_src = QGroupBox(tr("matching.group_src_load_impedance", "源/负载阻抗设置"))
        self._grp_src.setObjectName("MatchingGroup")
        src_layout = QVBoxLayout(self._grp_src)
        self._src_tab = QTabWidget()
        
        # Tab 1: 单点
        tab1 = QWidget()
        form1 = QVBoxLayout(tab1)
        
        # Freq Range
        row_f = QHBoxLayout()
        row_f.addWidget(QLabel(tr("matching.lbl_start_freq", "起始频率 (MHz):")))
        self._freq_start = QDoubleSpinBox()
        self._freq_start.setRange(0.1, 100000)
        self._freq_start.setValue(2400) 
        row_f.addWidget(self._freq_start)
        
        row_f.addWidget(QLabel(tr("matching.lbl_stop_freq", "终止频率 (MHz):")))
        self._freq_stop = QDoubleSpinBox()
        self._freq_stop.setRange(0.1, 100000)
        self._freq_stop.setValue(2500)
        self._freq_stop.setToolTip(tr("matching.tip_single_freq", "如果起始=终止，则为单频点模式"))
        row_f.addWidget(self._freq_stop)
        form1.addLayout(row_f)
        
        # R, X
        row_z = QHBoxLayout()
        row_z.addWidget(QLabel("R (Ω):"))
        self._r_input = QDoubleSpinBox()
        self._r_input.setRange(0, 10000)
        self._r_input.setValue(100) # Default 100
        row_z.addWidget(self._r_input)
        
        row_z.addWidget(QLabel("jX (Ω):"))
        self._x_input = QDoubleSpinBox()
        self._x_input.setRange(-10000, 10000)
        self._x_input.setValue(0)
        row_z.addWidget(self._x_input)
        form1.addLayout(row_z)
        
        btn_set_single = QPushButton(tr("matching.btn_set_update", "设置 / 更新"))
        btn_set_single.setFixedHeight(32)
        btn_set_single.setStyleSheet("""
            QPushButton {
                background-color: #0070F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0060DF;
            }
            QPushButton:pressed {
                background-color: #0050C0;
            }
        """)
        btn_set_single.clicked.connect(self._on_set_single_point)
        form1.addWidget(btn_set_single)
        
        # Tab 2: 文件
        tab2 = QWidget()
        form2 = QVBoxLayout(tab2)
        btn_load = QPushButton(tr("matching.btn_load_touchstone", "导入 Touchstone (.s1p/.s2p)"))
        btn_load.clicked.connect(self._on_load_file)
        self._file_label = QLabel(tr("matching.lbl_no_file_loaded", "未加载文件"))
        form2.addWidget(btn_load)
        form2.addWidget(self._file_label)
        
        self._src_tab.addTab(tab1, tr("matching.tab_custom", "自定义"))
        self._src_tab.addTab(tab2, tr("matching.tab_file_import", "文件导入"))
        src_layout.addWidget(self._src_tab)
        layout.addWidget(self._grp_src)
        
        # ── 匹配网络构建 ──
        self._grp_net = QGroupBox(tr("matching.group_matching_network", "匹配网络"))
        net_layout = QVBoxLayout(self._grp_net)
        
        # 添加按钮行 (Grid Layout)
        grid_add = QGridLayout()
        grid_add.setSpacing(5)
        
        # 定义按钮: (Label, Type, Row, Col)
        buttons = [
            (tr("matching.btn_series_l", "+串L"), ELEMENT_SERIES_L, 0, 0), (tr("matching.btn_shunt_l", "+并L"), ELEMENT_SHUNT_L, 0, 1),
            (tr("matching.btn_series_c", "+串C"), ELEMENT_SERIES_C, 1, 0), (tr("matching.btn_shunt_c", "+并C"), ELEMENT_SHUNT_C, 1, 1),
            (tr("matching.btn_series_r", "+串R"), ELEMENT_SERIES_R, 2, 0), (tr("matching.btn_shunt_r", "+并R"), ELEMENT_SHUNT_R, 2, 1)
        ]
        
        
        for label, type_, r, c in buttons:
            btn = QPushButton(label)
            btn.setFixedHeight(24) # [FIX] 减小按钮高度 (原默认约30)
            btn.setStyleSheet("font-size: 11px; padding: 0px;") # 减小字体
            btn.clicked.connect(lambda _, t=type_: self._add_element(t))
            grid_add.addWidget(btn, r, c)
            
        net_layout.addLayout(grid_add)
        
        # 列表 -> 改为原理图
        # self._list_widget = QListWidget()
        # self._list_widget.currentRowChanged.connect(self._on_element_selected)
        # net_layout.addWidget(self._list_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # 原理图最小高度180，scroll area 给 200 以展示完整
        # 同时利用 sizePolicy 自动伸缩
        scroll.setMinimumHeight(200) 
        
        self._schematic = LadderSchematicWidget()
        self._schematic.element_selected.connect(self._on_element_selected)
        scroll.setWidget(self._schematic)
        net_layout.addWidget(scroll)
        
        # 删除按钮
        btn_del = QPushButton(tr("matching.btn_delete_selected", "删除选中元件"))
        btn_del.clicked.connect(self._del_element)
        net_layout.addWidget(btn_del)
        
        layout.addWidget(self._grp_net)
        
        # ── 参数调节 ──
        self._grp_ctrl = QGroupBox(tr("matching.group_element_params", "元件参数"))
        ctrl_layout = QVBoxLayout(self._grp_ctrl)
        self._control_widget = ElementControlWidget()
        self._control_widget.value_changed.connect(self._on_value_adjusted)
        self._control_widget.setEnabled(False)
        ctrl_layout.addWidget(self._control_widget)
        layout.addWidget(self._grp_ctrl)
        
        # 初始设置默认点
        QTimer.singleShot(100, self._on_set_single_point)
        
        return panel

    def create_result_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0,0,0,0)
        
        self._chart = SmithChartCanvas(self)
        layout.addWidget(self._chart)
        
        return panel
        
    def _on_set_single_point(self):
        f_start = self._freq_start.value() * 1e6
        f_stop = self._freq_stop.value() * 1e6
        
        # 自动调整顺序
        if f_start > f_stop:
             f_start, f_stop = f_stop, f_start
             self._freq_start.blockSignals(True)
             self._freq_stop.blockSignals(True)
             self._freq_start.setValue(f_start / 1e6)
             self._freq_stop.setValue(f_stop / 1e6)
             self._freq_start.blockSignals(False)
             self._freq_stop.blockSignals(False)
        
        r = self._r_input.value()
        x = self._x_input.value()
        z = complex(r, x)
        
        bw = f_stop - f_start
        center_freq = (f_start + f_stop) / 2
        
        if bw > 1.0: # 认为是扫描模式 (bw > 1Hz)
            self._calculator.set_custom_range(center_freq, bw, z)
            msg = tr("matching.msg_scan_set", "已设置扫描: {r}+j{x} Ω (中心), 范围: {f_start:.1f}-{f_stop:.1f} MHz").format(
                r=r, x=x, f_start=f_start/1e6, f_stop=f_stop/1e6
            )
        else:
            # 单频点
            self._calculator.set_single_point(center_freq, z)
            msg = tr("matching.msg_load_set", "已设置负载: {r}+j{x} Ω @ {freq:.2f} MHz").format(
                r=r, x=x, freq=center_freq/1e6
            )
            
        self._update_chart()
        self._show_message(msg)
        
    def _on_load_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, tr("matching.dialog_open_touchstone", "打开 Touchstone 文件"), "", "Touchstone (*.s1p *.s2p)")
        if fname:
            if self._calculator.load_touchstone(fname):
                self._file_label.setText(os.path.basename(fname))
                self._update_chart()
                self._show_message(tr("matching.msg_file_loaded_success", "文件加载成功"))
            else:
                self._show_message(tr("matching.msg_file_loaded_fail", "文件加载失败"))
                
    def _add_element(self, type_):
        # 默认值
        val = 1e-9 if "L" in type_ else 1e-12
        new_id = self._calculator.add_element(type_, val)
        
        # 选中新加项
        new_idx = len(self._calculator._elements) - 1
        self._schematic.set_elements(self._calculator._elements, new_idx)
        self._on_element_selected(new_idx) # 触发参数面板更新
        
        self._update_chart()
        
    def _del_element(self):
        row = self._schematic._selected_index
        if row >= 0 and row < len(self._calculator._elements):
            self._calculator.remove_element(row)
            
            # 更新选中
            new_sel = -1
            if self._calculator._elements:
                new_sel = min(row, len(self._calculator._elements)-1)
                
            self._schematic.set_elements(self._calculator._elements, new_sel)
            
            if new_sel != -1:
                self._on_element_selected(new_sel)
            else:
                self._control_widget.setEnabled(False)
                
            self._update_chart()

    def _refresh_list(self):
        # Deprecated logic, functionality moved to _schematic.set_elements
        pass
            
    def _on_element_selected(self, row):
        if row < 0 or row >= len(self._calculator._elements):
            self._control_widget.setEnabled(False)
            return
            
        elem = self._calculator._elements[row]
        self._control_widget.setEnabled(True)
        
        # 更新原理图选中状态
        self._schematic._selected_index = row
        self._schematic.update()
        
        # 设置范围
        self._control_widget.blockSignals(True) # 避免回环
        if elem.type.endswith("_L"):
            self._control_widget.set_range(1e-10, 1e-7, "nH", elem.value)
        elif elem.type.endswith("_C"):
            self._control_widget.set_range(1e-13, 1e-10, "pF", elem.value)
        elif elem.type.endswith("_R"):
            self._control_widget.set_range(0.1, 1000, "Ω", elem.value)
        self._control_widget.blockSignals(False)
            
    def _on_value_adjusted(self, val):
        row = self._schematic._selected_index
        if row >= 0:
            # 更新模型
            self._calculator.update_element_value(row, val)
            # 更新原理图
            self._schematic.update()
            # 更新图表
            self._update_chart()
            
    def _update_chart(self):
        if not self._calculator._load_network:
            return
            
        try:
            matched = self._calculator.calculate_matched_network()
            self._chart.plot_networks(self._calculator._load_network, matched)
        except Exception as e:
            print(f"Plot Error: {e}")
            import traceback
            traceback.print_exc()
            
    def _show_message(self, msg):
        pass # 或者状态栏显示


    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新 UI 文字"""
        super().retranslate_ui(lang)
        if hasattr(self, "_grp_src"):
            self._grp_src.setTitle(tr("matching.group_src_load_impedance"))
        if hasattr(self, "_grp_net"):
            self._grp_net.setTitle(tr("matching.group_matching_network"))
        if hasattr(self, "_grp_ctrl"):
            self._grp_ctrl.setTitle(tr("matching.group_element_params"))
        
        # 刷新图表标题
        if hasattr(self, "_lbl_matched"):
            self._lbl_matched.setText(tr("matching.lbl_matched"))
        if hasattr(self, "_lbl_original"):
            self._lbl_original.setText(tr("matching.lbl_original"))
        if hasattr(self, "_smith_title"):
            self._smith_title.setText(tr("matching.title_smith_chart"))
            
        # 刷新 Tab 页
        if hasattr(self, "_src_tab"):
            self._src_tab.setTabText(0, tr("matching.tab_custom"))
            self._src_tab.setTabText(1, tr("matching.tab_file_import"))
            
        # 刷新标签 (如果有引用的话，代码中目前是 QLabel 直接创建，需在 retranslate 处理)
        # 为简化，通常在大型重构中将 QLabel 保存为成员变量

    def get_intuition_content(self) -> Optional[str]:
        return tr("matching.intuition_content")

    def get_math_model_content(self) -> Optional[str]:
        return tr("matching.math_content")

    def get_engineering_content(self) -> Optional[str]:
        return tr("matching.engineering_content")
