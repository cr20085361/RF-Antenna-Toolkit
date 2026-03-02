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
        
        # 调用父类初始化
        super().__init__(parent)
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 频率输入 ====================
        freq_group = QGroupBox("频率输入")
        freq_layout = QGridLayout(freq_group)
        freq_layout.setSpacing(12)
        
        # 频率值
        freq_label = QLabel("频率:")
        freq_label.setObjectName("InputLabel")
        freq_layout.addWidget(freq_label, 0, 0)
        
        self._freq_input = QLineEdit()
        self._freq_input.setPlaceholderText("请输入频率")
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
        medium_group = QGroupBox("介质设置")
        medium_layout = QGridLayout(medium_group)
        medium_layout.setSpacing(12)
        
        # 材料选择
        material_label = QLabel("材料:")
        material_label.setObjectName("InputLabel")
        medium_layout.addWidget(material_label, 0, 0)
        
        self._material_combo = QComboBox()
        self._material_combo.addItems(list(DIELECTRIC_CONSTANTS.keys()))
        self._material_combo.addItem("自定义")
        self._material_combo.currentTextChanged.connect(self._on_material_changed)
        medium_layout.addWidget(self._material_combo, 0, 1, 1, 2)
        
        # 介电常数
        epsilon_label = QLabel("介电常数 εr:")
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
        calc_button = QPushButton("📊 计算")
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
            "自由空间波长 λ₀",
            "在真空/空气中的电磁波波长"
        )
        results_grid.addWidget(free_space_result, 0, 0)
        
        # 介质波长
        medium_result = self._create_result_card(
            "medium",
            "介质波长 λ",
            "在所选介质中的有效波长"
        )
        results_grid.addWidget(medium_result, 0, 1)
        
        # 四分之一波长
        quarter_result = self._create_result_card(
            "quarter",
            "四分之一波长 λ/4",
            "常用于阻抗匹配段长度"
        )
        results_grid.addWidget(quarter_result, 1, 0)
        
        # 二分之一波长
        half_result = self._create_result_card(
            "half",
            "二分之一波长 λ/2",
            "常用于偶极子天线长度"
        )
        results_grid.addWidget(half_result, 1, 1)
        
        layout.addLayout(results_grid)
        layout.addStretch()
        
        return panel
    
    def _create_result_card(
        self,
        key: str,
        title: str,
        description: str
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
        
        return card
    
    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        """直观理解 - 物理本质"""
        return """
        <b>🌊 什么是电磁波波长？</b><br><br>
        
        想象往平静的湖面扔一块石头，水波会向外扩散。<b>波长</b>就是<b>相邻两个波峰之间的距离</b>。<br><br>
        
        电磁波也一样：当电场和磁场以光速振荡传播时，波长就是振荡一个完整周期后电磁波传播的距离。<br><br>
        
        <b>🔑 关键物理本质：</b><br>
        • 频率越高 → 振荡越快 → 波长越短<br>
        • 介质中光速变慢 → 同样频率下波长变短<br>
        • 波长决定了天线的物理尺寸（天线长度通常是波长的分数）
        """
    
    def get_math_model_content(self) -> Optional[str]:
        """数学模型 - 精确公式"""
        return """
        <b>📐 基本公式</b><br><br>
        
        <b>自由空间波长：</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 16px;">
        λ₀ = c / f
        </span><br>
        其中：c = 299,792,458 m/s（真空光速），f = 频率 (Hz)<br><br>
        
        <b>介质中波长：</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 16px;">
        λ = λ₀ / √εᵣ = c / (f · √εᵣ)
        </span><br>
        其中：εᵣ = 介质相对介电常数<br><br>
        
        <b>📊 常用分数波长：</b><br>
        • λ/4 = 四分之一波长（阻抗变换、匹配网络）<br>
        • λ/2 = 二分之一波长（偶极子天线、谐振结构）
        """
    
    def get_engineering_content(self) -> Optional[str]:
        """工程边界 - 适用范围与避坑"""
        return """
        <b>✅ 适用范围：</b><br>
        • 远场区电磁波分析（距离 > 2D²/λ）<br>
        • 均匀介质中的传播计算<br>
        • 平面波假设成立的场景<br><br>
        
        <b>⚠️ 常见错误（避坑指南）：</b><br><br>
        
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 错误1：忽略介质色散
        </span><br>
        高频时εᵣ会随频率变化，不能用静态值<br><br>
        
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 错误2：混淆自由空间波长和介质波长
        </span><br>
        PCB微带线设计必须用介质波长！<br><br>
        
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 错误3：忽略有效介电常数
        </span><br>
        微带线的有效εᵣ ≠ 基板εᵣ，需用经验公式修正<br><br>
        
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px; color: #276749;">
        💡 建议：实际设计时预留5-10%调试余量
        </span>
        """
    
    def get_history_content(self) -> Optional[str]:
        """发现历史 - 趣味故事"""
        return """
        <b>📜 电磁波的发现之旅</b><br><br>
        
        <b>1865年</b> - 詹姆斯·克拉克·<b>麦克斯韦</b>通过数学推导预言：电磁波以光速传播，光也是电磁波的一种。<br><br>
        
        <b>1887年</b> - 海因里希·<b>赫兹</b>首次用实验证实了电磁波的存在，成功产生并检测到了无线电波。为纪念他，频率单位被命名为"赫兹(Hz)"。<br><br>
        
        <i>💭 有趣的是，赫兹当时认为这个发现"没有任何实际用途"。仅仅几年后，马可尼就用它实现了跨大西洋无线通信！</i>
        """
    
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
                self._result_labels[key].setText("错误")
    
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
        if material == "自定义":
            self._epsilon_input.setEnabled(True)
        else:
            self._epsilon_input.setEnabled(False)
            epsilon = DIELECTRIC_CONSTANTS.get(material, 1.0)
            self._epsilon_input.setText(str(epsilon))
    
    def _on_input_changed(self):
        """输入变化时自动计算"""
        # 可以选择是否启用实时计算
        pass
