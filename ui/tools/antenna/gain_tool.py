# -*- coding: utf-8 -*-
"""
射频天线工具集 - 天线增益计算工具
RF Antenna Toolkit - Antenna Gain Calculator Tool

版本: v2.0.0
功能: 提供多种天线增益计算界面
"""

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QRadioButton, QButtonGroup,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

from ui.base.tool_base import ToolBase
from core.i18n import tr
from core.antenna.gain import GainCalculator, GainResult


class GainTool(ToolBase):
    """
    天线增益计算工具
    
    功能:
    - 波束宽度法: 根据E面/H面3dB波束宽度估算增益
    - 口径效率法: 根据口径尺寸和效率计算增益
    - 增益单位转换: dBi/dBd/线性值互转
    """
    
    # 工具元信息
    tool_name = tr("gain.tool_name", "天线增益")
    tool_icon = "📶"
    tool_category = "antenna"
    tool_description = tr("gain.tool_desc", "根据波束宽度或口径计算天线增益")
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化增益计算工具"""
        # 计算器实例
        self._calculator = GainCalculator()
        
        # 结果显示控件引用
        self._result_labels: Dict[str, QLabel] = {}
        
        # 调用父类初始化
        self._static_labels = []
        super().__init__(parent)
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 计算方法选择 ====================
        method_group = QGroupBox(tr("gain.calc_method", "计算方法"))
        self._static_labels.append((method_group, "gain", "calc_method", "title"))
        method_layout = QVBoxLayout(method_group)
        method_layout.setSpacing(12)
        
        self._method_group = QButtonGroup(self)
        
        # 方法1: 波束宽度法 (最常用)
        beamwidth_radio = QRadioButton(tr("gain.method_beamwidth", "波束宽度法 (3dB波束角)"))
        self._static_labels.append((beamwidth_radio, "gain", "method_beamwidth", "text"))
        beamwidth_radio.setChecked(True)
        self._method_group.addButton(beamwidth_radio, 0)
        method_layout.addWidget(beamwidth_radio)
        
        # 波束宽度输入
        beamwidth_layout = QGridLayout()
        
        lbl_theta_e = QLabel(tr("gain.theta_e", "E面 θ_E:"))
        self._static_labels.append((lbl_theta_e, "gain", "theta_e", "text"))
        beamwidth_layout.addWidget(lbl_theta_e, 0, 0)
        self._theta_e_input = QLineEdit()
        self._theta_e_input.setPlaceholderText(tr("gain.placeholder_theta", "E面波束角"))
        self._static_labels.append((self._theta_e_input, "gain", "placeholder_theta", "placeholder"))
        self._theta_e_input.setValidator(QDoubleValidator(0.1, 180, 2))
        self._theta_e_input.setText("30")
        beamwidth_layout.addWidget(self._theta_e_input, 0, 1)
        beamwidth_layout.addWidget(QLabel("°"), 0, 2)
        
        lbl_theta_h = QLabel(tr("gain.theta_h", "H面 θ_H:"))
        self._static_labels.append((lbl_theta_h, "gain", "theta_h", "text"))
        beamwidth_layout.addWidget(lbl_theta_h, 1, 0)
        self._theta_h_input = QLineEdit()
        self._theta_h_input.setPlaceholderText(tr("gain.placeholder_theta_h", "H面波束角"))
        self._static_labels.append((self._theta_h_input, "gain", "placeholder_theta_h", "placeholder"))
        self._theta_h_input.setValidator(QDoubleValidator(0.1, 180, 2))
        self._theta_h_input.setText("30")
        beamwidth_layout.addWidget(self._theta_h_input, 1, 1)
        beamwidth_layout.addWidget(QLabel("°"), 1, 2)
        
        # 公式常数选择
        lbl_k = QLabel(tr("gain.constant_k", "公式常数K:"))
        self._static_labels.append((lbl_k, "gain", "constant_k", "text"))
        beamwidth_layout.addWidget(lbl_k, 2, 0)
        self._constant_combo = QComboBox()
        self._constant_combo.addItems([
            tr("gain.const_ieee", "41253 (IEEE标准)"),
            tr("gain.const_uniform", "32400 (均匀口径)"),
            tr("gain.const_typical", "26000 (典型值)")
        ])
        beamwidth_layout.addWidget(self._constant_combo, 2, 1, 1, 2)
        
        method_layout.addLayout(beamwidth_layout)
        
        # 方法2: 口径效率法 (支持圆形/矩形)
        aperture_radio = QRadioButton(tr("gain.method_aperture", "口径效率法"))
        self._static_labels.append((aperture_radio, "gain", "method_aperture", "text"))
        self._method_group.addButton(aperture_radio, 1)
        method_layout.addWidget(aperture_radio)
        
        aperture_layout = QGridLayout()
        
        # 口径形状选择
        lbl_shape = QLabel(tr("gain.aperture_shape", "口径形状:"))
        self._static_labels.append((lbl_shape, "gain", "aperture_shape", "text"))
        aperture_layout.addWidget(lbl_shape, 0, 0)
        self._aperture_shape = QComboBox()
        self._aperture_shape.addItems([tr("gain.shape_circ", "⚪ 圆形 (抛物面等)"), tr("gain.shape_rect", "▭ 矩形 (喇叭天线等)")])
        self._aperture_shape.setEnabled(False)
        self._aperture_shape.currentIndexChanged.connect(self._on_aperture_shape_changed)
        aperture_layout.addWidget(self._aperture_shape, 0, 1, 1, 2)
        
        # 圆形口径 - 直径
        self._diameter_label = QLabel(tr("gain.aperture_diameter", "口径直径:"))
        self._static_labels.append((self._diameter_label, "gain", "aperture_diameter", "text"))
        aperture_layout.addWidget(self._diameter_label, 1, 0)
        self._diameter_input = QLineEdit()
        self._diameter_input.setPlaceholderText(tr("gain.ph_diameter", "直径 D"))
        self._static_labels.append((self._diameter_input, "gain", "ph_diameter", "placeholder"))
        self._diameter_input.setValidator(QDoubleValidator(0.001, 1000, 4))
        self._diameter_input.setText("1.0")
        self._diameter_input.setEnabled(False)
        aperture_layout.addWidget(self._diameter_input, 1, 1)
        
        self._diameter_unit = QComboBox()
        self._diameter_unit.addItems(["m", "cm", "mm"])
        self._diameter_unit.setEnabled(False)
        aperture_layout.addWidget(self._diameter_unit, 1, 2)
        
        # 矩形口径 - 宽度
        self._width_label = QLabel(tr("gain.aperture_width", "口径宽度:"))
        self._static_labels.append((self._width_label, "gain", "aperture_width", "text"))
        self._width_label.hide()
        aperture_layout.addWidget(self._width_label, 1, 0)
        self._width_input = QLineEdit()
        self._width_input.setPlaceholderText(tr("gain.ph_width", "宽度 W"))
        self._static_labels.append((self._width_input, "gain", "ph_width", "placeholder"))
        self._width_input.setValidator(QDoubleValidator(0.001, 1000, 4))
        self._width_input.setText("0.3")
        self._width_input.setEnabled(False)
        self._width_input.hide()
        aperture_layout.addWidget(self._width_input, 1, 1)
        
        self._width_unit = QComboBox()
        self._width_unit.addItems(["m", "cm", "mm"])
        self._width_unit.setEnabled(False)
        self._width_unit.hide()
        aperture_layout.addWidget(self._width_unit, 1, 2)
        
        # 矩形口径 - 高度
        self._height_label = QLabel(tr("gain.aperture_height", "口径高度:"))
        self._static_labels.append((self._height_label, "gain", "aperture_height", "text"))
        self._height_label.hide()
        aperture_layout.addWidget(self._height_label, 2, 0)
        self._height_input = QLineEdit()
        self._height_input.setPlaceholderText(tr("gain.ph_height", "高度 H"))
        self._static_labels.append((self._height_input, "gain", "ph_height", "placeholder"))
        self._height_input.setValidator(QDoubleValidator(0.001, 1000, 4))
        self._height_input.setText("0.2")
        self._height_input.setEnabled(False)
        self._height_input.hide()
        aperture_layout.addWidget(self._height_input, 2, 1)
        
        self._height_unit = QComboBox()
        self._height_unit.addItems(["m", "cm", "mm"])
        self._height_unit.setEnabled(False)
        self._height_unit.hide()
        aperture_layout.addWidget(self._height_unit, 2, 2)
        
        # 工作频率 (行号根据形状变化)
        self._freq_label = QLabel(tr("gain.work_freq", "工作频率:"))
        self._static_labels.append((self._freq_label, "gain", "work_freq", "text"))
        aperture_layout.addWidget(self._freq_label, 3, 0)
        self._freq_input = QLineEdit()
        self._freq_input.setPlaceholderText(tr("gain.ph_freq", "频率"))
        self._static_labels.append((self._freq_input, "gain", "ph_freq", "placeholder"))
        self._freq_input.setValidator(QDoubleValidator(0.001, 1e6, 4))
        self._freq_input.setText("10")
        self._freq_input.setEnabled(False)
        aperture_layout.addWidget(self._freq_input, 3, 1)
        
        self._freq_unit = QComboBox()
        self._freq_unit.addItems(["GHz", "MHz", "kHz"])
        self._freq_unit.setEnabled(False)
        aperture_layout.addWidget(self._freq_unit, 3, 2)
        
        # 口径效率
        lbl_eff = QLabel(tr("gain.aperture_efficiency", "口径效率:"))
        self._static_labels.append((lbl_eff, "gain", "aperture_efficiency", "text"))
        aperture_layout.addWidget(lbl_eff, 4, 0)
        self._efficiency_input = QLineEdit()
        self._efficiency_input.setPlaceholderText("0~1")
        self._efficiency_input.setValidator(QDoubleValidator(0.01, 1.0, 3))
        self._efficiency_input.setText("0.55")
        self._efficiency_input.setEnabled(False)
        aperture_layout.addWidget(self._efficiency_input, 4, 1)
        
        self._efficiency_hint = QLabel(tr("gain.hint_circ", "(圆形典型0.55)"))
        aperture_layout.addWidget(self._efficiency_hint, 4, 2)
        
        method_layout.addLayout(aperture_layout)
        
        # 方法3: 增益单位转换
        convert_radio = QRadioButton(tr("gain.method_convert", "增益单位转换"))
        self._static_labels.append((convert_radio, "gain", "method_convert", "text"))
        self._method_group.addButton(convert_radio, 2)
        method_layout.addWidget(convert_radio)
        
        convert_layout = QHBoxLayout()
        
        self._convert_input = QLineEdit()
        self._convert_input.setPlaceholderText(tr("gain.ph_gain_val", "增益值"))
        self._static_labels.append((self._convert_input, "gain", "ph_gain_val", "placeholder"))
        self._convert_input.setValidator(QDoubleValidator(-50, 100, 4))
        self._convert_input.setText("12")
        self._convert_input.setEnabled(False)
        convert_layout.addWidget(self._convert_input)
        
        self._convert_from_unit = QComboBox()
        self._convert_from_unit.addItems(["dBi", "dBd", tr("gain.linear_val", "线性值")])
        self._convert_from_unit.setEnabled(False)
        convert_layout.addWidget(self._convert_from_unit)
        
        convert_layout.addWidget(QLabel("→"))
        
        self._convert_to_unit = QComboBox()
        self._convert_to_unit.addItems(["dBd", "dBi", tr("gain.linear_val", "线性值")])
        self._convert_to_unit.setEnabled(False)
        convert_layout.addWidget(self._convert_to_unit)
        
        method_layout.addLayout(convert_layout)
        
        # 切换输入类型
        self._method_group.buttonClicked.connect(self._on_method_changed)
        
        layout.addWidget(method_group)
        
        # ==================== 计算按钮 ====================
        calc_button = QPushButton(tr("gain.btn_calc"))
        self._static_labels.append((calc_button, "gain", "btn_calc", "text"))
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
        self._error_label.hide()
        layout.addWidget(self._error_label)
        
        # 天线类型评估
        quality_card = QWidget()
        quality_card.setObjectName("ResultPanel")
        quality_layout = QVBoxLayout(quality_card)
        
        quality_title = QLabel(tr("gain.type_eval", "天线类型评估"))
        self._static_labels.append((quality_title, "gain", "type_eval", "text"))
        quality_title.setObjectName("ResultTitle")
        quality_layout.addWidget(quality_title)
        
        self._quality_label = QLabel("--")
        self._quality_label.setObjectName("ResultValue")
        quality_layout.addWidget(self._quality_label)
        
        layout.addWidget(quality_card)
        
        # 增益结果区域
        gain_card = QWidget()
        gain_card.setObjectName("ResultPanel")
        gain_layout = QVBoxLayout(gain_card)
        
        gain_title = QLabel(tr("gain.res_gain", "📡 增益结果"))
        self._static_labels.append((gain_title, "gain", "res_gain", "text"))
        gain_title.setObjectName("ResultTitle")
        gain_layout.addWidget(gain_title)
        
        gain_grid = QGridLayout()
        gain_grid.setSpacing(12)
        
        # dBi增益
        lbl_res_dbi = QLabel(tr("gain.res_dbi", "增益 (dBi):"))
        self._static_labels.append((lbl_res_dbi, "gain", "res_dbi", "text"))
        gain_grid.addWidget(lbl_res_dbi, 0, 0)
        self._gain_dbi_label = QLabel("--")
        self._gain_dbi_label.setStyleSheet("font-weight: bold; color: #2C7BE5; font-size: 18px;")
        gain_grid.addWidget(self._gain_dbi_label, 0, 1)
        
        # dBd增益
        lbl_res_dbd = QLabel(tr("gain.res_dbd", "增益 (dBd):"))
        self._static_labels.append((lbl_res_dbd, "gain", "res_dbd", "text"))
        gain_grid.addWidget(lbl_res_dbd, 1, 0)
        self._gain_dbd_label = QLabel("--")
        gain_grid.addWidget(self._gain_dbd_label, 1, 1)
        
        # 线性增益
        lbl_res_linear = QLabel(tr("gain.res_linear", "线性增益:"))
        self._static_labels.append((lbl_res_linear, "gain", "res_linear", "text"))
        gain_grid.addWidget(lbl_res_linear, 2, 0)
        self._gain_linear_label = QLabel("--")
        gain_grid.addWidget(self._gain_linear_label, 2, 1)
        
        gain_layout.addLayout(gain_grid)
        layout.addWidget(gain_card)
        
        # 估算波束宽度 (反向推导)
        estimate_card = QWidget()
        estimate_card.setObjectName("ResultPanel")
        estimate_layout = QVBoxLayout(estimate_card)
        
        estimate_title = QLabel(tr("gain.res_est_beam", "📐 估算波束宽度 (对称)"))
        self._static_labels.append((estimate_title, "gain", "res_est_beam", "text"))
        estimate_title.setObjectName("ResultTitle")
        estimate_layout.addWidget(estimate_title)
        
        self._beamwidth_estimate_label = QLabel("--")
        estimate_layout.addWidget(self._beamwidth_estimate_label)
        
        layout.addWidget(estimate_card)
        
        layout.addStretch()
        
        return panel
    
    def _on_method_changed(self, button):
        """计算方法切换"""
        method_id = self._method_group.id(button)
        
        # 波束宽度法
        self._theta_e_input.setEnabled(method_id == 0)
        self._theta_h_input.setEnabled(method_id == 0)
        self._constant_combo.setEnabled(method_id == 0)
        
        # 口径效率法
        is_aperture = method_id == 1
        self._aperture_shape.setEnabled(is_aperture)
        self._freq_input.setEnabled(is_aperture)
        self._freq_unit.setEnabled(is_aperture)
        self._efficiency_input.setEnabled(is_aperture)
        
        # 根据口径形状启用对应输入
        if is_aperture:
            self._on_aperture_shape_changed(self._aperture_shape.currentIndex())
        else:
            self._diameter_input.setEnabled(False)
            self._diameter_unit.setEnabled(False)
            self._width_input.setEnabled(False)
            self._width_unit.setEnabled(False)
            self._height_input.setEnabled(False)
            self._height_unit.setEnabled(False)
        
        # 单位转换
        self._convert_input.setEnabled(method_id == 2)
        self._convert_from_unit.setEnabled(method_id == 2)
        self._convert_to_unit.setEnabled(method_id == 2)
    
    def _on_aperture_shape_changed(self, index):
        """口径形状切换"""
        is_circular = index == 0
        method_active = self._method_group.checkedId() == 1
        
        # 圆形口径 - 显示直径
        self._diameter_label.setVisible(is_circular)
        self._diameter_input.setVisible(is_circular)
        self._diameter_input.setEnabled(is_circular and method_active)
        self._diameter_unit.setVisible(is_circular)
        self._diameter_unit.setEnabled(is_circular and method_active)
        
        # 矩形口径 - 显示宽度和高度
        self._width_label.setVisible(not is_circular)
        self._width_input.setVisible(not is_circular)
        self._width_input.setEnabled(not is_circular and method_active)
        self._width_unit.setVisible(not is_circular)
        self._width_unit.setEnabled(not is_circular and method_active)
        
        self._height_label.setVisible(not is_circular)
        self._height_input.setVisible(not is_circular)
        self._height_input.setEnabled(not is_circular and method_active)
        self._height_unit.setVisible(not is_circular)
        self._height_unit.setEnabled(not is_circular and method_active)
        
        # 更新效率提示
        if is_circular:
            self._efficiency_hint.setText(tr("gain.hint_circ", "(圆形典型0.55)"))
            self._efficiency_input.setText("0.55")
        else:
            self._efficiency_hint.setText(tr("gain.hint_rect", "(矩形典型0.60)"))
            self._efficiency_input.setText("0.60")
    
    def calculate(self) -> Dict[str, Any]:
        """执行计算，带详细验证提示"""
        try:
            method_id = self._method_group.checkedId()
            
            if method_id == 0:  # 波束宽度法
                theta_e_text = self._theta_e_input.text().strip()
                theta_h_text = self._theta_h_input.text().strip()
                
                if not theta_e_text:
                    return {"success": False, "error": tr("gain.err_no_e", "⚠️ 请输入E面波束宽度")}
                if not theta_h_text:
                    return {"success": False, "error": tr("gain.err_no_h", "⚠️ 请输入H面波束宽度")}
                
                try:
                    theta_e = float(theta_e_text)
                    theta_h = float(theta_h_text)
                except ValueError:
                    return {"success": False, "error": tr("gain.err_format_beam", "⚠️ 波束角格式错误，请输入有效数字")}
                
                if theta_e <= 0 or theta_h <= 0:
                    return {"success": False, "error": tr("gain.err_beam_positive", "⚠️ 波束宽度必须为正值")}
                if theta_e > 180 or theta_h > 180:
                    return {"success": False, "error": tr("gain.err_beam_too_large", "⚠️ 波束宽度不能超过180°\n（全向天线约为360°/2=180°）")}
                
                # 解析常数
                const_text = self._constant_combo.currentText()
                if "41253" in const_text:
                    constant = 41253
                elif "32400" in const_text:
                    constant = 32400
                else:
                    constant = 26000
                
                result = self._calculator.calculate_from_beamwidth(theta_e, theta_h, constant)
                return {"success": True, "result": result, "method": "beamwidth"}
                
            elif method_id == 1:  # 口径效率法
                is_circular = self._aperture_shape.currentIndex() == 0
                freq_text = self._freq_input.text().strip()
                efficiency_text = self._efficiency_input.text().strip()
                
                if not freq_text:
                    return {"success": False, "error": tr("gain.err_no_freq", "⚠️ 请输入工作频率")}
                if not efficiency_text:
                    return {"success": False, "error": tr("gain.err_no_eff", "⚠️ 请输入口径效率")}
                
                try:
                    freq = float(freq_text)
                    efficiency = float(efficiency_text)
                except ValueError:
                    return {"success": False, "error": tr("gain.err_format_fe", "⚠️ 频率/效率格式错误，请输入有效数字")}
                
                if freq <= 0:
                    return {"success": False, "error": tr("gain.err_freq_positive", "⚠️ 频率必须为正值")}
                if efficiency <= 0 or efficiency > 1:
                    return {"success": False, "error": tr("gain.err_eff_range", "⚠️ 口径效率必须在 (0, 1] 范围内\n（圆形典型0.55, 矩形典型0.60）")}
                
                # 频率单位转换
                freq_unit = self._freq_unit.currentText()
                if freq_unit == "GHz":
                    freq_hz = freq * 1e9
                elif freq_unit == "MHz":
                    freq_hz = freq * 1e6
                else:
                    freq_hz = freq * 1e3
                
                if is_circular:
                    # 圆形口径
                    diameter_text = self._diameter_input.text().strip()
                    if not diameter_text:
                        return {"success": False, "error": tr("gain.err_no_dia", "⚠️ 请输入口径直径")}
                    try:
                        diameter = float(diameter_text)
                    except ValueError:
                        return {"success": False, "error": tr("gain.err_format_dia", "⚠️ 直径格式错误，请输入有效数字")}
                    if diameter <= 0:
                        return {"success": False, "error": tr("gain.err_dia_positive", "⚠️ 口径直径必须为正值")}
                    
                    # 单位转换
                    diameter_unit = self._diameter_unit.currentText()
                    if diameter_unit == "cm":
                        diameter_m = diameter / 100
                    elif diameter_unit == "mm":
                        diameter_m = diameter / 1000
                    else:
                        diameter_m = diameter
                    
                    result = self._calculator.calculate_from_diameter(diameter_m, freq_hz, efficiency)
                else:
                    # 矩形口径
                    width_text = self._width_input.text().strip()
                    height_text = self._height_input.text().strip()
                    
                    if not width_text:
                        return {"success": False, "error": tr("gain.err_no_w", "⚠️ 请输入口径宽度")}
                    if not height_text:
                        return {"success": False, "error": tr("gain.err_no_h_dim", "⚠️ 请输入口径高度")}
                    
                    try:
                        width = float(width_text)
                        height = float(height_text)
                    except ValueError:
                        return {"success": False, "error": tr("gain.err_format_dim", "⚠️ 尺寸格式错误，请输入有效数字")}
                    
                    if width <= 0:
                        return {"success": False, "error": tr("gain.err_w_positive", "⚠️ 口径宽度必须为正值")}
                    if height <= 0:
                        return {"success": False, "error": tr("gain.err_h_positive", "⚠️ 口径高度必须为正值")}
                    
                    # 宽度单位转换
                    width_unit = self._width_unit.currentText()
                    if width_unit == "cm":
                        width_m = width / 100
                    elif width_unit == "mm":
                        width_m = width / 1000
                    else:
                        width_m = width
                    
                    # 高度单位转换
                    height_unit = self._height_unit.currentText()
                    if height_unit == "cm":
                        height_m = height / 100
                    elif height_unit == "mm":
                        height_m = height / 1000
                    else:
                        height_m = height
                    
                    result = self._calculator.calculate_from_rectangle(width_m, height_m, freq_hz, efficiency)
                
                return {"success": True, "result": result, "method": "aperture"}
                
            else:  # 单位转换
                value_text = self._convert_input.text().strip()
                
                if not value_text:
                    return {"success": False, "error": tr("gain.err_no_gain", "⚠️ 请输入增益值")}
                
                try:
                    value = float(value_text)
                except ValueError:
                    return {"success": False, "error": tr("gain.err_format_gain", "⚠️ 增益值格式错误，请输入有效数字")}
                
                from_unit = self._convert_from_unit.currentText()
                to_unit = self._convert_to_unit.currentText()
                
                # 映射单位名称
                unit_map = {"dBi": "dBi", "dBd": "dBd", tr("gain.linear_val", "线性值"): "linear"}
                from_u = unit_map.get(from_unit, from_unit)
                to_u = unit_map.get(to_unit, to_unit)
                
                if from_u == "linear" and value <= 0:
                    return {"success": False, "error": tr("gain.err_linear_positive", "⚠️ 线性增益必须为正值")}
                
                # 计算所有单位的值
                gain_dbi = self._calculator.convert_gain(value, from_u, "dBi")
                gain_dbd = self._calculator.convert_gain(value, from_u, "dBd")
                gain_linear = self._calculator.convert_gain(value, from_u, "linear")
                
                result = GainResult(
                    gain_dbi=gain_dbi,
                    gain_dbd=gain_dbd,
                    gain_linear=gain_linear,
                    method="单位转换"
                )
                return {"success": True, "result": result, "method": "convert"}
            
        except Exception as e:
            return {"success": False, "error": tr("gain.err_calc", "⚠️ 计算错误: {0}").format(str(e))}
    
    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()
        
        if calc_result["success"]:
            # 隐藏错误提示
            self._error_label.hide()
            
            result: GainResult = calc_result["result"]
            
            # 更新增益显示
            self._gain_dbi_label.setText(f"{result.gain_dbi:.2f} dBi")
            self._gain_dbd_label.setText(f"{result.gain_dbd:.2f} dBd")
            self._gain_linear_label.setText(f"{result.gain_linear:.2f}")
            
            # 更新天线类型评估
            quality = self._calculator.get_gain_quality(result.gain_dbi)
            self._quality_label.setText(quality)
            
            # 估算波束宽度
            theta_e, theta_h = self._calculator.estimate_beamwidth_from_gain(result.gain_dbi)
            self._beamwidth_estimate_label.setText(tr("gain.est_res", "≈ {0:.1f}° × {1:.1f}° (对称假设)").format(theta_e, theta_h))
            
        else:
            # 显示错误提示
            self._error_label.setText(calc_result.get("error", tr("gain.err_unknown", "未知错误")))
            self._error_label.show()
            
            self._gain_dbi_label.setText("--")
            self._gain_dbd_label.setText("--")
            self._gain_linear_label.setText("--")
            self._quality_label.setText("--")
            self._beamwidth_estimate_label.setText("--")
    
    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        return tr("gain.intuition_content", """
        <b>📡 {t_what_is}</b><br><br>
        
        {t_desc_1}<br><br>
        
        <b>🎯 {t_key_concept}:</b><br>
        • <b>dBi</b>: {t_dbi_desc}<br>
        • <b>dBd</b>: {t_dbd_desc}<br>
        • dBi = dBd + 2.15<br><br>
        
        <b>💡 {t_core}:</b> {t_core_desc}
        """).format(
            t_what_is=tr("gain.dd_what_is", "什么是天线增益？"),
            t_desc_1=tr("gain.dd_desc_1", "天线增益描述天线在特定方向上<b>聚焦能量</b>的能力。就像手电筒的反射镜把灯泡的光聚集成一束光一样。"),
            t_key_concept=tr("gain.dd_key_concept", "关键概念"),
            t_dbi_desc=tr("gain.dd_dbi_desc", "相对于理想全向天线的增益"),
            t_dbd_desc=tr("gain.dd_dbd_desc", "相对于半波偶极子的增益"),
            t_core=tr("gain.dd_core", "核心理解"),
            t_core_desc=tr("gain.dd_core_desc", "天线不能\"放大\"信号，只能把能量集中到特定方向，牺牲其他方向来换取更强的定向辐射。")
        )
    
    def get_math_model_content(self) -> Optional[str]:
        return tr("gain.math_content", """
        <b>📐 {t_formula}</b><br><br>
        
        <b>{t_method_beam}:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        G ≈ 41253 / (θ<sub>E</sub> × θ<sub>H</sub>)
        </span><br>
        {t_beam_desc}<br><br>
        
        <b>{t_method_apt}:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        G = η × (πD/λ)²
        </span><br>
        {t_apt_desc}<br><br>
        
        <b>{t_unit_conv}:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        G(dBi) = G(dBd) + 2.15<br>
        G(线性) = 10^(G(dB)/10)
        </span>
        """).format(
            t_formula=tr("gain.dd_formula", "增益公式"),
            t_method_beam=tr("gain.dd_method_beam", "波束宽度法"),
            t_beam_desc=tr("gain.dd_beam_desc", "其中 θ 为半功率(-3dB)波束宽度(度)"),
            t_method_apt=tr("gain.dd_method_apt", "口径效率法"),
            t_apt_desc=tr("gain.dd_apt_desc", "其中 η 为口径效率, D 为直径, λ 为波长"),
            t_unit_conv=tr("gain.dd_unit_conv", "单位转换")
        )
    
    def get_engineering_content(self) -> Optional[str]:
        return tr("gain.engineering_content", """
        <b>✅ {t_ref_title}:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>{t_dipole}</td><td>→ 2.15 dBi (0 dBd)</td></tr>
        <tr><td>{t_yagi}</td><td>→ 10~12 dBi</td></tr>
        <tr><td>{t_horn}</td><td>→ 15~25 dBi</td></tr>
        <tr><td>{t_para}</td><td>→ 35~40 dBi</td></tr>
        </table><br>
        
        <b>⚠️ {t_notice}:</b><br><br>
        
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ {t_err_title}
        </span><br>
        • {t_err_1}<br>
        • {t_err_2}<br><br>
        
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px; color: #276749;">
        💡 {t_tip_title}
        </span><br>
        {t_tip_1}
        """).format(
            t_ref_title=tr("gain.dd_ref_title", "典型天线增益参考"),
            t_dipole=tr("gain.dd_dipole", "半波偶极子"),
            t_yagi=tr("gain.dd_yagi", "八木天线(5单元)"),
            t_horn=tr("gain.dd_horn", "喇叭天线"),
            t_para=tr("gain.dd_para", "抛物面(1m@10GHz)"),
            t_notice=tr("gain.dd_notice", "注意事项"),
            t_err_title=tr("gain.dd_err_title", "常见误区"),
            t_err_1=tr("gain.dd_err_1", "波束宽度法是<b>近似公式</b>，精度约±1~2dB"),
            t_err_2=tr("gain.dd_err_2", "常数K因天线类型而异 (26000~41253)"),
            t_tip_title=tr("gain.dd_tip_title", "口径效率典型值"),
            t_tip_1=tr("gain.dd_tip_1", "抛物面: 0.5~0.6 | 喇叭: 0.6~0.7 | 优化型: 0.7~0.85")
        )
    
    def get_history_content(self) -> Optional[str]:
        return tr("gain.history_content", """
        <b>📜 {t_hist_title}</b><br><br>
        
        <b>{t_era1}</b> - {t_era1_desc}<br><br>
        
        <b>{t_era2}</b> - {t_era2_desc}<br><br>
        
        <b>{t_era3}</b> - {t_era3_desc}<br><br>
        
        <i>💭 {t_quote}</i>
        """).format(
            t_hist_title=tr("gain.hist_title", "天线增益的故事"),
            t_era1=tr("gain.hist_era1", "1888年"),
            t_era1_desc=tr("gain.hist_era1_desc", "赫兹用抛物面反射器进行了最早的\"高增益\"天线实验，证明了电磁波可以像光一样被聚焦。"),
            t_era2=tr("gain.hist_era2", "1926年"),
            t_era2_desc=tr("gain.hist_era2_desc", "八木秀次和宇田太郎发明了\"八木天线\"，成为世界上最著名的高增益天线，至今仍广泛用于电视接收。"),
            t_era3=tr("gain.hist_era3", "1960年代"),
            t_era3_desc=tr("gain.hist_era3_desc", "阿雷西博射电望远镜建成，305米口径提供了约70dBi的惊人增益，用于探测遥远的宇宙信号。"),
            t_quote=tr("gain.hist_quote", "天线增益是无源的，就像放大镜聚焦阳光——不创造能量，只是重新分配！")
        )

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
        
        # 处理下拉框选项
        if hasattr(self, '_aperture_shape'):
            self._aperture_shape.setItemText(0, tr("gain.shape_circ"))
            self._aperture_shape.setItemText(1, tr("gain.shape_rect"))
        
        if hasattr(self, '_constant_combo'):
            self._constant_combo.setItemText(0, tr("gain.const_ieee"))
            self._constant_combo.setItemText(1, tr("gain.const_uniform"))
            self._constant_combo.setItemText(2, tr("gain.const_typical"))
            
        if hasattr(self, '_convert_from_unit'):
            self._convert_from_unit.setItemText(2, tr("gain.linear_val"))
        if hasattr(self, '_convert_to_unit'):
            self._convert_to_unit.setItemText(2, tr("gain.linear_val"))
            
        if hasattr(self, '_efficiency_hint'):
            # 根据当前形状刷新效率提示
            if self._aperture_shape.currentIndex() == 0:
                self._efficiency_hint.setText(tr("gain.hint_circ"))
            else:
                self._efficiency_hint.setText(tr("gain.hint_rect"))
