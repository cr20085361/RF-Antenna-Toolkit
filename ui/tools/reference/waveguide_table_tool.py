# -*- coding: utf-8 -*-
"""
标准波导法兰参考表工具
Standard Waveguide & Flange Reference Table Tool

版本: v2.0.0
功能: 提供 EIA WR 系列标准矩形波导的结构尺寸、工作频段和法兰型号速查
数据来源: MIL-DTL-3922, IEC 60154, EIA RS-261
"""

from typing import Dict, List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QHeaderView, QLineEdit,
    QTableWidget, QTableWidgetItem, QFrame, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.i18n import tr
from ui.base.tool_base import ToolBase


class WaveguideInfo:
    """波导信息数据类"""
    def __init__(
        self,
        wr: str,            # WR 编号 (EIA)
        iec: str,            # IEC 编号
        a_mm: float,         # 宽边内尺寸 a (mm)
        b_mm: float,         # 窄边内尺寸 b (mm)
        fc_ghz: float,       # TE₁₀ 截止频率 (GHz)
        f_low: float,        # 推荐工作频段下限 (GHz)
        f_high: float,       # 推荐工作频段上限 (GHz)
        ieee_band: str,      # 对应 IEEE 频段
        flange_cover: str,   # 标准 Cover 法兰 (MIL-DTL-3922)
        flange_choke: str,   # 标准 Choke 法兰 (MIL-DTL-3922)
        color: str = "#F0F7FF"  # 行背景色
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


class WaveguideTableTool(ToolBase):
    """
    标准波导法兰参考表
    v2.0.0 - 覆盖 EIA WR 系列标准矩形波导
    """

    tool_name = tr("waveguide.tool_name", "波导法兰")
    tool_icon = "🔲"
    tool_category = "reference"
    tool_description = tr("waveguide.tool_desc", "标准矩形波导管、法兰型号及尺寸速查表 (EIA/WR)")
    i18n_title_key = "waveguide.tool_name"
    i18n_desc_key = "waveguide.tool_desc"

    # ========== 回调方法 ==========

    def on_band_filter_changed(self, index: int):
        """IEEE 频段筛选切换"""
        self._current_band = self._band_combo.itemData(index)
        self._update_table()

    def on_search_text_changed(self, text: str):
        """搜索文字变化"""
        self._update_table(filter_text=text)

    # ========== 初始化 ==========

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化"""
        self._current_band = "ALL"  # 默认显示全部
        self._init_data()
        super().__init__(parent)

    def _init_data(self):
        """
        初始化波导数据
        数据来源:
        - 波导尺寸: EIA RS-261, IEC 60154
        - 截止频率: fc = c / (2a), c = 299792458 m/s
        - 法兰型号: MIL-DTL-3922 (美军标)
        注意: 同一波导可能适配多种法兰标准，此处列出最常用的 MIL 法兰。
        """
        # 统一浅色背景
        C = "#F0F7FF"

        self.waveguide_data: List[WaveguideInfo] = [
            # ==================== 低频段 (L/S) ====================
            WaveguideInfo("WR-2300", "R3",   584.20, 292.10, 0.257,  0.32,   0.49,  "UHF/L", "—",          "—",          C),
            WaveguideInfo("WR-2100", "R4",   533.40, 266.70, 0.281,  0.35,   0.53,  "UHF/L", "—",          "—",          C),
            WaveguideInfo("WR-1800", "R5",   457.20, 228.60, 0.328,  0.39,   0.63,  "UHF/L", "—",          "—",          C),
            WaveguideInfo("WR-1500", "R6",   381.00, 190.50, 0.394,  0.49,   0.75,  "UHF/L", "—",          "—",          C),
            WaveguideInfo("WR-1150", "R8",   292.10, 146.05, 0.514,  0.64,   0.96,  "UHF",   "—",          "—",          C),
            WaveguideInfo("WR-975",  "R9",   247.65, 123.83, 0.605,  0.75,   1.12,  "UHF/L", "—",          "—",          C),
            WaveguideInfo("WR-770",  "R12",  195.58,  97.79, 0.767,  0.96,   1.45,  "L",     "—",          "—",          C),
            WaveguideInfo("WR-650",  "R14",  165.10,  82.55, 0.908,  1.12,   1.70,  "L",     "UG-419/U",   "UG-420/U",   C),
            WaveguideInfo("WR-510",  "R18",  129.54,  64.77, 1.158,  1.45,   2.20,  "L/S",   "UG-51A/U",   "UG-52/U",    C),
            WaveguideInfo("WR-430",  "R22",  109.22,  54.61, 1.372,  1.70,   2.60,  "L/S",   "UG-435/U",   "UG-436/U",   C),

            # ==================== 中频段 (S/C/X) ====================
            WaveguideInfo("WR-340",  "R26",   86.36,  43.18, 1.737,  2.20,   3.30,  "S",     "UG-553/U",   "UG-554/U",   C),
            WaveguideInfo("WR-284",  "R32",   72.14,  34.04, 2.079,  2.60,   3.95,  "S",     "UG-584/U",   "UG-585/U",   C),
            WaveguideInfo("WR-229",  "R40",   58.17,  29.08, 2.577,  3.30,   4.90,  "S/C",   "UG-599/U",   "UG-600/U",   C),
            WaveguideInfo("WR-187",  "R48",   47.55,  22.15, 3.155,  3.95,   5.85,  "C",     "UG-149/U",   "UG-148/U",   C),
            WaveguideInfo("WR-159",  "R58",   40.39,  20.19, 3.714,  4.64,   7.05,  "C",     "UG-1731/U",  "UG-1732/U",  C),
            WaveguideInfo("WR-137",  "R70",   34.85,  15.80, 4.304,  5.85,   8.20,  "C/X",   "UG-344/U",   "UG-343/U",   C),
            WaveguideInfo("WR-112",  "R84",   28.50,  12.62, 5.263,  7.05,  10.00,  "X",     "UG-51/U",    "UG-52/U",    C),
            WaveguideInfo("WR-90",   "R100",  22.86,  10.16, 6.562,  8.20,  12.40,  "X",     "UG-135/U",   "UG-136/U",   C),

            # ==================== 高频段 (Ku/K/Ka) ====================
            WaveguideInfo("WR-75",   "R120",  19.05,   9.53, 7.874, 10.00,  15.00,  "X/Ku",  "UG-383/U",   "UG-384/U",   C),
            WaveguideInfo("WR-62",   "R140",  15.80,   7.90, 9.494, 12.40,  18.00,  "Ku",    "UG-541/U",   "UG-542/U",   C),
            WaveguideInfo("WR-51",   "R180",  12.95,   6.48, 11.583,15.00,  22.00,  "Ku/K",  "UG-417/U",   "UG-418/U",   C),
            WaveguideInfo("WR-42",   "R220",  10.67,   4.32, 14.058,18.00,  26.50,  "K",     "UG-595/U",   "UG-596/U",   C),
            WaveguideInfo("WR-34",   "R260",   8.64,   4.32, 17.361,22.00,  33.00,  "K/Ka",  "UG-1530/U",  "UG-1531/U",  C),
            WaveguideInfo("WR-28",   "R320",   7.11,   3.56, 21.097,26.50,  40.00,  "Ka",    "UG-599/U",   "UG-600/U",   C),

            # ==================== 毫米波 (Q/U/V/E/W) ====================
            WaveguideInfo("WR-22",   "R400",   5.69,   2.84, 26.363,33.00,  50.00,  "Q",     "UG-383/U",   "UG-384/U",   C),
            WaveguideInfo("WR-19",   "R500",   4.78,   2.39, 31.381,40.00,  60.00,  "U",     "UG-383/U",   "UG-384/U",   C),
            WaveguideInfo("WR-15",   "R620",   3.76,   1.88, 39.894,50.00,  75.00,  "V",     "UG-385/U",   "UG-386/U",   C),
            WaveguideInfo("WR-12",   "R740",   3.10,   1.55, 48.387,60.00,  90.00,  "E",     "UG-387/U",   "—",          C),
            WaveguideInfo("WR-10",   "R900",   2.54,   1.27, 59.055,75.00, 110.00,  "W",     "UG-387/U",   "—",          C),

            # ==================== 亚毫米波 (高端) ====================
            WaveguideInfo("WR-8",    "R1200",  2.03,   1.02, 73.892, 90.0, 140.0,   "F",     "UG-387/U",   "—",          C),
            WaveguideInfo("WR-6.5",  "R1400",  1.65,   0.83, 90.909,110.0, 170.0,   "D",     "UG-387/U",   "—",          C),
            WaveguideInfo("WR-5.1",  "R1800",  1.30,   0.65,115.385,140.0, 220.0,   "G",     "UG-387/U",   "—",          C),
            WaveguideInfo("WR-4.3",  "R2200",  1.09,   0.55,137.615,170.0, 260.0,   "—",     "UG-387/U",   "—",          C),
            WaveguideInfo("WR-3.4",  "R2600",  0.86,   0.43,174.419,220.0, 325.0,   "—",     "UG-387/U",   "—",          C),
        ]

        # IEEE 频段列表 (用于筛选)
        self.ieee_bands = [
            "ALL", "UHF", "L", "S", "C", "X", "Ku", "K", "Ka",
            "Q", "U", "V", "E", "W", "F", "D", "G"
        ]

    # ========== UI 面板 ==========

    def create_input_panel(self) -> QWidget:
        """创建左侧筛选面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 标题
        title = QLabel(tr("waveguide.lbl_filter_control", "🔍 筛选与控制"))
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title)

        # 1. IEEE 频段筛选
        band_label = QLabel(tr("waveguide.lbl_filter_ieee_band", "按 IEEE 频段筛选:"))
        layout.addWidget(band_label)

        self._band_combo = QComboBox()
        self._band_combo.addItem(tr("waveguide.opt_all_bands", "全部频段"), "ALL")
        for band in self.ieee_bands[1:]:
            self._band_combo.addItem(f"{band} {tr('waveguide.opt_band_suffix', '频段')}", band)
        self._band_combo.currentIndexChanged.connect(self.on_band_filter_changed)
        layout.addWidget(self._band_combo)

        # 2. 搜索框
        search_label = QLabel(tr("waveguide.lbl_search_waveguide", "搜索波导:"))
        layout.addWidget(search_label)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(tr("waveguide.ph_search_waveguide", "输入 WR 编号或频率 (如 'WR-90' 或 '10')"))
        self._search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self._search_input)

        # 说明
        info = QLabel(
            tr("waveguide.lbl_table_info_title", "表格数据说明:") + "\n"
            + tr("waveguide.lbl_table_info_eia", "• 波导尺寸依据 EIA RS-261") + "\n"
            + tr("waveguide.lbl_table_info_mil", "• 法兰型号依据 MIL-DTL-3922") + "\n"
            + tr("waveguide.lbl_table_info_multi_flange", "• 同一波导可能适配多种法兰") + "\n"
            + tr("waveguide.lbl_table_info_cover_choke", "  此处列出最常用的 Cover/Choke") + "\n"
            + tr("waveguide.lbl_table_info_no_std_flange", "• '—' 表示该型号无标准化法兰") + "\n"
            + tr("waveguide.lbl_table_info_custom_flange", "  或通常使用非标/专用法兰")
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 11px; margin-top: 10px;")
        layout.addWidget(info)

        layout.addStretch()
        return panel

    def create_result_panel(self) -> QWidget:
        """创建右侧结果表格"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # 表格
        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels([
            tr("waveguide.tbl_col_wr", "WR 编号"),
            tr("waveguide.tbl_col_iec", "IEC"),
            tr("waveguide.tbl_col_dim", "a×b (mm)"),
            tr("waveguide.tbl_col_fc", "截止频率\n(GHz)"),
            tr("waveguide.tbl_col_freq_range", "工作频段\n(GHz)"),
            tr("waveguide.tbl_col_ieee_band", "IEEE\n频段"),
            tr("waveguide.tbl_col_cover_flange", "Cover 法兰\n(MIL)"),
            tr("waveguide.tbl_col_choke_flange", "Choke 法兰\n(MIL)")
        ])

        # 表头设置
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self._table)

        # 初始填充
        self._update_table()

        return panel

    def _update_table(self, filter_text: str = ""):
        """更新表格内容"""
        filter_text = filter_text.lower().strip()
        band_filter = self._current_band

        filtered = []
        for wg in self.waveguide_data:
            # IEEE 频段筛选
            if band_filter != "ALL":
                # 频段字段可能包含斜杠 (如 "S/C")
                bands = [b.strip() for b in wg.ieee_band.split("/")]
                if band_filter not in bands:
                    continue

            # 文本搜索
            if filter_text:
                searchable = (
                    wg.wr.lower() + " " +
                    wg.iec.lower() + " " +
                    wg.ieee_band.lower() + " " +
                    wg.flange_cover.lower() + " " +
                    wg.flange_choke.lower() + " " +
                    str(wg.f_low) + " " + str(wg.f_high)
                )
                if filter_text not in searchable:
                    continue

            filtered.append(wg)

        # 填充
        self._table.setRowCount(len(filtered))
        for row, wg in enumerate(filtered):
            # WR 编号
            wr_item = QTableWidgetItem(wg.wr)
            wr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            wr_item.setBackground(QColor(wg.color))
            font = wr_item.font()
            font.setBold(True)
            wr_item.setFont(font)
            self._table.setItem(row, 0, wr_item)

            # IEC
            iec_item = QTableWidgetItem(wg.iec)
            iec_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, iec_item)

            # a×b (mm)
            dim_str = f"{wg.a_mm:.2f} × {wg.b_mm:.2f}"
            dim_item = QTableWidgetItem(dim_str)
            dim_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, dim_item)

            # 截止频率
            fc_item = QTableWidgetItem(f"{wg.fc_ghz:.3f}")
            fc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, fc_item)

            # 工作频段
            freq_item = QTableWidgetItem(f"{wg.f_low:.2f} - {wg.f_high:.2f}")
            freq_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 4, freq_item)

            # IEEE 频段
            band_item = QTableWidgetItem(wg.ieee_band)
            band_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 5, band_item)

            # Cover 法兰
            cover_item = QTableWidgetItem(wg.flange_cover)
            cover_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 6, cover_item)

            # Choke 法兰
            choke_item = QTableWidgetItem(wg.flange_choke)
            choke_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 7, choke_item)

    # ========== 基类接口 ==========

    def calculate(self):
        """无计算逻辑"""
        pass

    def get_intuition_content(self) -> Optional[str]:
        return None

    def get_math_model_content(self) -> Optional[str]:
        return None

    def get_engineering_content(self) -> Optional[str]:
        """工程选型指南"""
        return tr("waveguide.eng_content", """
        <b>🏗️ {t_eng_title}</b><br><br>

        <b>1. {t_basic_principles}:</b><br>
        • {t_bp_1}<br>
        • {t_bp_2}<br>
        • {t_bp_3}: fc = c/(2a)<br>
        • {t_bp_4}: b ≈ a/2 ({t_std_ratio})<br><br>

        <b>2. {t_flange_selection}:</b><br>
        • <b>Cover ({t_flat_flange})</b>: {t_flat_desc}<br>
        • <b>Choke ({t_choke_flange})</b>: {t_choke_desc}<br>
        • {t_pair_usage}<br>
        • {t_multi_stds}:<br>
        &nbsp;&nbsp;— MIL-DTL-3922 ({t_mil_std})<br>
        &nbsp;&nbsp;— IEC 60154 ({t_iec_std})<br>
        &nbsp;&nbsp;— CPRF ({t_cprf})<br>
        &nbsp;&nbsp;— CMR ({t_cmr})<br><br>

        <b>3. {t_common_pitfalls}:</b><br>
        • {t_cp_1}<br>
        • {t_cp_2}<br>
        • {t_cp_3}
        """).format(
            t_eng_title=tr("waveguide.eng_title", "波导选型工程指南"),
            t_basic_principles=tr("waveguide.eng_basic_principles", "基本原则"),
            t_bp_1=tr("waveguide.eng_bp_1", "工作频率必须在 TE₁₀ 截止频率 (fc) 到 2fc 之间"),
            t_bp_2=tr("waveguide.eng_bp_2", "推荐工作带宽约为 fc×1.25 ~ fc×1.9 (单模传输)"),
            t_bp_3=tr("waveguide.eng_bp_3", "宽边尺寸 a 决定截止频率"),
            t_bp_4=tr("waveguide.eng_bp_4", "窄边尺寸"),
            t_std_ratio=tr("waveguide.eng_std_ratio", "标准比例"),
            t_flange_selection=tr("waveguide.eng_flange_selection", "法兰选型"),
            t_flat_flange=tr("waveguide.eng_flat_flange", "平面法兰"),
            t_flat_desc=tr("waveguide.eng_flat_desc", "结构简单，适合一般连接"),
            t_choke_flange=tr("waveguide.eng_choke_flange", "扼流法兰"),
            t_choke_desc=tr("waveguide.eng_choke_desc", "含环形槽，接触要求低"),
            t_pair_usage=tr("waveguide.eng_pair_usage", "Cover+Choke 配对使用效果最佳"),
            t_multi_stds=tr("waveguide.eng_multi_stds", "同一波导可能有多种法兰标准"),
            t_mil_std=tr("waveguide.eng_mil_std", "UG 系列, 美军标"),
            t_iec_std=tr("waveguide.eng_iec_std", "国际标准"),
            t_cprf=tr("waveguide.eng_cprf", "商业精密法兰"),
            t_cmr=tr("waveguide.eng_cmr", "商业微波法兰"),
            t_common_pitfalls=tr("waveguide.eng_common_pitfalls", "常见陷阱"),
            t_cp_1=tr("waveguide.eng_cp_1", "WR-28 的 UG-599/U 法兰与 WR-229 的同名法兰不同!"),
            t_cp_2=tr("waveguide.eng_cp_2", "高频段 (>40 GHz) 法兰对准精度要求极高"),
            t_cp_3=tr("waveguide.eng_cp_3", "毫米波段建议使用带定位销的精密法兰")
        )

    def get_history_content(self) -> Optional[str]:
        """波导发展历史"""
        return tr("waveguide.history_content", """
        <b>📜 {t_history_title}</b><br><br>

        <b>{t_theory} (1890s):</b><br>
        {t_theory_desc}<br><br>

        <b>{t_experiment} (1930s):</b><br>
        {t_exp_desc}<br><br>

        <b>{t_ww2} (1940s):</b><br>
        {t_ww2_desc}<br><br>

        <b>{t_flange_stds}:</b><br>
        {t_flange_desc}
        """).format(
            t_history_title=tr("waveguide.his_title", "矩形波导发展简史"),
            t_theory=tr("waveguide.his_theory", "理论奠基"),
            t_theory_desc=tr("waveguide.his_theory_desc", "Lord Rayleigh 于 1897 年首次从数学上证明了电磁波可以在中空金属管中传播，但当时没有实际应用。"),
            t_experiment=tr("waveguide.his_experiment", "实验验证"),
            t_exp_desc=tr("waveguide.his_exp_desc", "George Southworth (AT&T Bell Labs) 和 Wilmer Barrow (MIT) 在 1936 年几乎同时独立实验验证了波导传输。"),
            t_ww2=tr("waveguide.his_ww2", "二战驱动"),
            t_ww2_desc=tr("waveguide.his_ww2_desc", "雷达技术的爆发式发展使波导成为核心元件。MIT 辐射实验室 (Rad Lab) 系统整理了波导理论，奠定了现代微波工程的基础。EIA WR 命名体系也在此时期确立。"),
            t_flange_stds=tr("waveguide.his_flange_stds", "法兰标准化"),
            t_flange_desc=tr("waveguide.his_flange_desc", "MIL-DTL-3922 标准定义了 UG 系列法兰接口，确保不同厂商的波导组件可以互换连接。随着频率升高 (>40 GHz)，传统 UG 法兰的对准精度已不能满足需求，催生了 CPRF 等精密法兰标准。")
        )

    def get_boundary_content(self) -> Optional[str]:
        return None
