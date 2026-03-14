# -*- coding: utf-8 -*-
"""
射频天线工具集 - 驻波(VSWR)计算工具
RF Antenna Toolkit - VSWR Calculator Tool

版本: v2.0.0
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
        title_text = tr("vswr.meter_title")
        if self.show_power_values:
            title_text += f" ({tr('vswr.meter_input')} {self._format_power(self.input_power_w)})"
        painter.drawText(x, y - 10, title_text)
        
        # 计算实际功率
        transmitted_power = self.input_power_w * self.transmitted_ratio
        reflected_power = self.input_power_w * self.reflected_ratio
        
        # 传输功率百分比/数值
        painter.setPen(QPen(QColor("#276749")))
        if self.show_power_values:
            trans_text = f"✓ {tr('vswr.meter_trans')} {self.transmitted_ratio*100:.1f}% ({self._format_power(transmitted_power)})"
        else:
            trans_text = f"✓ {tr('vswr.meter_trans')} {self.transmitted_ratio*100:.1f}%"
        painter.drawText(x + 5, y + height + 20, trans_text)
        
        # 反射功率百分比/数值
        painter.setPen(QPen(QColor("#C53030")))
        if self.show_power_values:
            refl_text = f"✗ {tr('vswr.meter_refl')} {self.reflected_ratio*100:.1f}% ({self._format_power(reflected_power)})"
        else:
            refl_text = f"✗ {tr('vswr.meter_refl')} {self.reflected_ratio*100:.1f}%"
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
    tool_name = tr("vswr.tool_name")
    tool_icon = "📊"
    tool_category = "rf"
    tool_description = tr("vswr.tool_desc")
    i18n_title_key = "vswr.tool_name"
    i18n_desc_key = "vswr.tool_desc"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化驻波计算工具"""
        # 计算器实例
        self._calculator = VSWRCalculator()
        
        # 结果显示控件引用
        self._result_labels: Dict[str, QLabel] = {}
        self._result_titles: Dict[str, QLabel] = {}
        
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
        self._grp_input = QGroupBox(tr("vswr.lbl_input_param"))
        input_layout = QVBoxLayout(self._grp_input)
        input_layout.setSpacing(12)
        
        # 输入类型选择
        self._input_type_group = QButtonGroup(self)
        
        # VSWR输入
        self._vswr_radio = QRadioButton(tr("vswr.radio_vswr"))
        self._vswr_radio.setChecked(True)
        self._input_type_group.addButton(self._vswr_radio, 0)
        input_layout.addWidget(self._vswr_radio)
        
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
        self._gamma_radio = QRadioButton(tr("vswr.radio_gamma"))
        self._input_type_group.addButton(self._gamma_radio, 1)
        input_layout.addWidget(self._gamma_radio)
        
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
        self._rl_radio = QRadioButton(tr("vswr.radio_rl"))
        self._input_type_group.addButton(self._rl_radio, 2)
        input_layout.addWidget(self._rl_radio)
        
        rl_input_layout = QHBoxLayout()
        self._rl_input = QLineEdit()
        self._rl_input.setPlaceholderText("> 0")
        self._rl_input.setValidator(QDoubleValidator(0.001, 100, 4))
        self._rl_input.setText("14")
        self._rl_input.setEnabled(False)
        rl_input_layout.addWidget(self._rl_input)
        
        self._rl_unit_label = QLabel("dB")
        rl_input_layout.addWidget(self._rl_unit_label)
        rl_input_layout.addStretch()
        input_layout.addLayout(rl_input_layout)
        
        # 切换输入类型时启用/禁用对应输入框
        self._input_type_group.buttonClicked.connect(self._on_input_type_changed)
        
        layout.addWidget(self._grp_input)
        
        # ==================== 输入功率设置 (大功率场景) ====================
        self._grp_power = QGroupBox(tr("vswr.group_power"))
        power_layout = QVBoxLayout(self._grp_power)
        power_layout.setSpacing(8)
        
        power_desc = QLabel(tr("vswr.desc_power"))
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
        z0_layout.addWidget(QLabel(tr("vswr.lbl_z0")))
        self._z0_input = QLineEdit()
        self._z0_input.setValidator(QDoubleValidator(1, 1000, 2))
        self._z0_input.setText("50")
        self._z0_input.setMaximumWidth(80)
        z0_layout.addWidget(self._z0_input)
        z0_layout.addWidget(QLabel("Ω"))
        z0_layout.addStretch()
        power_layout.addLayout(z0_layout)
        
        layout.addWidget(self._grp_power)
        
        # ==================== 计算按钮 ====================
        self._btn_calc = QPushButton(tr("vswr.btn_calc"))
        self._btn_calc.setObjectName("PrimaryButton")
        self._btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_calc.clicked.connect(self._do_calculate)
        layout.addWidget(self._btn_calc)
        
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
        
        self._quality_title = QLabel(tr("vswr.lbl_quality"))
        self._quality_title.setObjectName("ResultTitle")
        quality_layout.addWidget(self._quality_title)
        
        self._quality_label = QLabel("--")
        self._quality_label.setObjectName("ResultValue")
        self._result_labels["quality"] = self._quality_label
        quality_layout.addWidget(self._quality_label)
        
        layout.addWidget(quality_card)
        
        # 结果网格
        results_grid = QGridLayout()
        results_grid.setSpacing(12)
        
        # VSWR
        vswr_card = self._create_result_card("vswr", tr("vswr.lbl_result_vswr"), ": 1")
        results_grid.addWidget(vswr_card, 0, 0)
        
        # 反射系数
        gamma_card = self._create_result_card("gamma", tr("vswr.lbl_result_gamma"), "")
        results_grid.addWidget(gamma_card, 0, 1)
        
        # 回波损耗
        rl_card = self._create_result_card("return_loss", tr("vswr.lbl_result_rl"), "dB")
        results_grid.addWidget(rl_card, 0, 2)
        
        # 失配损耗
        ml_card = self._create_result_card("mismatch_loss", tr("vswr.lbl_result_ml"), "dB")
        results_grid.addWidget(ml_card, 1, 0)
        
        # 负载阻抗 (估算, 相位=0时)
        zl_card = self._create_result_card("load_z", tr("vswr.lbl_result_zl"), "Ω")
        results_grid.addWidget(zl_card, 1, 1)
        
        layout.addLayout(results_grid)
        
        # 最大电压/电流区 (大功率场景)
        voltage_card = QWidget()
        voltage_card.setObjectName("ResultPanel")
        voltage_layout = QVBoxLayout(voltage_card)
        
        voltage_title = QLabel(tr("vswr.title_voltage"))
        voltage_title.setObjectName("ResultTitle")
        voltage_layout.addWidget(voltage_title)
        
        voltage_grid = QGridLayout()
        voltage_grid.setSpacing(8)
        
        voltage_grid.addWidget(QLabel(tr("vswr.lbl_vmax")), 0, 0)
        self._vmax_label = QLabel("--")
        self._vmax_label.setStyleSheet("color: #C53030; font-weight: bold;")
        voltage_grid.addWidget(self._vmax_label, 0, 1)
        
        voltage_grid.addWidget(QLabel(tr("vswr.lbl_imax")), 0, 2)
        self._imax_label = QLabel("--")
        self._imax_label.setStyleSheet("color: #C53030; font-weight: bold;")
        voltage_grid.addWidget(self._imax_label, 0, 3)
        
        voltage_layout.addLayout(voltage_grid)
        layout.addWidget(voltage_card)
        
        # 功率损失结果区 (当输入功率时显示)
        power_loss_card = QWidget()
        power_loss_card.setObjectName("ResultPanel")
        power_loss_layout = QVBoxLayout(power_loss_card)
        
        self._power_loss_title = QLabel(tr("vswr.title_loss"))
        self._power_loss_title.setObjectName("ResultTitle")
        power_loss_layout.addWidget(self._power_loss_title)
        
        # 功率损失结果网格
        power_grid = QGridLayout()
        power_grid.setSpacing(8)
        
        # 反射功率
        power_grid.addWidget(QLabel(tr("vswr.lbl_refl_power")), 0, 0)
        self._reflected_power_label = QLabel("--")
        self._reflected_power_label.setStyleSheet("color: #C53030; font-weight: bold;")
        power_grid.addWidget(self._reflected_power_label, 0, 1)
        
        # 传输功率
        power_grid.addWidget(QLabel(tr("vswr.lbl_trans_power")), 1, 0)
        self._transmitted_power_label = QLabel("--")
        self._transmitted_power_label.setStyleSheet("color: #276749; font-weight: bold;")
        power_grid.addWidget(self._transmitted_power_label, 1, 1)
        
        # 给PA的补偿功率建议
        power_grid.addWidget(QLabel(tr("vswr.lbl_comp")), 2, 0)
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
        self._result_titles[key] = title_label # 同时保存标题
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
                    return {"success": False, "error": tr("vswr.err_vswr_empty")}
                try:
                    vswr = float(vswr_text)
                except ValueError:
                    return {"success": False, "error": tr("vswr.err_vswr_fmt")}
                if vswr < 1.0:
                    return {"success": False, "error": tr("vswr.err_vswr_val")}
                result = self._calculator.calculate_from_vswr(vswr)
                
            elif input_type == 1:  # 反射系数
                gamma_text = self._gamma_input.text().strip()
                if not gamma_text:
                    return {"success": False, "error": tr("vswr.err_gamma_empty")}
                try:
                    gamma = float(gamma_text)
                except ValueError:
                    return {"success": False, "error": tr("vswr.err_gamma_fmt")}
                if gamma < 0:
                    return {"success": False, "error": tr("vswr.err_gamma_neg")}
                if gamma >= 1:
                    return {"success": False, "error": tr("vswr.err_gamma_1")}
                result = self._calculator.calculate_from_reflection_coefficient(gamma)
                
            else:  # 回波损耗
                rl_text = self._rl_input.text().strip()
                if not rl_text:
                    return {"success": False, "error": tr("vswr.err_rl_empty")}
                try:
                    rl = float(rl_text)
                except ValueError:
                    return {"success": False, "error": tr("vswr.err_rl_fmt")}
                if rl <= 0:
                    return {"success": False, "error": tr("vswr.err_rl_pos")}
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
                self._vmax_label.setText(tr("vswr.err_power_req", "请输入功率"))
                self._imax_label.setText(tr("vswr.err_power_req", "请输入功率"))
            
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
                    self._compensation_label.setText(tr("vswr.err_no_comp", "无法补偿"))
            else:
                self._reflected_power_label.setText(tr("vswr.err_power_req", "请输入功率"))
                self._transmitted_power_label.setText(tr("vswr.err_power_req", "请输入功率"))
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
            self._error_label.setText(calc_result.get("error", tr("vswr.err_unknown", "未知错误")))
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
    

    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新 UI 文字"""
        super().retranslate_ui(lang)
        
        # 刷新 GroupBox
        if hasattr(self, '_grp_input'): self._grp_input.setTitle(tr("vswr.lbl_input_param"))
        if hasattr(self, '_grp_power'): self._grp_power.setTitle(tr("vswr.group_power"))
        
        # 刷新 Radio 和 Label
        if hasattr(self, '_vswr_radio'): self._vswr_radio.setText(tr("vswr.radio_vswr"))
        if hasattr(self, '_gamma_radio'): self._gamma_radio.setText(tr("vswr.radio_gamma"))
        if hasattr(self, '_rl_radio'): self._rl_radio.setText(tr("vswr.radio_rl"))
        
        # 刷新按钮
        if hasattr(self, '_btn_calc'): self._btn_calc.setText(tr("vswr.btn_calc"))
        
        # 刷新标题Label
        if hasattr(self, '_quality_title'): self._quality_title.setText(tr("vswr.lbl_quality"))
        if hasattr(self, '_voltage_title'): self._voltage_title.setText(tr("vswr.title_voltage"))
        if hasattr(self, '_power_loss_title'): self._power_loss_title.setText(tr("vswr.title_loss"))
        
        # 刷新结果卡片标题
        if hasattr(self, '_result_titles'):
            self._result_titles["vswr"].setText(tr("vswr.lbl_result_vswr"))
            self._result_titles["gamma"].setText(tr("vswr.lbl_result_gamma"))
            self._result_titles["return_loss"].setText(tr("vswr.lbl_result_rl"))
            self._result_titles["mismatch_loss"].setText(tr("vswr.lbl_result_ml"))
            self._result_titles["load_z"].setText(tr("vswr.lbl_result_zl"))
            
        # 刷新功率仪表盘 (触发重绘)
        if hasattr(self, '_power_meter') and self._power_meter is not None:
            self._power_meter.update()
            
        # 刷新当前计算结果 (以更新翻译文字)
        self._do_calculate()

    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> str:
        return tr("vswr.intuition")

    def get_math_model_content(self) -> str:
        return tr("vswr.math_model")

    def get_engineering_content(self) -> str:
        return tr("vswr.eng_content")

    def get_history_content(self) -> str:
        return tr("vswr.history_content")
