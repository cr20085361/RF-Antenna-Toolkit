# -*- coding: utf-8 -*-
"""
射频天线工具集 - 链路预算工具
RF Antenna Toolkit - Link Budget Tool

版本: v1.0.0
功能: 射频链路增益、噪声系数、P1dB 级联计算与可视化
"""

from typing import Dict, Any, Optional, List
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QScrollArea, QSizePolicy,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtSvgWidgets import QSvgWidget
import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

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
            "放大器 (LNA/PA)", 
            "滤波器 (Filter)", 
            "衰减器 (Attenuator)", 
            "线缆 (Cable)", 
            "开关 (Switch)", 
            "混频器 (Mixer)",
            "功分器 (Splitter)"
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
        self.f1_label = QLabel("Gain (dB):")
        self.input_layout.addWidget(self.f1_label, 0, 0)
        self.f1_spin = QDoubleSpinBox()
        self.f1_spin.setRange(-100, 100)
        self.f1_spin.setDecimals(2)
        self.f1_spin.setValue(10.0)
        self.f1_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons) # [FIX] 移除上下箭头
        self.f1_spin.valueChanged.connect(self.paramChanged.emit)
        self.input_layout.addWidget(self.f1_spin, 0, 1)
        
        # Field 2 (NF)
        self.f2_label = QLabel("NF (dB):")
        self.input_layout.addWidget(self.f2_label, 1, 0)
        self.f2_spin = QDoubleSpinBox()
        self.f2_spin.setRange(0, 100)
        self.f2_spin.setDecimals(2)
        self.f2_spin.setValue(1.0)
        self.f2_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons) # [FIX] 移除上下箭头
        self.f2_spin.valueChanged.connect(self.paramChanged.emit)
        self.input_layout.addWidget(self.f2_spin, 1, 1)
        
        # Field 3 (OP1dB)
        self.f3_label = QLabel("OP1dB:")
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
        
        if "放大器" in type_name:
            self.icon_widget.load(self._get_icon_path("amplifier.svg"))
            self.f1_label.setText("Gain (dB):")
            self.f1_spin.setValue(15.0)
            self.f2_label.setText("NF (dB):")
            self.f2_spin.setValue(1.5)
            self.f3_label.setText("OP1dB:")
            self.f3_spin.setValue(20.0)
        elif "滤波器" in type_name or "衰减器" in type_name or "线缆" in type_name or "功分器" in type_name:
            if "滤波器" in type_name:
                self.icon_widget.load(self._get_icon_path("filter.svg"))
                default_loss = 1.0
            elif "衰减器" in type_name:
                self.icon_widget.load(self._get_icon_path("attenuator.svg"))
                default_loss = 3.0
            elif "线缆" in type_name:
                self.icon_widget.load(self._get_icon_path("cable.svg"))
                default_loss = 0.5
            else: # 功分器
                self.icon_widget.load(self._get_icon_path("splitter.svg"))
                default_loss = 3.5
                
            self.f1_label.setText("插入损耗(dB):" if "衰减器" not in type_name else "衰减值(dB):")
            self.f1_spin.setValue(default_loss)
            
            # 无源器件隐藏独立的 NF 和 OP1dB
            self.f2_label.hide()
            self.f2_spin.hide()
            self.f3_label.hide()
            self.f3_spin.hide()
            
        elif "开关" in type_name:
            self.icon_widget.load(self._get_icon_path("switch.svg"))
            self.f1_label.setText("插入损耗(dB):")
            self.f1_spin.setValue(0.8)
            
            # 开关隐藏独立的 NF，但保留 OP1dB
            self.f2_label.hide()
            self.f2_spin.hide()
            self.f3_label.setText("OP1dB:")
            self.f3_spin.setValue(30.0)
            
        elif "混频器" in type_name:
            self.icon_widget.load(self._get_icon_path("mixer.svg"))
            self.f1_label.setText("变频增益(dB):") # 混频器可以是无源(损耗)也可以是有源(增益)
            self.f1_spin.setValue(-6.0)
            self.f2_label.setText("NF (dB):")
            self.f2_spin.setValue(6.5)
            self.f3_label.setText("OP1dB:")
            self.f3_spin.setValue(10.0)
            
        self.blockSignals(False)
        self.paramChanged.emit()

    def get_params(self) -> StageParams:
        """获取当前配置参数"""
        type_name = self.type_combo.currentText()
        stage_type = type_name.split(" ")[0]
        
        # 提取动态逻辑
        if "放大器" in type_name or "混频器" in type_name:
            gain = self.f1_spin.value()
            nf = self.f2_spin.value()
            p1 = self.f3_spin.value()
            is_active = True
        elif "开关" in type_name:
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
        self.title_label.setText(f"Stage {new_index + 1}")


class LinkBudgetTool(ToolBase):
    """链路预算工具"""
    
    tool_name = "链路预算"
    tool_icon = "🔗"
    tool_category = "rf"
    tool_description = "计算射频链路级联增益、NF、P1dB"
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
        btn_add = QPushButton("➕ 添加组件")
        btn_add.clicked.connect(lambda: self._add_stage())
        toolbar.addWidget(btn_add)
        
        btn_clear = QPushButton("🗑️ 清空链路")
        btn_clear.clicked.connect(self._clear_stages)
        toolbar.addWidget(btn_clear)
        
        btn_calc = QPushButton("🔄 刷新计算")
        btn_calc.setObjectName("PrimaryButton")
        btn_calc.clicked.connect(self._recalc)
        toolbar.addWidget(btn_calc)
        
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
        result_group = QGroupBox("📊 链路指标汇总")
        res_layout = QVBoxLayout(result_group)
        
        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels([
            "级数", "类型", "增益(dB)", "NF(dB)", "OP1dB(dBm)", 
            "累计增益(dB)", "累计NF(dB)", "系统IIP1(dBm)"
        ])
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setMinimumHeight(200)
        res_layout.addWidget(self._table)
        
        # 底部总结果摘要
        self._summary_label = QLabel("总增益: -- dB  |  总NF: -- dB  |  输出P1dB: -- dBm")
        self._summary_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2D3748; padding: 12px; background: #EBF8FF; border-radius: 6px;")
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        res_layout.addWidget(self._summary_label)
        
        layout.addWidget(result_group)
        
        return panel
        
    def create_result_panel(self) -> Optional[QWidget]:
        """原右侧结果面板为空，强制让 input_panel 占据 100% 宽度"""
        return None

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

    # ==================== 知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        return tr("linkbudget.intuition_content")
        
    def get_math_model_content(self) -> Optional[str]:
        return tr("linkbudget.math_content")
