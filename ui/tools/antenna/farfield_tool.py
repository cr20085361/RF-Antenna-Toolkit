# -*- coding: utf-8 -*-
"""
射频天线工具集 - 远场距离计算工具
RF Antenna Toolkit - Far-Field Distance Calculator Tool

版本: v1.0.0
功能: 基于 IEEE 149-2019 / 3GPP TS 38.810 计算天线远场距离
      支持电大/电小天线自动判据切换与相控阵扫描角修正
"""

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QPixmap

from ui.base.tool_base import ToolBase
from core.antenna.farfield import (
    FarFieldCalculator, FarFieldResult, ApertureShape
)
import os


class FarFieldTool(ToolBase):
    """
    远场距离计算工具

    功能:
    - 按 IEEE 149 三分区模型输出完整的近场/远场边界
    - 电大/电小天线智能判据切换 (2D²/λ vs 5λ/10λ)
    - 矩形/圆形口径自动转换最大尺寸
    - 相控阵波束扫描角有效口径修正
    - 工程测试建议生成
    """

    # 工具元信息
    tool_name = "远场计算器"
    tool_icon = "🎯"
    tool_category = "antenna"
    tool_description = "计算天线远场测试距离 (IEEE 149 / 3GPP 38.810)"

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化远场计算工具"""
        self._calculator = FarFieldCalculator()
        self._result_labels: Dict[str, QLabel] = {}
        super().__init__(parent)

    # ==================== 输入面板 ====================

    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # ==================== 频率输入 ====================
        freq_group = QGroupBox("测试频率")
        freq_layout = QGridLayout(freq_group)
        freq_layout.setSpacing(12)

        freq_label = QLabel("频率:")
        freq_label.setObjectName("InputLabel")
        freq_layout.addWidget(freq_label, 0, 0)

        self._freq_input = QLineEdit()
        self._freq_input.setPlaceholderText("输入测试频率")
        self._freq_input.setValidator(QDoubleValidator(0.001, 1e6, 6))
        self._freq_input.setText("10")
        freq_layout.addWidget(self._freq_input, 0, 1)

        self._freq_unit = QComboBox()
        self._freq_unit.addItems(["GHz", "MHz"])
        self._freq_unit.setCurrentText("GHz")
        freq_layout.addWidget(self._freq_unit, 0, 2)

        layout.addWidget(freq_group)

        # ==================== 口径输入 ====================
        aperture_group = QGroupBox("天线口径 (最大物理尺寸)")
        aperture_layout = QVBoxLayout(aperture_group)
        aperture_layout.setSpacing(12)

        # 口径输入模式选择
        mode_layout = QHBoxLayout()
        self._aperture_mode_group = QButtonGroup(self)

        self._radio_direct = QRadioButton("直接输入 D")
        self._radio_direct.setChecked(True)
        self._aperture_mode_group.addButton(self._radio_direct, 0)
        mode_layout.addWidget(self._radio_direct)

        self._radio_rect = QRadioButton("矩形 (长×宽)")
        self._aperture_mode_group.addButton(self._radio_rect, 1)
        mode_layout.addWidget(self._radio_rect)

        self._radio_circular = QRadioButton("圆形 (直径)")
        self._aperture_mode_group.addButton(self._radio_circular, 2)
        mode_layout.addWidget(self._radio_circular)

        aperture_layout.addLayout(mode_layout)

        # 口径数值输入区
        self._aperture_grid = QGridLayout()
        self._aperture_grid.setSpacing(12)

        # 直接输入 D
        self._d_label = QLabel("口径 D:")
        self._d_label.setObjectName("InputLabel")
        self._aperture_grid.addWidget(self._d_label, 0, 0)

        self._d_input = QLineEdit()
        self._d_input.setPlaceholderText("天线最大物理尺寸")
        self._d_input.setValidator(QDoubleValidator(0.001, 1e6, 4))
        self._d_input.setText("300")
        self._aperture_grid.addWidget(self._d_input, 0, 1)

        # 矩形长
        self._length_label = QLabel("长 L:")
        self._length_label.setObjectName("InputLabel")
        self._aperture_grid.addWidget(self._length_label, 1, 0)

        self._length_input = QLineEdit()
        self._length_input.setPlaceholderText("矩形长边")
        self._length_input.setValidator(QDoubleValidator(0.001, 1e6, 4))
        self._length_input.setText("200")
        self._aperture_grid.addWidget(self._length_input, 1, 1)

        # 矩形宽
        self._width_label = QLabel("宽 W:")
        self._width_label.setObjectName("InputLabel")
        self._aperture_grid.addWidget(self._width_label, 2, 0)

        self._width_input = QLineEdit()
        self._width_input.setPlaceholderText("矩形短边")
        self._width_input.setValidator(QDoubleValidator(0.001, 1e6, 4))
        self._width_input.setText("200")
        self._aperture_grid.addWidget(self._width_input, 2, 1)

        # 口径尺寸单位 (共用)
        unit_label = QLabel("尺寸单位:")
        unit_label.setObjectName("InputLabel")
        self._aperture_grid.addWidget(unit_label, 0, 2)

        self._aperture_unit = QComboBox()
        self._aperture_unit.addItems(["mm", "cm", "m"])
        self._aperture_unit.setCurrentText("mm")
        self._aperture_grid.addWidget(self._aperture_unit, 0, 3)

        aperture_layout.addLayout(self._aperture_grid)

        # 初始化显示状态
        self._aperture_mode_group.idClicked.connect(self._on_aperture_mode_changed)
        self._on_aperture_mode_changed(0)

        layout.addWidget(aperture_group)

        # ==================== 相控阵扫描角 (可选) ====================
        scan_group = QGroupBox("相控阵波束扫描 (可选)")
        scan_layout = QGridLayout(scan_group)
        scan_layout.setSpacing(12)

        scan_label = QLabel("扫描角 θ:")
        scan_label.setObjectName("InputLabel")
        scan_layout.addWidget(scan_label, 0, 0)

        self._scan_angle_input = QLineEdit()
        self._scan_angle_input.setPlaceholderText("默认 0 (法线方向)")
        self._scan_angle_input.setValidator(QDoubleValidator(0, 89.9, 2))
        self._scan_angle_input.setText("0")
        scan_layout.addWidget(self._scan_angle_input, 0, 1)

        scan_unit_label = QLabel("°")
        scan_layout.addWidget(scan_unit_label, 0, 2)

        layout.addWidget(scan_group)

        # ==================== 计算按钮 ====================
        calc_button = QPushButton("🎯 计算远场距离")
        calc_button.setObjectName("PrimaryButton")
        calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_button.clicked.connect(self._do_calculate)
        layout.addWidget(calc_button)

        # ==================== 三分区示意图 ====================
        diagram_card = QWidget()
        diagram_card.setObjectName("ResultPanel")
        diagram_layout = QVBoxLayout(diagram_card)

        diagram_title = QLabel("📊 天线场区三分区示意 (IEEE 149)")
        diagram_title.setObjectName("ResultTitle")
        diagram_layout.addWidget(diagram_title)

        self._diagram_label = QLabel()
        self._diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 加载三分区示意图
        diagram_path = self.get_asset_path("assets/diagrams/farfield_zones.png")
        if os.path.exists(diagram_path):
            pixmap = QPixmap(diagram_path)
            scaled = pixmap.scaledToWidth(
                380, Qt.TransformationMode.SmoothTransformation)
            self._diagram_label.setPixmap(scaled)
        else:
            self._diagram_label.setText(
                "反应性近场 (0~0.62√(D³/λ))\n"
                "↓\n"
                "辐射近场 / 菲涅尔区\n"
                "↓\n"
                "远场 / 夫琅禾费区 (≥ 2D²/λ)")
            self._diagram_label.setStyleSheet(
                "color: #718096; font-size: 13px; padding: 20px;")

        diagram_layout.addWidget(self._diagram_label)
        layout.addWidget(diagram_card)

        layout.addStretch()

        return panel

    def _on_aperture_mode_changed(self, mode_id: int):
        """口径输入模式切换"""
        # 模式 0: 直接输入 D
        # 模式 1: 矩形 (取对角线)
        # 模式 2: 圆形 (直径 = D)
        is_direct = mode_id == 0
        is_rect = mode_id == 1

        self._d_label.setVisible(is_direct or mode_id == 2)
        self._d_input.setVisible(is_direct or mode_id == 2)
        self._length_label.setVisible(is_rect)
        self._length_input.setVisible(is_rect)
        self._width_label.setVisible(is_rect)
        self._width_input.setVisible(is_rect)

        if mode_id == 2:
            self._d_label.setText("直径 D:")
        else:
            self._d_label.setText("口径 D:")

    # ==================== 结果面板 ====================

    def create_result_panel(self) -> QWidget:
        """创建结果面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 错误提示区域
        self._error_label = QLabel("")
        self._error_label.setObjectName("ErrorLabel")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # ---- 核心结果: 远场距离 ----
        far_field_card = self._create_result_card(
            "far_field", "🎯 远场距离 (Far-Field Boundary)",
            "满足所有判据的最短合法远场测量距离"
        )
        layout.addWidget(far_field_card)

        # ---- 天线电尺寸评估 ----
        size_card = QWidget()
        size_card.setObjectName("ResultPanel")
        size_layout = QVBoxLayout(size_card)

        size_title = QLabel("📐 天线电尺寸评估")
        size_title.setObjectName("ResultTitle")
        size_layout.addWidget(size_title)

        size_grid = QGridLayout()
        size_grid.setSpacing(8)

        size_grid.addWidget(QLabel("D/λ 比值:"), 0, 0)
        self._result_labels["d_over_lambda"] = QLabel("--")
        self._result_labels["d_over_lambda"].setStyleSheet(
            "font-weight: bold; font-size: 15px; color: #3182CE;")
        size_grid.addWidget(self._result_labels["d_over_lambda"], 0, 1)

        size_grid.addWidget(QLabel("电尺寸分类:"), 1, 0)
        self._result_labels["electrical_size"] = QLabel("--")
        self._result_labels["electrical_size"].setStyleSheet(
            "font-weight: bold; font-size: 14px;")
        size_grid.addWidget(self._result_labels["electrical_size"], 1, 1)

        size_grid.addWidget(QLabel("主导判据:"), 2, 0)
        self._result_labels["dominant"] = QLabel("--")
        self._result_labels["dominant"].setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #D69E2E;")
        size_grid.addWidget(self._result_labels["dominant"], 2, 1)

        size_layout.addLayout(size_grid)
        layout.addWidget(size_card)

        # ---- 三分区边界详细结果 ----
        zone_card = QWidget()
        zone_card.setObjectName("ResultPanel")
        zone_layout = QVBoxLayout(zone_card)

        zone_title = QLabel("📊 三分区边界 (IEEE 149)")
        zone_title.setObjectName("ResultTitle")
        zone_layout.addWidget(zone_title)

        zone_grid = QGridLayout()
        zone_grid.setSpacing(8)

        zone_grid.addWidget(QLabel("反应性近场 R_nf:"), 0, 0)
        self._result_labels["reactive_nf"] = QLabel("--")
        zone_grid.addWidget(self._result_labels["reactive_nf"], 0, 1)

        zone_grid.addWidget(QLabel("辐射近场/菲涅尔区:"), 1, 0)
        self._result_labels["radiative_nf"] = QLabel("--")
        zone_grid.addWidget(self._result_labels["radiative_nf"], 1, 1)

        zone_grid.addWidget(QLabel("远场/夫琅禾费区:"), 2, 0)
        self._result_labels["far_field_zone"] = QLabel("--")
        self._result_labels["far_field_zone"].setStyleSheet(
            "font-weight: bold; color: #38A169;")
        zone_grid.addWidget(self._result_labels["far_field_zone"], 2, 1)

        zone_layout.addLayout(zone_grid)
        layout.addWidget(zone_card)

        # ---- 各判据分项值 ----
        criteria_card = QWidget()
        criteria_card.setObjectName("ResultPanel")
        criteria_layout = QVBoxLayout(criteria_card)

        criteria_title = QLabel("🧮 各判据分项计算")
        criteria_title.setObjectName("ResultTitle")
        criteria_layout.addWidget(criteria_title)

        criteria_grid = QGridLayout()
        criteria_grid.setSpacing(8)

        criteria_grid.addWidget(QLabel("相位判据 (2D²/λ):"), 0, 0)
        self._result_labels["phase"] = QLabel("--")
        criteria_grid.addWidget(self._result_labels["phase"], 0, 1)

        criteria_grid.addWidget(QLabel("场衰减判据 (5λ):"), 1, 0)
        self._result_labels["lambda5"] = QLabel("--")
        criteria_grid.addWidget(self._result_labels["lambda5"], 1, 1)

        criteria_grid.addWidget(QLabel("保守场衰减 (10λ):"), 2, 0)
        self._result_labels["lambda10"] = QLabel("--")
        criteria_grid.addWidget(self._result_labels["lambda10"], 2, 1)

        criteria_grid.addWidget(QLabel("最小距离 (5D):"), 3, 0)
        self._result_labels["d5"] = QLabel("--")
        criteria_grid.addWidget(self._result_labels["d5"], 3, 1)

        criteria_layout.addLayout(criteria_grid)
        layout.addWidget(criteria_card)

        # ---- 输入参数回显 ----
        echo_card = QWidget()
        echo_card.setObjectName("ResultPanel")
        echo_layout = QVBoxLayout(echo_card)

        echo_title = QLabel("📋 输入参数回显")
        echo_title.setObjectName("ResultTitle")
        echo_layout.addWidget(echo_title)

        echo_grid = QGridLayout()
        echo_grid.setSpacing(8)

        echo_grid.addWidget(QLabel("波长 λ:"), 0, 0)
        self._result_labels["wavelength"] = QLabel("--")
        echo_grid.addWidget(self._result_labels["wavelength"], 0, 1)

        echo_grid.addWidget(QLabel("口径 D:"), 1, 0)
        self._result_labels["aperture_d"] = QLabel("--")
        echo_grid.addWidget(self._result_labels["aperture_d"], 1, 1)

        echo_grid.addWidget(QLabel("有效口径 D_eff:"), 2, 0)
        self._result_labels["effective_d"] = QLabel("--")
        echo_grid.addWidget(self._result_labels["effective_d"], 2, 1)

        echo_layout.addLayout(echo_grid)
        layout.addWidget(echo_card)

        # ---- 工程建议 ----
        rec_card = QWidget()
        rec_card.setObjectName("ResultPanel")
        rec_layout = QVBoxLayout(rec_card)

        rec_title = QLabel("💡 测量建议")
        rec_title.setObjectName("ResultTitle")
        rec_layout.addWidget(rec_title)

        self._result_labels["recommendation"] = QLabel("--")
        self._result_labels["recommendation"].setWordWrap(True)
        self._result_labels["recommendation"].setStyleSheet("line-height: 1.6;")
        rec_layout.addWidget(self._result_labels["recommendation"])

        layout.addWidget(rec_card)

        layout.addStretch()
        return panel

    def _create_result_card(
        self, key: str, title: str, description: str
    ) -> QWidget:
        """创建结果卡片"""
        card = QWidget()
        card.setObjectName("ResultPanel")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("ResultTitle")
        card_layout.addWidget(title_label)

        value_label = QLabel("--")
        value_label.setObjectName("ResultValue")
        value_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #2B6CB0;")
        self._result_labels[key] = value_label
        card_layout.addWidget(value_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("ResultDescription")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        return card

    # ==================== 计算逻辑 ====================

    def calculate(self) -> Dict[str, Any]:
        """执行计算"""
        try:
            # 1. 解析频率
            freq_value = float(self._freq_input.text() or "0")
            freq_unit = self._freq_unit.currentText()
            if freq_unit == "GHz":
                freq_hz = freq_value * 1e9
            else:
                freq_hz = freq_value * 1e6

            if freq_hz <= 0:
                return {"success": False,
                        "error": "⚠️ 测试频率必须为正数"}

            # 2. 解析口径
            aperture_mode = self._aperture_mode_group.checkedId()
            unit_text = self._aperture_unit.currentText()
            unit_scale = {"mm": 1e-3, "cm": 1e-2, "m": 1.0}[unit_text]

            if aperture_mode == 0:  # 直接输入 D
                d_raw = float(self._d_input.text() or "0")
                aperture_d_m = FarFieldCalculator.resolve_aperture(
                    ApertureShape.DIRECT, d_m=d_raw * unit_scale)
            elif aperture_mode == 1:  # 矩形
                l_raw = float(self._length_input.text() or "0")
                w_raw = float(self._width_input.text() or "0")
                aperture_d_m = FarFieldCalculator.resolve_aperture(
                    ApertureShape.RECTANGULAR,
                    length_m=l_raw * unit_scale,
                    width_m=w_raw * unit_scale)
            else:  # 圆形
                d_raw = float(self._d_input.text() or "0")
                aperture_d_m = FarFieldCalculator.resolve_aperture(
                    ApertureShape.CIRCULAR, diameter_m=d_raw * unit_scale)

            # 3. 解析扫描角
            scan_angle = float(self._scan_angle_input.text() or "0")

            # 4. 执行计算
            result = self._calculator.calculate(
                frequency_hz=freq_hz,
                aperture_d_m=aperture_d_m,
                scan_angle_deg=scan_angle,
            )

            return {"success": True, "result": result}

        except ValueError as e:
            return {"success": False, "error": f"⚠️ {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"⚠️ 计算内部错误: {str(e)}"}

    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()

        if calc_result["success"]:
            self._error_label.hide()
            result: FarFieldResult = calc_result["result"]

            # 核心结果
            self._result_labels["far_field"].setText(
                result.far_field_formatted)

            # 电尺寸评估
            self._result_labels["d_over_lambda"].setText(
                f"{result.d_over_lambda:.2f}")
            self._result_labels["electrical_size"].setText(
                result.electrical_size_label)
            self._result_labels["dominant"].setText(
                result.dominant_criterion)

            # 三分区边界
            self._result_labels["reactive_nf"].setText(
                f"0 ~ {self._fmt_dist(result.reactive_near_field_m)}")
            self._result_labels["radiative_nf"].setText(
                f"{self._fmt_dist(result.reactive_near_field_m)} ~ "
                f"{self._fmt_dist(result.radiative_near_field_m)}")
            self._result_labels["far_field_zone"].setText(
                f"≥ {self._fmt_dist(result.far_field_distance_m)}")

            # 各判据分项
            self._result_labels["phase"].setText(
                self._fmt_dist(result.criterion_phase_m))
            self._result_labels["lambda5"].setText(
                self._fmt_dist(result.criterion_5lambda_m))
            self._result_labels["lambda10"].setText(
                self._fmt_dist(result.criterion_10lambda_m))
            self._result_labels["d5"].setText(
                self._fmt_dist(result.criterion_5d_m))

            # 参数回显
            self._result_labels["wavelength"].setText(
                self._fmt_dist(result.wavelength_m))
            self._result_labels["aperture_d"].setText(
                self._fmt_dist(result.aperture_d_m))
            self._result_labels["effective_d"].setText(
                self._fmt_dist(result.effective_d_m))

            # 工程建议
            recommendation = FarFieldCalculator.get_measurement_recommendation(
                result)
            self._result_labels["recommendation"].setText(recommendation)

        else:
            self._error_label.setText(calc_result.get("error", "未知错误"))
            self._error_label.show()
            for key in self._result_labels:
                self._result_labels[key].setText("--")

    @staticmethod
    def _fmt_dist(distance_m: float) -> str:
        """格式化距离显示，自适应单位"""
        if distance_m >= 1000:
            return f"{distance_m / 1000:.3f} km"
        elif distance_m >= 1:
            return f"{distance_m:.3f} m"
        elif distance_m >= 0.01:
            return f"{distance_m * 100:.3f} cm"
        else:
            return f"{distance_m * 1000:.3f} mm"

    # ==================== 四维度知识内容 ====================

    def get_intuition_content(self) -> Optional[str]:
        """直观理解 - 物理本质"""
        return """
        <b>🎯 什么是远场？——从生活场景理解三分区</b><br><br>

        想象你站在一个正在演奏的<b>大鼓</b>旁边：<br><br>

        <span style="background-color: #FED7E2; padding: 6px 10px;
        border-radius: 6px; display: inline-block; margin: 4px 0;">
        <b>🔴 第一区：反应性近场</b> — 就像贴着鼓面
        </span><br>
        • 你能<b>感到气流推着你的皮肤</b>，空气在来回震荡。<br>
        • 电磁波在此区像"呼吸"——能量在天线周围<b>来回涌动</b>，
        并不真正向外传播。<br>
        • 电场和磁场<b>不同步</b>、方向杂乱，像搅动的水面。<br>
        • <b>类比</b>：水龙头刚出水口处——水柱扭曲混沌。<br><br>

        <span style="background-color: #FEFCBF; padding: 6px 10px;
        border-radius: 6px; display: inline-block; margin: 4px 0;">
        <b>🟡 第二区：辐射近场 (菲涅尔区)</b> — 走远了几步
        </span><br>
        • 你能<b>清楚听到鼓声</b>了，但方向感还不太对——
        走两步声音大小就变化很大。<br>
        • 电磁波已经开始向外"飞行"，但波前仍然是<b>弯曲的球面</b>，
        各处场强还不均匀。<br>
        • 在这里测天线方向图，结果会<b>随距离变化</b>，不可靠。<br>
        • <b>类比</b>：手电筒近处照墙——光斑中心亮、边缘暗且范围随距离快速变化。<br><br>

        <span style="background-color: #C6F6D5; padding: 6px 10px;
        border-radius: 6px; display: inline-block; margin: 4px 0;">
        <b>🟢 第三区：远场 (夫琅禾费区)</b> — 站得足够远了
        </span><br>
        • 鼓声变成了平稳的"<b>声波</b>"——哪个方向响就是哪个方向响，
        不再受距离影响。<br>
        • 电磁波在局部可看作<b>平面波</b>：电场、磁场垂直且同步振荡，
        能量只沿径向传播。<br>
        • 天线的方向图、增益在此区<b>稳定不变</b>，是"真正的辐射特性"。<br>
        • <b>类比</b>：远处看太阳光——光线几乎所有都是平行射来的。<br><br>

        <b>🔑 一句话总结：</b><br>
        <i>远场就是电磁波"长大成人"、行为稳定的区域。
        只有在这里测得的数据才能代表天线的真实实力。</i>
        """

    def get_math_model_content(self) -> Optional[str]:
        """数学模型 - 精确公式"""
        return """
        <b>📐 三分区边界公式</b><br><br>

        <b>反应性近场外边界 (Reactive Near-field):</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        R<sub>rn</sub> = 0.62 √(D³/λ)
        </span><br><br>

        <b>远场内边界 (Fraunhofer Region):</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        R<sub>ff</sub> = max(2D²/λ,  5λ,  5D)
        </span><br><br>

        <b>各判据物理含义:</b><br>
        • <b>2D²/λ</b> — 相位判据:  口径面上各点到观测点的
        最大路径差 < λ/16 (≈ 22.5° 相位偏差)<br>
        • <b>5λ</b>  — 场衰减判据:  确保辐射场 (1/r) 远大于
        反应场 (1/r²), 部分标准取 10λ<br>
        • <b>5D</b>  — 最小绝对距离, 确保 AUT 口径的张角
        对方向图测量误差可忽略<br><br>

        <b>相控阵口径修正:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 15px;">
        D<sub>eff</sub> = D × cos(θ)
        </span><br>
        θ 为波束偏转角，扫描后投影口径缩小，远场距离随之降低。
        """

    def get_engineering_content(self) -> Optional[str]:
        """工程边界 - 适用范围与避坑"""
        return """
        <b>✅ 行业标准参考:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>IEEE 149-2019</td><td>天线标准测量规程 (通用)</td></tr>
        <tr><td>3GPP TS 38.810</td><td>5G NR OTA 测量方法论</td></tr>
        <tr><td>CTIA Test Plan</td><td>移动终端 OTA 测试规范</td></tr>
        </table><br>

        <b>⚠️ 典型天线远场距离速查:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>λ/4 单极子 @2.4GHz</td><td>≈ 0.63m (5λ主导)</td></tr>
        <tr><td>300mm 反射面 @10GHz</td><td>≈ 6.0m (2D²/λ主导)</td></tr>
        <tr><td>5G AAS 200×200mm @28GHz</td><td>≈ 14.9m (2D²/λ主导)</td></tr>
        </table><br>

        <span style="background-color: #FED7D7; padding: 4px 8px;
        border-radius: 4px; color: #C53030;">
        ❌ 常见误区
        </span><br>
        • 对小天线仍套用 2D²/λ，得到过短的远场距离<br>
        • 忽略相控阵扫描角对有效口径的缩减<br>
        • 将近场数据直接当作远场方向图使用<br><br>

        <span style="background-color: #C6F6D5; padding: 4px 8px;
        border-radius: 4px; color: #276749;">
        💡 不满足远场距离的替代方案
        </span><br>
        • 紧缩场 (CATR) 天线测量系统<br>
        • 近场-远场变换 (NF→FF Transformation)<br>
        • 球面近场扫描 (SNF) 测量
        """

    def get_history_content(self) -> Optional[str]:
        """发现历史 - 趣味故事"""
        return """
        <b>📜 从光学到微波——远场的跨界源流</b><br><br>

        <b>1818年</b> - 奥古斯丁·<b>菲涅尔</b>提出波动光学理论，
        首次系统地区分了近场（菲涅尔衍射）和远场（夫琅禾费衍射），
        解释了不同距离范围内衍射图样的差异。<br><br>

        <b>1823年</b> - 约瑟夫·<b>夫琅禾费</b>实验验证了远距离
        平行光条件下的衍射规律，远场区从此以他命名。<br><br>

        <b>1940年代</b> - 雷达技术的爆发式发展催生了对大型天线
        辐射方向图的精确测量需求。工程师们将光学中的远场判据
        2D²/λ 移植到了天线测量领域。<br><br>

        <b>2019年</b> - IEEE 149 标准最新修订版正式收编了对 5G
        大规模相控阵 (Massive MIMO) 的 OTA 远场测量指导，
        标志着远场理论进入了大阵面时代。<br><br>

        <i>💭 有趣的是：你在做天线远场测量时用到的 "2D²/λ" 公式，
        竟然来自 200 年前光学家对星光衍射的研究！</i>
        """
