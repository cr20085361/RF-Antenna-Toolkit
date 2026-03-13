# -*- coding: utf-8 -*-
"""
射频天线工具集 - 波长频率计算工具
RF Antenna Toolkit - Wavelength/Frequency Calculator Tool

版本: v1.0.0
功能: 提供频率与波长之间的转换计算界面
"""

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

from ui.base.tool_base import ToolBase
from core.antenna.wavelength import WavelengthCalculator, WavelengthResult
from core.i18n import tr
from core.constants import DIELECTRIC_CONSTANTS, GHZ_TO_HZ, MHZ_TO_HZ


class WavelengthTool(ToolBase):
    """
    波长频率计算工具
    
    功能:
    - 输入频率，计算自由空间波长和介质中波长
    - 支持选择不同介质材料
    - 支持自定义介电常数
    - 显示λ/4和λ/2波长
    """
    
    # 工具元信息
    tool_name = "波长计算器"
    tool_icon = "📏"
    tool_category = "antenna"
    tool_description = "根据频率计算自由空间波长和介质中波长，支持常用介质材料选择"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化波长计算工具"""
        # 计算器实例
        self._calculator = WavelengthCalculator()
        
        # 结果显示控件引用
        self._result_labels: Dict[str, QLabel] = {}
        self._static_labels = []
        
        # 调用父类初始化
        super().__init__(parent)
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 频率输入 ====================
        freq_group = QGroupBox(tr("wavelength.group_freq"))
        self._static_labels.append((freq_group, "wavelength", "group_freq", "title"))
        freq_layout = QGridLayout(freq_group)
        freq_layout.setSpacing(12)
        
        # 频率值
        freq_label = QLabel(tr("wavelength.lbl_freq"))
        self._static_labels.append((freq_label, "wavelength", "lbl_freq", "text"))
        freq_label.setObjectName("InputLabel")
        freq_layout.addWidget(freq_label, 0, 0)
        
        self._freq_input = QLineEdit()
        self._freq_input.setPlaceholderText(tr("wavelength.place_freq"))
        self._static_labels.append((self._freq_input, "wavelength", "place_freq", "placeholder"))
        self._freq_input.setValidator(QDoubleValidator(0.001, 1e12, 6))
        self._freq_input.setText("2.4")
        self._freq_input.textChanged.connect(self._on_input_changed)
        freq_layout.addWidget(self._freq_input, 0, 1)
        
        # 频率单位
        self._freq_unit = QComboBox()
        self._freq_unit.addItems(["GHz", "MHz", "kHz", "Hz"])
        self._freq_unit.setCurrentText("GHz")
        self._freq_unit.currentTextChanged.connect(self._on_input_changed)
        freq_layout.addWidget(self._freq_unit, 0, 2)
        
        layout.addWidget(freq_group)
        
        # ==================== 介质选择 ====================
        medium_group = QGroupBox(tr("wavelength.group_medium"))
        self._static_labels.append((medium_group, "wavelength", "group_medium", "title"))
        medium_layout = QGridLayout(medium_group)
        medium_layout.setSpacing(12)
        
        # 材料选择
        material_label = QLabel(tr("wavelength.lbl_material"))
        self._static_labels.append((material_label, "wavelength", "lbl_material", "text"))
        material_label.setObjectName("InputLabel")
        medium_layout.addWidget(material_label, 0, 0)
        
        self._material_combo = QComboBox()
        self._material_combo.addItems(list(DIELECTRIC_CONSTANTS.keys()))
        self._material_combo.addItem(tr("wavelength.custom_material"))
        # combobox update in retranslate_ui if strictly needed, here we simplify
        self._material_combo.currentTextChanged.connect(self._on_material_changed)
        medium_layout.addWidget(self._material_combo, 0, 1, 1, 2)
        
        # 介电常数
        epsilon_label = QLabel(tr("wavelength.lbl_epsilon"))
        self._static_labels.append((epsilon_label, "wavelength", "lbl_epsilon", "text"))
        epsilon_label.setObjectName("InputLabel")
        medium_layout.addWidget(epsilon_label, 1, 0)
        
        self._epsilon_input = QLineEdit()
        self._epsilon_input.setValidator(QDoubleValidator(0.1, 1000, 4))
        self._epsilon_input.setText("1.0")
        self._epsilon_input.setEnabled(False)  # 默认禁用，选择自定义时启用
        self._epsilon_input.textChanged.connect(self._on_input_changed)
        medium_layout.addWidget(self._epsilon_input, 1, 1, 1, 2)
        
        layout.addWidget(medium_group)
        
        # ==================== 计算按钮 ====================
        calc_button = QPushButton(tr("wavelength.btn_calc"))
        self._static_labels.append((calc_button, "wavelength", "btn_calc", "text"))
        calc_button.setObjectName("PrimaryButton")
        calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_button.clicked.connect(self._do_calculate)
        layout.addWidget(calc_button)
        
        layout.addStretch()
        
        return panel
    
    def create_result_panel(self) -> QWidget:
        """创建结果面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 结果网格
        results_grid = QGridLayout()
        results_grid.setSpacing(12)
        
        # 自由空间波长
        free_space_result = self._create_result_card(
            "free_space",
            tr("wavelength.card_free_space"),
            tr("wavelength.desc_free_space"),
            "card_free_space",
            "desc_free_space"
        )
        results_grid.addWidget(free_space_result, 0, 0)
        
        # 介质波长
        medium_result = self._create_result_card(
            "medium",
            tr("wavelength.card_medium"),
            tr("wavelength.desc_medium"),
            "card_medium",
            "desc_medium"
        )
        results_grid.addWidget(medium_result, 0, 1)
        
        # 四分之一波长
        quarter_result = self._create_result_card(
            "quarter",
            tr("wavelength.card_quarter"),
            tr("wavelength.desc_quarter"),
            "card_quarter",
            "desc_quarter"
        )
        results_grid.addWidget(quarter_result, 1, 0)
        
        # 二分之一波长
        half_result = self._create_result_card(
            "half",
            tr("wavelength.card_half"),
            tr("wavelength.desc_half"),
            "card_half",
            "desc_half"
        )
        results_grid.addWidget(half_result, 1, 1)
        
        layout.addLayout(results_grid)
        layout.addStretch()
        
        return panel
    
    def _create_result_card(
        self,
        key: str,
        title: str,
        description: str,
        title_key: str = "",
        desc_key: str = ""
    ) -> QWidget:
        """创建结果卡片"""
        card = QWidget()
        card.setObjectName("ResultPanel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("ResultTitle")
        layout.addWidget(title_label)
        if title_key:
            self._static_labels.append((title_label, "wavelength", title_key, "text"))
        
        # 值
        value_label = QLabel("--")
        value_label.setObjectName("ResultValue")
        self._result_labels[key] = value_label
        layout.addWidget(value_label)
        
        # 单位
        unit_label = QLabel("mm")
        unit_label.setObjectName("ResultUnit")
        self._result_labels[f"{key}_unit"] = unit_label
        layout.addWidget(unit_label)
        
        # 描述
        desc_label = QLabel(description)
        desc_label.setObjectName("ResultDescription")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        if desc_key:
            self._static_labels.append((desc_label, "wavelength", desc_key, "text"))
        
        return card
    
    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        return tr("wavelength.intuition_content")
    
    def get_math_model_content(self) -> Optional[str]:
        return tr("wavelength.math_content")
    
    def get_engineering_content(self) -> Optional[str]:
        return tr("wavelength.engineering_content")
    
    def get_history_content(self) -> Optional[str]:
        return tr("wavelength.history_content")
    
    def calculate(self) -> Dict[str, Any]:
        """执行计算"""
        try:
            # 获取频率
            freq_value = float(self._freq_input.text() or "0")
            freq_unit = self._freq_unit.currentText()
            
            # 转换为Hz
            if freq_unit == "GHz":
                freq_hz = freq_value * 1e9
            elif freq_unit == "MHz":
                freq_hz = freq_value * 1e6
            elif freq_unit == "kHz":
                freq_hz = freq_value * 1e3
            else:
                freq_hz = freq_value
            
            # 获取介电常数
            epsilon_r = float(self._epsilon_input.text() or "1")
            material = self._material_combo.currentText()
            
            # 计算
            result = self._calculator.calculate_from_frequency(
                freq_hz, epsilon_r, material
            )
            
            return {
                "success": True,
                "result": result
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()
        
        if calc_result["success"]:
            result: WavelengthResult = calc_result["result"]
            
            # 更新结果显示
            self._update_result_display(
                "free_space",
                result.wavelength_free_space_mm,
                "mm"
            )
            self._update_result_display(
                "medium",
                result.wavelength_medium_mm,
                "mm"
            )
            self._update_result_display(
                "quarter",
                result.quarter_wave_mm,
                "mm"
            )
            self._update_result_display(
                "half",
                result.half_wave_mm,
                "mm"
            )
        else:
            # 显示错误
            for key in ["free_space", "medium", "quarter", "half"]:
                self._result_labels[key].setText(tr("wavelength.lbl_error"))
    
    def _update_result_display(self, key: str, value: float, unit: str):
        """更新结果显示"""
        # 格式化数值
        if value >= 1000:
            display_value = f"{value/1000:.4f}"
            display_unit = "m"
        elif value >= 1:
            display_value = f"{value:.4f}"
            display_unit = "mm"
        else:
            display_value = f"{value*1000:.4f}"
            display_unit = "μm"
        
        self._result_labels[key].setText(display_value)
        self._result_labels[f"{key}_unit"].setText(display_unit)
    
    def _on_material_changed(self, material: str):
        """材料选择变化"""
        if material == tr("wavelength.custom_material") or material == "自定义" or material == "Custom":
            self._epsilon_input.setEnabled(True)
        else:
            self._epsilon_input.setEnabled(False)
            epsilon = DIELECTRIC_CONSTANTS.get(material, 1.0)
            self._epsilon_input.setText(str(epsilon))
    
    def _on_input_changed(self):
        """输入变化时自动计算"""
        # 可以选择是否启用实时计算
        pass

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
                
        # Custom material option update in combobox
        idx = self._material_combo.findData(None)
        if idx < 0:
            idx = self._material_combo.count() - 1
        current_idx = self._material_combo.currentIndex()
        self._material_combo.setItemText(idx, tr("wavelength.custom_material"))
        
        # Default error updating requires re-calculation or simply let it be
