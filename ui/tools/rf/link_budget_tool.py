# -*- coding: utf-8 -*-
"""
射频天线工具集 - 链路预算工具
RF Antenna Toolkit - Link Budget Tool

版本: v2.0.0
功能: 射频链路增益、噪声系数、P1dB 级联计算与可视化
"""

from typing import Dict, Any, Optional, List
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QScrollArea, QSizePolicy,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PyQt6.QtSvgWidgets import QSvgWidget
import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QDoubleValidator

from core.i18n import tr
from ui.base.tool_base import ToolBase
from core.rf.link_budget_calculator import LinkBudgetCalculator, StageParams, StageResult

class StageWidget(QFrame):
    """单级组件控件"""
    
    # 参数变更信号
    paramChanged = pyqtSignal()
    removeRequested = pyqtSignal(int)      # 发送自己的 index (删除)
    moveLeftRequested = pyqtSignal(int)    # 发送自己的 index (向左移)
    moveRightRequested = pyqtSignal(int)   # 发送自己的 index (向右移)
    
    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self._setup_ui()
        
    def _setup_ui(self):
        self.setObjectName("StageCard")
        self.setStyleSheet("""
            #StageCard {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        self.setFixedWidth(240)  # [FIX] 从 200 改为 240 防止内容截断
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 1. 顶部栏 (移动按钮 + 标题 + 删除按钮)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧占位容器 (保证对称性)
        left_container = QWidget()
        left_container.setFixedWidth(64)
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # 左移按钮
        self.btn_left = QPushButton("<")
        self.btn_left.setFixedSize(28, 28)
        self.btn_left.setStyleSheet("""
            QPushButton { border: 1px solid #E2E8F0; border-radius: 14px; background: #F7FAFC; color: #4A5568; font-weight: bold; font-family: Arial; font-size: 14px; padding: 0; }
            QPushButton:hover { background: #EDF2F7; }
            QPushButton:disabled { border: none; background: transparent; color: transparent; }
        """)
        self.btn_left.clicked.connect(lambda: self.moveLeftRequested.emit(self.index))
        self.btn_left.setToolTip("向左移动")
        left_layout.addWidget(self.btn_left)
        left_layout.addStretch()
        header_layout.addWidget(left_container)
        
        # 标题 (剧中伸展)
        self.title_label = QLabel(f"Stage {self.index + 1}")
        self.title_label.setStyleSheet("font-weight: bold; color: #2D3748; background-color: #EDF2F7; padding: 4px 12px; border-radius: 12px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.title_label, 1)
        
        # 右侧容器
        right_container = QWidget()
        right_container.setFixedWidth(64)
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # 右移按钮
        self.btn_right = QPushButton(">")
        self.btn_right.setFixedSize(28, 28)
        self.btn_right.setStyleSheet("""
            QPushButton { border: 1px solid #E2E8F0; border-radius: 14px; background: #F7FAFC; color: #4A5568; font-weight: bold; font-family: Arial; font-size: 14px; padding: 0; }
            QPushButton:hover { background: #EDF2F7; }
            QPushButton:disabled { border: none; background: transparent; color: transparent; }
        """)
        self.btn_right.clicked.connect(lambda: self.moveRightRequested.emit(self.index))
        self.btn_right.setToolTip("向右移动")
        right_layout.addWidget(self.btn_right)
        
        # 删除按钮
        self.btn_remove = QPushButton("×")
        self.btn_remove.setFixedSize(28, 28)
        self.btn_remove.setStyleSheet("""
            QPushButton {
                border: 1px solid #E2E8F0; border-radius: 14px; background: #FFF5F5; color: #E53E3E; font-weight: bold; font-family: Arial; font-size: 18px; padding: 0;
            }
            QPushButton:hover { background-color: #FED7D7; border: 1px solid #FEB2B2; }
        """)
        self.btn_remove.setToolTip("删除此级")
        self.btn_remove.clicked.connect(lambda: self.removeRequested.emit(self.index))
        right_layout.addWidget(self.btn_remove)
        
        header_layout.addWidget(right_container)
        
        layout.addLayout(header_layout)
        
        # 2. 图标 (居中)
        self.icon_widget = QSvgWidget()
        self.icon_widget.setFixedSize(60, 60)
        
        # 将图标放入居中布局
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(self.icon_widget)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)
        
        # 3. 类型选择
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            tr("linkbudget.stage_type_amp", "放大器 (LNA/PA)"), 
            tr("linkbudget.stage_type_filter", "滤波器 (Filter)"), 
            tr("linkbudget.stage_type_attenuator", "衰减器 (Attenuator)"), 
            tr("linkbudget.stage_type_cable", "线缆 (Cable)"), 
            tr("linkbudget.stage_type_switch", "开关 (Switch)"), 
            tr("linkbudget.stage_type_mixer", "混频器 (Mixer)"),
            tr("linkbudget.stage_type_splitter", "功分器 (Splitter)")
        ])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        layout.addWidget(self.type_combo)
        
        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(sep)
        
        # 4. 参数输入
        self.input_layout = QGridLayout()
        self.input_layout.setVerticalSpacing(4)
        
        # Field 1 (Gain / Loss)
        self.f1_label = QLabel(tr("linkbudget.lbl_gain", "增益 (dB):"))
        self.input_layout.addWidget(self.f1_label, 0, 0)
        self.f1_spin = QDoubleSpinBox()
        self.f1_spin.setRange(-100, 100)
        self.f1_spin.setDecimals(2)
        self.f1_spin.setValue(10.0)
        self.f1_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons) # [FIX] 移除上下箭头
        self.f1_spin.valueChanged.connect(self.paramChanged.emit)
        self.input_layout.addWidget(self.f1_spin, 0, 1)
        
        # Field 2 (NF)
        self.f2_label = QLabel(tr("linkbudget.lbl_nf", "NF (dB):"))
        self.input_layout.addWidget(self.f2_label, 1, 0)
        self.f2_spin = QDoubleSpinBox()
        self.f2_spin.setRange(0, 100)
        self.f2_spin.setDecimals(2)
        self.f2_spin.setValue(1.0)
        self.f2_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons) # [FIX] 移除上下箭头
        self.f2_spin.valueChanged.connect(self.paramChanged.emit)
        self.input_layout.addWidget(self.f2_spin, 1, 1)
        
        # Field 3 (OP1dB)
        self.f3_label = QLabel(tr("linkbudget.lbl_op1db", "OP1dB:"))
        self.input_layout.addWidget(self.f3_label, 2, 0)
        self.f3_spin = QDoubleSpinBox()
        self.f3_spin.setRange(-100, 100) # dBm
        self.f3_spin.setValue(20.0)
        self.f3_spin.setSuffix(" dBm")
        self.f3_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons) # [FIX] 移除上下箭头
        self.f3_spin.valueChanged.connect(self.paramChanged.emit)
        self.input_layout.addWidget(self.f3_spin, 2, 1)
        
        layout.addLayout(self.input_layout)
        
        # 填充底部多余空位，确保内容强制靠上对齐
        layout.addStretch()
        
        # 初始化状态
        self._on_type_changed(0)
        
    def _get_icon_path(self, basename: str) -> str:
        import sys
        if hasattr(sys, '_MEIPASS'):
            root_dir = sys._MEIPASS
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
        return os.path.join(root_dir, "resources", "icons", basename)

    def _on_type_changed(self, index):
        """根据类型更新默认值、图标、以及显示的参数字段"""
        self.blockSignals(True)
        type_name = self.type_combo.currentText()
        
        # 默认全部显示
        self.f1_label.show()
        self.f1_spin.show()
        self.f2_label.show()
        self.f2_spin.show()
        self.f3_label.show()
        self.f3_spin.show()
        
        if tr("linkbudget.stage_type_amp", "放大器") in type_name:
            self.icon_widget.load(self._get_icon_path("amplifier.svg"))
            self.f1_label.setText(tr("linkbudget.lbl_gain", "增益 (dB):"))
            self.f1_spin.setValue(15.0)
            self.f2_label.setText(tr("linkbudget.lbl_nf", "NF (dB):"))
            self.f2_spin.setValue(1.5)
            self.f3_label.setText(tr("linkbudget.lbl_op1db", "OP1dB:"))
            self.f3_spin.setValue(20.0)
        elif tr("linkbudget.stage_type_filter", "滤波器") in type_name or \
             tr("linkbudget.stage_type_attenuator", "衰减器") in type_name or \
             tr("linkbudget.stage_type_cable", "线缆") in type_name or \
             tr("linkbudget.stage_type_splitter", "功分器") in type_name:
            if tr("linkbudget.stage_type_filter", "滤波器") in type_name:
                self.icon_widget.load(self._get_icon_path("filter.svg"))
                default_loss = 1.0
            elif tr("linkbudget.stage_type_attenuator", "衰减器") in type_name:
                self.icon_widget.load(self._get_icon_path("attenuator.svg"))
                default_loss = 3.0
            elif tr("linkbudget.stage_type_cable", "线缆") in type_name:
                self.icon_widget.load(self._get_icon_path("cable.svg"))
                default_loss = 0.5
            else: # 功分器
                self.icon_widget.load(self._get_icon_path("splitter.svg"))
                default_loss = 3.5
                
            self.f1_label.setText(tr("linkbudget.lbl_insertion_loss", "插入损耗(dB):") if tr("linkbudget.stage_type_attenuator", "衰减器") not in type_name else tr("linkbudget.lbl_attenuation", "衰减值(dB):"))
            self.f1_spin.setValue(default_loss)
            
            # 无源器件隐藏独立的 NF 和 OP1dB
            self.f2_label.hide()
            self.f2_spin.hide()
            self.f3_label.hide()
            self.f3_spin.hide()
            
        elif tr("linkbudget.stage_type_switch", "开关") in type_name:
            self.icon_widget.load(self._get_icon_path("switch.svg"))
            self.f1_label.setText(tr("linkbudget.lbl_insertion_loss", "插入损耗(dB):"))
            self.f1_spin.setValue(0.8)
            
            # 开关隐藏独立的 NF，但保留 OP1dB
            self.f2_label.hide()
            self.f2_spin.hide()
            self.f3_label.setText(tr("linkbudget.lbl_op1db", "OP1dB:"))
            self.f3_spin.setValue(30.0)
            
        elif tr("linkbudget.stage_type_mixer", "混频器") in type_name:
            self.icon_widget.load(self._get_icon_path("mixer.svg"))
            self.f1_label.setText(tr("linkbudget.lbl_conversion_gain", "变频增益(dB):")) # 混频器可以是无源(损耗)也可以是有源(增益)
            self.f1_spin.setValue(-6.0)
            self.f2_label.setText(tr("linkbudget.lbl_nf", "NF (dB):"))
            self.f2_spin.setValue(6.5)
            self.f3_label.setText(tr("linkbudget.lbl_op1db", "OP1dB:"))
            self.f3_spin.setValue(10.0)
            
        self.blockSignals(False)
        self.paramChanged.emit()

    def get_params(self) -> StageParams:
        """获取当前配置参数"""
        type_name = self.type_combo.currentText()
        stage_type = type_name.split(" ")[0]
        
        # 提取动态逻辑
        if tr("linkbudget.stage_type_amp", "放大器") in type_name or tr("linkbudget.stage_type_mixer", "混频器") in type_name:
            gain = self.f1_spin.value()
            nf = self.f2_spin.value()
            p1 = self.f3_spin.value()
            is_active = True
        elif tr("linkbudget.stage_type_switch", "开关") in type_name:
            loss = self.f1_spin.value()
            gain = -1 * abs(loss) # 强制损耗为负增益
            nf = abs(loss)        # 无源室温下 NF = 损耗
            p1 = self.f3_spin.value()
            is_active = True      # 开关作为线性度瓶颈，标记为 Active 以参与 P1 计算
        else:
            # 滤波器, 衰减器, 线缆, 功分器 (纯无源)
            loss = self.f1_spin.value()
            gain = -1 * abs(loss)
            nf = abs(loss)
            p1 = 100.0            # 极高值，忽略其压缩点
            is_active = False
            
        return StageParams(
            name=f"S{self.index+1}",
            stage_type=stage_type,
            gain_db=gain,
            nf_db=nf,
            op1db_dbm=p1,
            is_active=is_active
        )
    
    def update_index(self, new_index: int):
        self.index = new_index
        self.retranslate_ui()

    def retranslate_ui(self):
        """刷新卡片内部文字"""
        self.title_label.setText(f"{tr('linkbudget.stage', '级')} {self.index + 1}")
        
        # 刷新 ComboBox (保持当前索引)
        curr_idx = self.type_combo.currentIndex()
        self.type_combo.blockSignals(True)
        self.type_combo.clear()
        self.type_combo.addItems([
            tr("linkbudget.stage_type_amp", "放大器 (LNA/PA)"), 
            tr("linkbudget.stage_type_filter", "滤波器 (Filter)"), 
            tr("linkbudget.stage_type_attenuator", "衰减器 (Attenuator)"), 
            tr("linkbudget.stage_type_cable", "线缆 (Cable)"), 
            tr("linkbudget.stage_type_switch", "开关 (Switch)"), 
            tr("linkbudget.stage_type_mixer", "混频器 (Mixer)"),
            tr("linkbudget.stage_type_splitter", "功分器 (Splitter)")
        ])
        self.type_combo.setCurrentIndex(curr_idx)
        self.type_combo.blockSignals(False)
        
        # 刷新 Label (根据当前选中的类型手动刷新，因为 text 是动态设置的)
        self._on_type_changed(curr_idx)
        
        # 刷新 Tooltip
        self.btn_left.setToolTip(tr("linkbudget.tip_move_left", "向左移动"))
        self.btn_right.setToolTip(tr("linkbudget.tip_move_right", "向右移动"))
        self.btn_remove.setToolTip(tr("linkbudget.tip_remove", "删除此级"))


class LinkBudgetTool(ToolBase):
    """链路预算工具"""
    
    tool_name = tr("linkbudget.tool_name", "链路预算")
    tool_icon = "🔗"
    tool_category = "rf"
    tool_description = tr("linkbudget.tool_desc", "计算射频链路级联增益、NF、P1dB")
    i18n_title_key = "linkbudget.tool_name"
    i18n_desc_key = "linkbudget.tool_desc"
    
    def __init__(self):
        self._calculator = LinkBudgetCalculator()
        self._stages: List[StageWidget] = []
        self._connectors: List[QWidget] = []
        super().__init__()
        
        # 初始添加 3 级
        self._add_stage() # LNA
        self._add_stage() # Filter
        self._add_stage() # Mixer
        
        # 修正默认选择
        if len(self._stages) >= 3:
            self._stages[1].type_combo.setCurrentIndex(1) # Filter
            self._stages[2].type_combo.setCurrentIndex(5) # Mixer
        
    def create_input_panel(self) -> QWidget:
        """输入面板 (包含链路搭建和结果表格的上下布局)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 1. 顶部工具栏
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton(tr("linkbudget.btn_add_component", "➕ 添加组件"))
        self.btn_add.clicked.connect(lambda: self._add_stage())
        toolbar.addWidget(self.btn_add)
        
        self.btn_clear = QPushButton(tr("linkbudget.btn_clear_link", "🗑️ 清空链路"))
        self.btn_clear.clicked.connect(self._clear_stages)
        toolbar.addWidget(self.btn_clear)
        
        self.btn_calc_refresh = QPushButton(tr("linkbudget.btn_refresh_calc", "🔄 刷新计算"))
        self.btn_calc_refresh.setObjectName("PrimaryButton")
        self.btn_calc_refresh.clicked.connect(self._recalc)
        toolbar.addWidget(self.btn_calc_refresh)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 2. 滚动区域 (链路图)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(400) # 保证卡片能完整显示
        scroll.setStyleSheet("background-color: #F7FAFC; border: 1px solid #E2E8F0; border-radius: 8px;")
        
        self._canvas = QWidget()
        self._canvas_layout = QHBoxLayout(self._canvas)
        self._canvas_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._canvas_layout.setSpacing(10) # 间距缩小，因为有箭头
        
        scroll.setWidget(self._canvas)
        layout.addWidget(scroll)
        
        # 3. 结果面板 (表格) - 整合到这里形成上下排布
        self._grp_result = QGroupBox(tr("linkbudget.title_summary", "📊 链路指标汇总"))
        res_layout = QVBoxLayout(self._grp_result)
        
        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels([
            tr("linkbudget.tbl_col_stage_num", "级数"), 
            tr("linkbudget.tbl_col_type", "类型"), 
            tr("linkbudget.tbl_col_gain", "增益(dB)"), 
            tr("linkbudget.tbl_col_nf", "NF(dB)"), 
            tr("linkbudget.tbl_col_op1db", "OP1dB(dBm)"), 
            tr("linkbudget.tbl_col_cascaded_gain", "累计增益(dB)"), 
            tr("linkbudget.tbl_col_cascaded_nf", "累计NF(dB)"), 
            tr("linkbudget.tbl_col_system_iip1", "系统IIP1(dBm)")
        ])
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setMinimumHeight(200)
        res_layout.addWidget(self._table)
        
        # 底部总结果摘要
        self._summary_label = QLabel(tr("linkbudget.summary_placeholder", "总增益: -- dB  |  总NF: -- dB  |  输出P1dB: -- dBm"))
        self._summary_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2D3748; padding: 12px; background: #EBF8FF; border-radius: 6px;")
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        res_layout.addWidget(self._summary_label)
        
        layout.addWidget(self._grp_result)
        
        # 4. 链路预算参数输入
        self._grp_link = QGroupBox(tr("linkbudget.title_link_params", "📡 链路预算参数"))
        link_params_layout = QGridLayout(self._grp_link)
        link_params_layout.setSpacing(10)

        # 发射端
        self._grp_tx = QGroupBox(tr("linkbudget.title_tx", "📡 发射端 (Tx)"))
        tx_layout = QGridLayout(self._grp_tx)
        tx_layout.setSpacing(10)
        
        tx_layout.addWidget(QLabel(tr("linkbudget.lbl_ptx", "发射功率 (P_tx):")), 0, 0)
        self._ptx_input = QLineEdit("30")  # 默认 30 dBm (1W)
        self._ptx_input.setValidator(QDoubleValidator())
        tx_layout.addWidget(self._ptx_input, 0, 1)
        tx_layout.addWidget(QLabel("dBm"), 0, 2)
        
        tx_layout.addWidget(QLabel(tr("linkbudget.lbl_ltx", "发射端馈线损耗 (L_tx):")), 1, 0)
        self._ltx_input = QLineEdit("2.0")
        self._ltx_input.setValidator(QDoubleValidator())
        tx_layout.addWidget(self._ltx_input, 1, 1)
        tx_layout.addWidget(QLabel("dB"), 1, 2)
        
        tx_layout.addWidget(QLabel(tr("linkbudget.lbl_gtx", "发射天线增益 (G_tx):")), 2, 0)
        self._gtx_input = QLineEdit("10.0")
        self._gtx_input.setValidator(QDoubleValidator())
        tx_layout.addWidget(self._gtx_input, 2, 1)
        tx_layout.addWidget(QLabel("dBi"), 2, 2)
        
        link_params_layout.addWidget(self._grp_tx, 0, 0)

        # 接收端
        self._grp_rx = QGroupBox(tr("linkbudget.title_rx", "📡 接收端 (Rx)"))
        rx_layout = QGridLayout(self._grp_rx)
        rx_layout.setSpacing(10)
        
        rx_layout.addWidget(QLabel(tr("linkbudget.lbl_grx", "接收天线增益 (G_rx):")), 0, 0)
        self._grx_input = QLineEdit("10.0")
        self._grx_input.setValidator(QDoubleValidator())
        rx_layout.addWidget(self._grx_input, 0, 1)
        rx_layout.addWidget(QLabel("dBi"), 0, 2)
        
        rx_layout.addWidget(QLabel(tr("linkbudget.lbl_lrx", "接收端馈线损耗 (L_rx):")), 1, 0)
        self._lrx_input = QLineEdit("2.0")
        self._lrx_input.setValidator(QDoubleValidator())
        rx_layout.addWidget(self._lrx_input, 1, 1)
        rx_layout.addWidget(QLabel("dB"), 1, 2)
        
        rx_layout.addWidget(QLabel(tr("linkbudget.lbl_min_rx_pwr", "最小接收功率 (P_min):")), 2, 0)
        self._pmin_input = QLineEdit("-90.0")
        self._pmin_input.setValidator(QDoubleValidator())
        rx_layout.addWidget(self._pmin_input, 2, 1)
        rx_layout.addWidget(QLabel("dBm"), 2, 2)
        
        link_params_layout.addWidget(self._grp_rx, 0, 1)

        # 信道
        self._grp_ch = QGroupBox(tr("linkbudget.title_channel", "📡 信道参数"))
        ch_layout = QGridLayout(self._grp_ch)
        ch_layout.setSpacing(10)
        
        ch_layout.addWidget(QLabel(tr("linkbudget.lbl_freq", "频率 (Freq):")), 0, 0)
        self._freq_input = QLineEdit("2.4")
        self._freq_input.setValidator(QDoubleValidator())
        ch_layout.addWidget(self._freq_input, 0, 1)
        self._freq_unit = QComboBox()
        self._freq_unit.addItems([tr("linkbudget.unit_ghz", "GHz"), tr("linkbudget.unit_mhz", "MHz")])
        ch_layout.addWidget(self._freq_unit, 0, 2)
        
        ch_layout.addWidget(QLabel(tr("linkbudget.lbl_distance", "距离 (Distance):")), 1, 0)
        self._dist_input = QLineEdit("1.0")
        self._dist_input.setValidator(QDoubleValidator())
        ch_layout.addWidget(self._dist_input, 1, 1)
        self._dist_unit = QComboBox()
        self._dist_unit.addItems([tr("linkbudget.unit_km", "km"), tr("linkbudget.unit_m", "m")])
        ch_layout.addWidget(self._dist_unit, 1, 2)
        
        fspl_layout = QHBoxLayout()
        fspl_layout.addWidget(QLabel(tr("linkbudget.lbl_fsl", "自由空间路径损耗 (FSPL):")))
        self._btn_calc_fspl = QPushButton(tr("linkbudget.btn_calc_fspl", "计算FSPL"))
        self._btn_calc_fspl.clicked.connect(self._auto_calc_fspl)
        fspl_layout.addWidget(self._btn_calc_fspl)
        fspl_layout.addStretch()
        ch_layout.addLayout(fspl_layout, 2, 0)
        
        self._fsl_input = QLineEdit("100.04") # 2.4GHz @ 1km
        self._fsl_input.setValidator(QDoubleValidator())
        ch_layout.addWidget(self._fsl_input, 2, 1)
        ch_layout.addWidget(QLabel("dB"), 2, 2)
        
        ch_layout.addWidget(QLabel(tr("linkbudget.lbl_fade", "衰落裕量 (Fading):")), 3, 0)
        self._fade_input = QLineEdit("10.0")
        self._fade_input.setValidator(QDoubleValidator())
        ch_layout.addWidget(self._fade_input, 3, 1)
        ch_layout.addWidget(QLabel("dB"), 3, 2)
        
        ch_layout.addWidget(QLabel(tr("linkbudget.lbl_misc", "其他损耗 (Misc):")), 4, 0)
        self._misc_loss_input = QLineEdit("0.0")
        self._misc_loss_input.setValidator(QDoubleValidator())
        ch_layout.addWidget(self._misc_loss_input, 4, 1)
        ch_layout.addWidget(QLabel("dB"), 4, 2)
        
        link_params_layout.addWidget(self._grp_ch, 1, 0, 1, 2)  # 跨两列

        layout.addWidget(self._grp_link)

        # ── 计算按钮 ──
        self.btn_calc_budget = QPushButton(tr("linkbudget.btn_calc", "计算链路预算"))
        self.btn_calc_budget.setObjectName("PrimaryButton")
        self.btn_calc_budget.clicked.connect(self._calculate)
        layout.addWidget(self.btn_calc_budget)
        
        # ── 结果区 ──
        self._grp_res = QGroupBox(tr("linkbudget.title_link_budget_results", "📊 链路预算结果"))
        res_layout = QVBoxLayout(self._grp_res)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        grid.addWidget(QLabel(tr("linkbudget.lbl_rx_pwr", "接收功率 (P_rx)")), 0, 0)
        self._prx_label = QLabel("--")
        self._prx_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2B6CB0;")
        grid.addWidget(self._prx_label, 0, 1)
        
        grid.addWidget(QLabel(tr("linkbudget.lbl_margin", "链路裕量 (Margin)")), 1, 0)
        self._margin_label = QLabel("--")
        self._margin_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2B6CB0;")
        grid.addWidget(self._margin_label, 1, 1)
        
        grid.addWidget(QLabel(tr("linkbudget.lbl_status", "链路状态")), 2, 0)
        self._status_label = QLabel(tr("linkbudget.status_unknown", "未知"))
        self._status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        grid.addWidget(self._status_label, 2, 1)
        
        res_layout.addLayout(grid)
        layout.addWidget(self._grp_res)
        
        # 连接信号槽
        self._ptx_input.textChanged.connect(self._clear_link_budget_results)
        self._ltx_input.textChanged.connect(self._clear_link_budget_results)
        self._gtx_input.textChanged.connect(self._clear_link_budget_results)
        self._grx_input.textChanged.connect(self._clear_link_budget_results)
        self._lrx_input.textChanged.connect(self._clear_link_budget_results)
        self._pmin_input.textChanged.connect(self._clear_link_budget_results)
        self._freq_input.textChanged.connect(self._clear_link_budget_results)
        self._freq_unit.currentIndexChanged.connect(self._clear_link_budget_results)
        self._dist_input.textChanged.connect(self._clear_link_budget_results)
        self._dist_unit.currentIndexChanged.connect(self._clear_link_budget_results)
        self._fsl_input.textChanged.connect(self._clear_link_budget_results)
        self._fade_input.textChanged.connect(self._clear_link_budget_results)
        self._misc_loss_input.textChanged.connect(self._clear_link_budget_results)
        
        return panel
        
    def create_result_panel(self) -> Optional[QWidget]:
        """原右侧结果面板为空，强制让 input_panel 占据 100% 宽度"""
        return None


    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新 UI 文字"""
        super().retranslate_ui(lang)
        
        # 刷新所有卡片
        for stage in self._stages:
            stage.retranslate_ui()
            
        # 刷新按钮
        if hasattr(self, 'btn_add'): self.btn_add.setText(tr("linkbudget.btn_add_component"))
        if hasattr(self, 'btn_clear'): self.btn_clear.setText(tr("linkbudget.btn_clear_link"))
        if hasattr(self, 'btn_calc_refresh'): self.btn_calc_refresh.setText(tr("linkbudget.btn_refresh_calc"))
        if hasattr(self, 'btn_calc_budget'): self.btn_calc_budget.setText(tr("linkbudget.btn_calc"))
        if hasattr(self, '_btn_calc_fspl'): self._btn_calc_fspl.setText(tr("linkbudget.btn_calc_fspl"))

        # 刷新 GroupBox
        if hasattr(self, '_grp_result'): self._grp_result.setTitle(tr("linkbudget.title_summary"))
        if hasattr(self, '_grp_link'): self._grp_link.setTitle(tr("linkbudget.title_link_params"))
        if hasattr(self, '_grp_tx'): self._grp_tx.setTitle(tr("linkbudget.title_tx"))
        if hasattr(self, '_grp_rx'): self._grp_rx.setTitle(tr("linkbudget.title_rx"))
        if hasattr(self, '_grp_ch'): self._grp_ch.setTitle(tr("linkbudget.title_channel"))
        if hasattr(self, '_grp_res'): self._grp_res.setTitle(tr("linkbudget.title_link_budget_results"))

        # 刷新表格表头
        if hasattr(self, '_table'):
            self._table.setHorizontalHeaderLabels([
                tr("linkbudget.tbl_col_stage_num", "级数"), 
                tr("linkbudget.tbl_col_type", "类型"), 
                tr("linkbudget.tbl_col_gain", "增益(dB)"), 
                tr("linkbudget.tbl_col_nf", "NF(dB)"), 
                tr("linkbudget.tbl_col_op1db", "OP1dB(dBm)"), 
                tr("linkbudget.tbl_col_cascaded_gain", "累计增益(dB)"), 
                tr("linkbudget.tbl_col_cascaded_nf", "累计NF(dB)"), 
                tr("linkbudget.tbl_col_system_iip1", "系统IIP1(dBm)")
            ])
            # 同步更新表格中的数据（主要是类型列需要重新翻译）
            self._recalc()

        # 刷新 Label
        if hasattr(self, '_prx_label'): self._clear_link_budget_results()
        
        # 刷新频率和距离单位
        if hasattr(self, '_freq_unit'):
            curr_freq = self._freq_unit.currentIndex()
            self._freq_unit.blockSignals(True)
            self._freq_unit.clear()
            self._freq_unit.addItems([tr("linkbudget.unit_ghz", "GHz"), tr("linkbudget.unit_mhz", "MHz")])
            self._freq_unit.setCurrentIndex(curr_freq)
            self._freq_unit.blockSignals(False)
            
        if hasattr(self, '_dist_unit'):
            curr_dist = self._dist_unit.currentIndex()
            self._dist_unit.blockSignals(True)
            self._dist_unit.clear()
            self._dist_unit.addItems([tr("linkbudget.unit_km", "km"), tr("linkbudget.unit_m", "m")])
            self._dist_unit.setCurrentIndex(curr_dist)
            self._dist_unit.blockSignals(False)

    def calculate(self) -> Dict[str, Any]:
        """接口实现"""
        return {}

    def _add_stage(self):
        index = len(self._stages)
        stage = StageWidget(index)
        stage.paramChanged.connect(self._recalc)
        stage.removeRequested.connect(self._remove_stage)
        stage.moveLeftRequested.connect(lambda idx: self._move_stage(idx, -1))
        stage.moveRightRequested.connect(lambda idx: self._move_stage(idx, 1))
        
        self._stages.append(stage)
        self._rebuild_canvas()
        
    def _move_stage(self, index: int, direction: int):
        target_index = index + direction
        if 0 <= target_index < len(self._stages) and 0 <= index < len(self._stages):
            # 交换列表中的位置
            self._stages[index], self._stages[target_index] = self._stages[target_index], self._stages[index]
            self._rebuild_canvas()
            
    def _remove_stage(self, index):
        if 0 <= index < len(self._stages):
            stage = self._stages.pop(index)
            stage.deleteLater()
            self._rebuild_canvas()

    def _clear_stages(self):
        while self._stages:
            stage = self._stages.pop(0)
            stage.deleteLater()
        self._rebuild_canvas()

    def _rebuild_canvas(self):
        """完全重建画布以处理增删和重排序，比动态插入更加干净"""
        # 1. 移除布局中现有所有的 Widget 和 Connector
        while self._canvas_layout.count():
            child = self._canvas_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
                
        # 2. 清理旧的连接符
        for conn in self._connectors:
            conn.deleteLater()
        self._connectors.clear()
        
        # 3. 按当前列表重新添加并加上箭头
        for i, stage in enumerate(self._stages):
            stage.update_index(i)
            
            # 第一级之后，加上箭头
            if i > 0:
                conn = QLabel("➡️")  # 箭头这里改不改无所谓，主要是卡片上的能看到就行，或者改成 "→"
                conn.setAlignment(Qt.AlignmentFlag.AlignCenter)
                conn.setStyleSheet("font-size: 24px; color: #A0AEC0;")
                conn.setFixedWidth(40)
                self._connectors.append(conn)
                self._canvas_layout.addWidget(conn)
                
            self._canvas_layout.addWidget(stage)
            
            # 禁用边缘阶段的左右移动按钮 (依靠 stylesheet 的 :disabled 伪类即可实现视觉变化)
            stage.btn_left.setEnabled(i > 0)
            stage.btn_right.setEnabled(i < len(self._stages) - 1)
            
        # 4. 重新计算
        self._recalc()

    def _recalc(self):
        """执行计算"""
        # 收集参数
        params_list = [s.get_params() for s in self._stages]
        
        if not params_list:
            self._table.setRowCount(0)
            self._summary_label.setText("请添加射频组件...")
            return
            
        # 计算
        results: List[StageResult] = self._calculator.calculate_chain(params_list)
        
        # 更新表格
        self._table.setRowCount(len(results))
        self._table.blockSignals(True)
        
        for i, res in enumerate(results):
            # 基础参数
            self._set_table_item(i, 0, f"{i+1}")
            self._set_table_item(i, 1, res.params.stage_type)
            self._set_table_item(i, 2, f"{res.params.gain_db:.2f}")
            self._set_table_item(i, 3, f"{res.params.nf_db:.2f}")
            
            p1_str = f"{res.params.op1db_dbm:.1f}" if res.params.is_active else "-"
            self._set_table_item(i, 4, p1_str)
            
            # 级联结果
            self._set_table_item(i, 5, f"{res.cascaded_gain_db:.2f}", is_bold=True, bg_color="#EBF8FF")
            self._set_table_item(i, 6, f"{res.cascaded_nf_db:.2f}", is_bold=True, bg_color="#F0FFF4")
            
            sys_ip1_str = f"{res.cascaded_iip1db_dbm:.2f}"
            self._set_table_item(i, 7, sys_ip1_str, is_bold=True, bg_color="#FFF5F5")
            
        self._table.blockSignals(False)
        
        # 更新摘要
        last_res = results[-1]
        self._summary_label.setText(
            f"总增益: {last_res.cascaded_gain_db:.2f} dB  |  "
            f"系统NF: {last_res.cascaded_nf_db:.2f} dB  |  "
            f"系统IIP1: {last_res.cascaded_iip1db_dbm:.2f} dBm"
        )

    def _set_table_item(self, row, col, text, is_bold=False, bg_color=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        
        if is_bold:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            
        if bg_color:
            item.setBackground(QColor(bg_color))
            
        self._table.setItem(row, col, item)

    def _auto_calc_fspl(self):
        """自动计算自由空间路径损耗"""
        try:
            freq = float(self._freq_input.text())
            dist = float(self._dist_input.text())
            
            freq_mhz = freq * 1000 if self._freq_unit.currentText() == tr("linkbudget.unit_ghz", "GHz") else freq
            dist_km = dist if self._dist_unit.currentText() == tr("linkbudget.unit_km", "km") else dist / 1000.0
            
            # FSPL = 32.44 + 20log10(d_km) + 20log10(f_MHz)
            if dist_km > 0 and freq_mhz > 0:
                fspl = 32.44 + 20 * math.log10(dist_km) + 20 * math.log10(freq_mhz)
                self._fsl_input.setText(f"{fspl:.2f}")
        except ValueError:
            pass

    def _clear_link_budget_results(self):
        """清除计算结果"""
        self._prx_label.setText("--")
        self._margin_label.setText("--")
        self._status_label.setText(tr("linkbudget.status_unknown", "未知"))
        self._status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: gray;")

    def _calculate(self):
        """计算核心链路总预算"""
        if not self._stages:
            QMessageBox.warning(self, tr("linkbudget.warning_title", "未配置链路"), tr("linkbudget.warning_msg", "请至少添加一个射频链路阶段。"))
            return
            
        try:
            # 读取全部参数
            ptx = float(self._ptx_input.text())
            ltx = float(self._ltx_input.text())
            gtx = float(self._gtx_input.text())
            
            grx = float(self._grx_input.text())
            lrx = float(self._lrx_input.text())
            pmin = float(self._pmin_input.text())
            
            fspl = float(self._fsl_input.text())
            fade = float(self._fade_input.text())
            misc = float(self._misc_loss_input.text())
            
            # 1. 刷新硬件链路级联合计算
            self._recalc()
            
            # 获取汇总的硬件增益
            params_list = [s.get_params() for s in self._stages]
            results = self._calculator.calculate_chain(params_list)
            if not results:
                return
            hw_gain_db = results[-1].cascaded_gain_db
            
            # 2. 计算接收功率 (Prx)
            # Prx = Ptx - Ltx + Gtx - FSPL - Fade - Misc + Grx - Lrx + HW_Gain
            prx = ptx - ltx + gtx - fspl - fade - misc + grx - lrx + hw_gain_db
            self._prx_label.setText(f"{prx:.2f} dBm")
            
            # 3. 链路裕量 (Margin)
            margin = prx - pmin
            self._margin_label.setText(f"{margin:.2f} dB")
            
            # 4. 状态判定
            if margin >= 10:
                self._status_label.setText(tr("linkbudget.status_excellent", "链路极佳 (Excellent)"))
                self._status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #38A169;")
            elif margin >= 0:
                self._status_label.setText(tr("linkbudget.status_good", "符合要求 (Good)"))
                self._status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3182CE;")
            else:
                self._status_label.setText(tr("linkbudget.status_fail", "链路中断 (Fail)"))
                self._status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E53E3E;")
                
        except ValueError:
            QMessageBox.warning(self, tr("linkbudget.error_title", "输入错误"), tr("linkbudget.error_msg_num", "请输入有效的数字！"))

    # ==================== 知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        return tr("linkbudget.intuition_content")
        
    def get_math_model_content(self) -> Optional[str]:
        return tr("linkbudget.math_content")
