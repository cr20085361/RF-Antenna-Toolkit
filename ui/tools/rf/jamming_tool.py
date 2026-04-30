# -*- coding: utf-8 -*-
"""
射频天线工具集 - 干扰压制计算器
RF Antenna Toolkit - Interference Suppression Calculator
"""

import math
from typing import Dict, Any, Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QDoubleSpinBox, QGroupBox, QFrame,
    QComboBox, QRadioButton, QButtonGroup, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.base.tool_base import ToolBase
from core.rf.jamming_calculator import JammingCalculator, JammingParams, JammingResult


class ValueUnitWidget(QWidget):
    """带单位切换的数值输入组件"""
    def __init__(self, default_val: float, min_val: float, max_val: float, units: List[str], callback, decimals: int = 2):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.spin = QDoubleSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setValue(default_val)
        self.spin.setDecimals(decimals)
        self.spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        
        # 禁用鼠标滚轮调节数值以防误操作，并将事件忽略给父控件（如 ScrollArea）处理
        self.spin.wheelEvent = lambda event: event.ignore()
        
        self.combo = QComboBox()
        self.combo.addItems(units)
        self._last_unit = units[0] if units else ""
        
        layout.addWidget(self.spin, 1)
        if len(units) > 1:
            layout.addWidget(self.combo)
        else:
            self.combo.hide()
            unit_label = QLabel(units[0])
            layout.addWidget(unit_label)
        
        self.spin.valueChanged.connect(callback)
        self.combo.currentIndexChanged.connect(self._on_unit_changed)
        self.combo.currentIndexChanged.connect(callback)

    def _on_unit_changed(self, idx):
        new_unit = self.combo.currentText()
        if new_unit == self._last_unit:
            return
            
        val = self.spin.value()
        new_val = val
        
        if self._last_unit == "MHz" and new_unit == "GHz":
            new_val = val / 1000.0
        elif self._last_unit == "GHz" and new_unit == "MHz":
            new_val = val * 1000.0
        elif self._last_unit == "dBm" and new_unit == "W":
            new_val = (10 ** (val / 10.0)) / 1000.0
        elif self._last_unit == "W" and new_unit == "dBm":
            if val <= 0: val = 1e-10
            new_val = 10 * math.log10(val * 1000.0)
        elif self._last_unit == "km" and new_unit == "m":
            new_val = val * 1000.0
        elif self._last_unit == "m" and new_unit == "km":
            new_val = val / 1000.0
            
        self.spin.blockSignals(True)
        if new_unit == "W" and new_val < 0.1:
            self.spin.setDecimals(4)
        elif new_unit == "dBm" or new_unit == "MHz":
            self.spin.setDecimals(2)
            
        self.spin.setValue(new_val)
        self.spin.blockSignals(False)
        self._last_unit = new_unit

    def get_value_in_base(self, base_type: str) -> float:
        val = self.spin.value()
        unit = self.combo.currentText()
        if base_type == "freq":  # base MHz
            if unit == "GHz": return val * 1000.0
            return val
        elif base_type == "power":  # base dBm
            if unit == "W":
                if val <= 0: return -100.0
                return 10 * math.log10(val * 1000.0)
            return val
        elif base_type == "dist":  # base km
            if unit == "m": return val / 1000.0
            return val
        return val


class JammingTool(ToolBase):
    """干扰压制计算器前端工具"""
    
    tool_name = "干扰压制计算器"
    tool_icon = "💥"
    tool_category = "antenna"
    tool_description = "计算单频或宽带下发射机对目标的电磁干扰压制效果"
    
    def __init__(self):
        self.calculator = JammingCalculator()
        self._is_updating = False
        super().__init__()
        
        self._fix_layout_stretch()
        self._init_default_bb_rows()
        self._calculate_and_update()
        
    def _fix_layout_stretch(self):
        """覆盖 ToolBase 中固定的 1:2 宽度比例，设为 1:1 等宽"""
        for child in self.findChildren(QHBoxLayout):
            if child.count() == 2:
                item0 = child.itemAt(0)
                item1 = child.itemAt(1)
                if item0 and item1 and item0.widget() and item1.widget():
                    child.setStretch(0, 1)
                    child.setStretch(1, 1)

    def create_input_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # --- 模式选择 ---
        mode_group = QGroupBox("⚙️ 评估模式")
        mode_layout = QHBoxLayout(mode_group)
        self.btn_single = QRadioButton("单频点评估")
        self.btn_broadband = QRadioButton("宽频段评估")
        self.btn_single.setChecked(True)
        
        # 增加最小宽度以防字体导致文案截断
        self.btn_broadband.setMinimumWidth(120)
        
        self.mode_group_btn = QButtonGroup(self)
        self.mode_group_btn.addButton(self.btn_single, 0)
        self.mode_group_btn.addButton(self.btn_broadband, 1)
        self.mode_group_btn.buttonClicked.connect(self._on_mode_changed)
        
        mode_layout.addWidget(self.btn_single)
        mode_layout.addWidget(self.btn_broadband)
        mode_layout.addStretch()
        layout.addWidget(mode_group)
        
        # --- 频率输入区域 ---
        
        # 宽带频率输入
        self.bb_freq_widget = QWidget()
        bb_layout = QVBoxLayout(self.bb_freq_widget)
        bb_layout.setContentsMargins(0, 0, 0, 0)
        bb_layout.setSpacing(8)
        
        self._last_bb_power_unit = "dBm"
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ 添加频点")
        btn_add.clicked.connect(self._add_row)
        btn_remove = QPushButton("➖ 删除")
        btn_remove.clicked.connect(self._remove_row)
        btn_clear = QPushButton("🗑️ 清空")
        btn_clear.clicked.connect(self._clear_table)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_clear)
        
        btn_layout.addSpacing(16)
        btn_layout.addWidget(QLabel("功率单位:"))
        self.bb_power_unit_combo = QComboBox()
        self.bb_power_unit_combo.addItems(["dBm", "W"])
        self.bb_power_unit_combo.currentIndexChanged.connect(self._on_bb_power_unit_changed)
        btn_layout.addWidget(self.bb_power_unit_combo)
        
        btn_layout.addStretch()
        bb_layout.addLayout(btn_layout)
        
        self.table_bb_input = QTableWidget()
        self.table_bb_input.setColumnCount(4)
        self.table_bb_input.setHorizontalHeaderLabels(["频率\n(MHz)", "发射功率\n(dBm)", "发射增益\n(dBi)", "接收增益\n(dBi)"])
        self.table_bb_input.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_bb_input.setMinimumHeight(160)
        font = self.table_bb_input.horizontalHeader().font()
        font.setPointSize(9)
        self.table_bb_input.horizontalHeader().setFont(font)
        self.table_bb_input.verticalHeader().setDefaultSectionSize(38)
        self.table_bb_input.setStyleSheet("""
            QTableWidget::item { padding: 4px; }
            QLineEdit { 
                border: 1px solid #4299E1; 
                border-radius: 4px;
                padding: 0px 4px;
                margin: 2px;
            }
        """)
        
        self.table_bb_input.itemChanged.connect(self._on_table_input_changed)
        bb_layout.addWidget(self.table_bb_input)
        
        # --- 干扰机参数组 ---
        tx_group = QGroupBox("📡 干扰机全局参数 (Jammer)")
        tx_layout = QVBoxLayout(tx_group)
        tx_layout.addWidget(self.bb_freq_widget)
        self.bb_freq_widget.hide() # 默认隐藏宽带控件
        
        tx_grid = QGridLayout()
        
        self.lbl_freq = QLabel("发射频率:")
        self.wu_freq = ValueUnitWidget(1000.0, 1.0, 100000.0, ["MHz", "GHz"], self._trigger_update)
        tx_grid.addWidget(self.lbl_freq, 0, 0)
        tx_grid.addWidget(self.wu_freq, 0, 1)
        
        self.wu_tx_power = ValueUnitWidget(40.0, -100.0, 10000.0, ["dBm", "W"], self._trigger_update)
        self.wu_tx_gain = ValueUnitWidget(10.0, -50.0, 100.0, ["dBi"], self._trigger_update)
        self.wu_tx_cable = ValueUnitWidget(1.0, 0.0, 50.0, ["dB"], self._trigger_update)
        
        self.lbl_tx_power = QLabel("功放输出功率:")
        self.lbl_tx_gain = QLabel("发射天线增益:")
        
        tx_grid.addWidget(self.lbl_tx_power, 1, 0)
        tx_grid.addWidget(self.wu_tx_power, 1, 1)
        tx_grid.addWidget(self.lbl_tx_gain, 2, 0)
        tx_grid.addWidget(self.wu_tx_gain, 2, 1)
        tx_grid.addWidget(QLabel("发射端馈线损耗:"), 3, 0)
        tx_grid.addWidget(self.wu_tx_cable, 3, 1)
        tx_layout.addLayout(tx_grid)
        layout.addWidget(tx_group)
        
        # --- 目标参数组 ---
        rx_group = QGroupBox("🎯 目标全局参数 (Target)")
        rx_layout = QGridLayout(rx_group)
        
        self.wu_rx_gain = ValueUnitWidget(2.0, -50.0, 100.0, ["dBi"], self._trigger_update)
        self.wu_rx_cable = ValueUnitWidget(0.0, 0.0, 50.0, ["dB"], self._trigger_update)
        self.wu_threshold = ValueUnitWidget(-90.0, -150.0, 50.0, ["dBm"], self._trigger_update)
        self.wu_js_req = ValueUnitWidget(3.0, -50.0, 50.0, ["dB"], self._trigger_update)
        self.wu_target_dist = ValueUnitWidget(5.0, 0.001, 10000.0, ["km", "m"], self._trigger_update, decimals=3)
        
        self.lbl_rx_gain = QLabel("接收天线增益:")
        rx_layout.addWidget(self.lbl_rx_gain, 0, 0)
        rx_layout.addWidget(self.wu_rx_gain, 0, 1)
        rx_layout.addWidget(QLabel("接收馈线损耗:"), 1, 0)
        rx_layout.addWidget(self.wu_rx_cable, 1, 1)
        rx_layout.addWidget(QLabel("目标接收门限:"), 2, 0)
        rx_layout.addWidget(self.wu_threshold, 2, 1)
        rx_layout.addWidget(QLabel("要求干信比(J/S):"), 3, 0)
        rx_layout.addWidget(self.wu_js_req, 3, 1)
        rx_layout.addWidget(QLabel("目标距离:"), 4, 0)
        rx_layout.addWidget(self.wu_target_dist, 4, 1)
        
        layout.addWidget(rx_group)
        layout.addStretch()
        return panel
        
    def create_result_panel(self) -> Optional[QWidget]:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 结果区域使用 StackedWidget 切分单频和宽带
        self.res_stack = QStackedWidget()
        
        # ===== 单频点结果页 =====
        single_res_page = QWidget()
        single_layout = QVBoxLayout(single_res_page)
        single_layout.setContentsMargins(0, 0, 0, 0)
        
        res_group = QGroupBox("📊 单频点压制评估")
        vbox = QVBoxLayout(res_group)
        self.lbl_status = QLabel("评估中...")
        self.lbl_status.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.lbl_status)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #E2E8F0;")
        vbox.addWidget(line)
        
        grid = QGridLayout()
        self.lbl_actual_pj = QLabel("-- dBm")
        self.lbl_max_dist = QLabel("-- km")
        self.lbl_margin = QLabel("-- dB")
        
        self.lbl_actual_pj.setStyleSheet("font-size: 16px; font-weight: bold; color: #2B6CB0;")
        self.lbl_max_dist.setStyleSheet("font-size: 16px; font-weight: bold; color: #2B6CB0;")
        self.lbl_margin.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        grid.addWidget(QLabel("到达目标干扰功率 (P<sub>J</sub>):"), 0, 0)
        grid.addWidget(self.lbl_actual_pj, 0, 1)
        grid.addWidget(QLabel("最大有效压制距离 (D<sub>max</sub>):"), 1, 0)
        grid.addWidget(self.lbl_max_dist, 1, 1)
        grid.addWidget(QLabel("当前距离下压制余量:"), 2, 0)
        grid.addWidget(self.lbl_margin, 2, 1)
        vbox.addLayout(grid)
        single_layout.addWidget(res_group)
        
        rec_group = QGroupBox("💡 量化建议")
        rec_layout = QVBoxLayout(rec_group)
        self.lbl_recommendation = QLabel("...")
        self.lbl_recommendation.setWordWrap(True)
        rec_layout.addWidget(self.lbl_recommendation)
        single_layout.addWidget(rec_group)
        single_layout.addStretch()
        self.res_stack.addWidget(single_res_page)
        
        # ===== 宽带结果页 =====
        bb_res_page = QWidget()
        bb_layout = QVBoxLayout(bb_res_page)
        bb_layout.setContentsMargins(0, 0, 0, 0)
        bb_group = QGroupBox("📊 宽带频率压制评估结果 (依据可变参数表计算)")
        bb_vbox = QVBoxLayout(bb_group)
        
        self.table_bb = QTableWidget()
        self.table_bb.setColumnCount(5)
        self.table_bb.setHorizontalHeaderLabels(["频率(MHz)", "到达功率(dBm)", "压制余量(dB)", "压制状态", "最大距离(km)"])
        self.table_bb.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # 表头加粗
        font = self.table_bb.horizontalHeader().font()
        font.setBold(True)
        self.table_bb.horizontalHeader().setFont(font)
        
        bb_vbox.addWidget(self.table_bb)
        bb_layout.addWidget(bb_group)
        self.res_stack.addWidget(bb_res_page)
        
        layout.addWidget(self.res_stack)
        return panel

    def _trigger_update(self):
        if not self._is_updating:
            self._calculate_and_update()

    def _on_bb_power_unit_changed(self, idx):
        new_unit = self.bb_power_unit_combo.currentText()
        if new_unit == self._last_bb_power_unit:
            return
            
        self._is_updating = True
        self.table_bb_input.blockSignals(True)
        
        # 1. 更新表头
        header_item = self.table_bb_input.horizontalHeaderItem(1)
        if header_item:
            header_item.setText(f"发射功率\n({new_unit})")
            
        # 2. 转换数据
        for row in range(self.table_bb_input.rowCount()):
            item = self.table_bb_input.item(row, 1)
            if not item: continue
            try:
                val = float(item.text())
                new_val = val
                if self._last_bb_power_unit == "dBm" and new_unit == "W":
                    new_val = (10 ** (val / 10.0)) / 1000.0
                elif self._last_bb_power_unit == "W" and new_unit == "dBm":
                    if val <= 0: val = 1e-10
                    new_val = 10 * math.log10(val * 1000.0)
                
                if new_unit == "W" and new_val < 0.1:
                    item.setText(f"{new_val:.4f}")
                else:
                    item.setText(f"{new_val:.2f}")
            except ValueError:
                pass
                
        self._last_bb_power_unit = new_unit
        self.table_bb_input.blockSignals(False)
        self._is_updating = False
        self._trigger_update()

    def _on_table_input_changed(self, item):
        self._trigger_update()

    def _on_mode_changed(self, button):
        idx = self.mode_group_btn.id(button)
        is_single = (idx == 0)
        
        # 宽带输入表的显示隐藏
        self.bb_freq_widget.setVisible(not is_single)
        
        # 频率输入的显示隐藏
        self.lbl_freq.setVisible(is_single)
        self.wu_freq.setVisible(is_single)
        
        self.res_stack.setCurrentIndex(idx)
        
        # 宽带模式下，将已经在表格中的参数输入框从全局面板隐藏，避免逻辑冲突
        is_single = (idx == 0)
        self.lbl_tx_power.setVisible(is_single)
        self.wu_tx_power.setVisible(is_single)
        self.lbl_tx_gain.setVisible(is_single)
        self.wu_tx_gain.setVisible(is_single)
        self.lbl_rx_gain.setVisible(is_single)
        self.wu_rx_gain.setVisible(is_single)
        
        self._calculate_and_update()

    def _init_default_bb_rows(self):
        """初始化几个默认的宽带评估频点行"""
        self._is_updating = True
        self.table_bb_input.setRowCount(0)
        for f in [800.0, 1800.0, 2400.0]:
            self._add_row_data(f)
        self._is_updating = False

    def _add_row(self):
        self._is_updating = True
        self._add_row_data(1000.0)
        self._is_updating = False
        self._trigger_update()

    def _add_row_data(self, freq: float):
        row = self.table_bb_input.rowCount()
        self.table_bb_input.insertRow(row)
        
        base_tx_p_dbm = self.wu_tx_power.get_value_in_base("power")
        base_tx_g = self.wu_tx_gain.get_value_in_base("none")
        base_rx_g = self.wu_rx_gain.get_value_in_base("none")
        
        if self._last_bb_power_unit == "W":
            base_tx_p = (10 ** (base_tx_p_dbm / 10.0)) / 1000.0
            p_text = f"{base_tx_p:.4f}" if base_tx_p < 0.1 else f"{base_tx_p:.2f}"
        else:
            p_text = f"{base_tx_p_dbm:.2f}"
        
        item_f = QTableWidgetItem(f"{freq:g}")
        item_p = QTableWidgetItem(p_text)
        item_tg = QTableWidgetItem(f"{base_tx_g:.2f}")
        item_rg = QTableWidgetItem(f"{base_rx_g:.2f}")
        
        item_f.setBackground(QColor("#F7FAFC"))
        for item in [item_f, item_p, item_tg, item_rg]:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
        self.table_bb_input.setItem(row, 0, item_f)
        self.table_bb_input.setItem(row, 1, item_p)
        self.table_bb_input.setItem(row, 2, item_tg)
        self.table_bb_input.setItem(row, 3, item_rg)

    def _remove_row(self):
        row = self.table_bb_input.currentRow()
        if row >= 0:
            self.table_bb_input.removeRow(row)
            self._trigger_update()

    def _clear_table(self):
        self.table_bb_input.setRowCount(0)
        self._trigger_update()

    def _parse_bb_inputs(self) -> List[Dict[str, float]]:
        overrides = []
        for row in range(self.table_bb_input.rowCount()):
            try:
                freq = float(self.table_bb_input.item(row, 0).text())
                tx_p = float(self.table_bb_input.item(row, 1).text())
                tx_g = float(self.table_bb_input.item(row, 2).text())
                rx_g = float(self.table_bb_input.item(row, 3).text())
                if self._last_bb_power_unit == "W":
                    if tx_p <= 0: tx_p = 1e-10
                    tx_p_dbm = 10 * math.log10(tx_p * 1000.0)
                else:
                    tx_p_dbm = tx_p
                    
                overrides.append({
                    'freq_mhz': freq,
                    'tx_power_dbm': tx_p_dbm,
                    'tx_gain_dbi': tx_g,
                    'rx_gain_dbi': rx_g
                })
            except (ValueError, AttributeError):
                continue
        return overrides

    def _calculate_and_update(self):
        """执行计算并更新UI"""
        if self._is_updating:
            return
            
        # 读取全局参数
        base_params = JammingParams(
            freq_mhz=1000.0, # 稍后覆盖
            tx_power_dbm=self.wu_tx_power.get_value_in_base("power"),
            tx_gain_dbi=self.wu_tx_gain.get_value_in_base("none"),
            tx_cable_loss_db=self.wu_tx_cable.get_value_in_base("none"),
            rx_gain_dbi=self.wu_rx_gain.get_value_in_base("none"),
            rx_cable_loss_db=self.wu_rx_cable.get_value_in_base("none"),
            rx_threshold_dbm=self.wu_threshold.get_value_in_base("none"),
            js_req_db=self.wu_js_req.get_value_in_base("none"),
            target_distance_km=self.wu_target_dist.get_value_in_base("dist")
        )
        
        mode = self.mode_group_btn.checkedId()
        
        if mode == 0:
            # === 单频点模式 ===
            base_params.freq_mhz = self.wu_freq.get_value_in_base("freq")
            result = self.calculator.calculate(base_params)
            
            self.lbl_actual_pj.setText(f"{result.actual_pj_dbm:.2f} dBm")
            self.lbl_max_dist.setText(f"{result.max_distance_km:.3f} km")
            
            if result.margin_db >= 0:
                self.lbl_margin.setText(f"+{result.margin_db:.2f} dB")
                self.lbl_margin.setStyleSheet("font-size: 16px; font-weight: bold; color: #38A169;")
                
                self.lbl_status.setText("✔️ 压制成功")
                self.lbl_status.setStyleSheet("color: #38A169; background-color: #F0FFF4; border-radius: 8px; padding: 8px;")
                
                rec_text = (
                    f"在当前距离 ({base_params.target_distance_km:.2f} km) 下，到达干扰功率为 {result.actual_pj_dbm:.2f} dBm，"
                    f"超过要求门限 {result.margin_db:.2f} dB，压制效果良好。\n\n"
                    f"如需节能，可考虑将功放功率降低至 {result.required_tx_power_dbm:.2f} dBm。"
                )
                self.lbl_recommendation.setStyleSheet("background-color: #F0FFF4; border: 1px solid #9AE6B4; border-radius: 6px; padding: 12px; color: #22543D; font-size: 13px;")
            else:
                self.lbl_margin.setText(f"{result.margin_db:.2f} dB")
                self.lbl_margin.setStyleSheet("font-size: 16px; font-weight: bold; color: #E53E3E;")
                
                self.lbl_status.setText("❌ 压制失败")
                self.lbl_status.setStyleSheet("color: #E53E3E; background-color: #FFF5F5; border-radius: 8px; padding: 8px;")
                
                deficit = abs(result.margin_db)
                rec_text = (
                    f"存在 {deficit:.2f} dB 的缺口！建议采取以下任一措施：\n"
                    f"1. 提升功放输出功率至：{result.required_tx_power_dbm:.2f} dBm (增加 {deficit:.2f} dB)\n"
                    f"2. 提升发射天线增益至：{result.required_tx_gain_dbi:.2f} dBi (增加 {deficit:.2f} dB)\n"
                    f"3. 缩短目标距离至：{result.max_distance_km:.3f} km 以内"
                )
                self.lbl_recommendation.setStyleSheet("background-color: #FFF5F5; border: 1px solid #FEB2B2; border-radius: 6px; padding: 12px; color: #742A2A; font-size: 13px;")
                
            self.lbl_recommendation.setText(rec_text)
            
        else:
            # === 宽带模式 ===
            overrides = self._parse_bb_inputs()
            if not overrides:
                self.table_bb.setRowCount(0)
                return
                
            results = self.calculator.calculate_broadband(base_params, overrides)
            
            self.table_bb.setRowCount(len(overrides))
            for row, override in enumerate(overrides):
                freq = override['freq_mhz']
                res = results.get(freq)
                if not res: continue
                
                item_freq = QTableWidgetItem(f"{freq:g}")
                item_pj = QTableWidgetItem(f"{res.actual_pj_dbm:.2f}")
                
                margin_str = f"+{res.margin_db:.2f}" if res.margin_db >= 0 else f"{res.margin_db:.2f}"
                item_margin = QTableWidgetItem(margin_str)
                item_margin.setForeground(QColor("#38A169") if res.margin_db >= 0 else QColor("#E53E3E"))
                
                font = item_margin.font()
                font.setBold(True)
                item_margin.setFont(font)
                
                item_status = QTableWidgetItem("✔️ 成功" if res.is_suppressed else "❌ 失败")
                item_status.setForeground(QColor("#38A169") if res.is_suppressed else QColor("#E53E3E"))
                
                item_dist = QTableWidgetItem(f"{res.max_distance_km:.3f}")
                
                for item in [item_freq, item_pj, item_margin, item_status, item_dist]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                self.table_bb.setItem(row, 0, item_freq)
                self.table_bb.setItem(row, 1, item_pj)
                self.table_bb.setItem(row, 2, item_margin)
                self.table_bb.setItem(row, 3, item_status)
                self.table_bb.setItem(row, 4, item_dist)

    def calculate(self) -> Dict[str, Any]:
        return {}

    def get_intuition_content(self) -> Optional[str]:
        return """
        <b>💥 干扰压制直观理解：</b><br>
        要想成功“喊话”盖过别人的声音（压制），你要么嗓门足够大（发射功率），要么找个喇叭帮你定向扩音（天线增益），要么靠得足够近（减小路径损耗）。<br>
        <br>
        <b>J/S (干信比) 要求：</b><br>
        对于抗干扰能力强的通信系统（如扩频通信），可能需要您的噪声功率比它的信号大 10dB 甚至更多才能彻底阻断其通信。
        """
        
    def get_math_model_content(self) -> Optional[str]:
        return """
        <b>📐 核心公式：</b><br>
        到达干扰功率：<br>
        P<sub>J</sub> (dBm) = P<sub>tx</sub> + G<sub>tx</sub> - L<sub>cable</sub> - FSPL + G<sub>rx</sub><br>
        <br>
        其中自由空间路径损耗 (Free Space Path Loss)：<br>
        FSPL (dB) = 32.44 + 20 log<sub>10</sub>(f<sub>MHz</sub>) + 20 log<sub>10</sub>(d<sub>km</sub>)<br>
        <br>
        <b>🎯 压制成功条件：</b><br>
        P<sub>J</sub> ≥ P<sub>threshold</sub> + J/S<sub>req</sub>
        """
