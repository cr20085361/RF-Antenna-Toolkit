# -*- coding: utf-8 -*-
"""
射频天线工具集 - 级联驻波计算工具
RF Antenna Toolkit - Cascaded VSWR Calculator Tool

版本: v2.0.0
功能: 计算多个射频组件级联后的总驻波比范围
"""

from typing import Dict, Any, Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

from core.i18n import tr
from ui.base.tool_base import ToolBase
from core.rf.cascade import CascadeCalculator, CascadeResult


class CascadeTool(ToolBase):
    """
    级联驻波计算工具
    
    功能:
    - 计算多个射频组件级联后的驻波范围
    - 支持2~4级组件输入
    - 支持VSWR和回波损耗两种输入方式
    - 显示最佳/最差情况分析
    
    适用场景:
    - 同轴转波导 + 喇叭天线
    - 功分器 + 天线阵列
    - 多级馈电网络
    """
    
    # 工具元信息
    tool_name = tr("cascade.tool_name")
    tool_icon = "🔗"
    tool_category = "rf"
    tool_description = tr("cascade.tool_desc")
    i18n_title_key = "cascade.tool_name"
    i18n_desc_key = "cascade.tool_desc"
    
    # 最大支持级联数
    MAX_STAGES = 4
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化级联驻波工具"""
        # 计算器实例
        self._calculator = CascadeCalculator()
        
        # 输入控件引用
        self._stage_inputs: List[Dict] = []
        
        # 调用父类初始化
        super().__init__(parent)
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 输入方式选择 ====================
        self._grp_input_mode = QGroupBox(tr("cascade.group_mode"))
        input_mode_layout = QHBoxLayout(self._grp_input_mode)
        
        self._input_mode = QComboBox()
        self._input_mode.addItems([tr("cascade.mode_vswr"), tr("cascade.mode_rl")])
        self._input_mode.currentIndexChanged.connect(self._on_input_mode_changed)
        input_mode_layout.addWidget(self._input_mode)
        
        layout.addWidget(self._grp_input_mode)
        
        # ==================== 组件输入区 ====================
        self._grp_stages = QGroupBox(tr("cascade.group_stages"))
        stages_layout = QVBoxLayout(self._grp_stages)
        stages_layout.setSpacing(12)
        
        # 创建各级输入
        self._stage_inputs = []
        stage_names = [
            tr("cascade.stage_1"),
            tr("cascade.stage_2"),
            tr("cascade.stage_3"),
            tr("cascade.stage_4")
        ]
        
        for i in range(self.MAX_STAGES):
            stage_widget = self._create_stage_input(i, stage_names[i])
            stages_layout.addWidget(stage_widget)
        
        layout.addWidget(self._grp_stages)
        
        # ==================== 计算按钮 ====================
        calc_button = QPushButton(tr("cascade.btn_calc"))
        calc_button.setObjectName("PrimaryButton")
        calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_button.clicked.connect(self._do_calculate)
        layout.addWidget(calc_button)
        
        layout.addStretch()
        
        return panel
    
    def _create_stage_input(self, index: int, label: str) -> QWidget:
        """创建单级输入控件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 4, 0, 4)
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(160)
        layout.addWidget(label_widget)
        
        # 输入框
        input_field = QLineEdit()
        input_field.setPlaceholderText("VSWR" if index < 2 else tr("cascade.place_ignore"))
        input_field.setValidator(QDoubleValidator(0.001, 1000, 4))
        
        # 前两级有默认值
        if index == 0:
            input_field.setText("1.3")
        elif index == 1:
            input_field.setText("1.5")
        
        layout.addWidget(input_field)
        
        # 单位标签
        unit_label = QLabel(":1")
        unit_label.setMinimumWidth(30)
        layout.addWidget(unit_label)
        
        # 保存引用
        self._stage_inputs.append({
            "widget": widget,
            "input": input_field,
            "label": label_widget,
            "unit": unit_label,
            "name_label": label
        })
        
        return widget
    
    def _on_input_mode_changed(self, index: int):
        """输入方式切换"""
        is_vswr = index == 0
        
        for stage in self._stage_inputs:
            if is_vswr:
                stage["input"].setPlaceholderText("VSWR")
                stage["unit"].setText(":1")
            else:
                stage["input"].setPlaceholderText("dB")
                stage["unit"].setText("dB")
    
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
        
        # 匹配质量评估
        quality_card = QWidget()
        quality_card.setObjectName("ResultPanel")
        quality_layout = QVBoxLayout(quality_card)
        
        quality_title = QLabel(tr("cascade.title_eval"))
        quality_title.setObjectName("ResultTitle")
        quality_layout.addWidget(quality_title)
        
        self._quality_label = QLabel("--")
        self._quality_label.setObjectName("ResultValue")
        quality_layout.addWidget(self._quality_label)
        
        layout.addWidget(quality_card)
        
        # 驻波范围结果
        vswr_card = QWidget()
        vswr_card.setObjectName("ResultPanel")
        vswr_layout = QVBoxLayout(vswr_card)
        
        vswr_title = QLabel(tr("cascade.title_vswr"))
        vswr_title.setObjectName("ResultTitle")
        vswr_layout.addWidget(vswr_title)
        
        vswr_grid = QGridLayout()
        vswr_grid.setSpacing(12)
        
        # 最佳情况
        vswr_grid.addWidget(QLabel(tr("cascade.lbl_best_vswr")), 0, 0)
        self._vswr_min_label = QLabel("--")
        self._vswr_min_label.setStyleSheet("font-weight: bold; color: #38A169; font-size: 16px;")
        vswr_grid.addWidget(self._vswr_min_label, 0, 1)
        
        # 最差情况
        vswr_grid.addWidget(QLabel(tr("cascade.lbl_worst_vswr")), 1, 0)
        self._vswr_max_label = QLabel("--")
        self._vswr_max_label.setStyleSheet("font-weight: bold; color: #E53E3E; font-size: 16px;")
        vswr_grid.addWidget(self._vswr_max_label, 1, 1)
        
        vswr_layout.addLayout(vswr_grid)
        layout.addWidget(vswr_card)
        
        # 回波损耗结果
        rl_card = QWidget()
        rl_card.setObjectName("ResultPanel")
        rl_layout = QVBoxLayout(rl_card)
        
        rl_title = QLabel(tr("cascade.title_rl"))
        rl_title.setObjectName("ResultTitle")
        rl_layout.addWidget(rl_title)
        
        rl_grid = QGridLayout()
        rl_grid.setSpacing(12)
        
        rl_grid.addWidget(QLabel(tr("cascade.lbl_best_rl")), 0, 0)
        self._rl_best_label = QLabel("--")
        rl_grid.addWidget(self._rl_best_label, 0, 1)
        
        rl_grid.addWidget(QLabel(tr("cascade.lbl_worst_rl")), 1, 0)
        self._rl_worst_label = QLabel("--")
        rl_grid.addWidget(self._rl_worst_label, 1, 1)
        
        rl_layout.addLayout(rl_grid)
        layout.addWidget(rl_card)
        
        # 反射系数结果
        gamma_card = QWidget()
        gamma_card.setObjectName("ResultPanel")
        gamma_layout = QVBoxLayout(gamma_card)
        
        gamma_title = QLabel(tr("cascade.title_gamma"))
        gamma_title.setObjectName("ResultTitle")
        gamma_layout.addWidget(gamma_title)
        
        gamma_grid = QGridLayout()
        gamma_grid.setSpacing(12)
        
        gamma_grid.addWidget(QLabel(tr("cascade.lbl_min_gamma")), 0, 0)
        self._gamma_min_label = QLabel("--")
        gamma_grid.addWidget(self._gamma_min_label, 0, 1)
        
        gamma_grid.addWidget(QLabel(tr("cascade.lbl_max_gamma")), 1, 0)
        self._gamma_max_label = QLabel("--")
        gamma_grid.addWidget(self._gamma_max_label, 1, 1)
        
        gamma_layout.addLayout(gamma_grid)
        layout.addWidget(gamma_card)
        
        # 失配损耗
        loss_card = QWidget()
        loss_card.setObjectName("ResultPanel")
        loss_layout = QVBoxLayout(loss_card)
        
        loss_title = QLabel(tr("cascade.title_loss"))
        loss_title.setObjectName("ResultTitle")
        loss_layout.addWidget(loss_title)
        
        self._mismatch_loss_label = QLabel("--")
        loss_layout.addWidget(self._mismatch_loss_label)
        
        layout.addWidget(loss_card)
        
        layout.addStretch()
        
        return panel
    
    def calculate(self) -> Dict[str, Any]:
        """执行计算，带详细验证提示"""
        try:
            is_vswr_mode = self._input_mode.currentIndex() == 0
            
            # 收集有效输入
            values = []
            for i, stage in enumerate(self._stage_inputs):
                text = stage["input"].text().strip()
                if text:
                    try:
                        value = float(text)
                    except ValueError:
                        return {"success": False, "error": tr("cascade.err_fmt_pl").format(stage=i+1)}
                    
                    if is_vswr_mode:
                        if value < 1:
                            return {"success": False, "error": tr("cascade.err_vswr_val_pl").format(stage=i+1)}
                    else:
                        if value <= 0:
                            return {"success": False, "error": tr("cascade.err_rl_pos_pl").format(stage=i+1)}
                    
                    values.append(value)
            
            # 验证至少两级
            if len(values) < 2:
                return {"success": False, "error": tr("cascade.err_min_stage")}
            
            # 执行计算
            if is_vswr_mode:
                result = self._calculator.calculate_cascade(values)
            else:
                result = self._calculator.calculate_from_return_loss(values)
            
            return {"success": True, "result": result}
            
        except Exception as e:
            return {"success": False, "error": tr("cascade.err_calc", "⚠️ 计算错误: {err}").format(err=str(e))}
    
    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()
        
        if calc_result["success"]:
            # 隐藏错误提示
            self._error_label.hide()
            
            result: CascadeResult = calc_result["result"]
            
            # 更新驻波范围
            self._vswr_min_label.setText(f"{result.vswr_min:.3f}:1")
            self._vswr_max_label.setText(f"{result.vswr_max:.3f}:1")
            
            # 更新回波损耗
            if result.return_loss_best > 100:
                self._rl_best_label.setText(tr("cascade.rl_perfect", "> 100 dB (近似完美)"))
            else:
                self._rl_best_label.setText(f"{result.return_loss_best:.2f} dB")
            self._rl_worst_label.setText(f"{result.return_loss_worst:.2f} dB")
            
            # 更新反射系数
            self._gamma_min_label.setText(f"{result.gamma_min:.4f}")
            self._gamma_max_label.setText(f"{result.gamma_max:.4f}")
            
            # 更新质量评估
            quality = self._calculator.get_quality_assessment(result.vswr_max)
            self._quality_label.setText(quality)
            
            # 更新失配损耗
            mismatch_loss = self._calculator.get_mismatch_loss(result.vswr_max)
            self._mismatch_loss_label.setText(f"{mismatch_loss:.3f} dB")
            
        else:
            # 显示错误提示
            self._error_label.setText(calc_result.get("error", tr("cascade.err_unknown", "未知错误")))
            self._error_label.show()
            
            self._vswr_min_label.setText("--")
            self._vswr_max_label.setText("--")
            self._rl_best_label.setText("--")
            self._rl_worst_label.setText("--")
            self._gamma_min_label.setText("--")
            self._gamma_max_label.setText("--")
            self._quality_label.setText("--")
            self._mismatch_loss_label.setText("--")
    

    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新 UI 文字"""
        super().retranslate_ui(lang)
        if hasattr(self, '_grp_input_mode'):
            self._grp_input_mode.setTitle(tr("cascade.group_mode"))
        if hasattr(self, '_input_mode'):
            current_idx = self._input_mode.currentIndex()
            self._input_mode.clear()
            self._input_mode.addItems([tr("cascade.mode_vswr"), tr("cascade.mode_rl")])
            self._input_mode.setCurrentIndex(current_idx)
            
        if hasattr(self, '_grp_stages'):
            self._grp_stages.setTitle(tr("cascade.group_stages"))
            
        stage_names = [
            tr("cascade.stage_1"), tr("cascade.stage_2"),
            tr("cascade.stage_3"), tr("cascade.stage_4")
        ]
        
        is_vswr = self._input_mode.currentIndex() == 0
        
        for i, stage in enumerate(self._stage_inputs):
            if i < len(stage_names):
                stage["label"].setText(stage_names[i])
            
            # 刷新占位符
            if i >= 2:
                stage["input"].setPlaceholderText(tr("cascade.place_ignore"))
            else:
                stage["input"].setPlaceholderText("VSWR" if is_vswr else "dB")
            
            # 刷新单位
            stage["unit"].setText(":1" if is_vswr else "dB")

        if hasattr(self, '_quality_label'):
             # 触发重新显示计算结果（包含翻译）
             self._do_calculate()

    # ==================== 知识面板内容 ====================

    def get_intuition_content(self) -> str:
        return tr("cascade.intuition_content")

    def get_math_model_content(self) -> str:
        return tr("cascade.math_content")

    def get_engineering_content(self) -> str:
        return tr("cascade.engineering_content")

    def get_history_content(self) -> str:
        return tr("cascade.history_content")
