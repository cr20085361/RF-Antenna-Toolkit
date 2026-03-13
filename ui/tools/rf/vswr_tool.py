# -*- coding: utf-8 -*-
"""
射频天线工具集 - 驻波(VSWR)计算工具
RF Antenna Toolkit - VSWR Calculator Tool

版本: v1.0.0
功能: 提供驻波比计算界面，显示反射系数、回波损耗等指标
"""

from typing import Dict, Any, Optional
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QPainter, QColor, QPen, QBrush, QFont

from core.i18n import tr
from ui.base.tool_base import ToolBase
from core.rf.vswr import VSWRCalculator, VSWRResult


class PowerMeter(QWidget):
    """功率分布可视化仪表盘
    
    v1.1: 支持显示实际功率值 (W)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.transmitted_ratio = 1.0
        self.reflected_ratio = 0.0
        self.input_power_w = 0.0  # 输入功率 (W)
        self.show_power_values = False  # 是否显示实际功率值
        self.setMinimumSize(200, 140)
        self.setMaximumHeight(170)
    
    def set_values(self, transmitted: float, reflected: float, input_power_w: float = 0.0):
        """设置传输和反射功率比"""
        self.transmitted_ratio = transmitted
        self.reflected_ratio = reflected
        self.input_power_w = input_power_w
        self.show_power_values = input_power_w > 0
        self.update()
    
    def paintEvent(self, event):
        """绘制功率分布图"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制区域
        width = self.width() - 40
        height = 40
        x = 20
        y = 50
        
        # 背景框
        painter.setPen(QPen(QColor("#E2E8F0"), 1))
        painter.setBrush(QBrush(QColor("#F5F6F7")))
        painter.drawRoundedRect(x, y, width, height, 8, 8)
        
        # 传输功率（绿色）
        transmitted_width = int(width * self.transmitted_ratio)
        if transmitted_width > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#48BB78")))
            painter.drawRoundedRect(x, y, transmitted_width, height, 8, 8)
        
        # 反射功率（红色，从右侧开始）
        reflected_width = int(width * self.reflected_ratio)
        if reflected_width > 0:
            painter.setBrush(QBrush(QColor("#FC8181")))
            painter.drawRoundedRect(x + width - reflected_width, y, reflected_width, height, 8, 8)
        
        # 标签
        painter.setPen(QPen(QColor("#1A1A1A")))
        font = QFont("Microsoft YaHei UI", 10)
        painter.setFont(font)
        
        # 标题
        title_text = "功率分布"
        if self.show_power_values:
            title_text += f" (输入: {self._format_power(self.input_power_w)})"
        painter.drawText(x, y - 10, title_text)
        
        # 计算实际功率
        transmitted_power = self.input_power_w * self.transmitted_ratio
        reflected_power = self.input_power_w * self.reflected_ratio
        
        # 传输功率百分比/数值
        painter.setPen(QPen(QColor("#276749")))
        if self.show_power_values:
            trans_text = f"✓ 传输: {self.transmitted_ratio*100:.1f}% ({self._format_power(transmitted_power)})"
        else:
            trans_text = f"✓ 传输: {self.transmitted_ratio*100:.1f}%"
        painter.drawText(x + 5, y + height + 20, trans_text)
        
        # 反射功率百分比/数值
        painter.setPen(QPen(QColor("#C53030")))
        if self.show_power_values:
            refl_text = f"✗ 反射: {self.reflected_ratio*100:.1f}% ({self._format_power(reflected_power)})"
        else:
            refl_text = f"✗ 反射: {self.reflected_ratio*100:.1f}%"
        # 计算文本宽度以右对齐
        painter.drawText(x + 5, y + height + 40, refl_text)
    
    def _format_power(self, power_w: float) -> str:
        """格式化功率显示"""
        if power_w >= 1000:
            return f"{power_w/1000:.2f} kW"
        elif power_w >= 1:
            return f"{power_w:.2f} W"
        elif power_w >= 0.001:
            return f"{power_w*1000:.2f} mW"
        else:
            return f"{power_w*1e6:.2f} μW"


class VSWRTool(ToolBase):
    """
    驻波比(VSWR)计算工具
    
    功能:
    - 输入VSWR/反射系数/回波损耗计算其他参数
    - 可视化显示功率分布
    - 匹配质量评估
    """
    
    # 工具元信息
    tool_name = "驻波计算器"
    tool_icon = "📊"
    tool_category = "rf"
    tool_description = "根据驻波比(VSWR)计算反射系数、回波损耗、失配损耗等指标"
    i18n_title_key = "vswr.tool_name"
    i18n_desc_key = "vswr.tool_desc"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化驻波计算工具"""
        # 计算器实例
        self._calculator = VSWRCalculator()
        
        # 结果显示控件引用
        self._result_labels: Dict[str, QLabel] = {}
        
        # 功率仪表盘
        self._power_meter: Optional[PowerMeter] = None
        
        # 调用父类初始化
        super().__init__(parent)
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 输入方式选择 ====================
        input_group = QGroupBox("输入参数")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(12)
        
        # 输入类型选择
        self._input_type_group = QButtonGroup(self)
        
        # VSWR输入
        vswr_radio = QRadioButton("驻波比 (VSWR)")
        vswr_radio.setChecked(True)
        self._input_type_group.addButton(vswr_radio, 0)
        input_layout.addWidget(vswr_radio)
        
        vswr_input_layout = QHBoxLayout()
        self._vswr_input = QLineEdit()
        self._vswr_input.setPlaceholderText("≥ 1.0")
        self._vswr_input.setValidator(QDoubleValidator(1.0, 1000, 4))
        self._vswr_input.setText("1.5")
        vswr_input_layout.addWidget(self._vswr_input)
        vswr_input_layout.addWidget(QLabel(": 1"))
        vswr_input_layout.addStretch()
        input_layout.addLayout(vswr_input_layout)
        
        # 反射系数输入
        gamma_radio = QRadioButton("反射系数 |Γ|")
        self._input_type_group.addButton(gamma_radio, 1)
        input_layout.addWidget(gamma_radio)
        
        gamma_input_layout = QHBoxLayout()
        self._gamma_input = QLineEdit()
        self._gamma_input.setPlaceholderText("0 ~ 1")
        self._gamma_input.setValidator(QDoubleValidator(0, 0.999, 4))
        self._gamma_input.setText("0.2")
        self._gamma_input.setEnabled(False)
        gamma_input_layout.addWidget(self._gamma_input)
        gamma_input_layout.addStretch()
        input_layout.addLayout(gamma_input_layout)
        
        # 回波损耗输入
        rl_radio = QRadioButton("回波损耗 (Return Loss)")
        self._input_type_group.addButton(rl_radio, 2)
        input_layout.addWidget(rl_radio)
        
        rl_input_layout = QHBoxLayout()
        self._rl_input = QLineEdit()
        self._rl_input.setPlaceholderText("> 0")
        self._rl_input.setValidator(QDoubleValidator(0.001, 100, 4))
        self._rl_input.setText("14")
        self._rl_input.setEnabled(False)
        rl_input_layout.addWidget(self._rl_input)
        rl_input_layout.addWidget(QLabel("dB"))
        rl_input_layout.addStretch()
        input_layout.addLayout(rl_input_layout)
        
        # 切换输入类型时启用/禁用对应输入框
        self._input_type_group.buttonClicked.connect(self._on_input_type_changed)
        
        layout.addWidget(input_group)
        
        # ==================== 输入功率设置 (大功率场景) ====================
        power_group = QGroupBox("输入功率 (可选)")
        power_layout = QVBoxLayout(power_group)
        power_layout.setSpacing(8)
        
        power_desc = QLabel("输入发射功率，计算失配导致的实际功率损失")
        power_desc.setObjectName("ResultDescription")
        power_desc.setWordWrap(True)
        power_layout.addWidget(power_desc)
        
        power_input_layout = QHBoxLayout()
        
        self._power_input = QLineEdit()
        self._power_input.setPlaceholderText("例如: 100")
        self._power_input.setValidator(QDoubleValidator(0, 1e9, 4))
        self._power_input.setText("")
        power_input_layout.addWidget(self._power_input)
        
        # 功率单位选择
        self._power_unit = QComboBox()
        self._power_unit.addItems(["W", "kW", "mW", "dBm"])
        self._power_unit.setCurrentText("W")
        power_input_layout.addWidget(self._power_unit)
        
        power_input_layout.addStretch()
        power_layout.addLayout(power_input_layout)
        
        # 特性阻抗输入
        z0_layout = QHBoxLayout()
        z0_layout.addWidget(QLabel("特性阻抗 Z₀:"))
        self._z0_input = QLineEdit()
        self._z0_input.setValidator(QDoubleValidator(1, 1000, 2))
        self._z0_input.setText("50")
        self._z0_input.setMaximumWidth(80)
        z0_layout.addWidget(self._z0_input)
        z0_layout.addWidget(QLabel("Ω"))
        z0_layout.addStretch()
        power_layout.addLayout(z0_layout)
        
        layout.addWidget(power_group)
        
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
        layout.setSpacing(16)
        
        # 错误提示区域
        self._error_label = QLabel("")
        self._error_label.setObjectName("ErrorLabel")
        self._error_label.setWordWrap(True)
        self._error_label.hide()  # 默认隐藏
        layout.addWidget(self._error_label)
        
        # 匹配质量评估
        quality_card = QWidget()
        quality_card.setObjectName("ResultPanel")
        quality_layout = QVBoxLayout(quality_card)
        
        quality_title = QLabel("匹配质量评估")
        quality_title.setObjectName("ResultTitle")
        quality_layout.addWidget(quality_title)
        
        self._quality_label = QLabel("--")
        self._quality_label.setObjectName("ResultValue")
        self._result_labels["quality"] = self._quality_label
        quality_layout.addWidget(self._quality_label)
        
        layout.addWidget(quality_card)
        
        # 结果网格
        results_grid = QGridLayout()
        results_grid.setSpacing(12)
        
        # VSWR
        vswr_card = self._create_result_card("vswr", "驻波比 VSWR", ": 1")
        results_grid.addWidget(vswr_card, 0, 0)
        
        # 反射系数
        gamma_card = self._create_result_card("gamma", "反射系数 |Γ|", "")
        results_grid.addWidget(gamma_card, 0, 1)
        
        # 回波损耗
        rl_card = self._create_result_card("return_loss", "回波损耗", "dB")
        results_grid.addWidget(rl_card, 0, 2)
        
        # 失配损耗
        ml_card = self._create_result_card("mismatch_loss", "失配损耗", "dB")
        results_grid.addWidget(ml_card, 1, 0)
        
        # 负载阻抗 (估算, 相位=0时)
        zl_card = self._create_result_card("load_z", "负载阻抗 Z_L", "Ω")
        results_grid.addWidget(zl_card, 1, 1)
        
        layout.addLayout(results_grid)
        
        # 最大电压/电流区 (大功率场景)
        voltage_card = QWidget()
        voltage_card.setObjectName("ResultPanel")
        voltage_layout = QVBoxLayout(voltage_card)
        
        voltage_title = QLabel("⚡ 传输线电压/电流")
        voltage_title.setObjectName("ResultTitle")
        voltage_layout.addWidget(voltage_title)
        
        voltage_grid = QGridLayout()
        voltage_grid.setSpacing(8)
        
        voltage_grid.addWidget(QLabel("最大电压 V_max:"), 0, 0)
        self._vmax_label = QLabel("--")
        self._vmax_label.setStyleSheet("color: #C53030; font-weight: bold;")
        voltage_grid.addWidget(self._vmax_label, 0, 1)
        
        voltage_grid.addWidget(QLabel("最大电流 I_max:"), 0, 2)
        self._imax_label = QLabel("--")
        self._imax_label.setStyleSheet("color: #C53030; font-weight: bold;")
        voltage_grid.addWidget(self._imax_label, 0, 3)
        
        voltage_layout.addLayout(voltage_grid)
        layout.addWidget(voltage_card)
        
        # 功率损失结果区 (当输入功率时显示)
        power_loss_card = QWidget()
        power_loss_card.setObjectName("ResultPanel")
        power_loss_layout = QVBoxLayout(power_loss_card)
        
        power_loss_title = QLabel("⚡ 功率损失详情")
        power_loss_title.setObjectName("ResultTitle")
        power_loss_layout.addWidget(power_loss_title)
        
        # 功率损失结果网格
        power_grid = QGridLayout()
        power_grid.setSpacing(8)
        
        # 反射功率
        power_grid.addWidget(QLabel("反射功率:"), 0, 0)
        self._reflected_power_label = QLabel("--")
        self._reflected_power_label.setStyleSheet("color: #C53030; font-weight: bold;")
        power_grid.addWidget(self._reflected_power_label, 0, 1)
        
        # 传输功率
        power_grid.addWidget(QLabel("传输功率:"), 1, 0)
        self._transmitted_power_label = QLabel("--")
        self._transmitted_power_label.setStyleSheet("color: #276749; font-weight: bold;")
        power_grid.addWidget(self._transmitted_power_label, 1, 1)
        
        # 给PA的补偿功率建议
        power_grid.addWidget(QLabel("建议补偿:"), 2, 0)
        self._compensation_label = QLabel("--")
        self._compensation_label.setStyleSheet("color: #2C7BE5; font-weight: bold;")
        power_grid.addWidget(self._compensation_label, 2, 1)
        
        power_loss_layout.addLayout(power_grid)
        layout.addWidget(power_loss_card)
        
        # 功率分布可视化
        self._power_meter = PowerMeter()
        layout.addWidget(self._power_meter)
        
        layout.addStretch()
        
        return panel
    
    def _create_result_card(self, key: str, title: str, unit: str) -> QWidget:
        """创建结果卡片"""
        card = QWidget()
        card.setObjectName("ResultPanel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("ResultTitle")
        layout.addWidget(title_label)
        
        # 值和单位
        value_row = QHBoxLayout()
        value_label = QLabel("--")
        value_label.setObjectName("ResultValue")
        self._result_labels[key] = value_label
        value_row.addWidget(value_label)
        
        if unit:
            unit_label = QLabel(unit)
            unit_label.setObjectName("ResultUnit")
            value_row.addWidget(unit_label)
        
        value_row.addStretch()
        layout.addLayout(value_row)
        
        return card
    
    def _on_input_type_changed(self, button):
        """输入类型切换"""
        button_id = self._input_type_group.id(button)
        
        self._vswr_input.setEnabled(button_id == 0)
        self._gamma_input.setEnabled(button_id == 1)
        self._rl_input.setEnabled(button_id == 2)
    
    def calculate(self) -> Dict[str, Any]:
        """执行计算，带详细验证提示"""
        try:
            input_type = self._input_type_group.checkedId()
            
            if input_type == 0:  # VSWR
                vswr_text = self._vswr_input.text().strip()
                if not vswr_text:
                    return {"success": False, "error": "⚠️ 请输入驻波比 (VSWR) 值"}
                try:
                    vswr = float(vswr_text)
                except ValueError:
                    return {"success": False, "error": "⚠️ 驻波比格式错误，请输入有效数字"}
                if vswr < 1.0:
                    return {"success": False, "error": "⚠️ 驻波比必须 ≥ 1\n（完美匹配时 VSWR = 1:1）"}
                result = self._calculator.calculate_from_vswr(vswr)
                
            elif input_type == 1:  # 反射系数
                gamma_text = self._gamma_input.text().strip()
                if not gamma_text:
                    return {"success": False, "error": "⚠️ 请输入反射系数 |Γ| 值"}
                try:
                    gamma = float(gamma_text)
                except ValueError:
                    return {"success": False, "error": "⚠️ 反射系数格式错误，请输入有效数字"}
                if gamma < 0:
                    return {"success": False, "error": "⚠️ 反射系数不能为负值\n（|Γ| 范围: 0 ~ 1）"}
                if gamma >= 1:
                    return {"success": False, "error": "⚠️ 反射系数必须 < 1\n（|Γ| = 1 表示全反射）"}
                result = self._calculator.calculate_from_reflection_coefficient(gamma)
                
            else:  # 回波损耗
                rl_text = self._rl_input.text().strip()
                if not rl_text:
                    return {"success": False, "error": "⚠️ 请输入回波损耗值"}
                try:
                    rl = float(rl_text)
                except ValueError:
                    return {"success": False, "error": "⚠️ 回波损耗格式错误，请输入有效数字"}
                if rl <= 0:
                    return {"success": False, "error": "⚠️ 回波损耗必须为正值 (dB)\n（值越大匹配越好）"}
                result = self._calculator.calculate_from_return_loss(rl)
            
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"⚠️ 计算错误: {str(e)}"}
    
    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()
        
        if calc_result["success"]:
            # 隐藏错误提示
            self._error_label.hide()
            
            result: VSWRResult = calc_result["result"]
            
            # 获取特性阻抗
            try:
                z0 = float(self._z0_input.text() or "50")
                if z0 <= 0:
                    z0 = 50
            except:
                z0 = 50
            
            # 更新基本结果显示
            self._result_labels["vswr"].setText(f"{result.vswr:.4f}")
            self._result_labels["gamma"].setText(f"{result.reflection_coefficient:.4f}")
            self._result_labels["return_loss"].setText(f"{result.return_loss_db:.2f}")
            self._result_labels["mismatch_loss"].setText(f"{result.mismatch_loss_db:.3f}")
            
            # 负载阻抗 (假设相位=0，纯电阻情况)
            z_load = self._calculator.calculate_load_impedance(
                result.reflection_coefficient, z0, 0
            )
            if z_load.imag == 0:
                self._result_labels["load_z"].setText(f"{z_load.real:.1f}")
            else:
                self._result_labels["load_z"].setText(f"{z_load.real:.1f}+j{z_load.imag:.1f}")
            
            # 更新匹配质量
            quality = self._calculator.get_vswr_quality(result.vswr)
            self._quality_label.setText(quality)
            
            # 获取输入功率
            input_power_w = self._get_input_power_watts()
            
            # 最大电压/电流计算
            if input_power_w > 0:
                v_max, v_min, i_max, i_min = self._calculator.calculate_max_voltage(
                    input_power_w, z0, result.vswr
                )
                self._vmax_label.setText(f"{v_max:.2f} V")
                self._imax_label.setText(f"{i_max:.3f} A")
            else:
                self._vmax_label.setText("请输入功率")
                self._imax_label.setText("请输入功率")
            
            # 更新功率损失详情
            if input_power_w > 0:
                transmitted_power = input_power_w * result.transmitted_power_ratio
                reflected_power = input_power_w * result.reflected_power_ratio
                
                self._reflected_power_label.setText(self._format_power(reflected_power))
                self._transmitted_power_label.setText(self._format_power(transmitted_power))
                
                # 计算需要补偿的功率 (为达到目标输出需增加的发射功率)
                if result.transmitted_power_ratio > 0:
                    required_power = input_power_w / result.transmitted_power_ratio
                    compensation = required_power - input_power_w
                    self._compensation_label.setText(f"+{self._format_power(compensation)}")
                else:
                    self._compensation_label.setText("无法补偿")
            else:
                self._reflected_power_label.setText("请输入功率")
                self._transmitted_power_label.setText("请输入功率")
                self._compensation_label.setText("--")
            
            # 更新功率仪表盘
            if self._power_meter:
                self._power_meter.set_values(
                    result.transmitted_power_ratio,
                    result.reflected_power_ratio,
                    input_power_w
                )
        else:
            # 显示错误提示
            self._error_label.setText(calc_result.get("error", "未知错误"))
            self._error_label.show()
            
            for key in ["vswr", "gamma", "return_loss", "mismatch_loss", "load_z"]:
                self._result_labels[key].setText("--")
            self._quality_label.setText("--")
            self._reflected_power_label.setText("--")
            self._transmitted_power_label.setText("--")
            self._compensation_label.setText("--")
            self._vmax_label.setText("--")
            self._imax_label.setText("--")
    
    def _get_input_power_watts(self) -> float:
        """获取输入功率并转换为瓦特"""
        power_text = self._power_input.text().strip()
        if not power_text:
            return 0.0
        
        try:
            power_value = float(power_text)
            unit = self._power_unit.currentText()
            
            if unit == "kW":
                return power_value * 1000
            elif unit == "mW":
                return power_value / 1000
            elif unit == "dBm":
                # dBm转瓦特: P(W) = 10^((dBm - 30) / 10)
                return 10 ** ((power_value - 30) / 10)
            else:  # W
                return power_value
        except ValueError:
            return 0.0
    
    def _format_power(self, power_w: float) -> str:
        """格式化功率显示"""
        if power_w >= 1000:
            return f"{power_w/1000:.2f} kW"
        elif power_w >= 1:
            return f"{power_w:.2f} W"
        elif power_w >= 0.001:
            return f"{power_w*1000:.2f} mW"
        else:
            return f"{power_w*1e6:.2f} μW"
    
    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        """直观理解 - 物理本质"""
        return """
        <b>🌊 什么是驻波？</b><br><br>
        
        想象你拿着绳子的一端不停地上下抖动，产生波向另一端传播。如果另一端固定在墙上，
        波会<b>反射</b>回来，与入射波叠加形成<b>"驻波"</b>——看起来绳子在原地振动，而不是波在移动。<br><br>
        
        <b>🔑 射频系统中的驻波:</b><br>
        当传输线与负载阻抗<b>不匹配</b>时，部分功率被反射回源端，形成驻波。<br><br>
        
        • <b>VSWR = 1:1</b> → 完美匹配，无反射<br>
        • <b>VSWR = ∞:1</b> → 全反射（开路/短路）<br><br>
        
        <b>💡 核心理解:</b> VSWR越大，失配越严重，反射越多，传输效率越低。
        """
    
    def get_math_model_content(self) -> Optional[str]:
        """数学模型 - 精确公式"""
        return """
        <b>📐 核心公式</b><br><br>
        
        <b>反射系数 Γ (Gamma):</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        Γ = (Z<sub>L</sub> - Z<sub>0</sub>) / (Z<sub>L</sub> + Z<sub>0</sub>)
        </span><br>
        Z<sub>L</sub> = 负载阻抗, Z<sub>0</sub> = 特性阻抗<br><br>
        
        <b>VSWR与反射系数关系:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        VSWR = (1 + |Γ|) / (1 - |Γ|)
        </span><br><br>
        
        <b>回波损耗 (Return Loss):</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        RL = -20 log₁₀|Γ| (dB)
        </span><br><br>
        
        <b>失配损耗 (Mismatch Loss):</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        ML = -10 log₁₀(1 - |Γ|²) (dB)
        </span>
        """
    
    def get_engineering_content(self) -> Optional[str]:
        """工程边界 - 适用范围与避坑"""
        return """
        <b>✅ 工程经验参考值:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>VSWR &lt; 1.2</td><td>→ 专业级射频系统</td></tr>
        <tr><td>VSWR &lt; 1.5</td><td>→ 大多数无线通信</td></tr>
        <tr><td>VSWR &lt; 2.0</td><td>→ 可接受最低要求</td></tr>
        <tr><td>VSWR &gt; 3.0</td><td>→ 严重问题，需排查</td></tr>
        </table><br>
        
        <b>⚠️ 常见问题避坑:</b><br><br>
        
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 高VSWR的后果
        </span><br>
        • 功率放大器过热甚至损坏<br>
        • 发射效率降低，信号变弱<br>
        • 可能触发保护电路降功率<br><br>
        
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px; color: #276749;">
        💡 测量提示
        </span><br>
        VSWR随频率变化，需在工作频段内全频段测量
        """
    
    def get_history_content(self) -> Optional[str]:
        """发现历史 - 趣味故事"""
        return """
        <b>📜 驻波的发现</b><br><br>
        
        <b>1820年代</b> - 法国科学家<b>菲涅尔</b>研究光学干涉时首次描述了驻波现象。<br><br>
        
        <b>1888年</b> - <b>赫兹</b>在验证电磁波实验中，用金属反射板产生驻波，
        并用检测环测量电场强度分布，成功验证了电磁波的波动性质。<br><br>
        
        <i>💭 驻波测量曾是早期无线电工程师的必备技能。在史密斯圆图发明之前，
        工程师们需要沿传输线移动探针，手工绘制电压分布曲线来分析阻抗匹配情况！</i>
        """
