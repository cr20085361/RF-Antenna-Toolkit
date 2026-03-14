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

from core.i18n import tr
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
        "E6"  : {"tol": "±20%", "sig_figs": 2, "desc": tr("eseries.desc_e6", "基础容差，适用于早期粗精度元件或大电解电容")},
        "E12" : {"tol": "±10%", "sig_figs": 2, "desc": tr("eseries.desc_e12", "常规容差，多用于普通电容及非关键电路电阻")},
        "E24" : {"tol": "±5%",  "sig_figs": 2, "desc": tr("eseries.desc_e24", "【最常用】标准碳膜/厚膜电阻、主流片式电容及电感")},
        "E48" : {"tol": "±2%",  "sig_figs": 3, "desc": tr("eseries.desc_e48", "较高精度，主要用于金属膜电阻 (使用3位有效数字)")},
        "E96" : {"tol": "±1%",  "sig_figs": 3, "desc": tr("eseries.desc_e96", "【高精常用】精密金属膜/贴片电阻 (1%阻值必须选用此表)")},
        "E192": {"tol": "±0.5% 及以下", "sig_figs": 3, "desc": tr("eseries.desc_e192", "最高精度，用于仪器仪表级超精细电阻 (0.5%, 0.25%, 0.1%)")}
    }

    def __init__(self, parent=None):
        self.tool_id = "eseries_table"
        self.tool_name = tr("nominal.tool_name", "标称值速查")
        self.tool_icon = "🏷️"
        self.tool_category = "reference"
        self.tool_description = tr("nominal.tool_desc", "标准电阻(E24/E96)、电感(E12/E24)、电容常用标称值速查表")
        self.i18n_title_key = "nominal.tool_name"
        self.i18n_desc_key = "nominal.tool_desc"
        
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
        
        sg_layout.addWidget(QLabel(tr("eseries.lbl_select_standard", "<b>1. 选择容差标准 (E 系列)</b>")))
        
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
        
        mg_layout.addWidget(QLabel(tr("eseries.lbl_smart_match", "<b>2. 智能就近匹配</b>")))
        mg_layout.addWidget(QLabel(tr("eseries.lbl_smart_match_desc", "<span style='color:#718096;font-size:12px;'>输入理论计算值，寻找最接近的标准元件</span>")))
        
        input_layout = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(tr("eseries.ph_match_input", "例如: 4700 或 3.8"))
        self._search_input.setFixedHeight(36)
        self._search_input.returnPressed.connect(self._do_match)
        
        btn_match = QPushButton(tr("eseries.btn_match", "匹配"))
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
        self._table_title = QLabel(tr("eseries.table_title_e24", "E24 标准标称值基数 (1.0 ~ 9.9)"))
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
            f"<b>{tr('eseries.lbl_tolerance_std', '容差标准:')}</b> {config['tol']}<br>"
            f"<b>{tr('eseries.lbl_sig_figs', '有效数字:')}</b> {config['sig_figs']} {tr('eseries.lbl_digits', '位')}<br>"
            f"<b>{tr('eseries.lbl_typical_app', '典型应用:')}</b> {config['desc']}"
        )
        self._desc_label.setText(desc)
        
        if self._table:
            self._update_table()
            # 更新表头提示
            self._table_title.setText(tr("eseries.table_title_dynamic", "{0} 标准元器件数值速查表 (×0.01 ~ ×1M)").format(series))
            
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
            self._match_result.setText(tr("eseries.err_invalid_input", "<span style='color:#E53E3E;'>错误: 请输入有效的正数计算值</span>"))
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
            f"{tr('eseries.target_theoretical', '目标理论值:')} <b>{format_val(target_val)}</b></div>"
            f"<div style='color: #2B6CB0; font-size: 14px; margin-bottom: 5px;'>"
            f"→ {tr('eseries.best_match', '最匹配的')} <b>{self._current_series}</b> {tr('eseries.nominal_val', '标称值:')}<br>"
            f"<b><span style='font-size: 18px;'>{format_val(standard_val)}</span></b> "
            f"({tr('eseries.base_val', '基数')} {base_str} ×10<sup>{power}</sup>)</div>"
            f"<div style='color: {'#E53E3E' if abs(error_pct)>5 else '#38A169'};'>"
            f"{tr('eseries.deviation_rate', '偏差率:')} <b>{error_pct:+.2f}%</b></div>"
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
        return tr("eseries.intuition_content")

    def get_math_model_content(self) -> Optional[str]:
        return tr("eseries.math_content")

    def get_engineering_content(self) -> Optional[str]:
        return tr("eseries.engineering_content")

    def get_history_content(self) -> Optional[str]:
        return tr("eseries.history_content")
