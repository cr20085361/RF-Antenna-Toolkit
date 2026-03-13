# -*- coding: utf-8 -*-
"""
射频天线工具集 - 衰减计算器工具
RF Antenna Toolkit - Attenuator Calculator Tool

版本: v1.0.0
功能: 计算 T 型和 π 型衰减器电阻值，支持标准阻值系列匹配
迭代: 初始版本
"""

from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QFrame, QPushButton,
    QRadioButton, QButtonGroup, QGroupBox, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QDoubleValidator, QPainter, QColor, QPen,
    QBrush, QFont, QPainterPath
)

from core.i18n import tr
from ui.base.tool_base import ToolBase
from core.rf.attenuator import (
    AttenuatorCalculator, AttenuatorResult,
    SERIES_MAP, SERIES_TOLERANCE
)


class SchematicWidget(QWidget):
    """
    衰减器电路原理图绘制组件

    根据拓扑类型 (T/π) 绘制电路示意图，并标注电阻值
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(180)
        self.setMaximumHeight(220)
        self._topology = "T"        # "T" 或 "π"
        self._r1_text = "R₁"
        self._r2_text = "R₂"
        self._r3_text = "R₃"
        self._r1_std_text = ""
        self._r2_std_text = ""
        self._r3_std_text = ""

    def set_data(self, topology: str,
                 r1: str, r2: str, r3: str,
                 r1_std: str = "", r2_std: str = "", r3_std: str = ""):
        """设置绘图数据"""
        self._topology = topology
        self._r1_text = r1
        self._r2_text = r2
        self._r3_text = r3
        self._r1_std_text = r1_std
        self._r2_std_text = r2_std
        self._r3_std_text = r3_std
        self.update()

    def paintEvent(self, event):
        """绘制电路原理图"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w // 2       # 中心 X
        cy = h // 2        # 中心 Y

        # 颜色定义
        wire_color = QColor("#4A5568")
        resistor_color = QColor("#2C7BE5")
        text_color = QColor("#1A202C")
        std_color = QColor("#E53E3E")
        bg_color = QColor("#FAFBFC")

        # 背景
        painter.fillRect(self.rect(), bg_color)

        # 画笔设置
        wire_pen = QPen(wire_color, 2)
        resistor_pen = QPen(resistor_color, 2.5)

        # 电阻符号尺寸
        rw = 50   # 电阻宽度
        rh = 16   # 电阻高度

        if self._topology == "T":
            self._draw_t_type(painter, w, h, cx, cy,
                              wire_pen, resistor_pen, resistor_color,
                              text_color, std_color, rw, rh)
        else:
            self._draw_pi_type(painter, w, h, cx, cy,
                               wire_pen, resistor_pen, resistor_color,
                               text_color, std_color, rw, rh)

        # 标题
        painter.setPen(QPen(text_color))
        title_font = QFont("Microsoft YaHei", 10, QFont.Weight.Bold)
        painter.setFont(title_font)
        title = "T 型 (星型) 衰减器" if self._topology == "T" else "π 型衰减器"
        painter.drawText(10, 20, title)

        # 端口标签
        port_font = QFont("Microsoft YaHei", 9)
        painter.setFont(port_font)
        painter.setPen(QPen(QColor("#718096")))
        painter.drawText(15, cy - 15, "IN")
        painter.drawText(w - 35, cy - 15, "OUT")

        painter.end()

    def _draw_resistor_box(self, painter: QPainter, x: int, y: int,
                           w: int, h: int, pen: QPen, fill: QColor):
        """绘制电阻矩形符号"""
        painter.setPen(pen)
        painter.setBrush(QBrush(fill.lighter(190)))
        painter.drawRect(x, y, w, h)

    def _draw_t_type(self, painter, w, h, cx, cy,
                     wire_pen, res_pen, res_color, text_color, std_color, rw, rh):
        """绘制 T 型电路"""
        # 主线 y 位置
        y_main = cy - 10

        # ── 左导线 ──[R1]── 中间节点 ──[R3]── 右导线 ──
        # 左导线
        painter.setPen(wire_pen)
        painter.drawLine(40, y_main, cx - rw - 20, y_main)
        # R1
        self._draw_resistor_box(painter, cx - rw - 20, y_main - rh // 2,
                                rw, rh, res_pen, res_color)
        # 中间导线
        painter.setPen(wire_pen)
        painter.drawLine(cx - 20, y_main, cx + 20, y_main)
        # R3
        self._draw_resistor_box(painter, cx + 20, y_main - rh // 2,
                                rw, rh, res_pen, res_color)
        # 右导线
        painter.setPen(wire_pen)
        painter.drawLine(cx + 20 + rw, y_main, w - 40, y_main)

        # 中间节点向下 ──[R2]── 地
        painter.setPen(wire_pen)
        painter.drawLine(cx, y_main, cx, y_main + 20)
        self._draw_resistor_box(painter, cx - rh // 2, y_main + 20,
                                rh, rw - 10, res_pen, res_color)
        painter.setPen(wire_pen)
        painter.drawLine(cx, y_main + 20 + rw - 10, cx, y_main + rw + 20)

        # 地线
        gnd_y = y_main + rw + 20
        painter.drawLine(cx - 15, gnd_y, cx + 15, gnd_y)
        painter.drawLine(cx - 10, gnd_y + 4, cx + 10, gnd_y + 4)
        painter.drawLine(cx - 5, gnd_y + 8, cx + 5, gnd_y + 8)

        # 下地线 (左右)
        painter.drawLine(40, gnd_y, w - 40, gnd_y)

        # 标注文字
        label_font = QFont("Consolas", 9, QFont.Weight.Bold)
        std_font = QFont("Consolas", 8)
        painter.setFont(label_font)

        # R1 标注
        painter.setPen(QPen(text_color))
        painter.drawText(cx - rw - 20, y_main - rh // 2 - 5, f"R₁={self._r1_text}")
        if self._r1_std_text:
            painter.setFont(std_font)
            painter.setPen(QPen(std_color))
            painter.drawText(cx - rw - 20, y_main - rh // 2 - 20, f"→{self._r1_std_text}")
            painter.setFont(label_font)

        # R3 标注
        painter.setPen(QPen(text_color))
        painter.drawText(cx + 22, y_main - rh // 2 - 5, f"R₃={self._r3_text}")
        if self._r3_std_text:
            painter.setFont(std_font)
            painter.setPen(QPen(std_color))
            painter.drawText(cx + 22, y_main - rh // 2 - 20, f"→{self._r3_std_text}")
            painter.setFont(label_font)

        # R2 标注
        painter.setPen(QPen(text_color))
        painter.drawText(cx + rh // 2 + 5, y_main + 30 + rw // 2, f"R₂={self._r2_text}")
        if self._r2_std_text:
            painter.setFont(std_font)
            painter.setPen(QPen(std_color))
            painter.drawText(cx + rh // 2 + 5, y_main + 45 + rw // 2, f"→{self._r2_std_text}")

    def _draw_pi_type(self, painter, w, h, cx, cy,
                      wire_pen, res_pen, res_color, text_color, std_color, rw, rh):
        """绘制 π 型电路"""
        y_main = cy - 10

        # 上导线
        painter.setPen(wire_pen)
        painter.drawLine(40, y_main, w - 40, y_main)

        # R2 (串联电阻，放中间)
        r2_x = cx - rw // 2
        self._draw_resistor_box(painter, r2_x, y_main - rh // 2,
                                rw, rh, res_pen, res_color)

        # R1 (左并联) - 从上导线到地
        r1_x = cx - rw - 40
        painter.setPen(wire_pen)
        painter.drawLine(r1_x, y_main, r1_x, y_main + 15)
        self._draw_resistor_box(painter, r1_x - rh // 2, y_main + 15,
                                rh, rw - 10, res_pen, res_color)
        painter.setPen(wire_pen)
        painter.drawLine(r1_x, y_main + 15 + rw - 10, r1_x, y_main + rw + 15)

        # R3 (右并联) - 从上导线到地
        r3_x = cx + rw + 40
        painter.setPen(wire_pen)
        painter.drawLine(r3_x, y_main, r3_x, y_main + 15)
        self._draw_resistor_box(painter, r3_x - rh // 2, y_main + 15,
                                rh, rw - 10, res_pen, res_color)
        painter.setPen(wire_pen)
        painter.drawLine(r3_x, y_main + 15 + rw - 10, r3_x, y_main + rw + 15)

        # 地线
        gnd_y = y_main + rw + 15
        painter.drawLine(40, gnd_y, w - 40, gnd_y)

        # 地线符号 (两个)
        for gx in [r1_x, r3_x]:
            painter.drawLine(gx - 10, gnd_y + 4, gx + 10, gnd_y + 4)
            painter.drawLine(gx - 5, gnd_y + 8, gx + 5, gnd_y + 8)

        # 标注文字
        label_font = QFont("Consolas", 9, QFont.Weight.Bold)
        std_font = QFont("Consolas", 8)
        painter.setFont(label_font)

        # R2 标注 (上方)
        painter.setPen(QPen(text_color))
        painter.drawText(r2_x, y_main - rh // 2 - 5, f"R₂={self._r2_text}")
        if self._r2_std_text:
            painter.setFont(std_font)
            painter.setPen(QPen(std_color))
            painter.drawText(r2_x, y_main - rh // 2 - 20, f"→{self._r2_std_text}")
            painter.setFont(label_font)

        # R1 标注 (左侧)
        painter.setPen(QPen(text_color))
        painter.drawText(r1_x + rh // 2 + 5, y_main + 25 + rw // 2, f"R₁={self._r1_text}")
        if self._r1_std_text:
            painter.setFont(std_font)
            painter.setPen(QPen(std_color))
            painter.drawText(r1_x + rh // 2 + 5, y_main + 40 + rw // 2, f"→{self._r1_std_text}")
            painter.setFont(label_font)

        # R3 标注 (右侧)
        painter.setPen(QPen(text_color))
        painter.drawText(r3_x + rh // 2 + 5, y_main + 25 + rw // 2, f"R₃={self._r3_text}")
        if self._r3_std_text:
            painter.setFont(std_font)
            painter.setPen(QPen(std_color))
            painter.drawText(r3_x + rh // 2 + 5, y_main + 40 + rw // 2, f"→{self._r3_std_text}")


class AttenuatorTool(ToolBase):
    """
    衰减计算器工具

    功能:
    - T 型 / π 型衰减器电阻值计算
    - 标准阻值系列自动匹配 (E12/E24/E48/E96)
    - 偏差分析与可视化
    """

    tool_name = "衰减计算"
    tool_icon = "📉"
    tool_category = "rf"
    tool_description = "T 型/π 型衰减器电阻值计算，支持标准阻值系列匹配"
    i18n_title_key = "attenuator.tool_name"
    i18n_desc_key = "attenuator.tool_desc"

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化"""
        self._calculator = AttenuatorCalculator()
        self._result: Optional[AttenuatorResult] = None
        super().__init__(parent)

    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # ── 标题 ──
        title = QLabel("🔧 筛选与控制")
        title.setObjectName("InputTitle")
        layout.addWidget(title)

        # ── 拓扑选择 ──
        topo_group = QGroupBox("衰减器拓扑")
        topo_layout = QVBoxLayout(topo_group)

        self._topo_btn_group = QButtonGroup()
        self._radio_t = QRadioButton("T 型 (星型)")
        self._radio_pi = QRadioButton("π 型")
        self._radio_t.setChecked(True)
        self._topo_btn_group.addButton(self._radio_t, 0)
        self._topo_btn_group.addButton(self._radio_pi, 1)
        topo_layout.addWidget(self._radio_t)
        topo_layout.addWidget(self._radio_pi)
        layout.addWidget(topo_group)

        # ── 系统阻抗 ──
        z0_group = QGroupBox("系统阻抗")
        z0_layout = QHBoxLayout(z0_group)
        self._z0_input = QLineEdit("50")
        self._z0_input.setValidator(QDoubleValidator(0.1, 10000, 2))
        self._z0_input.setPlaceholderText("50")
        z0_unit = QLabel("Ω")
        z0_layout.addWidget(self._z0_input)
        z0_layout.addWidget(z0_unit)
        layout.addWidget(z0_group)

        # ── 目标衰减值 ──
        atten_group = QGroupBox("目标衰减值")
        atten_layout = QHBoxLayout(atten_group)
        self._atten_input = QLineEdit("6")
        self._atten_input.setValidator(QDoubleValidator(0.1, 100, 2))
        self._atten_input.setPlaceholderText("6")
        atten_unit = QLabel("dB")
        atten_layout.addWidget(self._atten_input)
        atten_layout.addWidget(atten_unit)
        layout.addWidget(atten_group)

        # ── 阻值系列 ──
        series_group = QGroupBox("标准阻值系列")
        series_layout = QVBoxLayout(series_group)
        self._series_combo = QComboBox()
        self._series_combo.addItem("理想值 (不匹配)", "IDEAL")
        self._series_combo.addItem("E12 (±10%)", "E12")
        self._series_combo.addItem("E24 (±5%)", "E24")
        self._series_combo.addItem("E48 (±2%)", "E48")
        self._series_combo.addItem("E96 (±1%)", "E96")
        self._series_combo.setCurrentIndex(2)  # 默认 E24
        series_layout.addWidget(self._series_combo)
        layout.addWidget(series_group)

        # ── 计算按钮 ──
        self._calc_btn = QPushButton("计算")
        self._calc_btn.setObjectName("PrimaryButton")
        self._calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._calc_btn.clicked.connect(self.calculate)
        layout.addWidget(self._calc_btn)

        # ── 数据说明 ──
        info = QLabel(
            "<b>数据说明:</b><br>"
            "• 对称衰减器 (R₁ = R₃)<br>"
            "• 阻值系列: IEC 60063<br>"
            "• 匹配算法: 对数最近邻"
        )
        info.setObjectName("DataSourceLabel")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()
        return panel

    def create_result_panel(self) -> QWidget:
        """创建结果面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ── 标题 ──
        title = QLabel("📊 计算结果")
        title.setObjectName("ResultTitle")
        layout.addWidget(title)

        # ── 电路示意图 ──
        self._schematic = SchematicWidget()
        self._schematic.setStyleSheet(
            "border: 1px solid #E2E8F0; border-radius: 8px;"
        )
        layout.addWidget(self._schematic)

        # ── 结果卡片区 ──
        cards_frame = QFrame()
        cards_frame.setObjectName("ResultCards")
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(10)

        # 创建结果卡片
        self._cards: Dict[str, QLabel] = {}

        # 第一行: 理想值
        cards_layout.addWidget(self._create_header("理想电阻值"), 0, 0, 1, 3)
        self._cards["r1_ideal"] = self._create_card("R₁", cards_layout, 1, 0)
        self._cards["r2_ideal"] = self._create_card("R₂", cards_layout, 1, 1)
        self._cards["r3_ideal"] = self._create_card("R₃", cards_layout, 1, 2)

        # 分割线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        cards_layout.addWidget(sep, 2, 0, 1, 3)

        # 第二行: 标准值
        self._std_header = self._create_header("标准阻值 (E24)")
        cards_layout.addWidget(self._std_header, 3, 0, 1, 3)
        self._cards["r1_std"] = self._create_card("R₁'", cards_layout, 4, 0)
        self._cards["r2_std"] = self._create_card("R₂'", cards_layout, 4, 1)
        self._cards["r3_std"] = self._create_card("R₃'", cards_layout, 4, 2)

        # 分割线
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #E2E8F0;")
        cards_layout.addWidget(sep2, 5, 0, 1, 3)

        # 第三行: 偏差分析
        cards_layout.addWidget(self._create_header("偏差分析"), 6, 0, 1, 3)
        self._cards["actual_atten"] = self._create_card("实际衰减", cards_layout, 7, 0)
        self._cards["deviation"] = self._create_card("偏差", cards_layout, 7, 1)
        self._cards["quality"] = self._create_card("评估", cards_layout, 7, 2)

        layout.addWidget(cards_frame)
        layout.addStretch()

        # 初始计算 (默认值)
        self.calculate()

        return panel

    def _create_header(self, text: str) -> QLabel:
        """创建区域标题"""
        label = QLabel(text)
        label.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #4A5568; "
            "padding: 4px 0; border-bottom: 1px solid #E2E8F0;"
        )
        return label

    def _create_card(self, name: str, layout: QGridLayout,
                     row: int, col: int) -> QLabel:
        """创建结果数值卡片"""
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #F7FAFC; border: 1px solid #E2E8F0; "
            "border-radius: 6px; padding: 8px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 6, 8, 6)
        card_layout.setSpacing(4)

        # 标签名
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 11px; color: #718096; border: none;")
        card_layout.addWidget(name_label)

        # 数值
        value_label = QLabel("—")
        value_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #1A202C; border: none;"
        )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)

        layout.addWidget(card, row, col)
        return value_label

    def calculate(self):
        """执行计算"""
        try:
            z0 = float(self._z0_input.text() or "50")
            atten_db = float(self._atten_input.text() or "6")
        except ValueError:
            return

        if z0 <= 0 or atten_db <= 0:
            return

        # 获取拓扑和系列
        is_t_type = self._radio_t.isChecked()
        series_key = self._series_combo.currentData()
        series = series_key if series_key != "IDEAL" else None

        # 计算
        try:
            if is_t_type:
                result = self._calculator.calculate_t_type(z0, atten_db, series)
            else:
                result = self._calculator.calculate_pi_type(z0, atten_db, series)
        except ValueError as e:
            return

        self._result = result
        self._update_display(result)

    def _update_display(self, r: AttenuatorResult):
        """更新显示"""
        fmt = AttenuatorCalculator.format_resistance

        # 更新理想值卡片
        self._cards["r1_ideal"].setText(fmt(r.r1_ideal))
        self._cards["r2_ideal"].setText(fmt(r.r2_ideal))
        self._cards["r3_ideal"].setText(fmt(r.r3_ideal))

        # 更新示意图
        if r.series_name:
            self._schematic.set_data(
                r.topology,
                fmt(r.r1_ideal), fmt(r.r2_ideal), fmt(r.r3_ideal),
                fmt(r.r1_std), fmt(r.r2_std), fmt(r.r3_std)
            )
            # 更新标准值卡片
            self._std_header.setText(f"标准阻值 ({r.series_name})")
            self._cards["r1_std"].setText(fmt(r.r1_std))
            self._cards["r2_std"].setText(fmt(r.r2_std))
            self._cards["r3_std"].setText(fmt(r.r3_std))

            # 偏差分析
            self._cards["actual_atten"].setText(f"{r.actual_atten_db:.3f} dB")
            dev = r.deviation_db
            self._cards["deviation"].setText(f"{dev:+.3f} dB")

            # 偏差颜色编码
            abs_dev = abs(dev)
            if abs_dev <= 0.1:
                color = "#38A169"  # 绿色: 偏差很小
                quality = "🟢 精确"
            elif abs_dev <= 0.3:
                color = "#2C7BE5"  # 蓝色: 偏差可接受
                quality = "🔵 良好"
            elif abs_dev <= 0.5:
                color = "#DD6B20"  # 橙色: 有一定偏差
                quality = "🟡 可接受"
            else:
                color = "#E53E3E"  # 红色: 偏差较大
                quality = "🔴 偏差较大"

            self._cards["deviation"].setStyleSheet(
                f"font-size: 16px; font-weight: 700; color: {color}; border: none;"
            )
            self._cards["quality"].setText(quality)
        else:
            # 理想值模式: 无标准值匹配
            self._schematic.set_data(
                r.topology,
                fmt(r.r1_ideal), fmt(r.r2_ideal), fmt(r.r3_ideal)
            )
            self._std_header.setText("标准阻值 (未选择系列)")
            self._cards["r1_std"].setText("—")
            self._cards["r2_std"].setText("—")
            self._cards["r3_std"].setText("—")
            self._cards["actual_atten"].setText(f"{r.target_atten_db:.3f} dB")
            self._cards["deviation"].setText("0.000 dB")
            self._cards["deviation"].setStyleSheet(
                "font-size: 16px; font-weight: 700; color: #38A169; border: none;"
            )
            self._cards["quality"].setText("🟢 精确")

    # ==================== 知识面板 ====================

    def get_intuition_content(self) -> Optional[str]:
        """直观理解 - 物理本质"""
        return """
        <b>💡 衰减器的物理本质</b><br><br>

        射频衰减器是一种 <b>无源电阻网络</b>，通过精确的电阻分压来降低信号幅度，
        同时保持输入/输出端口的阻抗匹配。<br><br>

        <b>T 型 vs π 型:</b><br>
        • <b>T 型 (星型)</b>: 两个串联电阻 + 一个并联电阻。
          适合 <u>小衰减值</u> (≤10dB)，因为并联电阻较大，寄生电容影响小。<br>
        • <b>π 型</b>: 一个串联电阻 + 两个并联电阻。
          适合 <u>大衰减值</u> (>10dB)，因为串联电阻较大，布局上更容易接地。<br><br>

        <b>关键特性:</b><br>
        • 理想情况下，衰减量与频率无关<br>
        • 实际中，高频时电阻的寄生参数会导致衰减偏离理想值<br>
        • 功率容量取决于电阻的功率额定值
        """

    def get_math_model_content(self) -> Optional[str]:
        """数学模型"""
        return """
        <b>📐 衰减器计算公式</b><br><br>

        设衰减量 A (dB)，系统阻抗 Z<sub>0</sub> (Ω)，
        线性比值 K = 10<sup>A/20</sup><br><br>

        <b>T 型衰减器:</b><br>
        • R<sub>1</sub> = R<sub>3</sub> = Z<sub>0</sub> × (K−1) / (K+1)<br>
        • R<sub>2</sub> = Z<sub>0</sub> × 2K / (K²−1)<br><br>

        <b>π 型衰减器:</b><br>
        • R<sub>1</sub> = R<sub>3</sub> = Z<sub>0</sub> × (K+1) / (K−1)<br>
        • R<sub>2</sub> = Z<sub>0</sub> × (K²−1) / (2K)<br><br>

        <b>反算公式 (ABCD 矩阵):</b><br>
        利用二端口网络 ABCD 参数矩阵反算实际插入损耗:<br>
        IL = 20 log<sub>10</sub>(|A + B/Z<sub>0</sub> + CZ<sub>0</sub> + D| / 2)
        """

    def get_engineering_content(self) -> Optional[str]:
        """工程指南"""
        return """
        <b>⚙️ 工程设计指南</b><br><br>

        <b>阻值系列选择:</b><br>
        • <b>E24</b>: 最常用，成本低，偏差通常 ≤0.5dB<br>
        • <b>E48</b>: 精密应用推荐，偏差通常 ≤0.2dB<br>
        • <b>E96</b>: 测量级应用 (校准衰减器)，偏差极小<br>
        • <b>E12</b>: 仅用于精度要求极低的场合<br><br>

        <b>功率考量:</b><br>
        • 0402 贴片电阻: ~62.5mW (单片)<br>
        • 0603 贴片电阻: ~100mW<br>
        • 0805 贴片电阻: ~125mW<br>
        • 衰减器总功率 = 输入功率 × (1 − 10<sup>−A/10</sup>)<br><br>

        <b>频率限制:</b><br>
        • 0402 封装: 适用于 ≤26GHz<br>
        • 0201 封装: 适用于 ≤40GHz<br>
        • 薄膜电阻器: 寄生参数更小，高频性能更好
        """

    def get_history_content(self) -> Optional[str]:
        """历史"""
        return """
        <b>📜 衰减器发展简史</b><br><br>

        电阻衰减器的历史可以追溯到电报时代。早期的 "衰减箱" 使用
        机械开关选择不同的电阻网络来调节信号电平。<br><br>

        T 型和 π 型拓扑因结构简单、计算精确而成为最经典的衰减器设计。
        现代微波衰减器则广泛使用薄膜电阻工艺，在 GaAs 或 氮化铝基板上
        实现亚毫米级精密电阻网络。<br><br>

        标准阻值系列 (E 系列) 由 IEC 60063 标准定义，
        最早的 E12 系列可追溯到 1952 年。其设计原则是使相邻阻值之间
        的对数间距均匀分布，从而保证任何目标值都能找到足够接近的标准值。
        """
