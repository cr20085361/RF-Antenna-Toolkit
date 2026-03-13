# -*- coding: utf-8 -*-
"""
频段分类参考表工具
Frequency Band Reference Table Tool

版本: v1.0.0
功能: 提供主流频段分类标准 (IEEE/ITU/NATO/China) 的查询和对照
"""

from typing import Dict, List, Optional
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QHeaderView, QLineEdit,
    QTableWidget, QTableWidgetItem, QFrame, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

from core.i18n import tr
from ui.base.tool_base import ToolBase


class BandInfo:
    """频段信息类"""
    def __init__(self, name: str, start_freq: str, stop_freq: str, 
                 wavelength: str, application: str, color: str = "#FFFFFF"):
        self.name = name
        self.start_freq = start_freq
        self.stop_freq = stop_freq
        self.wavelength = wavelength
        self.application = application
        self.color = color


class BandTableTool(ToolBase):
    """
    频段分类参考表
    """
    
    tool_name = "频段分类"
    tool_icon = "📶"
    tool_category = "reference"
    tool_description = "主流无线电频段分类标准速查 (IEEE/ITU/NATO/China)"
    i18n_title_key = "bandtable.tool_name"
    i18n_desc_key = "bandtable.tool_desc"
    
    def on_standard_changed(self, index: int):
        """标准切换回调"""
        standard_key = self._standard_combo.itemData(index)
        self._current_standard = standard_key
        self._update_table()
        
    def on_search_text_changed(self, text: str):
        """搜索框文字变化回调"""
        self._update_table(filter_text=text)

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化"""
        self._current_standard = "IEEE"  # 默认标准
        self._init_data()
        super().__init__(parent)

    def _init_data(self):
        """初始化频段数据"""
        self.band_data: Dict[str, List[BandInfo]] = {}
        
        # 统一浅色背景，去除渐变
        COLOR_IEEE = "#E3F2FD"  # 浅蓝
        COLOR_ITU = "#F1F8E9"   # 浅绿
        COLOR_NATO = "#FFEBEE"  # 浅红
        COLOR_CN = "#FFF3E0"    # 浅橙
        COLOR_CELL = "#E1F5FE"  # 浅青 (手机)
        COLOR_GNSS = "#E8F5E9"  # 浅绿 (导航)
        COLOR_HAM = "#FFF8E1"   # 浅黄 (业余)

        # 1. IEEE 标准 (雷达/射频常用)
        self.band_data["IEEE"] = [
            BandInfo("HF", "3 MHz", "30 MHz", "100 - 10 m", "高频通信、超视距雷达", COLOR_IEEE),
            BandInfo("VHF", "30 MHz", "300 MHz", "10 - 1 m", "FM广播、电视、陆地移动通信", COLOR_IEEE),
            BandInfo("UHF", "300 MHz", "1 GHz", "1 m - 30 cm", "电视、手机、GPS、探测雷达", COLOR_IEEE),
            BandInfo("L", "1 GHz", "2 GHz", "30 - 15 cm", "GPS、北斗、GSM手机、空中交通管制", COLOR_IEEE),
            BandInfo("S", "2 GHz", "4 GHz", "15 - 7.5 cm", "WiFi 2.4G、蓝牙、微波炉、气象雷达", COLOR_IEEE),
            BandInfo("C", "4 GHz", "8 GHz", "7.5 - 3.75 cm", "卫星通信、WiFi 5G、气象雷达", COLOR_IEEE),
            BandInfo("X", "8 GHz", "12 GHz", "3.75 - 2.5 cm", "军用火控雷达、警用测速、卫星通信", COLOR_IEEE),
            BandInfo("Ku", "12 GHz", "18 GHz", "2.5 - 1.67 cm", "卫星电视直播、测速雷达", COLOR_IEEE),
            BandInfo("K", "18 GHz", "27 GHz", "1.67 - 1.11 cm", "多普勒雷达、卫星通信", COLOR_IEEE),
            BandInfo("Ka", "27 GHz", "40 GHz", "1.11 - 0.75 cm", "5G 毫米波、卫星宽带、汽车雷达", COLOR_IEEE),
            BandInfo("V", "40 GHz", "75 GHz", "7.5 - 4 mm", "毫米波通信、卫星链路", COLOR_IEEE),
            BandInfo("W", "75 GHz", "110 GHz", "4 - 2.7 mm", "汽车毫米波雷达(77G)、射电天文学", COLOR_IEEE),
            BandInfo("mm", "110 GHz", "300 GHz", "2.7 - 1 mm", "亚毫米波、太赫兹成像前沿", COLOR_IEEE),
        ]
        
        # 2. ITU 标准 (波段号)
        self.band_data["ITU"] = [
            BandInfo("4 (VLF)", "3 kHz", "30 kHz", "100 - 10 km", "水下通信、导航", COLOR_ITU),
            BandInfo("5 (LF)", "30 kHz", "300 kHz", "10 - 1 km", "长波广播、由于导航", COLOR_ITU),
            BandInfo("6 (MF)", "300 kHz", "3 MHz", "1 - 0.1 km", "AM广播、海事通信", COLOR_ITU),
            BandInfo("7 (HF)", "3 MHz", "30 MHz", "100 - 10 m", "短波广播、航空通信", COLOR_ITU),
            BandInfo("8 (VHF)", "30 MHz", "300 MHz", "10 - 1 m", "FM广播、电视", COLOR_ITU),
            BandInfo("9 (UHF)", "300 MHz", "3 GHz", "1 m - 10 cm", "电视、手机、微波炉", COLOR_ITU),
            BandInfo("10 (SHF)", "3 GHz", "30 GHz", "10 - 1 cm", "卫星、雷达、WiFi", COLOR_ITU),
            BandInfo("11 (EHF)", "30 GHz", "300 GHz", "10 - 1 mm", "毫米波、射电天文", COLOR_ITU),
            BandInfo("12 (THF)", "300 GHz", "3 THz", "1 - 0.1 mm", "太赫兹成像、光谱分析", COLOR_ITU),
        ]

        # 3. NATO 标准 (北约军事)
        self.band_data["NATO"] = [
            BandInfo("A", "0 MHz", "250 MHz", "-", "低频预警雷达、通信", COLOR_NATO),
            BandInfo("B", "250 MHz", "500 MHz", "-", "预警雷达、通信", COLOR_NATO),
            BandInfo("C", "500 MHz", "1000 MHz", "-", "雷达、通信、电子战", COLOR_NATO),
            BandInfo("D", "1 GHz", "2 GHz", "-", "L波段雷达、中继通信", COLOR_NATO),
            BandInfo("E", "2 GHz", "3 GHz", "-", "S波段雷达、通信", COLOR_NATO),
            BandInfo("F", "3 GHz", "4 GHz", "-", "S波段雷达、通信", COLOR_NATO),
            BandInfo("G", "4 GHz", "6 GHz", "-", "C波段雷达", COLOR_NATO),
            BandInfo("H", "6 GHz", "8 GHz", "-", "C波段雷达、卫星", COLOR_NATO),
            BandInfo("I", "8 GHz", "10 GHz", "-", "X波段雷达、精确制导", COLOR_NATO),
            BandInfo("J", "10 GHz", "20 GHz", "-", "Ku/K波段雷达、制导", COLOR_NATO),
            BandInfo("K", "20 GHz", "40 GHz", "-", "Ka波段雷达、通信", COLOR_NATO),
            BandInfo("L", "40 GHz", "60 GHz", "-", "V波段雷达、通信", COLOR_NATO),
            BandInfo("M", "60 GHz", "100 GHz", "-", "W波段雷达", COLOR_NATO),
        ]
        
        # 4. 中国/一般工业标准 (部分习惯用法)
        self.band_data["CN"] = [
            BandInfo("短波 (SW)", "3 MHz", "30 MHz", "100 - 10 m", "远距离广播、应急通信", COLOR_CN),
            BandInfo("米波", "30 MHz", "300 MHz", "10 - 1 m", "广播电视、对讲机", COLOR_CN),
            BandInfo("分米波", "300 MHz", "3 GHz", "10 - 1 dm", "移动通信、特高压监测", COLOR_CN),
            BandInfo("厘米波", "3 GHz", "30 GHz", "10 - 1 cm", "卫星通信、气象雷达", COLOR_CN),
            BandInfo("毫米波", "30 GHz", "300 GHz", "10 - 1 mm", "5G/6G通信、精确制导", COLOR_CN),
        ]

        # 5. 手机通信频段 (CN)
        self.band_data["CELL"] = [
            BandInfo("5G NR (n41)", "2515 - 2675 MHz", "11 cm", "中国移动 (160M带宽)", COLOR_CELL),
            BandInfo("5G NR (n78)", "3300 - 3500 MHz", "9 cm", "中国电信/联通 (共享)", COLOR_CELL),
            BandInfo("5G NR (n79)", "4800 - 4900 MHz", "6 cm", "中国移动", COLOR_CELL),
            BandInfo("5G NR (n1/n28)", "2100 / 700 MHz", "14 / 43 cm", "广电700M / 联通电信重耕", COLOR_CELL),
            BandInfo("4G LTE (FDD)", "1.8 / 2.1 GHz", "16 / 14 cm", "B3(联通/电信), B1(联通/电信)", COLOR_CELL),
            BandInfo("4G LTE (TDD)", "1.9 / 2.3 / 2.6 GHz", "15 / 13 / 11 cm", "B39/B40/B38/B41 (移动为主)", COLOR_CELL),
            BandInfo("3G (停用中)", "2000 MHz 附近", "15 cm", "WCDMA(联通)/TD(移动)/CDMA2000(电信)", COLOR_CELL),
            BandInfo("2G GSM/CDMA", "900 / 1800 MHz", "33 / 16 cm", "GSM900/1800 (移动/联通), CDMA 800 (电信)", COLOR_CELL),
        ]

        # 6. 卫星导航 (GNSS)
        self.band_data["GNSS"] = [
            BandInfo("GPS L1", "1575.42 MHz", "19.0 cm", "民用 C/A 码, 军用 P(Y) 码", COLOR_GNSS),
            BandInfo("GPS L2", "1227.60 MHz", "24.4 cm", "军用, 民用 L2C", COLOR_GNSS),
            BandInfo("GPS L5", "1176.45 MHz", "25.5 cm", "精密定位, 安全服务 (Safety-of-Life)", COLOR_GNSS),
            BandInfo("BDS B1I / B1C", "1561.1 / 1575.4 MHz", "19.2 cm", "北斗 B1 频段 (兼容 GPS L1)", COLOR_GNSS),
            BandInfo("BDS B2a", "1176.45 MHz", "25.5 cm", "北斗 B2 频段 (兼容 GPS L5)", COLOR_GNSS),
            BandInfo("BDS B3", "1268.52 MHz", "23.6 cm", "北斗特有, 抗干扰能力强", COLOR_GNSS),
            BandInfo("GLONASS G1", "1602 MHz (FDMA)", "18.7 cm", "俄罗斯格洛纳斯频段 (频分多址)", COLOR_GNSS),
            BandInfo("Galileo E1", "1575.42 MHz", "19.0 cm", "欧盟伽利略 (同频 GPS L1)", COLOR_GNSS),
            BandInfo("Galileo E6", "1278.75 MHz", "23.5 cm", "商用服务 (High Accuracy)", COLOR_GNSS),
        ]

        # 7. 业余无线电 (Ham)
        self.band_data["HAM"] = [
            BandInfo("160米波段", "1.8 - 2.0 MHz", "160 m", "MF (中波), 夜间传播好, 天线巨大", COLOR_HAM),
            BandInfo("80米波段", "3.5 - 3.9 MHz", "80 m", "HF (短波), 省内/国内通信", COLOR_HAM),
            BandInfo("40米波段", "7.0 - 7.2 MHz", "40 m", "HF (短波), 最热闹的DX段, 全天可用", COLOR_HAM),
            BandInfo("20米波段", "14.0 - 14.35 MHz", "20 m", "HF (短波), 国际联络主力频段", COLOR_HAM),
            BandInfo("15米波段", "21.0 - 21.45 MHz", "15 m", "HF (短波), 类似20米, 太阳黑子活跃期好", COLOR_HAM),
            BandInfo("10米波段", "28.0 - 29.7 MHz", "10 m", "HF (短波), 接近VHF, 偶发E层传播", COLOR_HAM),
            BandInfo("6米波段", "50 - 54 MHz", "6 m", "VHF, '魔术波段', 兼具短波和超短波特性", COLOR_HAM),
            BandInfo("2米波段", "144 - 148 MHz", "2 m", "VHF, 本地中继, 手台主力", COLOR_HAM),
            BandInfo("70厘米波段", "430 - 440 MHz", "0.7 m", "UHF, 城市穿透力强, 原森海/摩托常用的段", COLOR_HAM),
        ]

    def create_input_panel(self) -> QWidget:
        """创建左侧输入/控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 小标题
        title = QLabel("🔍 筛选与控制")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title)
        
        # 1. 标准选择
        std_label = QLabel("分类标准:")
        layout.addWidget(std_label)
        
        self._standard_combo = QComboBox()
        self._standard_combo.addItem("IEEE (雷达/射频常用)", "IEEE")
        self._standard_combo.addItem("ITU (国际电联/波段号)", "ITU")
        self._standard_combo.addItem("NATO (北约/军事)", "NATO")
        self._standard_combo.addItem("手机通信 (5G/4G/3G/2G)", "CELL")
        self._standard_combo.addItem("卫星导航 (GNSS)", "GNSS")
        self._standard_combo.addItem("业余无线电 (Ham)", "HAM")
        self._standard_combo.addItem("中国/通用工业习惯", "CN")
        self._standard_combo.currentIndexChanged.connect(self.on_standard_changed)
        layout.addWidget(self._standard_combo)
        
        # 2. 搜索框
        search_label = QLabel("搜索频段:")
        layout.addWidget(search_label)
        
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("输入名称或频率 (如 'S' 或 '2.4')")
        self._search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self._search_input)
        
        # 说明文字
        info_label = QLabel(
            "提示: 不同标准中相同的字母可能代表完全不同的频段。\n例如 'K' 频段:\n• IEEE: 18-27 GHz\n• NATO: 20-40 GHz"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        return panel

    def create_result_panel(self) -> QWidget:
        """创建右侧结果面板 (表格)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 表格控件
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["频段名称", "频率范围", "波长范围", "典型应用"])
        
        # 设置表格属性
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # 名称自适应
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # 频率自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # 波长自适应
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)          # 应用拉伸
        
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # 不可编辑
        
        layout.addWidget(self._table)
        
        # 初始填充
        self._update_table()
        
        return panel
        
    def _update_table(self, filter_text: str = ""):
        """更新表格内容"""
        data = self.band_data.get(self._current_standard, [])
        filter_text = filter_text.lower().strip()
        
        filtered_data = []
        if not filter_text:
            filtered_data = data
        else:
            for item in data:
                # 简单搜索: 匹配名称、频率、应用
                if (filter_text in item.name.lower() or 
                    filter_text in item.start_freq.lower() or 
                    filter_text in item.stop_freq.lower() or
                    filter_text in item.application.lower()):
                    filtered_data.append(item)
        
        # 填充表格
        self._table.setRowCount(len(filtered_data))
        for row, item in enumerate(filtered_data):
            # 名称
            name_item = QTableWidgetItem(item.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setBackground(QColor(item.color))  # 设置背景色
            # 字体加粗
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self._table.setItem(row, 0, name_item)
            
            # 频率
            freq_item = QTableWidgetItem(f"{item.start_freq} - {item.stop_freq}")
            freq_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, freq_item)
            
            # 波长
            wave_item = QTableWidgetItem(item.wavelength)
            wave_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, wave_item)
            
            # 应用
            app_item = QTableWidgetItem(item.application)
            self._table.setItem(row, 3, app_item)

    def calculate(self):
        """覆盖基类方法，此处无计算逻辑"""
        pass
        
    def get_intuition_content(self) -> Optional[str]:
        return None
        
    def get_math_model_content(self) -> Optional[str]:
        return None

    def get_engineering_content(self) -> Optional[str]:
        return tr("bandtable.engineering_content")

    def get_history_content(self) -> Optional[str]:
        return tr("bandtable.history_content")

    def get_boundary_content(self) -> Optional[str]:
        return None
