# -*- coding: utf-8 -*-
"""
射频天线工具集 - 带宽计算工具
RF Antenna Toolkit - Bandwidth Calculator Tool

版本: v1.0.0
功能: 提供带宽计算界面，支持多种带宽定义的输入和转换
"""

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

from core.i18n import tr
from ui.base.tool_base import ToolBase
from core.antenna.bandwidth import BandwidthCalculator, BandwidthResult


class BandwidthTool(ToolBase):
    """
    带宽计算工具
    
    功能:
    - 输入频率范围/中心频率+带宽计算各种带宽指标
    - 支持绝对带宽、分数带宽、倍频程、Q值等
    """
    
    # 工具元信息
    tool_name = "带宽计算器"
    tool_icon = "📶"
    tool_category = "antenna"
    tool_description = "根据工作频率计算各种带宽定义指标"
    i18n_title_key = "bandwidth.tool_name"
    i18n_desc_key = "bandwidth.tool_desc"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化带宽计算工具"""
        # 计算器实例
        self._calculator = BandwidthCalculator()
        
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
        
        # ==================== 输入方式选择 ====================
        self._input_group = QGroupBox("输入方式")
        input_layout = QVBoxLayout(self._input_group)
        input_layout.setSpacing(12)
        
        # 输入类型选择
        self._input_type_group = QButtonGroup(self)
        
        # 方式1: 频率范围
        self._range_radio = QRadioButton("频率范围 (下限 ~ 上限)")
        self._range_radio.setChecked(True)
        self._input_type_group.addButton(self._range_radio, 0)
        input_layout.addWidget(self._range_radio)
        
        freq_range_layout = QHBoxLayout()
        
        self._lower_freq_input = QLineEdit()
        self._lower_freq_input.setPlaceholderText("下限频率")
        self._lower_freq_input.setValidator(QDoubleValidator(0.001, 1e12, 6))
        self._lower_freq_input.setText("2400")
        self._lower_freq_input.setMinimumWidth(120)
        freq_range_layout.addWidget(self._lower_freq_input, 1)
        
        freq_range_layout.addWidget(QLabel("~"))
        
        self._upper_freq_input = QLineEdit()
        self._upper_freq_input.setPlaceholderText("上限频率")
        self._upper_freq_input.setValidator(QDoubleValidator(0.001, 1e12, 6))
        self._upper_freq_input.setText("2500")
        self._upper_freq_input.setMinimumWidth(120)
        freq_range_layout.addWidget(self._upper_freq_input, 1)
        
        self._freq_range_unit = QComboBox()
        self._freq_range_unit.addItems(["MHz", "GHz", "kHz", "Hz"])
        self._freq_range_unit.setFixedWidth(60)
        freq_range_layout.addWidget(self._freq_range_unit)
        
        input_layout.addLayout(freq_range_layout)
        
        # 方式2: 中心频率 + 绝对带宽
        self._center_bw_radio = QRadioButton("中心频率 + 绝对带宽")
        self._input_type_group.addButton(self._center_bw_radio, 1)
        input_layout.addWidget(self._center_bw_radio)
        
        center_bw_layout = QHBoxLayout()
        
        self._center_freq_input = QLineEdit()
        self._center_freq_input.setPlaceholderText("中心频率")
        self._center_freq_input.setValidator(QDoubleValidator(0.001, 1e12, 6))
        self._center_freq_input.setText("2450")
        self._center_freq_input.setEnabled(False)
        self._center_freq_input.setMinimumWidth(120)
        center_bw_layout.addWidget(self._center_freq_input, 1)
        
        self._center_freq_unit = QComboBox()
        self._center_freq_unit.addItems(["MHz", "GHz", "kHz", "Hz"])
        self._center_freq_unit.setEnabled(False)
        self._center_freq_unit.setFixedWidth(60)
        center_bw_layout.addWidget(self._center_freq_unit)
        
        center_bw_layout.addWidget(QLabel("BW:"))
        
        self._abs_bw_input = QLineEdit()
        self._abs_bw_input.setPlaceholderText("带宽")
        self._abs_bw_input.setValidator(QDoubleValidator(0.001, 1e12, 6))
        self._abs_bw_input.setText("100")
        self._abs_bw_input.setEnabled(False)
        self._abs_bw_input.setMinimumWidth(120)
        center_bw_layout.addWidget(self._abs_bw_input, 1)
        
        self._abs_bw_unit = QComboBox()
        self._abs_bw_unit.addItems(["MHz", "GHz", "kHz", "Hz"])
        self._abs_bw_unit.setEnabled(False)
        self._abs_bw_unit.setFixedWidth(60)
        center_bw_layout.addWidget(self._abs_bw_unit)
        
        input_layout.addLayout(center_bw_layout)
        
        # 方式3: 中心频率 + 分数带宽
        self._center_fbw_radio = QRadioButton("中心频率 + 分数带宽 (%)")
        self._input_type_group.addButton(self._center_fbw_radio, 2)
        input_layout.addWidget(self._center_fbw_radio)
        
        center_fbw_layout = QHBoxLayout()
        
        self._center_freq2_input = QLineEdit()
        self._center_freq2_input.setPlaceholderText("中心频率")
        self._center_freq2_input.setValidator(QDoubleValidator(0.001, 1e12, 6))
        self._center_freq2_input.setText("2450")
        self._center_freq2_input.setEnabled(False)
        self._center_freq2_input.setMinimumWidth(120)
        center_fbw_layout.addWidget(self._center_freq2_input, 1)
        
        self._center_freq2_unit = QComboBox()
        self._center_freq2_unit.addItems(["MHz", "GHz", "kHz", "Hz"])
        self._center_freq2_unit.setEnabled(False)
        self._center_freq2_unit.setFixedWidth(60)
        center_fbw_layout.addWidget(self._center_freq2_unit)
        
        center_fbw_layout.addWidget(QLabel("FBW:"))
        
        self._fbw_input = QLineEdit()
        self._fbw_input.setPlaceholderText("0~200")
        self._fbw_input.setValidator(QDoubleValidator(0.001, 199, 4))
        self._fbw_input.setText("10")
        self._fbw_input.setEnabled(False)
        self._fbw_input.setMinimumWidth(120)
        center_fbw_layout.addWidget(self._fbw_input, 1)
        
        center_fbw_layout.addWidget(QLabel("%"))
        
        input_layout.addLayout(center_fbw_layout)
        
        # 切换输入类型
        self._input_type_group.buttonClicked.connect(self._on_input_type_changed)
        
        layout.addWidget(self._input_group)
        
        # ==================== 计算按钮 ====================
        self._calc_button = QPushButton("📶 计算带宽")
        self._calc_button.setObjectName("PrimaryButton")
        self._calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._calc_button.clicked.connect(self._do_calculate)
        layout.addWidget(self._calc_button)
        
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
        
        # 带宽特性评估
        quality_card = QWidget()
        quality_card.setObjectName("ResultPanel")
        quality_layout = QVBoxLayout(quality_card)
        
        self._quality_title_lbl = QLabel("带宽特性评估")
        self._quality_title_lbl.setObjectName("ResultTitle")
        quality_layout.addWidget(self._quality_title_lbl)
        
        self._quality_label = QLabel("--")
        self._quality_label.setObjectName("ResultValue")
        quality_layout.addWidget(self._quality_label)
        
        layout.addWidget(quality_card)
        
        # 频率结果
        freq_card = QWidget()
        freq_card.setObjectName("ResultPanel")
        freq_layout = QVBoxLayout(freq_card)
        
        self._freq_params_lbl = QLabel("📡 频率参数")
        self._freq_params_lbl.setObjectName("ResultTitle")
        freq_layout.addWidget(self._freq_params_lbl)
        
        freq_grid = QGridLayout()
        freq_grid.setSpacing(8)
        
        self._lbl_center_freq = QLabel("中心频率:")
        freq_grid.addWidget(self._lbl_center_freq, 0, 0)
        self._center_freq_label = QLabel("--")
        self._center_freq_label.setStyleSheet("font-weight: bold; color: #2C7BE5;")
        freq_grid.addWidget(self._center_freq_label, 0, 1)
        
        self._lbl_lower_freq = QLabel("下限频率:")
        freq_grid.addWidget(self._lbl_lower_freq, 1, 0)
        self._lower_freq_label = QLabel("--")
        freq_grid.addWidget(self._lower_freq_label, 1, 1)
        
        self._lbl_upper_freq = QLabel("上限频率:")
        freq_grid.addWidget(self._lbl_upper_freq, 1, 2)
        self._upper_freq_label = QLabel("--")
        freq_grid.addWidget(self._upper_freq_label, 1, 3)
        
        freq_layout.addLayout(freq_grid)
        layout.addWidget(freq_card)
        
        # 结果卡片标题引用字典 (用于 retranslate_ui)
        self._result_title_keys = {
            "abs_bw": "bandwidth.res_abs_bw",
            "fbw": "bandwidth.res_fbw",
            "octave": "bandwidth.res_octave",
            "q_factor": "bandwidth.res_q_factor",
        }
        self._result_title_labels = {}
        # 带宽指标结果网格
        results_grid = QGridLayout()
        results_grid.setSpacing(12)
        
        # 绝对带宽
        abs_bw_card = self._create_result_card("abs_bw", "绝对带宽", "")
        results_grid.addWidget(abs_bw_card, 0, 0)
        
        # 分数带宽
        fbw_card = self._create_result_card("fbw", "分数带宽", "%")
        results_grid.addWidget(fbw_card, 0, 1)
        
        # 倍频程
        octave_card = self._create_result_card("octave", "倍频程", "oct")
        results_grid.addWidget(octave_card, 1, 0)
        
        # Q值
        q_card = self._create_result_card("q_factor", "Q值", "")
        results_grid.addWidget(q_card, 1, 1)
        
        layout.addLayout(results_grid)
        
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
        if hasattr(self, "_result_title_labels"):
            self._result_title_labels[key] = title_label
        
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
        
        # 方式0: 频率范围
        self._lower_freq_input.setEnabled(button_id == 0)
        self._upper_freq_input.setEnabled(button_id == 0)
        self._freq_range_unit.setEnabled(button_id == 0)
        
        # 方式1: 中心频率 + 绝对带宽
        self._center_freq_input.setEnabled(button_id == 1)
        self._center_freq_unit.setEnabled(button_id == 1)
        self._abs_bw_input.setEnabled(button_id == 1)
        self._abs_bw_unit.setEnabled(button_id == 1)
        
        # 方式2: 中心频率 + 分数带宽
        self._center_freq2_input.setEnabled(button_id == 2)
        self._center_freq2_unit.setEnabled(button_id == 2)
        self._fbw_input.setEnabled(button_id == 2)
    
    def calculate(self) -> Dict[str, Any]:
        """执行计算，带详细验证提示"""
        try:
            input_type = self._input_type_group.checkedId()
            
            if input_type == 0:  # 频率范围
                lower_text = self._lower_freq_input.text().strip()
                upper_text = self._upper_freq_input.text().strip()
                
                if not lower_text:
                    return {"success": False, "error": tr("bandwidth.err_no_lower", "⚠️ 请输入下限频率")}
                if not upper_text:
                    return {"success": False, "error": tr("bandwidth.err_no_upper", "⚠️ 请输入上限频率")}
                
                try:
                    lower = float(lower_text)
                    upper = float(upper_text)
                except ValueError:
                    return {"success": False, "error": tr("bandwidth.err_format", "⚠️ 频率格式错误，请输入有效数字")}
                
                if lower <= 0:
                    return {"success": False, "error": tr("bandwidth.err_lower_positive", "⚠️ 下限频率必须为正值")}
                if upper <= 0:
                    return {"success": False, "error": tr("bandwidth.err_upper_positive", "⚠️ 上限频率必须为正值")}
                if upper <= lower:
                    return {"success": False, "error": tr("bandwidth.err_upper_gt_lower", "⚠️ 上限频率必须大于下限频率\n（当前: 上限={:.2f} ≤ 下限={:.2f}）").format(upper, lower)}
                
                unit = self._freq_range_unit.currentText()
                lower_hz = self._calculator.parse_freq_with_unit(lower, unit)
                upper_hz = self._calculator.parse_freq_with_unit(upper, unit)
                result = self._calculator.calculate_from_freq_range(lower_hz, upper_hz)
                
            elif input_type == 1:  # 中心频率 + 绝对带宽
                center_text = self._center_freq_input.text().strip()
                bw_text = self._abs_bw_input.text().strip()
                
                if not center_text:
                    return {"success": False, "error": tr("bandwidth.err_no_center", "⚠️ 请输入中心频率")}
                if not bw_text:
                    return {"success": False, "error": tr("bandwidth.err_no_abs_bw", "⚠️ 请输入绝对带宽")}
                
                try:
                    center = float(center_text)
                    bw = float(bw_text)
                except ValueError:
                    return {"success": False, "error": tr("bandwidth.err_format2", "⚠️ 频率/带宽格式错误，请输入有效数字")}
                
                if center <= 0:
                    return {"success": False, "error": tr("bandwidth.err_center_positive", "⚠️ 中心频率必须为正值")}
                if bw <= 0:
                    return {"success": False, "error": tr("bandwidth.err_bw_positive", "⚠️ 带宽必须为正值")}
                
                center_unit = self._center_freq_unit.currentText()
                bw_unit = self._abs_bw_unit.currentText()
                center_hz = self._calculator.parse_freq_with_unit(center, center_unit)
                bw_hz = self._calculator.parse_freq_with_unit(bw, bw_unit)
                
                if bw_hz >= 2 * center_hz:
                    return {"success": False, "error": tr("bandwidth.err_bw_too_large", "⚠️ 带宽不能超过2倍中心频率\n（否则下限频率会为负值）")}
                
                result = self._calculator.calculate_from_center_and_bw(center_hz, bw_hz)
                
            else:  # 中心频率 + 分数带宽
                center_text = self._center_freq2_input.text().strip()
                fbw_text = self._fbw_input.text().strip()
                
                if not center_text:
                    return {"success": False, "error": tr("bandwidth.err_no_center", "⚠️ 请输入中心频率")}
                if not fbw_text:
                    return {"success": False, "error": tr("bandwidth.err_no_fbw", "⚠️ 请输入分数带宽")}
                
                try:
                    center = float(center_text)
                    fbw = float(fbw_text)
                except ValueError:
                    return {"success": False, "error": tr("bandwidth.err_format2", "⚠️ 频率/带宽格式错误，请输入有效数字")}
                
                if center <= 0:
                    return {"success": False, "error": tr("bandwidth.err_center_positive", "⚠️ 中心频率必须为正值")}
                if fbw <= 0:
                    return {"success": False, "error": tr("bandwidth.err_fbw_positive", "⚠️ 分数带宽必须为正值")}
                if fbw >= 200:
                    return {"success": False, "error": tr("bandwidth.err_fbw_too_large", "⚠️ 分数带宽不能超过200%\n（否则下限频率会为负值）")}
                
                center_unit = self._center_freq2_unit.currentText()
                center_hz = self._calculator.parse_freq_with_unit(center, center_unit)
                result = self._calculator.calculate_from_center_and_fbw(center_hz, fbw)
            
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": tr("bandwidth.err_calc", "⚠️ 计算错误: {0}").format(str(e))}
    
    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()
        
        if calc_result["success"]:
            # 隐藏错误提示
            self._error_label.hide()
            
            result: BandwidthResult = calc_result["result"]
            
            # 更新频率显示
            center_val, center_unit = self._calculator.freq_to_best_unit(result.center_freq_hz)
            lower_val, lower_unit = self._calculator.freq_to_best_unit(result.lower_freq_hz)
            upper_val, upper_unit = self._calculator.freq_to_best_unit(result.upper_freq_hz)
            bw_val, bw_unit = self._calculator.freq_to_best_unit(result.absolute_bw_hz)
            
            self._center_freq_label.setText(f"{center_val:.4f} {center_unit}")
            self._lower_freq_label.setText(f"{lower_val:.4f} {lower_unit}")
            self._upper_freq_label.setText(f"{upper_val:.4f} {upper_unit}")
            
            # 更新带宽指标
            self._result_labels["abs_bw"].setText(f"{bw_val:.4f} {bw_unit}")
            self._result_labels["fbw"].setText(f"{result.fractional_bw_percent:.2f}")
            self._result_labels["octave"].setText(f"{result.octave_bw:.4f}")
            self._result_labels["q_factor"].setText(f"{result.q_factor:.2f}")
            
            # 更新带宽特性评估
            quality = self._calculator.get_bandwidth_quality(result.fractional_bw_percent)
            self._quality_label.setText(quality)
            
        else:
            # 显示错误提示
            self._error_label.setText(calc_result.get("error", tr("bandwidth.err_unknown", "未知错误")))
            self._error_label.show()
            
            self._center_freq_label.setText("--")
            self._lower_freq_label.setText("--")
            self._upper_freq_label.setText("--")
            for key in ["abs_bw", "fbw", "octave", "q_factor"]:
                self._result_labels[key].setText("--")
            self._quality_label.setText("--")
    

    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新所有 UI 文字"""
        super().retranslate_ui(lang)
        # 输入面板
        if hasattr(self, '_input_group'):
            self._input_group.setTitle(tr("bandwidth.input_method"))
        if hasattr(self, '_range_radio'):
            self._range_radio.setText(tr("bandwidth.method_range"))
        if hasattr(self, '_center_bw_radio'):
            self._center_bw_radio.setText(tr("bandwidth.method_center_bw"))
        if hasattr(self, '_center_fbw_radio'):
            self._center_fbw_radio.setText(tr("bandwidth.method_center_fbw"))
            
        # 输入标签
        if hasattr(self, '_lbl_lower'):
            self._lbl_lower.setText(tr("bandwidth.lower_freq"))
        if hasattr(self, '_lbl_upper'):
            self._lbl_upper.setText(tr("bandwidth.upper_freq"))
        if hasattr(self, '_lbl_center'):
            self._lbl_center.setText(tr("bandwidth.center_freq"))
        if hasattr(self, '_lbl_abs_bw'):
            self._lbl_abs_bw.setText(tr("bandwidth.abs_bw"))
        if hasattr(self, '_lbl_center2'):
            self._lbl_center2.setText(tr("bandwidth.center_freq"))
        if hasattr(self, '_lbl_fbw'):
            self._lbl_fbw.setText(tr("bandwidth.fbw_0_200"))
            
        # 按钮
        if hasattr(self, '_calc_btn'):
            self._calc_btn.setText(tr("bandwidth.btn_calculate"))
            
        # 结果大盘
        if hasattr(self, '_res_group'):
            self._res_group.setTitle(tr("bandwidth.quality_eval"))
        if hasattr(self, '_freq_group'):
            self._freq_group.setTitle(tr("bandwidth.freq_params"))
            
        # 频率标签
        labels_map = {
            "_lbl_res_center": "bandwidth.lbl_center_freq",
            "_lbl_res_lower": "bandwidth.lbl_lower_freq",
            "_lbl_res_upper": "bandwidth.lbl_upper_freq"
        }
        for attr, key in labels_map.items():
            if hasattr(self, attr):
                getattr(self, attr).setText(tr(key))
                
        # 结果卡片标题
        # 由于 Card 内部可能没保存标签，这里暂时跳过，
        # 理想做法是在 _create_result_card 中保存标题标签
        
    def get_intuition_content(self) -> str:
        return tr("bandwidth.intuition")

    def get_math_model_content(self) -> str:
        return tr("bandwidth.math_model")

    def get_engineering_content(self) -> str:
        return tr("bandwidth.eng_content")

    def get_history_content(self) -> str:
        return tr("bandwidth.history_content")

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新所有 UI 文字"""
        # 调用父类 (会自动刷新 Deep Dive 面板，因为它在 ToolBase 中被定义为根据这些 get_xxx 函数重新获取内容)
        super().retranslate_ui(lang)
        
        # 输入面板
        if hasattr(self, '_input_group'):
            self._input_group.setTitle(tr("bandwidth.input_method"))
        if hasattr(self, '_range_radio'):
            self._range_radio.setText(tr("bandwidth.method_range"))
        if hasattr(self, '_center_bw_radio'):
            self._center_bw_radio.setText(tr("bandwidth.method_center_bw"))
        if hasattr(self, '_center_fbw_radio'):
            self._center_fbw_radio.setText(tr("bandwidth.method_center_fbw"))
            
        # 输入框占位符
        if hasattr(self, '_lower_freq_input'):
            self._lower_freq_input.setPlaceholderText(tr("bandwidth.lower_freq"))
        if hasattr(self, '_upper_freq_input'):
            self._upper_freq_input.setPlaceholderText(tr("bandwidth.upper_freq"))
        if hasattr(self, '_center_freq_input'):
            self._center_freq_input.setPlaceholderText(tr("bandwidth.center_freq"))
        if hasattr(self, '_center_freq2_input'):
            self._center_freq2_input.setPlaceholderText(tr("bandwidth.center_freq"))
        if hasattr(self, '_abs_bw_input'):
            self._abs_bw_input.setPlaceholderText(tr("bandwidth.abs_bw"))
        if hasattr(self, '_fbw_input'):
            self._fbw_input.setPlaceholderText(tr("bandwidth.fbw_0_200"))
            
        # 按钮
        if hasattr(self, '_calc_button'):
            self._calc_button.setText(tr("bandwidth.btn_calculate"))
            
        # 结果面板
        if hasattr(self, '_quality_title_lbl'):
            self._quality_title_lbl.setText(tr("bandwidth.quality_eval"))
        if hasattr(self, '_freq_params_lbl'):
            self._freq_params_lbl.setText(tr("bandwidth.freq_params"))
        if hasattr(self, '_lbl_center_freq'):
            self._lbl_center_freq.setText(tr("bandwidth.lbl_center_freq"))
        if hasattr(self, '_lbl_lower_freq'):
            self._lbl_lower_freq.setText(tr("bandwidth.lbl_lower_freq"))
        if hasattr(self, '_lbl_upper_freq'):
            self._lbl_upper_freq.setText(tr("bandwidth.lbl_upper_freq"))
            
        # 结果卡片标题
        if hasattr(self, '_result_title_labels') and hasattr(self, '_result_title_keys'):
            for key, i18n_key in self._result_title_keys.items():
                if key in self._result_title_labels:
                    self._result_title_labels[key].setText(tr(i18n_key))
        
        # 触发一次计算刷新评估结果的翻译
        self._do_calculate()
