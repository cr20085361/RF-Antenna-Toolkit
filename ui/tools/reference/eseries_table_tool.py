# -*- coding: utf-8 -*-
"""
E系列标准标称值速查工具 (电阻、电容、电感)
"""

import math
from typing import Dict, Any, List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from ui.base.tool_base import ToolBase


class ESeriesTableTool(ToolBase):
    """
    E系列标准标称值(电阻/电容/电感)速查工具
    展现 IEC 60063 中定义的电子元件优先数系
    """
    
    # 标准 E 系列数据字典
    # 根据 IEC 60063 标准，E3/E6/E12/E24 的基数固定
    E_SERIES_EXACT = {
        "E6" : [1.0, 1.5, 2.2, 3.3, 4.7, 6.8],
        "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
        "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
                3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
    }
    
    # E48, E96, E192 采用 3 位有效数字，且由算法 10^(i/N) 四舍五入得到，部分有微调
    # 在这里我们使用算法动态生成，避免冗长的硬编码
    
    SERIES_CONFIG = {
        "E6"  : {"tol": "±20%", "sig_figs": 2, "desc": "基础容差，适用于早期粗精度元件或大电解电容"},
        "E12" : {"tol": "±10%", "sig_figs": 2, "desc": "常规容差，多用于普通电容及非关键电路电阻"},
        "E24" : {"tol": "±5%",  "sig_figs": 2, "desc": "【最常用】标准碳膜/厚膜电阻、主流片式电容及电感"},
        "E48" : {"tol": "±2%",  "sig_figs": 3, "desc": "较高精度，主要用于金属膜电阻 (使用3位有效数字)"},
        "E96" : {"tol": "±1%",  "sig_figs": 3, "desc": "【高精常用】精密金属膜/贴片电阻 (1%阻值必须选用此表)"},
        "E192": {"tol": "±0.5% 及以下", "sig_figs": 3, "desc": "最高精度，用于仪器仪表级超精细电阻 (0.5%, 0.25%, 0.1%)"}
    }

    def __init__(self, parent=None):
        self.tool_id = "eseries_table"
        self.tool_name = "元件标称值 (E系列)"
        self.tool_icon = "🏷️"
        self.tool_description = "依据 IEC 60063 查询电阻/电容/电感的标准标称值，支持任意值就近匹配"
        
        self._current_series = "E24"
        self._table = None
        self._desc_label = None
        self._search_input = None
        self._match_result = None
        
        super().__init__(parent)
    
    @classmethod
    def get_series_values(cls, series_name: str) -> List[float]:
        """获取特定E系列的基准数值列表 (1.00 ~ 9.xx)"""
        # E6/E12/E24 使用固定表，因为历史原因它们不完全等于理论计算值
        if series_name in cls.E_SERIES_EXACT:
            return cls.E_SERIES_EXACT[series_name]
            
        # E48/E96/E192 使用理论公式 10^(i/N)
        n = int(series_name[1:])
        values = []
        for i in range(n):
            val = round((10 ** (i / n)), 2)
            values.append(val)
        return values
        
    def create_input_panel(self) -> QWidget:
        """创建左侧输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 系列选择区
        series_group = QWidget()
        sg_layout = QVBoxLayout(series_group)
        sg_layout.setContentsMargins(0, 0, 0, 0)
        
        sg_layout.addWidget(QLabel("<b>1. 选择容差标准 (E 系列)</b>"))
        
        self._combo_series = QComboBox()
        self._combo_series.addItems(list(self.SERIES_CONFIG.keys()))
        self._combo_series.setCurrentText("E24")
        self._combo_series.setFixedHeight(36)
        self._combo_series.currentTextChanged.connect(self._on_series_changed)
        sg_layout.addWidget(self._combo_series)
        
        # 系列说明信息
        self._desc_label = QLabel()
        self._desc_label.setWordWrap(True)
        self._desc_label.setStyleSheet("color: #718096; font-size: 13px; margin-top: 5px;")
        sg_layout.addWidget(self._desc_label)
        
        layout.addWidget(series_group)
        
        # 分隔线
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("color: #E2E8F0; margin: 15px 0;")
        layout.addWidget(line1)
        
        # 2. 智能匹配区
        match_group = QWidget()
        mg_layout = QVBoxLayout(match_group)
        mg_layout.setContentsMargins(0, 0, 0, 0)
        
        mg_layout.addWidget(QLabel("<b>2. 智能就近匹配</b>"))
        mg_layout.addWidget(QLabel("<span style='color:#718096;font-size:12px;'>输入理论计算值，寻找最接近的标准元件</span>"))
        
        input_layout = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("例如: 4700 或 3.8")
        self._search_input.setFixedHeight(36)
        self._search_input.returnPressed.connect(self._do_match)
        
        btn_match = QPushButton("匹配")
        btn_match.setFixedHeight(36)
        btn_match.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_match.clicked.connect(self._do_match)
        
        input_layout.addWidget(self._search_input)
        input_layout.addWidget(btn_match)
        mg_layout.addLayout(input_layout)
        
        # 匹配结果显示区
        self._match_result = QLabel("")
        self._match_result.setWordWrap(True)
        self._match_result.setStyleSheet("""
            background-color: #F8FAFC; 
            border: 1px solid #E2E8F0; 
            border-radius: 6px; 
            padding: 10px; 
            margin-top: 10px;
        """)
        self._match_result.hide()
        mg_layout.addWidget(self._match_result)
        
        layout.addWidget(match_group)
        layout.addStretch()
        
        # 初始化说明
        self._on_series_changed("E24")
        
        return panel

    def create_result_panel(self) -> QWidget:
        """创建右侧表格展示区"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 表格标题
        self._table_title = QLabel("E24 标准标称值基数 (1.0 ~ 9.9)")
        self._table_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(self._table_title)
        
        # 创建表格 (使用多列展示一维数据，避免过长)
        self._table = QTableWidget()
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #EDF2F7;
                border: none;
                border-right: 1px solid #E2E8F0;
                border-bottom: 1px solid #E2E8F0;
                padding: 6px;
                font-weight: bold;
                color: #4A5568;
            }
            QTableWidget::item:selected {
                background-color: #EBF4FF;
                color: #2B6CB0;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self._table)
        self._update_table()
        
        return panel

    def calculate(self) -> Dict[str, Any]:
        """工具核心是被动查询，无复杂自动计算"""
        return {}
        
    def _on_series_changed(self, series: str):
        self._current_series = series
        config = self.SERIES_CONFIG[series]
        
        desc = (
            f"<b>容差标准:</b> {config['tol']}<br>"
            f"<b>有效数字:</b> {config['sig_figs']} 位<br>"
            f"<b>典型应用:</b> {config['desc']}"
        )
        self._desc_label.setText(desc)
        
        if self._table:
            self._update_table()
            # 更新表头提示
            self._table_title.setText(f"{series} 标准元器件数值速查表 (×0.01 ~ ×1M)")
            
        # 如果搜索框有值，重新匹配
        if self._search_input and self._search_input.text().strip():
            self._do_match()

    def _update_table(self):
        """用该系列的实际数值填充二维表格 (行:基数, 列:数量级)"""
        values = self.get_series_values(self._current_series)
        sig_figs = self.SERIES_CONFIG[self._current_series]["sig_figs"]
        
        # 常用数量级乘数 (包含小数以支持毫欧电阻和小皮法电容)
        multipliers = [0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000]
        col_headers = ["×0.01", "×0.1", "×1", "×10", "×100", "×1k", "×10k", "×100k", "×1M"]
        
        self._table.clear()
        self._table.setRowCount(len(values))
        self._table.setColumnCount(len(multipliers))
        
        self._table.setHorizontalHeaderLabels(col_headers)
        
        # 设置行头为基数
        row_headers = []
        for val in values:
            if sig_figs == 2:
                row_headers.append(f"{val:.1f}")
            else:
                row_headers.append(f"{val:.2f}")
        self._table.setVerticalHeaderLabels(row_headers)
        
        self._table.verticalHeader().setVisible(True)
        self._table.horizontalHeader().setVisible(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        def format_val(v):
            if v >= 1e6:
                return f"{v/1e6:g} M"
            elif v >= 1e3:
                return f"{v/1e3:g} k"
            else:
                return f"{v:g}"
        
        for r, base_val in enumerate(values):
            for c, mult in enumerate(multipliers):
                real_val = base_val * mult
                # 处理由于浮点精度产生的问题
                real_val = round(real_val, 6)
                
                item = QTableWidgetItem(format_val(real_val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # 为常用基数提供不同的颜色区分
                if base_val in [1.0, 2.2, 3.3, 4.7, 6.8]:
                    item.setForeground(QColor("#2B6CB0"))
                    f = item.font()
                    f.setBold(True)
                    item.setFont(f)
                    
                self._table.setItem(r, c, item)

    def _do_match(self):
        """执行就近值匹配算法"""
        input_text = self._search_input.text().strip()
        if not input_text:
            self._match_result.hide()
            self._table.clearSelection()
            return
            
        try:
            target_val = float(input_text.replace(',', ''))
            if target_val <= 0:
                raise ValueError
        except ValueError:
            self._match_result.show()
            self._match_result.setText("<span style='color:#E53E3E;'>错误: 请输入有效的正数计算值</span>")
            return
            
        # 1. 提取数量级 (乘数) 和底数
        # 例: target_val = 4700 -> power = 3, base = 4.7
        # 例: target_val = 0.033 -> power = -2, base = 3.3
        if target_val == 0:
            return
            
        power = math.floor(math.log10(target_val))
        base = target_val / (10 ** power)
        
        # 获取当前系列字典
        values = self.get_series_values(self._current_series)
        
        # 2. 寻找最接近的基准阻值
        # 包含下一个周期的第一个值
        search_values = values + [values[0] * 10]
        closest_base = min(search_values, key=lambda x: abs(x - base))
        
        # 调整进位（如果是匹配到了 10 这个值）
        if closest_base >= 9.99:
            closest_base = values[0]
            power += 1
            
        # 3. 组装最终结果
        standard_val = closest_base * (10 ** power)
        error_pct = (standard_val - target_val) / target_val * 100
        
        def format_val(v):
            if v >= 1e6:
                return f"{v/1e6:.3g} M"
            elif v >= 1e3:
                return f"{v/1e3:.3g} k"
            else:
                return f"{v:.3g} "
                
        # 4. 更新UI提示
        base_str = f"{closest_base:.1f}" if self.SERIES_CONFIG[self._current_series]["sig_figs"] == 2 else f"{closest_base:.2f}"
        result_html = (
            f"<div style='margin-bottom: 5px;'>"
            f"目标理论值: <b>{format_val(target_val)}</b></div>"
            f"<div style='color: #2B6CB0; font-size: 14px; margin-bottom: 5px;'>"
            f"→ 最匹配的 <b>{self._current_series}</b> 标称值:<br>"
            f"<b><span style='font-size: 18px;'>{format_val(standard_val)}</span></b> "
            f"(基数 {base_str} ×10<sup>{power}</sup>)</div>"
            f"<div style='color: {'#E53E3E' if abs(error_pct)>5 else '#38A169'};'>"
            f"偏差率: <b>{error_pct:+.2f}%</b></div>"
        )
        self._match_result.setText(result_html)
        self._match_result.show()
        
        # 5. 高亮二维表格中对应的真实数值
        self._table.clearSelection()
        
        r = -1
        # 查找基数所在行
        for i, val in enumerate(values):
            if abs(val - closest_base) < 0.001:
                r = i
                break
                
        # 图表中展示的列是从 10^-2 (×0.01) 到 10^6 (×1M)
        # 如果 power 在 -2 到 6 之间，高亮它
        c = power + 2 if -2 <= power <= 6 else -1
        
        if r != -1 and c != -1:
            item = self._table.item(r, c)
            if item:
                self._table.setCurrentItem(item)
                self._table.scrollToItem(item)

    def get_intuition_content(self) -> Optional[str]:
        return """
        <b>为什么阻值不是 1, 2, 3...等差排布？</b><br>
        1952年，国际电工委员会(IEC)制定了 <b>IEC 60063</b> 标准，定义了被动元器件（电阻、电容、电感）的优先数值系列（即 E 系列）。<br><br>
        其核心哲学是：<b>容差是百分比，因此数值梯度也必须是百分比（基于对数刻度排列）</b>。<br>
        如果一个 100Ω 的电阻误差是 ±10%（范围 90~110），那么下一个阻值就应该设计成 120Ω（误差10%是 108~132）。
        这样它们两者在生产线上的误差边界（110 和 108）完美对接。无论工厂造出什么具体阻值的元件，都能归入其中一档，实现 100% 良品率可用。
        """

    def get_math_model_content(self) -> Optional[str]:
        return """
        E 系列基于公比为 <b>10的N次方根</b> 的几何级数 (等比数列)：
        <br><br>
        <div style="background:#F7FAFC; padding:10px; border-radius:4px; text-align:center;">
        <b>V<sub>i</sub> = 10<sup>(i / N)</sup></b>
        </div>
        <br>
        <li>其中 <span style="color:#2B6CB0"><b>N</b></span> 代表系列名称中的数字 (如 E24 中 N=24)</li>
        <li><span style="color:#2B6CB0"><b>i</b></span> 取值为 [0, 1, 2 ... N-1]</li>
        <li>结果会被四舍五入到规定的有效数字（E24及以下2位，E48及以上3位）</li><br>
        
        <b>相邻差值率 (公比步进):</b>
        • E12: 10^(1/12) ≈ 1.21 (相邻阻值相差约20%)<br>
        • E24: 10^(1/24) ≈ 1.10 (相邻阻值相差约10%)<br>
        • E96: 10^(1/96) ≈ 1.024 (相邻阻值相差约2.4%)
        """

    def get_engineering_content(self) -> Optional[str]:
        return """
        <b>工程师避坑指南 (实战选型建议)：</b><br><br>
        
        <b>1. 电阻 (Resistors)</b><br>
        • <b>设计首选</b>: 绝大部分数字电路下拉/上拉，应仅使用 <b>E12</b> 或 <b>E24</b> 常见值（如1K, 4.7K, 10K）。<br>
        • <b>分压器/运放反馈</b>: 优先尝试 E24 的组合。若精度不够，**允许使用 E96 (1%)**。<br>
        • <b>成本与交货期</b>: 不要随意选用冷僻的 E96 值，这可能导致 BOM 采购成本暴增并面临长交期。<br><br>
        
        <b>2. 电容 (Capacitors)</b><br>
        • <b>高度收敛</b>: 电容的制造误差极大(尤其是MLCC和电解)，实际上连 E12 都没填满。一般仅在 <b>E6</b> 范围内选型 (1.0, 1.5, 2.2, 3.3, 4.7, 6.8)。<br>
        • <span style="color:#E53E3E">避坑</span>: 从不使用 3.9uF，直接用 4.7uF 替代。<br><br>

        <b>3. 电感 (Inductors)</b><br>
        • <b>受限选择</b>: 常见于开关电源设计。同样高度收敛在 <b>E6 ~ E12</b> 之间。<br>
        • 例如电源 IC 手册计算出需要 3.8uH，你买不到 3.8uH，你应该去查 E12 表并选用 3.3uH 或 4.7uH 的标准品并重新核验纹波电流。
        """

    def get_history_content(self) -> Optional[str]:
        return """
        <b>轶事：</b><br>
        很多工程师好奇，为什么 E24 中 2.7 之后是 3.0，3.3 而不是严格按照数学算出来的 3.16？<br>
        当时(1950年代)制定标准时，考虑到那些已经在行业内约定俗成广泛使用了多年的阻值（比如 3.3uF、4.7K等），
        委员会在纯数学模型 10^(i/24) 之外进行了<b>人工微调</b>，这是一种科学向工程妥协的经典案例，也造就了今天背诵熟稔的这些独特数字美感。
        """
