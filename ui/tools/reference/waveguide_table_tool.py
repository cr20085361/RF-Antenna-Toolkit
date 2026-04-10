# -*- coding: utf-8 -*-
"""
标准波导法兰参考表工具
Standard Waveguide & Flange Reference Table Tool

版本: v2.1.0
功能: 提供 EIA WR 系列标准矩形波导与常见双脊波导的结构尺寸、工作频段和法兰实践速查
数据来源: MIL-DTL-3922, IEC 60154, EIA RS-261, 公开厂商数据手册
"""

from typing import List, Optional, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.base.tool_base import ToolBase


class WaveguideInfo:
    """波导信息数据类"""

    def __init__(
        self,
        wr: str,
        iec: str,
        a_mm: float,
        b_mm: float,
        fc_ghz: float,
        f_low: float,
        f_high: float,
        ieee_band: str,
        flange_cover: str,
        flange_choke: str,
        color: str = "#F0F7FF",
    ):
        self.wr = wr
        self.iec = iec
        self.a_mm = a_mm
        self.b_mm = b_mm
        self.fc_ghz = fc_ghz
        self.f_low = f_low
        self.f_high = f_high
        self.ieee_band = ieee_band
        self.flange_cover = flange_cover
        self.flange_choke = flange_choke
        self.color = color


class DoubleRidgeWaveguideInfo:
    """双脊波导补充信息"""

    def __init__(
        self,
        model: str,
        a_mm: Optional[float],
        b_mm: Optional[float],
        ridge_gap_mm: Optional[float],
        ridge_width_mm: Optional[float],
        f_low: float,
        f_high: float,
        ieee_band: str,
        flange_style: str,
        compatibility_note: str,
        notes: str,
        source: str,
        flange_outline_mm: Optional[Tuple[float, float]] = None,
        color: str = "#FFF8EA",
    ):
        self.model = model
        self.a_mm = a_mm
        self.b_mm = b_mm
        self.ridge_gap_mm = ridge_gap_mm
        self.ridge_width_mm = ridge_width_mm
        self.f_low = f_low
        self.f_high = f_high
        self.ieee_band = ieee_band
        self.flange_style = flange_style
        self.compatibility_note = compatibility_note
        self.notes = notes
        self.source = source
        self.flange_outline_mm = flange_outline_mm
        self.color = color


class WaveguideCrossSectionWidget(QWidget):
    """波导截面结构尺寸示意图"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._title = "截面结构尺寸图"
        self._placeholder = "点击上方表格中的型号，这里会显示对应的波导截面尺寸示意。"
        self._a_mm: Optional[float] = None
        self._b_mm: Optional[float] = None
        self._ridge_gap_mm: Optional[float] = None
        self._ridge_width_mm: Optional[float] = None
        self.setMinimumHeight(340)

    def clear_preview(self, title: str, placeholder: str):
        self._title = title
        self._placeholder = placeholder
        self._a_mm = None
        self._b_mm = None
        self._ridge_gap_mm = None
        self._ridge_width_mm = None
        self.update()

    def set_waveguide(
        self,
        title: str,
        a_mm: Optional[float],
        b_mm: Optional[float],
        ridge_gap_mm: Optional[float] = None,
        ridge_width_mm: Optional[float] = None,
    ):
        self._title = title
        self._placeholder = ""
        self._a_mm = a_mm
        self._b_mm = b_mm
        self._ridge_gap_mm = ridge_gap_mm
        self._ridge_width_mm = ridge_width_mm
        self.update()

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#FFFFFF"))

        outer_panel = QRectF(10, 10, self.width() - 20, self.height() - 20)
        painter.setPen(QPen(QColor("#E2E8F0"), 1.2))
        painter.setBrush(QColor("#FBFCFE"))
        painter.drawRoundedRect(outer_panel, 14, 14)

        painter.setPen(QPen(QColor("#1A1A1A")))
        painter.drawText(
            QRectF(24, 20, self.width() - 48, 24),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._title,
        )

        if self._a_mm is None or self._b_mm is None:
            painter.setPen(QPen(QColor("#718096")))
            painter.drawText(
                QRectF(40, 70, self.width() - 80, self.height() - 120),
                Qt.AlignmentFlag.AlignCenter,
                self._placeholder,
            )
            return

        is_double_ridge = self._ridge_gap_mm is not None or self._ridge_width_mm is not None
        content_rect = outer_panel.adjusted(18, 42, -18, -18)
        left_annotation = 38 if is_double_ridge else 24
        right_annotation = 64
        top_annotation = 56 if is_double_ridge else 28
        bottom_annotation = 48
        wall = 14.0
        draw_area = QRectF(
            content_rect.left() + left_annotation,
            content_rect.top() + top_annotation,
            max(content_rect.width() - left_annotation - right_annotation, 40.0),
            max(content_rect.height() - top_annotation - bottom_annotation, 40.0),
        )
        scale = min(draw_area.width() / self._a_mm, draw_area.height() / self._b_mm)
        aperture_w = self._a_mm * scale
        aperture_h = self._b_mm * scale
        outer_w = aperture_w + wall * 2
        outer_h = aperture_h + wall * 2
        outer_x = draw_area.left() + max((draw_area.width() - outer_w) / 2, 0)
        outer_y = draw_area.top() + max((draw_area.height() - outer_h) / 2, 0)

        metal_rect = QRectF(outer_x, outer_y, outer_w, outer_h)
        aperture_rect = QRectF(outer_x + wall, outer_y + wall, aperture_w, aperture_h)

        painter.setPen(QPen(QColor("#91A4BC"), 1.5))
        painter.setBrush(QColor("#D7E2EE"))
        painter.drawRoundedRect(metal_rect, 10, 10)

        painter.setPen(QPen(QColor("#8EA2B5"), 1.2))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRect(aperture_rect)

        self._draw_horizontal_dimension(
            painter,
            aperture_rect.left(),
            aperture_rect.right(),
            aperture_rect.bottom(),
            aperture_rect.bottom() + 26,
            f"a = {self._a_mm:.2f} mm",
            label_above=False,
        )
        self._draw_vertical_dimension(
            painter,
            aperture_rect.right(),
            aperture_rect.right() + 34,
            aperture_rect.top(),
            aperture_rect.bottom(),
            f"b = {self._b_mm:.2f} mm",
            label_on_left=False,
        )

        if is_double_ridge and self._ridge_gap_mm and self._ridge_width_mm:
            ridge_gap = self._ridge_gap_mm * scale
            ridge_width = self._ridge_width_mm * scale
            ridge_depth = max((aperture_h - ridge_gap) / 2, 0)
            ridge_x = aperture_rect.center().x() - ridge_width / 2

            top_ridge = QRectF(ridge_x, aperture_rect.top(), ridge_width, ridge_depth)
            bottom_ridge = QRectF(
                ridge_x,
                aperture_rect.bottom() - ridge_depth,
                ridge_width,
                ridge_depth,
            )

            painter.setPen(QPen(QColor("#D97706"), 1.2))
            painter.setBrush(QColor("#FDE8C4"))
            painter.drawRect(top_ridge)
            painter.drawRect(bottom_ridge)

            self._draw_horizontal_dimension(
                painter,
                top_ridge.left(),
                top_ridge.right(),
                top_ridge.top(),
                aperture_rect.top() - 22,
                f"w = {self._ridge_width_mm:.2f} mm",
                label_above=True,
            )
            self._draw_vertical_dimension(
                painter,
                aperture_rect.left(),
                aperture_rect.left() - 34,
                top_ridge.bottom(),
                bottom_ridge.top(),
                f"g = {self._ridge_gap_mm:.2f} mm",
                label_on_left=True,
            )
        elif is_double_ridge:
            painter.setPen(QPen(QColor("#D97706"), 1.2, Qt.PenStyle.DashLine))
            painter.drawLine(
                QPointF(aperture_rect.left(), aperture_rect.center().y()),
                QPointF(aperture_rect.right(), aperture_rect.center().y()),
            )
            painter.setPen(QPen(QColor("#718096")))
            painter.drawText(
                QRectF(aperture_rect.left(), aperture_rect.center().y() - 20, aperture_rect.width(), 40),
                Qt.AlignmentFlag.AlignCenter,
                "当前仅有频段与法兰信息，\nridge gap / ridge width 需按厂家图纸确认。",
            )

    def _draw_horizontal_dimension(
        self,
        painter: QPainter,
        start_x: float,
        end_x: float,
        reference_y: float,
        y: float,
        text: str,
        label_above: bool,
    ):
        arrow = 6
        painter.setPen(QPen(QColor("#94A3B8"), 1.0))
        painter.drawLine(QPointF(start_x, reference_y), QPointF(start_x, y))
        painter.drawLine(QPointF(end_x, reference_y), QPointF(end_x, y))

        painter.setPen(QPen(QColor("#4A5568"), 1.2))
        painter.drawLine(QPointF(start_x, y), QPointF(end_x, y))
        painter.drawLine(QPointF(start_x, y), QPointF(start_x + arrow, y - arrow / 2))
        painter.drawLine(QPointF(start_x, y), QPointF(start_x + arrow, y + arrow / 2))
        painter.drawLine(QPointF(end_x, y), QPointF(end_x - arrow, y - arrow / 2))
        painter.drawLine(QPointF(end_x, y), QPointF(end_x - arrow, y + arrow / 2))

        metrics = painter.fontMetrics()
        label_width = max(float(metrics.horizontalAdvance(text) + 16), 82.0)
        label_height = 22.0
        label_left = (start_x + end_x - label_width) / 2
        label_left = max(18.0, min(label_left, self.width() - label_width - 18.0))
        label_top = y - label_height - 6 if label_above else y + 6
        label_rect = QRectF(label_left, label_top, label_width, label_height)
        self._draw_dimension_label(painter, label_rect, text)

    def _draw_vertical_dimension(
        self,
        painter: QPainter,
        reference_x: float,
        x: float,
        start_y: float,
        end_y: float,
        text: str,
        label_on_left: bool,
    ):
        arrow = 6
        painter.setPen(QPen(QColor("#94A3B8"), 1.0))
        painter.drawLine(QPointF(reference_x, start_y), QPointF(x, start_y))
        painter.drawLine(QPointF(reference_x, end_y), QPointF(x, end_y))

        painter.setPen(QPen(QColor("#4A5568"), 1.2))
        painter.drawLine(QPointF(x, start_y), QPointF(x, end_y))
        painter.drawLine(QPointF(x, start_y), QPointF(x - arrow / 2, start_y + arrow))
        painter.drawLine(QPointF(x, start_y), QPointF(x + arrow / 2, start_y + arrow))
        painter.drawLine(QPointF(x, end_y), QPointF(x - arrow / 2, end_y - arrow))
        painter.drawLine(QPointF(x, end_y), QPointF(x + arrow / 2, end_y - arrow))

        metrics = painter.fontMetrics()
        label_length = max(float(metrics.horizontalAdvance(text) + 16), 82.0)
        label_thickness = 22.0
        label_center_x = x - 16 if label_on_left else x + 16
        label_center_x = max(18.0 + label_thickness / 2, min(label_center_x, self.width() - 18.0 - label_thickness / 2))
        label_center_y = (start_y + end_y) / 2
        label_center_y = max(20.0 + label_length / 2, min(label_center_y, self.height() - 20.0 - label_length / 2))

        painter.save()
        painter.translate(label_center_x, label_center_y)
        painter.rotate(-90)
        label_rect = QRectF(-label_length / 2, -label_thickness / 2, label_length, label_thickness)
        self._draw_dimension_label(painter, label_rect, text)
        painter.restore()

    def _draw_dimension_label(self, painter: QPainter, rect: QRectF, text: str):
        painter.save()
        painter.setPen(QPen(QColor("#D7DEE7"), 1.0))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(rect, 6, 6)
        painter.setPen(QPen(QColor("#334155"), 1.0))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()


class WaveguideTableTool(ToolBase):
    """标准波导法兰参考表"""

    tool_name = "波导法兰参考"
    tool_icon = "🔧"
    tool_category = "reference"
    tool_description = "标准矩形波导、双脊波导与截面尺寸速查 (EIA/IEC/MIL/WRD)"

    def on_band_filter_changed(self, index: int):
        self._current_band = self._band_combo.itemData(index)
        self._update_table()

    def on_search_text_changed(self, text: str):
        self._current_filter_text = text
        self._update_table()

    def __init__(self, parent: Optional[QWidget] = None):
        self._current_band = "ALL"
        self._current_filter_text = ""
        self._filtered_waveguide_data: List[WaveguideInfo] = []
        self._filtered_ridge_data: List[DoubleRidgeWaveguideInfo] = []
        self._selected_mode: Optional[str] = None
        self._selected_key: Optional[str] = None
        self._selection_sync_in_progress = False
        self._init_data()
        super().__init__(parent)

    def _init_data(self):
        C = "#F0F7FF"
        R = "#FFF8EA"

        self.waveguide_data: List[WaveguideInfo] = [
            WaveguideInfo("WR-2300", "R3", 584.20, 292.10, 0.257, 0.32, 0.49, "UHF/L", "—", "—", C),
            WaveguideInfo("WR-2100", "R4", 533.40, 266.70, 0.281, 0.35, 0.53, "UHF/L", "—", "—", C),
            WaveguideInfo("WR-1800", "R5", 457.20, 228.60, 0.328, 0.39, 0.63, "UHF/L", "—", "—", C),
            WaveguideInfo("WR-1500", "R6", 381.00, 190.50, 0.394, 0.49, 0.75, "UHF/L", "—", "—", C),
            WaveguideInfo("WR-1150", "R8", 292.10, 146.05, 0.514, 0.64, 0.96, "UHF", "—", "—", C),
            WaveguideInfo("WR-975", "R9", 247.65, 123.83, 0.605, 0.75, 1.12, "UHF/L", "—", "—", C),
            WaveguideInfo("WR-770", "R12", 195.58, 97.79, 0.767, 0.96, 1.45, "L", "—", "—", C),
            WaveguideInfo("WR-650", "R14", 165.10, 82.55, 0.908, 1.12, 1.70, "L", "UG-419/U", "UG-420/U", C),
            WaveguideInfo("WR-510", "R18", 129.54, 64.77, 1.158, 1.45, 2.20, "L/S", "UG-51A/U", "UG-52/U", C),
            WaveguideInfo("WR-430", "R22", 109.22, 54.61, 1.372, 1.70, 2.60, "L/S", "UG-435/U", "UG-436/U", C),
            WaveguideInfo("WR-340", "R26", 86.36, 43.18, 1.737, 2.20, 3.30, "S", "UG-553/U", "UG-554/U", C),
            WaveguideInfo("WR-284", "R32", 72.14, 34.04, 2.079, 2.60, 3.95, "S", "UG-584/U", "UG-585/U", C),
            WaveguideInfo("WR-229", "R40", 58.17, 29.08, 2.577, 3.30, 4.90, "S/C", "UG-599/U", "UG-600/U", C),
            WaveguideInfo("WR-187", "R48", 47.55, 22.15, 3.155, 3.95, 5.85, "C", "UG-149/U", "UG-148/U", C),
            WaveguideInfo("WR-159", "R58", 40.39, 20.19, 3.714, 4.64, 7.05, "C", "UG-1731/U", "UG-1732/U", C),
            WaveguideInfo("WR-137", "R70", 34.85, 15.80, 4.304, 5.85, 8.20, "C/X", "UG-344/U", "UG-343/U", C),
            WaveguideInfo("WR-112", "R84", 28.50, 12.62, 5.263, 7.05, 10.00, "X", "UG-51/U", "UG-52/U", C),
            WaveguideInfo("WR-90", "R100", 22.86, 10.16, 6.562, 8.20, 12.40, "X", "UG-135/U", "UG-136/U", C),
            WaveguideInfo("WR-75", "R120", 19.05, 9.53, 7.874, 10.00, 15.00, "X/Ku", "UG-383/U", "UG-384/U", C),
            WaveguideInfo("WR-62", "R140", 15.80, 7.90, 9.494, 12.40, 18.00, "Ku", "UG-541/U", "UG-542/U", C),
            WaveguideInfo("WR-51", "R180", 12.95, 6.48, 11.583, 15.00, 22.00, "Ku/K", "UG-417/U", "UG-418/U", C),
            WaveguideInfo("WR-42", "R220", 10.67, 4.32, 14.058, 18.00, 26.50, "K", "UG-595/U", "UG-596/U", C),
            WaveguideInfo("WR-34", "R260", 8.64, 4.32, 17.361, 22.00, 33.00, "K/Ka", "UG-1530/U", "UG-1531/U", C),
            WaveguideInfo("WR-28", "R320", 7.11, 3.56, 21.097, 26.50, 40.00, "Ka", "UG-599/U", "UG-600/U", C),
            WaveguideInfo("WR-22", "R400", 5.69, 2.84, 26.363, 33.00, 50.00, "Q", "UG-383/U", "UG-384/U", C),
            WaveguideInfo("WR-19", "R500", 4.78, 2.39, 31.381, 40.00, 60.00, "U", "UG-383/U", "UG-384/U", C),
            WaveguideInfo("WR-15", "R620", 3.76, 1.88, 39.894, 50.00, 75.00, "V", "UG-385/U", "UG-386/U", C),
            WaveguideInfo("WR-12", "R740", 3.10, 1.55, 48.387, 60.00, 90.00, "E", "UG-387/U", "—", C),
            WaveguideInfo("WR-10", "R900", 2.54, 1.27, 59.055, 75.00, 110.00, "W", "UG-387/U", "—", C),
            WaveguideInfo("WR-8", "R1200", 2.03, 1.02, 73.892, 90.0, 140.0, "F", "UG-387/U", "—", C),
            WaveguideInfo("WR-6.5", "R1400", 1.65, 0.83, 90.909, 110.0, 170.0, "D", "UG-387/U", "—", C),
            WaveguideInfo("WR-5.1", "R1800", 1.30, 0.65, 115.385, 140.0, 220.0, "G", "UG-387/U", "—", C),
            WaveguideInfo("WR-4.3", "R2200", 1.09, 0.55, 137.615, 170.0, 260.0, "—", "UG-387/U", "—", C),
            WaveguideInfo("WR-3.4", "R2600", 0.86, 0.43, 174.419, 220.0, 325.0, "—", "UG-387/U", "—", C),
        ]

        self.double_ridge_data: List[DoubleRidgeWaveguideInfo] = [
            DoubleRidgeWaveguideInfo(
                "WRD840", 156.61, 72.46, 31.11, 39.17, 0.80, 2.00, "L/S",
                "FPWRD840 大型双脊法兰",
                "FPWRD840 前视法兰外形常见约 188 × 127 mm，通常通过同系列宽带过渡或同厂家组件互连；与标准 WR 宽带转换时需同时核对孔距、定位基准与脊中心线。",
                "RFTOP 前视图可读 aperture 156.61 × 72.46 mm、ridge gap 31.11 mm、ridge width 39.17 mm；上部机身宽约 211 mm。",
                "RFTOP RWDDC840N-60 PDF 前视图 / RF ONE AWRD840N",
                (188.0, 127.0),
                R,
            ),
            DoubleRidgeWaveguideInfo(
                "WRD250", 42.04, 19.05, 3.81, 11.18, 2.60, 7.80, "S/C",
                "FPWRD250 / 专用双脊法兰",
                "孔位与定位基准通常按 FPWRD250 图纸执行，不能与 WR-284/WR-229 的标准 Cover/Choke 直接混配。",
                "适合 2.6-7.8 GHz 宽带过渡与测量，法兰板外形常见约 81 × 62 mm。",
                "公开法兰图 FPWRD250 与产品摘要",
                (81.0, 62.0),
                R,
            ),
            DoubleRidgeWaveguideInfo(
                "WRD350", 37.59, 17.48, 7.42, 9.40, 3.50, 8.20, "S/C/X",
                "FPWRD350 / 专用双脊法兰",
                "常见过渡链路会引到 WR-187 或 WR-159 附近频段，但直连仍需同图纸孔位和 ridge 对中。",
                "3.5-8.2 GHz 宽带常用，公开法兰图可读出约 69.9 × 50.8 mm 外形。",
                "公开法兰图 FPWRD350 与 RFTOP 产品页",
                (69.9, 50.8),
                R,
            ),
            DoubleRidgeWaveguideInfo(
                "WRD475", 27.69, 12.85, 5.46, 6.91, 4.75, 11.00, "C/X",
                "FPWRD475 / 专用双脊法兰",
                "法兰板常见约 50 × 35.3 mm，跨厂家互连时需重点核对定位销和面形公差。",
                "常见于宽带同轴过渡、宽带耦合器和双脊喇叭前端。",
                "公开法兰图 FPWRD475 与 RFTOP 产品页",
                (50.0, 35.3),
                R,
            ),
            DoubleRidgeWaveguideInfo(
                "WRD500", 19.10, 8.20, 1.60, 4.78, 5.00, 18.00, "C/X/Ku/K",
                "FPWRD500 / 专用双脊法兰",
                "常见法兰板约 42.93 × 31.75 mm，跨厂家时仍需复核螺孔、定位与 ridge 中心线。",
                "5-18 GHz 超过三倍频程，适合实验室宽带前端、EMC 夹具和测量治具。",
                "公开法兰图 FPWRD500 与产品摘要",
                (42.93, 31.75),
                R,
            ),
            DoubleRidgeWaveguideInfo(
                "WRD650", 18.29, 8.15, 2.57, 4.39, 6.50, 18.00, "X/Ku/K",
                "UG 方形外形 / 定制双脊法兰",
                "频段可覆盖 WR-90 至 WR-62 常见过渡，但不能直接把标准 WR Cover/Choke 当作通配法兰。",
                "6.5-18 GHz 宽带链路较常见，公开法兰图可读出约 35 × 25.4 mm 外形。",
                "公开法兰图 FPWRD650 与 RFTOP 产品页",
                (35.0, 25.4),
                R,
            ),
            DoubleRidgeWaveguideInfo(
                "WRD110", 11.96, 5.56, 2.36, 3.00, 11.00, 26.50, "Ku/K/Ka",
                "FPWRD110 精密双脊法兰",
                "FPWRD110 前视法兰外形常见约 25.4 × 25.4 mm，不能与标准 WR-42 / WR-34 法兰直接混配；推荐使用同系列宽带过渡件，并核对销孔与 ridge 对中。",
                "RFTOP 前视图可读 aperture 11.96 × 5.56 mm、ridge gap 2.36 mm、ridge width 3.00 mm；适合 11-26.5 GHz 宽带测试前端。",
                "RFTOP RWRD110S PDF 前视图 / RF ONE AWRD110SMA",
                (25.4, 25.4),
                R,
            ),
            DoubleRidgeWaveguideInfo(
                "WRD180", 7.32, 3.40, 1.45, 1.83, 18.00, 40.00, "K/Ka/Q",
                "FPWRD180 精密双脊法兰",
                "FPWRD180 前视法兰外形常见约 22.2 × 22.2 mm，多通过 WRD180 系列耦合器或转接器互连；跨厂硬配前需复核孔位、销孔和 ridge 中心线。",
                "RFTOP 前视图可读 aperture 7.32 × 3.40 mm、ridge gap 1.45 mm、ridge width 1.83 mm；18-40 GHz 对平面度与装配力矩更敏感。",
                "RFTOP RWDDCD180K-40 PDF 前视图 / ATM WRD180C24",
                (22.2, 22.2),
                R,
            ),
        ]

        self.ieee_bands = [
            "ALL", "UHF", "L", "S", "C", "X", "Ku", "K", "Ka",
            "Q", "U", "V", "E", "W", "F", "D", "G",
        ]

    def create_input_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("🔍 筛选与控制")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title)

        band_label = QLabel("按 IEEE 频段筛选:")
        layout.addWidget(band_label)

        self._band_combo = QComboBox()
        self._band_combo.addItem("全部频段", "ALL")
        for band in self.ieee_bands[1:]:
            self._band_combo.addItem(f"{band} 频段", band)
        self._band_combo.currentIndexChanged.connect(self.on_band_filter_changed)
        layout.addWidget(self._band_combo)

        search_label = QLabel("搜索波导 / 双脊型号:")
        layout.addWidget(search_label)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("输入 WR/WRD 编号或频率，例如 WR-90、WRD650、18")
        self._search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self._search_input)

        info = QLabel(
            "表格数据说明:\n"
            "• 标准 WR 尺寸依据 EIA RS-261，法兰参考 MIL-DTL-3922。\n"
            "• 双脊 WRD 条目补充 ridge gap、ridge width、典型过渡 WR 与法兰兼容备注。\n"
            "• 点击任意行可查看对应截面结构尺寸图和法兰说明。\n"
            "• WRD110、WRD180、WRD840 已补到可绘图级别，数值来自公开 PDF 前视图；最终加工仍建议回到原始厂家图纸复核。"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 11px; margin-top: 10px;")
        layout.addWidget(info)

        detail_card = QFrame()
        detail_card.setObjectName("ResultPanel")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(18, 18, 18, 18)
        detail_layout.setSpacing(8)

        detail_title = QLabel("截面结构尺寸图")
        detail_title.setObjectName("ResultTitle")
        detail_layout.addWidget(detail_title)

        detail_desc = QLabel("左侧联动显示当前所选波导的截面尺寸、ridge 参数与法兰摘要。")
        detail_desc.setObjectName("ResultDescription")
        detail_desc.setWordWrap(True)
        detail_layout.addWidget(detail_desc)

        self._diagram_widget = WaveguideCrossSectionWidget()
        self._diagram_widget.clear_preview(
            "截面结构尺寸图",
            "点击右侧表格中的型号，\n这里会显示对应的波导截面尺寸示意。",
        )
        detail_layout.addWidget(self._diagram_widget)

        self._detail_heading = QLabel("尚未选择型号")
        self._detail_heading.setStyleSheet("font-size: 16px; font-weight: 600; color: #1A1A1A;")
        detail_layout.addWidget(self._detail_heading)

        self._detail_body = QLabel("请选择右侧表格中的型号。")
        self._detail_body.setWordWrap(True)
        self._detail_body.setTextFormat(Qt.TextFormat.RichText)
        self._detail_body.setStyleSheet("font-size: 13px; color: #4A5568; line-height: 1.8;")
        detail_layout.addWidget(self._detail_body)

        layout.addWidget(detail_card, 1)
        return panel

    def create_result_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        standard_title = QLabel("标准矩形波导")
        standard_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(standard_title)

        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels([
            "WR 编号", "IEC", "a×b (mm)", "截止频率\n(GHz)", "工作频段\n(GHz)",
            "IEEE\n频段", "Cover 法兰\n(MIL)", "Choke 法兰\n(MIL)",
        ])
        header = self._table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        vertical_header = self._table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setMinimumHeight(330)
        self._table.itemSelectionChanged.connect(self._on_standard_selection_changed)
        layout.addWidget(self._table)

        ridge_title = QLabel("双脊波导补充速查")
        ridge_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(ridge_title)

        ridge_hint = QLabel(
            "WRD 表右侧仅保留核心几何参数和频段信息。"
            "典型过渡、法兰兼容和工程说明收敛到左侧详情区，点击型号后查看。"
        )
        ridge_hint.setWordWrap(True)
        ridge_hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(ridge_hint)

        self._ridge_table = QTableWidget()
        self._ridge_table.setColumnCount(4)
        self._ridge_table.setHorizontalHeaderLabels([
            "双脊型号", "a×b (mm)", "gap / width\n(mm)", "典型频段\n(GHz)",
        ])
        ridge_header = self._ridge_table.horizontalHeader()
        if ridge_header is not None:
            ridge_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            ridge_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            ridge_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            ridge_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        ridge_vertical_header = self._ridge_table.verticalHeader()
        if ridge_vertical_header is not None:
            ridge_vertical_header.setVisible(False)
        self._ridge_table.setAlternatingRowColors(True)
        self._ridge_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._ridge_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._ridge_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._ridge_table.setWordWrap(True)
        self._ridge_table.setMinimumHeight(260)
        self._ridge_table.itemSelectionChanged.connect(self._on_ridge_selection_changed)
        layout.addWidget(self._ridge_table)

        self._update_table()
        return panel

    def _matches_filters(self, band_text: str, searchable: str, filter_text: str) -> bool:
        if self._current_band != "ALL":
            bands = [band.strip() for band in band_text.split("/")]
            if self._current_band not in bands:
                return False

        if filter_text and filter_text not in searchable:
            return False

        return True

    def _format_optional_mm(self, value: Optional[float]) -> str:
        if value is None:
            return "待核图"
        return f"{value:.2f}"

    def _format_dimension_pair(self, a_mm: Optional[float], b_mm: Optional[float]) -> str:
        if a_mm is None or b_mm is None:
            return "待核图"
        return f"{a_mm:.2f} × {b_mm:.2f}"

    def _find_transition_targets(self, ridge: DoubleRidgeWaveguideInfo) -> List[str]:
        overlaps = []
        for wg in self.waveguide_data:
            if max(ridge.f_low, wg.f_low) < min(ridge.f_high, wg.f_high):
                overlaps.append(wg.wr)
        return overlaps

    def _build_transition_text(self, ridge: DoubleRidgeWaveguideInfo) -> str:
        overlaps = self._find_transition_targets(ridge)
        return ", ".join(overlaps) if overlaps else "暂无明确重叠"

    def _update_table(self):
        filter_text = self._current_filter_text.lower().strip()

        filtered_standard: List[WaveguideInfo] = []
        for wg in self.waveguide_data:
            searchable = (
                f"{wg.wr} {wg.iec} {wg.ieee_band} {wg.flange_cover} {wg.flange_choke} {wg.f_low} {wg.f_high}"
            ).lower()
            if self._matches_filters(wg.ieee_band, searchable, filter_text):
                filtered_standard.append(wg)

        self._filtered_waveguide_data = filtered_standard
        self._table.setRowCount(len(filtered_standard))
        for row, wg in enumerate(filtered_standard):
            wr_item = QTableWidgetItem(wg.wr)
            wr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            wr_item.setBackground(QColor(wg.color))
            wr_font = wr_item.font()
            wr_font.setBold(True)
            wr_item.setFont(wr_font)
            self._table.setItem(row, 0, wr_item)

            iec_item = QTableWidgetItem(wg.iec)
            iec_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, iec_item)

            dim_item = QTableWidgetItem(f"{wg.a_mm:.2f} × {wg.b_mm:.2f}")
            dim_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, dim_item)

            fc_item = QTableWidgetItem(f"{wg.fc_ghz:.3f}")
            fc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, fc_item)

            freq_item = QTableWidgetItem(f"{wg.f_low:.2f} - {wg.f_high:.2f}")
            freq_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 4, freq_item)

            band_item = QTableWidgetItem(wg.ieee_band)
            band_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 5, band_item)

            cover_item = QTableWidgetItem(wg.flange_cover)
            cover_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 6, cover_item)

            choke_item = QTableWidgetItem(wg.flange_choke)
            choke_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 7, choke_item)

        filtered_ridge: List[DoubleRidgeWaveguideInfo] = []
        for ridge in self.double_ridge_data:
            searchable = (
                f"{ridge.model} {ridge.ieee_band} {ridge.flange_style} {ridge.compatibility_note} {ridge.notes}"
                f" {ridge.source} {ridge.f_low} {ridge.f_high} {self._build_transition_text(ridge)}"
            ).lower()
            if self._matches_filters(ridge.ieee_band, searchable, filter_text):
                filtered_ridge.append(ridge)

        self._filtered_ridge_data = filtered_ridge
        self._ridge_table.setRowCount(len(filtered_ridge))
        for row, ridge in enumerate(filtered_ridge):
            model_item = QTableWidgetItem(ridge.model)
            model_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model_item.setBackground(QColor(ridge.color))
            model_font = model_item.font()
            model_font.setBold(True)
            model_item.setFont(model_font)
            self._ridge_table.setItem(row, 0, model_item)

            dim_item = QTableWidgetItem(self._format_dimension_pair(ridge.a_mm, ridge.b_mm))
            dim_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._ridge_table.setItem(row, 1, dim_item)

            gap_item = QTableWidgetItem(
                f"g={self._format_optional_mm(ridge.ridge_gap_mm)} / w={self._format_optional_mm(ridge.ridge_width_mm)}"
            )
            gap_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._ridge_table.setItem(row, 2, gap_item)

            freq_item = QTableWidgetItem(f"{ridge.f_low:.2f} - {ridge.f_high:.2f}")
            freq_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._ridge_table.setItem(row, 3, freq_item)

        self._ridge_table.resizeRowsToContents()
        self._restore_selection(filter_text)

    def _restore_selection(self, filter_text: str):
        if self._selected_mode == "standard" and self._selected_key:
            for index, wg in enumerate(self._filtered_waveguide_data):
                if wg.wr == self._selected_key:
                    self._select_standard_row(index)
                    return

        if self._selected_mode == "ridge" and self._selected_key:
            for index, ridge in enumerate(self._filtered_ridge_data):
                if ridge.model == self._selected_key:
                    self._select_ridge_row(index)
                    return

        if self._filtered_ridge_data and (filter_text.startswith("wrd") or not self._filtered_waveguide_data):
            self._select_ridge_row(0)
            return

        if self._filtered_waveguide_data:
            self._select_standard_row(0)
            return

        if self._filtered_ridge_data:
            self._select_ridge_row(0)
            return

        self._selected_mode = None
        self._selected_key = None
        self._detail_heading.setText("当前筛选条件下没有匹配型号")
        self._detail_body.setText("请调整频段筛选或搜索条件。")
        self._diagram_widget.clear_preview("截面结构尺寸图", "当前筛选条件下没有可展示的波导型号。")

    def _select_standard_row(self, row: int):
        if row < 0 or row >= len(self._filtered_waveguide_data):
            return
        self._selection_sync_in_progress = True
        self._table.blockSignals(True)
        self._ridge_table.blockSignals(True)
        self._ridge_table.clearSelection()
        self._table.selectRow(row)
        self._table.setCurrentCell(row, 0)
        self._ridge_table.blockSignals(False)
        self._table.blockSignals(False)
        self._selection_sync_in_progress = False
        self._show_standard_waveguide(self._filtered_waveguide_data[row])

    def _select_ridge_row(self, row: int):
        if row < 0 or row >= len(self._filtered_ridge_data):
            return
        self._selection_sync_in_progress = True
        self._table.blockSignals(True)
        self._ridge_table.blockSignals(True)
        self._table.clearSelection()
        self._ridge_table.selectRow(row)
        self._ridge_table.setCurrentCell(row, 0)
        self._table.blockSignals(False)
        self._ridge_table.blockSignals(False)
        self._selection_sync_in_progress = False
        self._show_ridge_waveguide(self._filtered_ridge_data[row])

    def _on_standard_selection_changed(self):
        if self._selection_sync_in_progress:
            return
        items = self._table.selectedItems()
        if not items:
            return
        row = items[0].row()
        if row >= len(self._filtered_waveguide_data):
            return
        self._show_standard_waveguide(self._filtered_waveguide_data[row])

    def _on_ridge_selection_changed(self):
        if self._selection_sync_in_progress:
            return
        items = self._ridge_table.selectedItems()
        if not items:
            return
        row = items[0].row()
        if row >= len(self._filtered_ridge_data):
            return
        self._show_ridge_waveguide(self._filtered_ridge_data[row])

    def _show_standard_waveguide(self, wg: WaveguideInfo):
        self._selected_mode = "standard"
        self._selected_key = wg.wr
        self._diagram_widget.set_waveguide(wg.wr, wg.a_mm, wg.b_mm)
        self._detail_heading.setText(f"{wg.wr} | 标准矩形波导")
        self._detail_body.setText(
            f"<b>截面尺寸</b>: {wg.a_mm:.2f} × {wg.b_mm:.2f} mm<br>"
            f"<b>截止频率</b>: {wg.fc_ghz:.3f} GHz<br>"
            f"<b>推荐工作频段</b>: {wg.f_low:.2f} - {wg.f_high:.2f} GHz ({wg.ieee_band})<br>"
            f"<b>常见法兰</b>: Cover {wg.flange_cover} / Choke {wg.flange_choke}<br>"
            "<b>工程提示</b>: 标准 WR 与双脊 WRD 之间应通过专用宽带过渡件连接，不能按法兰外形直接硬配。"
        )

    def _show_ridge_waveguide(self, ridge: DoubleRidgeWaveguideInfo):
        self._selected_mode = "ridge"
        self._selected_key = ridge.model
        self._diagram_widget.set_waveguide(
            ridge.model,
            ridge.a_mm,
            ridge.b_mm,
            ridge.ridge_gap_mm,
            ridge.ridge_width_mm,
        )

        flange_outline = "待核图"
        if ridge.flange_outline_mm:
            flange_outline = f"{ridge.flange_outline_mm[0]:.2f} × {ridge.flange_outline_mm[1]:.2f} mm"

        geometry_text = self._format_dimension_pair(ridge.a_mm, ridge.b_mm)
        ridge_text = f"g={self._format_optional_mm(ridge.ridge_gap_mm)} mm / w={self._format_optional_mm(ridge.ridge_width_mm)} mm"
        transition_text = self._build_transition_text(ridge)

        self._detail_heading.setText(f"{ridge.model} | 双脊波导")
        self._detail_body.setText(
            f"<b>结构尺寸</b>: {geometry_text}<br>"
            f"<b>ridge 参数</b>: {ridge_text}<br>"
            f"<b>典型频段</b>: {ridge.f_low:.2f} - {ridge.f_high:.2f} GHz ({ridge.ieee_band})<br>"
            f"<b>典型过渡到标准 WR</b>: {transition_text}<br>"
            f"<b>法兰做法</b>: {ridge.flange_style}<br>"
            f"<b>法兰板外形</b>: {flange_outline}<br>"
            f"<b>兼容备注</b>: {ridge.compatibility_note}<br>"
            f"<b>工程说明</b>: {ridge.notes}<br>"
            f"<b>数据来源</b>: {ridge.source}"
        )

    def calculate(self):
        return {}

    def get_intuition_content(self) -> Optional[str]:
        return None

    def get_math_model_content(self) -> Optional[str]:
        return None

    def get_engineering_content(self) -> Optional[str]:
        return """
        <b>🏗️ 波导选型工程指南</b><br><br>

        <b>1. 基本原则:</b><br>
        • 工作频率必须位于 TE₁₀ 截止频率以上，并尽量保持单模工作区间<br>
        • 标准 WR 的宽边 a 决定截止频率，双脊 WRD 则通过 ridge 进一步降低截止频率<br>
        • 宽带需求优先考虑双脊波导，但必须同时核对 ridge gap、ridge width 与法兰图纸<br><br>

        <b>2. 法兰选型:</b><br>
        • <b>Cover (平面法兰)</b>: 结构简单，适合一般连接<br>
        • <b>Choke (扼流法兰)</b>: 接触要求低，重复装配更稳健<br>
        • WRD 法兰命名通常不如标准 WR 统一，跨厂家互连前必须核对孔位、定位销和平面度<br><br>

        <b>3. 双脊过渡实践:</b><br>
        • 工具中的“典型过渡到 WR”按频段重叠自动给出候选标准 WR<br>
        • 这些候选只代表频段层面的常见过渡方向，不等于法兰可直接通配<br>
        • 高频双脊过渡建议优先选同厂家成套转接件，以保证 ridge 对中精度<br><br>

        <b>4. 使用建议:</b><br>
        • 先通过筛选锁定工作频段，再点击型号查看截面尺寸图和法兰兼容备注<br>
        • 对于仅有频段资料而缺少几何参数的 WRD 型号，应回到厂家图纸做最终确认
        """

    def get_history_content(self) -> Optional[str]:
        return """
        <b>📜 矩形波导发展简史</b><br><br>

        <b>理论奠基 (1890s):</b><br>
        Lord Rayleigh 于 1897 年从数学上证明了电磁波可在中空金属管中传播。<br><br>

        <b>实验验证 (1930s):</b><br>
        George Southworth 与 Wilmer Barrow 在 1936 年前后独立完成了波导实验验证。<br><br>

        <b>二战驱动 (1940s):</b><br>
        雷达系统推动了 WR 编号体系、法兰接口和整套微波工程实践快速成熟。<br><br>

        <b>宽带双脊波导 (1950s 以后):</b><br>
        为获得更宽单模带宽，工程界在矩形波导内引入双 ridge。它显著降低截止频率，
        但也带来了更高的机械公差要求。与标准 WR 相比，双脊波导更依赖具体厂家图纸，
        因而在工程互连中常需要“频段重叠 + 图纸核对”两步同时完成。
        """

    def get_boundary_content(self) -> Optional[str]:
        return None
