# -*- coding: utf-8 -*-
"""
射频天线工具集 - 级联驻波计算工具
RF Antenna Toolkit - Cascaded VSWR Calculator Tool

版本: v1.0.0
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
    tool_name = "级联驻波"
    tool_icon = "🔗"
    tool_category = "rf"
    tool_description = "计算多组件级联后的驻波范围"
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
        input_mode_group = QGroupBox("输入方式")
        input_mode_layout = QHBoxLayout(input_mode_group)
        
        self._input_mode = QComboBox()
        self._input_mode.addItems(["VSWR (驻波比)", "回波损耗 (dB)"])
        self._input_mode.currentIndexChanged.connect(self._on_input_mode_changed)
        input_mode_layout.addWidget(self._input_mode)
        
        layout.addWidget(input_mode_group)
        
        # ==================== 组件输入区 ====================
        stages_group = QGroupBox("级联组件 (至少2级)")
        stages_layout = QVBoxLayout(stages_group)
        stages_layout.setSpacing(12)
        
        # 创建各级输入
        self._stage_inputs = []
        stage_names = [
            "第1级 (如: 同轴转波导)",
            "第2级 (如: 喇叭天线)",
            "第3级 (可选)",
            "第4级 (可选)"
        ]
        
        for i in range(self.MAX_STAGES):
            stage_widget = self._create_stage_input(i, stage_names[i])
            stages_layout.addWidget(stage_widget)
        
        layout.addWidget(stages_group)
        
        # ==================== 计算按钮 ====================
        calc_button = QPushButton("🔗 计算级联驻波")
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
        input_field.setPlaceholderText("VSWR" if index < 2 else "留空忽略")
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
        
        quality_title = QLabel("级联匹配评估 (最差情况)")
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
        
        vswr_title = QLabel("🔗 级联驻波范围")
        vswr_title.setObjectName("ResultTitle")
        vswr_layout.addWidget(vswr_title)
        
        vswr_grid = QGridLayout()
        vswr_grid.setSpacing(12)
        
        # 最佳情况
        vswr_grid.addWidget(QLabel("最佳情况 (反相抵消):"), 0, 0)
        self._vswr_min_label = QLabel("--")
        self._vswr_min_label.setStyleSheet("font-weight: bold; color: #38A169; font-size: 16px;")
        vswr_grid.addWidget(self._vswr_min_label, 0, 1)
        
        # 最差情况
        vswr_grid.addWidget(QLabel("最差情况 (同相叠加):"), 1, 0)
        self._vswr_max_label = QLabel("--")
        self._vswr_max_label.setStyleSheet("font-weight: bold; color: #E53E3E; font-size: 16px;")
        vswr_grid.addWidget(self._vswr_max_label, 1, 1)
        
        vswr_layout.addLayout(vswr_grid)
        layout.addWidget(vswr_card)
        
        # 回波损耗结果
        rl_card = QWidget()
        rl_card.setObjectName("ResultPanel")
        rl_layout = QVBoxLayout(rl_card)
        
        rl_title = QLabel("📉 回波损耗范围")
        rl_title.setObjectName("ResultTitle")
        rl_layout.addWidget(rl_title)
        
        rl_grid = QGridLayout()
        rl_grid.setSpacing(12)
        
        rl_grid.addWidget(QLabel("最佳回波损耗:"), 0, 0)
        self._rl_best_label = QLabel("--")
        rl_grid.addWidget(self._rl_best_label, 0, 1)
        
        rl_grid.addWidget(QLabel("最差回波损耗:"), 1, 0)
        self._rl_worst_label = QLabel("--")
        rl_grid.addWidget(self._rl_worst_label, 1, 1)
        
        rl_layout.addLayout(rl_grid)
        layout.addWidget(rl_card)
        
        # 反射系数结果
        gamma_card = QWidget()
        gamma_card.setObjectName("ResultPanel")
        gamma_layout = QVBoxLayout(gamma_card)
        
        gamma_title = QLabel("📊 反射系数范围")
        gamma_title.setObjectName("ResultTitle")
        gamma_layout.addWidget(gamma_title)
        
        gamma_grid = QGridLayout()
        gamma_grid.setSpacing(12)
        
        gamma_grid.addWidget(QLabel("|Γ| 最小:"), 0, 0)
        self._gamma_min_label = QLabel("--")
        gamma_grid.addWidget(self._gamma_min_label, 0, 1)
        
        gamma_grid.addWidget(QLabel("|Γ| 最大:"), 1, 0)
        self._gamma_max_label = QLabel("--")
        gamma_grid.addWidget(self._gamma_max_label, 1, 1)
        
        gamma_layout.addLayout(gamma_grid)
        layout.addWidget(gamma_card)
        
        # 失配损耗
        loss_card = QWidget()
        loss_card.setObjectName("ResultPanel")
        loss_layout = QVBoxLayout(loss_card)
        
        loss_title = QLabel("⚡ 失配损耗 (最差情况)")
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
                        return {"success": False, "error": f"⚠️ 第{i+1}级输入格式错误，请输入有效数字"}
                    
                    if is_vswr_mode:
                        if value < 1:
                            return {"success": False, "error": f"⚠️ 第{i+1}级 VSWR 必须 ≥ 1\n（完美匹配时 VSWR = 1:1）"}
                    else:
                        if value <= 0:
                            return {"success": False, "error": f"⚠️ 第{i+1}级回波损耗必须为正值 (dB)"}
                    
                    values.append(value)
            
            # 验证至少两级
            if len(values) < 2:
                return {"success": False, "error": "⚠️ 至少需要输入2级组件的驻波值\n才能计算级联效果"}
            
            # 执行计算
            if is_vswr_mode:
                result = self._calculator.calculate_cascade(values)
            else:
                result = self._calculator.calculate_from_return_loss(values)
            
            return {"success": True, "result": result}
            
        except Exception as e:
            return {"success": False, "error": f"⚠️ 计算错误: {str(e)}"}
    
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
                self._rl_best_label.setText("> 100 dB (近似完美)")
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
            self._error_label.setText(calc_result.get("error", "未知错误"))
            self._error_label.show()
            
            self._vswr_min_label.setText("--")
            self._vswr_max_label.setText("--")
            self._rl_best_label.setText("--")
            self._rl_worst_label.setText("--")
            self._gamma_min_label.setText("--")
            self._gamma_max_label.setText("--")
            self._quality_label.setText("--")
            self._mismatch_loss_label.setText("--")
    
    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        """直观理解 - 物理本质"""
        return """
        <b>🔗 什么是级联驻波？</b><br><br>
        
        当两个有各自驻波的组件连接时，由于它们之间的<b>电气长度</b>
        （相位）未知，总驻波会在一个范围内变化：<br><br>
        
        <b>🎯 两种极端情况:</b><br>
        • <b>同相叠加</b>: 两者反射波同相，驻波最大<br>
        • <b>反相抵消</b>: 两者反射波反相，驻波最小<br><br>
        
        <b>💡 工程意义:</b><br>
        工程设计时应按<b>最差情况</b>考虑，确保极端情况下
        系统仍能正常工作。
        """
    
    def get_math_model_content(self) -> Optional[str]:
        """数学模型 - 精确公式"""
        return """
        <b>📐 级联反射系数</b><br><br>
        
        <b>两级级联 (相位未知):</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        |Γ|<sub>max</sub> = |Γ₁| + |Γ₂|<br>
        |Γ|<sub>min</sub> = ||Γ₁| - |Γ₂||
        </span><br><br>
        
        <b>VSWR与Γ的关系:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        Γ = (VSWR - 1) / (VSWR + 1)<br>
        VSWR = (1 + |Γ|) / (1 - |Γ|)
        </span><br><br>
        
        <b>失配损耗:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        L<sub>mismatch</sub> = -10 × log₁₀(1 - |Γ|²) dB
        </span>
        """
    
    def get_engineering_content(self) -> Optional[str]:
        """工程边界 - 适用范围与避坑"""
        return """
        <b>✅ 典型级联场景:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>同轴转波导</td><td>VSWR 1.2~1.5</td></tr>
        <tr><td>喇叭天线</td><td>VSWR 1.1~1.3</td></tr>
        <tr><td>级联后</td><td>VSWR 1.1~2.0 范围</td></tr>
        </table><br>
        
        <b>⚠️ 注意事项:</b><br><br>
        
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 常见误区
        </span><br>
        • 不能简单相加VSWR值，必须转换为Γ<br>
        • 实际驻波在范围内，不是固定值<br><br>
        
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px; color: #276749;">
        💡 工程建议
        </span><br>
        • 设计按最差情况（同相叠加）考虑<br>
        • 各级VSWR尽量控制在1.5以下<br>
        • 可调相位线优化匹配
        """
    
    def get_history_content(self) -> Optional[str]:
        """发现历史 - 趣味故事"""
        return """
        <b>📜 驻波比的故事</b><br><br>
        
        <b>1930年代</b> - 传输线理论成熟，工程师们发现
        不同组件连接时驻波会发生复杂变化。<br><br>
        
        <b>1940年代</b> - 雷达技术的发展推动了阻抗匹配理论，
        史密斯圆图成为分析级联效应的重要工具。<br><br>
        
        <b>工程智慧</b> - 老一辈工程师常用"抖线法"调整
        电缆长度来优化匹配，这其实就是在寻找最佳相位点。<br><br>
        
        <i>💭 "最差情况设计"是射频工程的金科玉律——
        因为墨菲定律在微波系统中特别有效！</i>
        """
