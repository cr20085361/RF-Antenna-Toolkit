# -*- coding: utf-8 -*-
"""
射频天线工具集 - 阻抗计算工具
RF Antenna Toolkit - Impedance Calculator Tool

版本: v1.0.0
功能: 计算传输线特性阻抗
支持结构:
  1. 同轴线 (Coaxial)
  2. 单微带线 (Microstrip)
  3. 共面波导微带线 (CPWG)
"""

from typing import Dict, Any, Optional
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QRadioButton, QButtonGroup,
    QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QPixmap

from ui.base.tool_base import ToolBase
from core.rf.impedance import ImpedanceCalculator, COMMON_MATERIALS


class ImpedanceTool(ToolBase):
    """阻抗计算工具
    
    支持三种传输线结构的特性阻抗计算:
    1. 同轴线 - 经典解析公式
    2. 微带线 - Hammerstad-Jensen 公式
    3. CPWG - Ghione-Naldi 公式
    """
    
    # 工具元信息
    tool_name = "阻抗计算"
    tool_icon = "Ω"
    tool_category = "rf"
    tool_description = "计算传输线特性阻抗 (同轴线/微带线/CPWG)"
    
    def __init__(self):
        # 注意：必须在 super().__init__() 之前初始化，因为基类会调用 create_input_panel()
        self.calculator = ImpedanceCalculator()
        self._current_mode = 0  # 0=同轴线, 1=微带线, 2=CPWG
        # mm/mil 转换系数: 1 mil = 0.0254 mm
        self._MIL_TO_MM = 0.0254
        # 存储各参数的单位选择控件 {参数名: QComboBox}
        self._unit_combos = {}
        super().__init__()
    
    # ==================== 辅助方法：创建参数行 ====================
    
    def _create_param_row(self, layout: 'QGridLayout', row: int, label: str, 
                          input_widget: 'QLineEdit', param_key: str,
                          has_unit: bool = True, has_calc_btn: bool = True,
                          unit_type: str = 'length') -> int:
        """创建一个参数行: [标签] [输入框] [单位选择] [计算按钮]
        
        v1.1 新增: 每个参数后带"计算"按钮和 mm/mil 单位切换
        
        参数:
            layout: 网格布局
            row: 当前行号
            label: 参数标签文字
            input_widget: 输入框控件
            param_key: 参数唯一标识 (用于反算定位)
            has_unit: 是否显示单位选择器
            has_calc_btn: 是否显示"计算"按钮
            unit_type: 单位类型 ('length'=mm/mil, 'thickness'=μm, 'impedance'=Ω, 'none')
        
        返回:
            下一行号
        """
        # 标签
        layout.addWidget(QLabel(label), row, 0)
        # 输入框 - 设置最小宽度确保数值完整显示
        input_widget.setMinimumWidth(100)
        layout.addWidget(input_widget, row, 1)
        
        col = 2
        
        # 单位选择/显示 (v1.2: 缩窄单位框，让输入框更宽)
        if has_unit:
            if unit_type == 'length':
                # mm/mil 切换下拉框
                unit_combo = QComboBox()
                unit_combo.addItem("mm", "mm")
                unit_combo.addItem("mil", "mil")
                unit_combo.setFixedWidth(48)
                unit_combo.currentIndexChanged.connect(
                    lambda idx, key=param_key, inp=input_widget, cb=unit_combo: 
                        self._on_unit_changed(key, inp, cb)
                )
                layout.addWidget(unit_combo, row, col)
                self._unit_combos[param_key] = unit_combo
            elif unit_type == 'thickness':
                unit_label = QLabel("μm")
                unit_label.setFixedWidth(30)
                layout.addWidget(unit_label, row, col)
            elif unit_type == 'impedance':
                unit_label = QLabel("Ω")
                unit_label.setFixedWidth(20)
                layout.addWidget(unit_label, row, col)
            else:
                layout.addWidget(QLabel(""), row, col)
        
        col = 3
        
        # "计算"按钮
        if has_calc_btn:
            calc_btn = QPushButton("计算")
            calc_btn.setFixedWidth(50)
            calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            calc_btn.setStyleSheet("""
                QPushButton {
                    background: #EBF5FB; color: #2C5282; border: 1px solid #BEE3F8;
                    border-radius: 3px; padding: 2px 6px; font-size: 12px;
                }
                QPushButton:hover { background: #BEE3F8; }
                QPushButton:pressed { background: #90CDF4; }
            """)
            calc_btn.clicked.connect(lambda checked, key=param_key: self._solve_param(key))
            layout.addWidget(calc_btn, row, col)
        
        return row + 1
    
    def _create_er_combo(self, default_index: int = 0) -> QComboBox:
        """创建可编辑的介电常数下拉框 (v1.2: 支持自定义输入)
        
        下拉框包含常用材料预设值，并支持用户直接输入自定义值。
        """
        combo = QComboBox()
        combo.setEditable(True)  # 允许手动输入
        for name, value in COMMON_MATERIALS.items():
            combo.addItem(f"{name} ({value})", value)
        combo.addItem("自定义", None)  # 自定义选项
        combo.setCurrentIndex(default_index)
        # 设置输入校验
        combo.setValidator(QDoubleValidator(0.1, 100, 3))
        # 提示文字
        combo.lineEdit().setPlaceholderText("输入或选择 εᵣ")
        return combo
    
    def _get_er_value(self, combo: QComboBox) -> float:
        """从介电常数下拉框获取值 (支持预设和自定义)"""
        data = combo.currentData()
        if data is not None:
            return float(data)
        # 自定义: 从文本中提取数值
        text = combo.currentText().strip()
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"无效的介电常数: {text}")
    
    def _on_unit_changed(self, param_key: str, input_widget: 'QLineEdit', combo: 'QComboBox'):
        """单位切换时自动转换输入值
        
        mm → mil: value / 0.0254
        mil → mm: value * 0.0254
        """
        text = input_widget.text().strip()
        if not text:
            return
        try:
            value = float(text)
            if combo.currentData() == "mil":
                # mm → mil
                converted = value / self._MIL_TO_MM
            else:
                # mil → mm
                converted = value * self._MIL_TO_MM
            input_widget.setText(f"{converted:.4f}")
        except ValueError:
            pass  # 无效输入不转换
    
    def _get_mm_value(self, input_widget: 'QLineEdit', param_key: str) -> float:
        """从输入框获取 mm 单位的值（自动处理 mil 转换）"""
        value = float(input_widget.text() or 0)
        if param_key in self._unit_combos:
            if self._unit_combos[param_key].currentData() == "mil":
                value *= self._MIL_TO_MM  # mil → mm
        return value
    
    def _set_mm_value(self, input_widget: 'QLineEdit', param_key: str, mm_value: float):
        """将 mm 值设置到输入框（自动处理 mil 转换）"""
        if param_key in self._unit_combos:
            if self._unit_combos[param_key].currentData() == "mil":
                display_value = mm_value / self._MIL_TO_MM  # mm → mil
                input_widget.setText(f"{display_value:.4f}")
                return
        input_widget.setText(f"{mm_value:.4f}")
    
    # ==================== 输入面板 ====================
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板 (v1.1 SI9000风格)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ===== 结构模式选择 =====
        mode_group = QGroupBox("结构模式")
        mode_layout = QVBoxLayout(mode_group)
        
        self._mode_button_group = QButtonGroup()
        
        coaxial_radio = QRadioButton("同轴线 (Coaxial)")
        coaxial_radio.setChecked(True)
        self._mode_button_group.addButton(coaxial_radio, 0)
        mode_layout.addWidget(coaxial_radio)
        
        microstrip_radio = QRadioButton("单微带线 (Microstrip)")
        self._mode_button_group.addButton(microstrip_radio, 1)
        mode_layout.addWidget(microstrip_radio)
        
        cpwg_radio = QRadioButton("共面波导 (CPWG)")
        self._mode_button_group.addButton(cpwg_radio, 2)
        mode_layout.addWidget(cpwg_radio)
        
        layout.addWidget(mode_group)
        
        # ===== 参数输入区 (堆叠面板) =====
        self._input_stack = QStackedWidget()
        self._input_stack.addWidget(self._create_coaxial_inputs())
        self._input_stack.addWidget(self._create_microstrip_inputs())
        self._input_stack.addWidget(self._create_cpwg_inputs())
        layout.addWidget(self._input_stack)
        
        # 模式切换信号
        self._mode_button_group.idClicked.connect(self._on_mode_changed)
        
        layout.addStretch()
        
        return panel
    
    def _create_coaxial_inputs(self) -> QWidget:
        """创建同轴线参数输入面板 (v1.1: 带计算按钮和单位切换)"""
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setColumnStretch(1, 1)  # 输入框列伸展
        
        row = 0
        
        # 内导体外径 d
        self._coax_inner_input = QLineEdit()
        self._coax_inner_input.setPlaceholderText("如: 0.91")
        self._coax_inner_input.setValidator(QDoubleValidator(0.001, 1000, 4))
        self._coax_inner_input.setText("0.91")
        row = self._create_param_row(layout, row, "内导体外径 d:", 
                                      self._coax_inner_input, "coax_d")
        
        # 外导体内径 D
        self._coax_outer_input = QLineEdit()
        self._coax_outer_input.setPlaceholderText("如: 2.98")
        self._coax_outer_input.setValidator(QDoubleValidator(0.001, 1000, 4))
        self._coax_outer_input.setText("2.98")
        row = self._create_param_row(layout, row, "外导体内径 D:", 
                                      self._coax_outer_input, "coax_D")
        
        # 介电常数 (v1.2: 支持自定义输入)
        layout.addWidget(QLabel("介电常数 εᵣ:"), row, 0)
        self._coax_er_combo = self._create_er_combo()
        # 同轴线默认选择聚乙烯
        for i in range(self._coax_er_combo.count()):
            if "聚乙烯" in self._coax_er_combo.itemText(i):
                self._coax_er_combo.setCurrentIndex(i)
                break
        layout.addWidget(self._coax_er_combo, row, 1, 1, 2)
        row += 1
        
        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep, row, 0, 1, 4)
        row += 1
        
        # 阻抗 Z₀ (输入目标值，点击"计算"执行正向计算)
        self._coax_z_input = QLineEdit()
        self._coax_z_input.setPlaceholderText("如: 50")
        self._coax_z_input.setValidator(QDoubleValidator(1, 500, 2))
        self._coax_z_input.setText("50")
        row = self._create_param_row(layout, row, "阻抗 Z₀:", 
                                      self._coax_z_input, "coax_Z",
                                      unit_type='impedance')
        
        return panel
    
    def _create_microstrip_inputs(self) -> QWidget:
        """创建微带线参数输入面板 (v1.1: 带计算按钮和单位切换)"""
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setColumnStretch(1, 1)
        
        row = 0
        
        # 导线宽度 W
        self._ms_width_input = QLineEdit()
        self._ms_width_input.setPlaceholderText("如: 1.1")
        self._ms_width_input.setValidator(QDoubleValidator(0.001, 100, 4))
        self._ms_width_input.setText("1.1")
        row = self._create_param_row(layout, row, "导线宽度 W:", 
                                      self._ms_width_input, "ms_W")
        
        # 介质厚度 H
        self._ms_height_input = QLineEdit()
        self._ms_height_input.setPlaceholderText("如: 0.6")
        self._ms_height_input.setValidator(QDoubleValidator(0.001, 100, 4))
        self._ms_height_input.setText("0.6")
        row = self._create_param_row(layout, row, "介质厚度 H:", 
                                      self._ms_height_input, "ms_H")
        
        # 铜箔厚度 T (μm，不做 mm/mil 切换)
        self._ms_thickness_input = QLineEdit()
        self._ms_thickness_input.setPlaceholderText("如: 35")
        self._ms_thickness_input.setValidator(QDoubleValidator(0, 500, 2))
        self._ms_thickness_input.setText("35")
        row = self._create_param_row(layout, row, "铜箔厚度 T:", 
                                      self._ms_thickness_input, "ms_T",
                                      has_calc_btn=False, unit_type='thickness')
        
        # 介电常数 (v1.2: 支持自定义输入)
        layout.addWidget(QLabel("介电常数 εᵣ:"), row, 0)
        self._ms_er_combo = self._create_er_combo(0)  # 默认 FR4
        layout.addWidget(self._ms_er_combo, row, 1, 1, 2)
        row += 1
        
        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep, row, 0, 1, 4)
        row += 1
        
        # 阻抗 Z₀
        self._ms_z_input = QLineEdit()
        self._ms_z_input.setPlaceholderText("如: 50")
        self._ms_z_input.setValidator(QDoubleValidator(1, 500, 2))
        self._ms_z_input.setText("50")
        row = self._create_param_row(layout, row, "阻抗 Z₀:", 
                                      self._ms_z_input, "ms_Z",
                                      unit_type='impedance')
        
        return panel
    
    def _create_cpwg_inputs(self) -> QWidget:
        """创建CPWG参数输入面板 (v1.1: 带计算按钮、单位切换和铜箔厚度)"""
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setColumnStretch(1, 1)
        
        row = 0
        
        # 中心导线宽度 W
        self._cpwg_center_input = QLineEdit()
        self._cpwg_center_input.setPlaceholderText("如: 0.3")
        self._cpwg_center_input.setValidator(QDoubleValidator(0.001, 100, 4))
        self._cpwg_center_input.setText("0.3")
        row = self._create_param_row(layout, row, "中心线宽 W:", 
                                      self._cpwg_center_input, "cpwg_W")
        
        # 间隙宽度 S
        self._cpwg_gap_input = QLineEdit()
        self._cpwg_gap_input.setPlaceholderText("如: 0.15")
        self._cpwg_gap_input.setValidator(QDoubleValidator(0.001, 100, 4))
        self._cpwg_gap_input.setText("0.15")
        row = self._create_param_row(layout, row, "间隙宽度 S:", 
                                      self._cpwg_gap_input, "cpwg_S")
        
        # 介质厚度 H
        self._cpwg_height_input = QLineEdit()
        self._cpwg_height_input.setPlaceholderText("如: 0.21")
        self._cpwg_height_input.setValidator(QDoubleValidator(0.001, 100, 4))
        self._cpwg_height_input.setText("0.21")
        row = self._create_param_row(layout, row, "介质厚度 H:", 
                                      self._cpwg_height_input, "cpwg_H")
        
        # 铜箔厚度 T (v1.1 新增)
        self._cpwg_thickness_input = QLineEdit()
        self._cpwg_thickness_input.setPlaceholderText("如: 35")
        self._cpwg_thickness_input.setValidator(QDoubleValidator(0, 500, 2))
        self._cpwg_thickness_input.setText("35")
        row = self._create_param_row(layout, row, "铜箔厚度 T:", 
                                      self._cpwg_thickness_input, "cpwg_T",
                                      has_calc_btn=False, unit_type='thickness')
        
        # 介电常数 (v1.2: 支持自定义输入)
        layout.addWidget(QLabel("介电常数 εᵣ:"), row, 0)
        self._cpwg_er_combo = self._create_er_combo(0)  # 默认 FR4
        layout.addWidget(self._cpwg_er_combo, row, 1, 1, 2)
        row += 1
        
        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep, row, 0, 1, 4)
        row += 1
        
        # 阻抗 Z₀
        self._cpwg_z_input = QLineEdit()
        self._cpwg_z_input.setPlaceholderText("如: 50")
        self._cpwg_z_input.setValidator(QDoubleValidator(1, 500, 2))
        self._cpwg_z_input.setText("50")
        row = self._create_param_row(layout, row, "阻抗 Z₀:", 
                                      self._cpwg_z_input, "cpwg_Z",
                                      unit_type='impedance')
        
        return panel
    
    def _on_mode_changed(self, mode_id: int):
        """模式切换处理"""
        self._current_mode = mode_id
        self._input_stack.setCurrentIndex(mode_id)
        self._update_diagram(mode_id)
    
    # ==================== 结果面板 ====================
    
    def create_result_panel(self) -> QWidget:
        """创建结果面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 错误提示
        self._error_label = QLabel()
        self._error_label.setStyleSheet("QLabel { color: #E53E3E; font-weight: bold; padding: 8px; background-color: #FED7D7; border-radius: 4px; }")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        
        # 主要结果卡片
        result_card = QWidget()
        result_card.setObjectName("ResultPanel")
        result_layout = QVBoxLayout(result_card)
        
        # 阻抗值 (大字体显示)
        self._impedance_label = QLabel("-- Ω")
        self._impedance_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #2B6CB0;
                padding: 10px;
            }
        """)
        self._impedance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self._impedance_label)
        
        # 阻抗评估
        self._quality_label = QLabel("--")
        self._quality_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._quality_label.setStyleSheet("QLabel { font-size: 14px; color: #4A5568; }")
        result_layout.addWidget(self._quality_label)
        
        layout.addWidget(result_card)
        
        # 详细参数卡片
        detail_card = QWidget()
        detail_card.setObjectName("ResultPanel")
        detail_layout = QVBoxLayout(detail_card)
        
        detail_title = QLabel("📊 详细参数")
        detail_title.setObjectName("ResultTitle")
        detail_layout.addWidget(detail_title)
        
        detail_grid = QGridLayout()
        detail_grid.setSpacing(8)
        
        # 详细参数标签
        self._detail_labels = {}
        detail_items = [
            ("effective_er", "有效介电常数 εₑ"),
            ("velocity", "速度因子"),
            ("capacitance", "单位长度电容"),
            ("ratio", "尺寸比例"),
        ]
        
        for i, (key, label) in enumerate(detail_items):
            name_label = QLabel(f"{label}:")
            name_label.setStyleSheet("color: #4A5568;")
            detail_grid.addWidget(name_label, i, 0)
            
            value_label = QLabel("--")
            value_label.setStyleSheet("font-weight: bold; color: #1A202C;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            detail_grid.addWidget(value_label, i, 1)
            self._detail_labels[key] = value_label
        
        detail_layout.addLayout(detail_grid)
        layout.addWidget(detail_card)
        
        # 截面示意图
        diagram_card = QWidget()
        diagram_card.setObjectName("ResultPanel")
        diagram_layout = QVBoxLayout(diagram_card)
        
        diagram_title = QLabel("📐 截面示意图")
        diagram_title.setObjectName("ResultTitle")
        diagram_layout.addWidget(diagram_title)
        
        self._diagram_label = QLabel()
        self._diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._diagram_label.setMinimumHeight(200)
        self._diagram_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px; }")
        
        # 加载默认图片
        from pathlib import Path
        diagram_path = Path(self.get_asset_path("assets/diagrams/coaxial.png"))
        if diagram_path.exists():
            pixmap = QPixmap(str(diagram_path))
            scaled_pixmap = pixmap.scaled(350, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._diagram_label.setPixmap(scaled_pixmap)
        else:
            self._diagram_label.setText("截面示意图")
        
        diagram_layout.addWidget(self._diagram_label)
        layout.addWidget(diagram_card)
        
        layout.addStretch()
        
        return panel
    
    def _update_diagram(self, mode_id: int):
        """根据模式更新示意图"""
        from pathlib import Path
        
        diagram_files = {
            0: "coaxial.png",
            1: "microstrip.png",
            2: "cpwg.png"
        }
        
        diagram_filename = diagram_files.get(mode_id, "coaxial.png")
        diagram_path = Path(self.get_asset_path(f"assets/diagrams/{diagram_filename}"))
        
        if diagram_path.exists():
            pixmap = QPixmap(str(diagram_path))
            scaled_pixmap = pixmap.scaled(350, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._diagram_label.setPixmap(scaled_pixmap)
        else:
            self._diagram_label.setText(f"示意图: {diagram_filename}")
    
    # ==================== 计算逻辑 (v1.1 SI9000风格) ====================
    
    def _solve_param(self, param_key: str):
        """
        SI9000 风格参数计算 (v1.1)
        
        点击某参数后的"计算"按钮时调用:
        - 如果点击的是 Z₀ 的"计算"按钮 → 正向计算阻抗
        - 如果点击的是其他参数的"计算"按钮 → 根据阻抗值反算该参数
        """
        try:
            self._error_label.hide()
            
            if param_key.startswith("coax_"):
                self._solve_coaxial_param(param_key)
            elif param_key.startswith("ms_"):
                self._solve_microstrip_param(param_key)
            elif param_key.startswith("cpwg_"):
                self._solve_cpwg_param(param_key)
                
        except ValueError as e:
            self._error_label.setText(f"⚠️ {str(e)}")
            self._error_label.show()
        except Exception as e:
            self._error_label.setText(f"⚠️ 计算错误: {str(e)}")
            self._error_label.show()
    
    def _solve_coaxial_param(self, param_key: str):
        """同轴线参数计算"""
        inner = self._get_mm_value(self._coax_inner_input, "coax_d")
        outer = self._get_mm_value(self._coax_outer_input, "coax_D")
        er = self._get_er_value(self._coax_er_combo)
        
        if param_key == "coax_Z":
            # 正向计算：d, D, εr → Z₀
            if inner <= 0 or outer <= 0:
                raise ValueError("请输入有效的尺寸")
            if outer <= inner:
                raise ValueError("外径必须大于内径")
            result = self.calculator.calculate_coaxial(inner, outer, er)
            self._coax_z_input.setText(f"{result.impedance:.2f}")
            self._show_result(result, "coaxial")
            
        elif param_key == "coax_d":
            # 反算内径 d: Z₀, D, εr → d
            target_z = float(self._coax_z_input.text() or 0)
            if target_z <= 0 or outer <= 0:
                raise ValueError("请输入有效的阻抗和外径")
            # d = D / exp(Z₀ × √εr / 60)
            import math
            d = outer / math.exp(target_z * math.sqrt(er) / 60)
            self._set_mm_value(self._coax_inner_input, "coax_d", d)
            # 验证
            result = self.calculator.calculate_coaxial(d, outer, er)
            self._show_result(result, "coaxial", solved=("d", d))
            
        elif param_key == "coax_D":
            # 反算外径 D: Z₀, d, εr → D
            target_z = float(self._coax_z_input.text() or 0)
            if target_z <= 0 or inner <= 0:
                raise ValueError("请输入有效的阻抗和内径")
            D = self.calculator.solve_coaxial_outer(target_z, inner, er)
            self._set_mm_value(self._coax_outer_input, "coax_D", D)
            result = self.calculator.calculate_coaxial(inner, D, er)
            self._show_result(result, "coaxial", solved=("D", D))
    
    def _solve_microstrip_param(self, param_key: str):
        """微带线参数计算"""
        width = self._get_mm_value(self._ms_width_input, "ms_W")
        height = self._get_mm_value(self._ms_height_input, "ms_H")
        thickness = float(self._ms_thickness_input.text() or 35)
        er = self._get_er_value(self._ms_er_combo)
        
        if param_key == "ms_Z":
            # 正向计算：W, H, T, εr → Z₀
            if width <= 0 or height <= 0:
                raise ValueError("请输入有效的尺寸")
            result = self.calculator.calculate_microstrip(width, height, er, thickness)
            self._ms_z_input.setText(f"{result.impedance:.2f}")
            self._show_result(result, "microstrip")
            
        elif param_key == "ms_W":
            # 反算线宽 W: Z₀, H, T, εr → W
            target_z = float(self._ms_z_input.text() or 0)
            if target_z <= 0 or height <= 0:
                raise ValueError("请输入有效的阻抗和介质厚度")
            W = self.calculator.solve_microstrip_width(target_z, height, er, thickness)
            self._set_mm_value(self._ms_width_input, "ms_W", W)
            result = self.calculator.calculate_microstrip(W, height, er, thickness)
            self._show_result(result, "microstrip", solved=("W", W))
            
        elif param_key == "ms_H":
            # 反算介质厚度 H: Z₀, W, T, εr → H (二分法)
            target_z = float(self._ms_z_input.text() or 0)
            if target_z <= 0 or width <= 0:
                raise ValueError("请输入有效的阻抗和线宽")
            H = self._bisect_solve(
                lambda h: self.calculator.calculate_microstrip(width, h, er, thickness).impedance,
                target_z, 0.01, 10.0, increasing=True
            )
            self._set_mm_value(self._ms_height_input, "ms_H", H)
            result = self.calculator.calculate_microstrip(width, H, er, thickness)
            self._show_result(result, "microstrip", solved=("H", H))
    
    def _solve_cpwg_param(self, param_key: str):
        """CPWG 参数计算"""
        center = self._get_mm_value(self._cpwg_center_input, "cpwg_W")
        gap = self._get_mm_value(self._cpwg_gap_input, "cpwg_S")
        height = self._get_mm_value(self._cpwg_height_input, "cpwg_H")
        thickness = float(self._cpwg_thickness_input.text() or 35)
        er = self._get_er_value(self._cpwg_er_combo)
        
        if param_key == "cpwg_Z":
            # 正向计算：W, S, H, T, εr → Z₀
            if center <= 0 or gap <= 0 or height <= 0:
                raise ValueError("请输入有效的尺寸")
            result = self.calculator.calculate_cpwg(center, gap, height, er, thickness)
            self._cpwg_z_input.setText(f"{result.impedance:.2f}")
            self._show_result(result, "cpwg")
            
        elif param_key == "cpwg_W":
            # 反算中心线宽 W: Z₀, S, H, T, εr → W (二分法)
            target_z = float(self._cpwg_z_input.text() or 0)
            if target_z <= 0 or gap <= 0 or height <= 0:
                raise ValueError("请输入有效的阻抗和尺寸")
            W = self._bisect_solve(
                lambda w: self.calculator.calculate_cpwg(w, gap, height, er, thickness).impedance,
                target_z, 0.01, 20.0, increasing=False
            )
            self._set_mm_value(self._cpwg_center_input, "cpwg_W", W)
            result = self.calculator.calculate_cpwg(W, gap, height, er, thickness)
            self._show_result(result, "cpwg", solved=("W", W))
            
        elif param_key == "cpwg_S":
            # 反算间隙 S: Z₀, W, H, T, εr → S
            target_z = float(self._cpwg_z_input.text() or 0)
            if target_z <= 0 or center <= 0 or height <= 0:
                raise ValueError("请输入有效的阻抗和尺寸")
            S = self.calculator.solve_cpwg_gap(target_z, center, height, er, thickness)
            self._set_mm_value(self._cpwg_gap_input, "cpwg_S", S)
            result = self.calculator.calculate_cpwg(center, S, height, er, thickness)
            self._show_result(result, "cpwg", solved=("S", S))
            
        elif param_key == "cpwg_H":
            # 反算介质厚度 H: Z₀, W, S, T, εr → H (二分法)
            target_z = float(self._cpwg_z_input.text() or 0)
            if target_z <= 0 or center <= 0 or gap <= 0:
                raise ValueError("请输入有效的阻抗和尺寸")
            H = self._bisect_solve(
                lambda h: self.calculator.calculate_cpwg(center, gap, h, er, thickness).impedance,
                target_z, 0.01, 10.0, increasing=False
            )
            self._set_mm_value(self._cpwg_height_input, "cpwg_H", H)
            result = self.calculator.calculate_cpwg(center, gap, H, er, thickness)
            self._show_result(result, "cpwg", solved=("H", H))
    
    def _bisect_solve(self, func, target: float, low: float, high: float,
                      increasing: bool = True, tol: float = 0.001, max_iter: int = 100) -> float:
        """通用二分法求解器
        
        参数:
            func: 计算函数 f(x) → impedance
            target: 目标阻抗值
            low, high: 搜索范围
            increasing: True=函数递增, False=函数递减
            tol: 收敛精度
            max_iter: 最大迭代次数
        """
        for _ in range(max_iter):
            mid = (low + high) / 2
            z_mid = func(mid)
            
            if abs(z_mid - target) < 0.01:
                return mid
            
            if increasing:
                if z_mid < target:
                    low = mid
                else:
                    high = mid
            else:
                if z_mid > target:
                    low = mid
                else:
                    high = mid
            
            if high - low < tol:
                return mid
        
        return (low + high) / 2
    
    def _show_result(self, result, mode: str, solved: tuple = None):
        """更新结果显示
        
        参数:
            result: 计算结果对象
            mode: 结构模式 (coaxial/microstrip/cpwg)
            solved: 反算的参数元组 (参数名, 参数值), None表示正向计算
        """
        if solved:
            param_name, param_value = solved
            self._impedance_label.setText(f"{param_name} = {param_value:.4f} mm")
            self._quality_label.setText(f"✅ 验证阻抗: {result.impedance:.2f} Ω")
            self._quality_label.setStyleSheet("QLabel { font-size: 14px; color: #38A169; }")
        else:
            self._impedance_label.setText(f"{result.impedance:.2f} Ω")
            # 阻抗评估
            if 45 <= result.impedance <= 55:
                self._quality_label.setText("✅ 接近 50Ω 标准阻抗")
                self._quality_label.setStyleSheet("QLabel { font-size: 14px; color: #38A169; }")
            elif 70 <= result.impedance <= 80:
                self._quality_label.setText("✅ 接近 75Ω 标准阻抗")
                self._quality_label.setStyleSheet("QLabel { font-size: 14px; color: #38A169; }")
            else:
                self._quality_label.setText("ℹ️ 非标准阻抗值")
                self._quality_label.setStyleSheet("QLabel { font-size: 14px; color: #4A5568; }")
        
        # 更新详细参数
        if mode == "coaxial":
            self._detail_labels["effective_er"].setText(f"{result.dielectric_constant:.2f}")
            self._detail_labels["velocity"].setText(f"{result.velocity_factor:.3f} c")
            self._detail_labels["capacitance"].setText(f"{result.capacitance_per_m:.2f} pF/m")
            self._detail_labels["ratio"].setText(f"D/d = {result.outer_diameter/result.inner_diameter:.2f}")
        elif mode == "microstrip":
            self._detail_labels["effective_er"].setText(f"{result.effective_er:.3f}")
            self._detail_labels["velocity"].setText(f"{result.velocity_factor:.3f} c")
            self._detail_labels["capacitance"].setText(f"{result.capacitance_per_m:.2f} pF/m")
            self._detail_labels["ratio"].setText(f"W/H = {result.w_h_ratio:.2f}")
        elif mode == "cpwg":
            self._detail_labels["effective_er"].setText(f"{result.effective_er:.3f}")
            self._detail_labels["velocity"].setText(f"{result.velocity_factor:.3f} c")
            self._detail_labels["capacitance"].setText(f"{result.capacitance_per_m:.2f} pF/m")
            self._detail_labels["ratio"].setText(f"W/(W+2S) = {result.center_width/(result.center_width + 2*result.gap_width):.2f}")
    
    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        return """
        <b>📡 什么是特性阻抗？</b><br><br>
        
        特性阻抗 Z₀ 是传输线的固有属性，描述信号在传输线中传播时的电压/电流比。<br><br>
        
        <b>🎯 为什么重要？</b><br>
        • 阻抗匹配：源/负载阻抗与传输线阻抗不匹配会导致信号反射<br>
        • 50Ω 和 75Ω 是常用标准阻抗<br>
        • 高频信号对阻抗匹配更敏感<br><br>
        
        <b>💡 常见应用：</b><br>
        • 50Ω：射频系统、仪器设备<br>
        • 75Ω：视频信号、有线电视
        """
    
    def get_math_model_content(self) -> Optional[str]:
        """数学模型 - 精确计算公式 (v1.2 更新)"""
        return """
        <b>📐 阻抗计算公式 (v1.2)</b><br><br>
        
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ 同轴线</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 13px;">
        Z₀ = (60 / √εᵣ) × ln(D/d)
        </span><br>
        • D = 外导体内径, d = 内导体外径<br>
        • 速度因子: v_f = 1 / √εᵣ
        </div>
        
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>2️⃣ 微带线 (Hammerstad-Jensen 1980)</b><br>
        <span style="font-family: serif; font-size: 12px;">
        窄线 (u≤1): Z₀ = (60/√εₑ) × ln(8/u + u/4)<br>
        宽线 (u>1): Z₀ = (120π/√εₑ) / (u + 1.393 + 0.667×ln(u + 1.444))
        </span><br><br>
        <b>有效介电常数:</b><br>
        <span style="font-family: serif; font-size: 12px;">
        εₑ = (εᵣ+1)/2 + (εᵣ-1)/2 × F₁ − (εᵣ-1)×T/(4.6H)
        </span><br>
        • u = W_eff/H (有效宽厚比)<br>
        • F₁ = (1+12/u)⁻⁰·⁵ + 0.04(1−u)² 当u≤1<br>
        • F₁ = (1+12/u)⁻⁰·⁵ 当u>1<br>
        <b>Wheeler 等效宽度:</b><br>
        <span style="font-family: serif; font-size: 11px;">
        W_eff = W + (T/π)×ln(4e/√((T/H)²+(T/(πW+1.1πT))²))
        </span>
        </div>
        
        <div style="background-color: #FEF3C7; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>3️⃣ CBCPW (Ghione-Naldi 1984 + Gevorgian 1995)</b><br>
        <span style="font-family: serif; font-size: 13px;">
        Z₀ = 60π / [√εₑ × (q₁ + q₃)]
        </span><br><br>
        <b>电容比法有效介电常数:</b><br>
        <span style="font-family: serif; font-size: 12px;">
        εₑ = (q₁ + εᵣ×q₃) / (q₁ + q₃)
        </span><br>
        • q₁ = K(k)/K(k') — 空气层贡献<br>
        • q₃ = K(k₃)/K(k₃') — 接地层贡献<br>
        • k = W/(W+2S), k₃ = tanh(πW/4H)/tanh(π(W+2S)/4H)<br>
        • K(x) = 完全椭圆积分第一类<br>
        <b>Gevorgian 厚度修正:</b><br>
        <span style="font-family: serif; font-size: 11px;">
        Δ = (1.25T/π)×(1+ln(2S/T))<br>
        W_eff = W + Δ, S_eff = S − Δ
        </span>
        </div>
        """
    
    def get_engineering_content(self) -> Optional[str]:
        return """
        <b>✅ 50Ω 微带线参考尺寸 (FR4 εᵣ=4.3):</b><br>
        <table style="margin: 8px 0;">
        <tr><td>H = 0.4mm</td><td>→ W ≈ 0.76mm</td></tr>
        <tr><td>H = 0.6mm</td><td>→ W ≈ 1.14mm</td></tr>
        <tr><td>H = 0.8mm</td><td>→ W ≈ 1.52mm</td></tr>
        <tr><td>H = 1.0mm</td><td>→ W ≈ 1.90mm</td></tr>
        </table>
        
        <b>⚠️ 设计注意事项:</b><br>
        • 铜箔厚度会略微影响阻抗（1oz ≈ 35μm）<br>
        • 高频时需考虑介质损耗（Df）<br>
        • CPWG 比微带线抗干扰性更好
        """
    
    def get_boundary_content(self) -> Optional[str]:
        """公式适用范围 (v1.2 更新)"""
        return """
        <b>⚠️ 公式适用范围:</b><br><br>
        
        <b>微带线 (Hammerstad-Jensen 1980):</b><br>
        • 适用: 0.05 ≤ W/H ≤ 20<br>
        • 频率 < 30 GHz (准静态近似)<br>
        • 含铜箔厚度修正 (Wheeler + Schneider)<br>
        • 与 SI9000 吻合度: ~0.1%<br><br>
        
        <b>CBCPW (Ghione-Naldi 1984):</b><br>
        • 适用: 底部有接地层的共面波导<br>
        • W/(W+2S) 在 0.2~0.8 范围精度最高<br>
        • 含 Gevorgian 铜箔厚度修正<br>
        • 使用 tanh 接地层修正 (非 sinh)<br>
        • 与 SI9000 吻合度: ~2%<br><br>
        
        <b>精度说明:</b><br>
        v1.2 公式经过与 SI9000 对照验证。<br>
        如需更高精度，建议使用全波仿真 (HFSS 等)。
        """
    
    def get_history_content(self) -> Optional[str]:
        """发现历史 - 趣味故事"""
        return """
        <b>📜 传输线理论简史</b><br><br>
        
        <div style="background-color: #F5F0FF; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🔬 1855 — 开尔文困境</b><br>
        威廉·汤姆森 (后来的开尔文勋爵) 在分析跨大西洋海底电报线缆时，
        首次建立了传输线的数学模型。当时的电报信号穿越 3000 多公里的海底，
        到达时已严重畸变 — 他的分析揭示了阻抗匹配的重要性。
        </div>
        
        <div style="background-color: #FFF5F0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>⚡ 1886 — 赫兹的验证</b><br>
        赫兹用一对平行导线传输电磁波，实验验证了麦克斯韦方程。
        他观察到驻波现象，这正是阻抗不匹配的直接表现。
        这个实验可以说是最早的传输线阻抗测量。
        </div>
        
        <div style="background-color: #F0F8FF; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>📡 为什么是 50Ω？</b><br>
        同轴线的功率容量在 30Ω 时最大，而衰减在 77Ω 时最小。
        50Ω 是两者的几何平均值 (√30×77 ≈ 48Ω)，
        成为射频系统的"黄金标准"。75Ω 则因为最小衰减，
        成为有线电视/视频的标准。
        </div>
        
        <div style="background-color: #FFFFF0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🏗️ 微带线革命 (1950s)</b><br>
        微带线由 ITT 实验室于 1950 年代发明，彻底改变了微波电路设计。
        之前的波导和同轴结构笨重且昂贵，微带线使得用 PCB 就能制作
        微波电路成为可能。Hammerstad 和 Jensen 在 1980 年的精确公式
        至今仍是 SI9000 等商业工具的理论基础。
        </div>
        
        <div style="background-color: #F0FFF0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🌊 共面波导 (1969)</b><br>
        C.P. Wen 在 1969 年首次提出共面波导结构 (CPW)。
        因为信号线和接地在同一面，大大简化了 MMIC (单片微波集成电路)
        的制造工艺。Ghione 和 Naldi 在 1984 年给出的精确解析公式
        使用完全椭圆积分，至今仍是工程计算的标准方法。
        </div>
        """
