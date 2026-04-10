# -*- coding: utf-8 -*-
"""
射频连接器选型参考表工具
RF Connector Selection Reference Tool

版本: v1.0.0
功能: 提供主流射频连接器的频率范围、功率容量、阻抗等关键选型参数速查
数据来源: MIL-STD-348, IEC 61169, 各厂商 (Amphenol/Rosenberger/Southwest) 典型规格
"""

from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QHeaderView, QLineEdit,
    QTableWidget, QTableWidgetItem, QFrame, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ui.base.tool_base import ToolBase

# Matplotlib
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import font_manager
import numpy as np


def _pick_plot_font_family() -> str:
    """选择 Matplotlib 中实际可用的中文/界面字体，避免启动警告"""
    preferred = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Segoe UI",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    available = {font.name for font in font_manager.fontManager.ttflist}
    for family in preferred:
        if family in available:
            return family
    return "sans-serif"


PLOT_FONT_FAMILY = _pick_plot_font_family()


class ConnectorInfo:
    """射频连接器信息数据类"""
    def __init__(
        self,
        name: str,              # 连接器类型名称
        impedance: str,         # 阻抗 (Ω)
        freq_max: str,          # 最高工作频率
        power_avg: str,         # 平均功率容量
        power_peak: str,        # 峰值功率容量
        vswr: str,              # 典型 VSWR
        coupling: str,          # 连接方式
        interface_mm: str,      # 接口尺寸 (mm)
        application: str,       # 典型应用
        color: str = "#F0F7FF"  # 行背景色
    ):
        self.name = name
        self.impedance = impedance
        self.freq_max = freq_max
        self.power_avg = power_avg
        self.power_peak = power_peak
        self.vswr = vswr
        self.coupling = coupling
        self.interface_mm = interface_mm
        self.application = application
        self.color = color


class ConnectorTableTool(ToolBase):
    """
    射频连接器选型参考表
    v1.0.0 - 覆盖主流射频/微波同轴连接器
    """

    tool_name = "连接器选型"
    tool_icon = "🔌"
    tool_category = "reference"
    tool_description = "射频连接器频率范围、功率容量与关键参数速查"

    # ========== 回调方法 ==========

    def on_filter_changed(self, index: int):
        """筛选切换"""
        self._current_filter = self._filter_combo.itemData(index)
        self._update_table()

    def on_search_text_changed(self, text: str):
        """搜索文字变化"""
        self._update_table(filter_text=text)

    # ========== 初始化 ==========

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化"""
        self._current_filter = "ALL"
        self._init_data()
        super().__init__(parent)

    # ==================== 降额因子表 (来自 Southwest Microwave 官方文档) ====================
    # 温度降额因子: {温度°C: 降额系数}
    TEMP_DERATING = {0: 1.20, 40: 1.00, 80: 0.80, 120: 0.60, 160: 0.40, 200: 0.20, 240: 0.05}
    # 海拔降额因子: {海拔(千英尺): 降额系数}
    ALT_DERATING_KFT = {0: 1.00, 20: 0.80, 30: 0.70, 40: 0.60, 50: 0.50, 60: 0.40, 70: 0.30}

    def _init_data(self):
        """
        初始化连接器数据
        
        数据来源与校准说明:
        - 平均功率容量 (CW): 基于 Southwest Microwave 官方 Power Handling Graph
          (对数坐标图，40°C / 海平面 / VSWR 1.0 条件)
        - 峰值功率: 基于电压击穿计算，与频率基本无关
        - 最高频率: 连接器支持的最高工作频率 (非截止频率)
        - 功率容量随频率升高而降低: P(f) = P_ref × √(f_ref / f)
        
        ⚠️ 注意: 功率值因供应商而异 (设计/材料/制造差异)，
              本表取行业领先厂商代表值，实际选型请查阅对应厂商规格书。
        """
        C = "#F0F7FF"  # 统一浅色背景

        self.connector_data: List[ConnectorInfo] = [
            # ==================== 大功率连接器 ====================
            ConnectorInfo(
                "7/16 DIN", "50", "7.5 GHz", "2500 W (@1GHz)", "20 kW",
                "≤1.15", "螺纹", "16/7 mm",
                "基站天线、大功率射频系统", C
            ),
            ConnectorInfo(
                "LC", "50", "6 GHz", "5000 W (@1GHz)", "30 kW",
                "≤1.20", "卡口", "—",
                "高功率雷达、广播发射", C
            ),
            ConnectorInfo(
                "SC", "50", "11 GHz", "2000 W (@1GHz)", "15 kW",
                "≤1.20", "螺纹", "—",
                "大功率微波系统", C
            ),
            ConnectorInfo(
                "HN", "50", "4 GHz", "5000 W (@1GHz)", "35 kW",
                "≤1.30", "螺纹", "—",
                "高压大功率射频", C
            ),

            # ==================== 通用连接器 ====================
            ConnectorInfo(
                "N 型", "50", "18 GHz", "1900 W (@1GHz)", "5 kW",
                "≤1.15", "螺纹", "外Ø 1/4″",
                "测试仪器、基站馈线、实验室", C
            ),
            ConnectorInfo(
                "N 型 (75Ω)", "75", "11 GHz", "1000 W (@1GHz)", "3 kW",
                "≤1.15", "螺纹", "外Ø 1/4″",
                "有线电视、视频传输", C
            ),
            ConnectorInfo(
                "TNC", "50", "18 GHz", "950 W (@1GHz)", "1.5 kW",
                "≤1.15", "螺纹", "外Ø 1/4″",
                "振动环境、军用、航空航天", C
            ),
            ConnectorInfo(
                "BNC", "50", "4 GHz", "350 W (@1GHz)", "500 W",
                "≤1.30", "卡口", "外Ø 1/4″",
                "示波器、低频测试、视频", C
            ),
            ConnectorInfo(
                "BNC (75Ω)", "75", "2 GHz", "200 W (@1GHz)", "200 W",
                "≤1.30", "卡口", "外Ø 1/4″",
                "视频监控、广播设备", C
            ),

            # ==================== 精密连接器 (毫米波) ====================
            ConnectorInfo(
                "SMA", "50", "27 GHz", "600 W (@1GHz)", "1.5 kW",
                "≤1.15", "螺纹", "外Ø 1/4″ (6.35)",
                "最广泛使用的射频连接器", C
            ),
            ConnectorInfo(
                "SMB", "50", "4 GHz", "200 W (@1GHz)", "250 W",
                "≤1.30", "推入式", "外Ø 3.5mm",
                "PCB 板端、GPS 模块", C
            ),
            ConnectorInfo(
                "SMC", "50", "10 GHz", "200 W (@1GHz)", "250 W",
                "≤1.30", "螺纹", "外Ø 3.5mm",
                "紧凑型微波组件", C
            ),
            ConnectorInfo(
                "SMP/SMPM", "50", "40 GHz", "200 W (@1GHz)", "200 W",
                "≤1.25", "推入式", "外Ø 2.5mm",
                "高密度板间连接、5G 模组", C
            ),
            ConnectorInfo(
                "SSMA", "50", "36 GHz", "320 W (@1GHz)", "500 W",
                "≤1.20", "螺纹", "外Ø 4.0mm",
                "小型化微波组件", C
            ),

            # ==================== 3.5mm/2.92mm/2.4mm/1.85mm/1.0mm 系列 ====================
            # (数据基于 Southwest Microwave 官方 Power Handling Graph 校准)
            ConnectorInfo(
                "3.5mm (APC-3.5)", "50", "33 GHz", "250 W (@1GHz)", "1 kW",
                "≤1.15", "螺纹", "外Ø 3.5mm",
                "精密测量、与 SMA 兼容", C
            ),
            ConnectorInfo(
                "2.92mm (K)", "50", "40 GHz", "140 W (@1GHz)", "500 W",
                "≤1.15", "螺纹", "外Ø 2.92mm",
                "毫米波测试、与 SMA/3.5mm 兼容", C
            ),
            ConnectorInfo(
                "2.4mm", "50", "50 GHz", "80 W (@1GHz)", "400 W",
                "≤1.20", "螺纹", "外Ø 2.4mm",
                "50 GHz 精密测量", C
            ),
            ConnectorInfo(
                "1.85mm (V)", "50", "67 GHz", "44 W (@1GHz)", "200 W",
                "≤1.25", "螺纹", "外Ø 1.85mm",
                "V 频段测试、与 2.4mm 兼容", C
            ),
            ConnectorInfo(
                "1.35mm", "50", "90 GHz", "25 W (@1GHz)", "100 W",
                "≤1.30", "螺纹", "外Ø 1.35mm",
                "E/W 频段精密测量", C
            ),
            ConnectorInfo(
                "1.0mm (W)", "50", "110 GHz", "16 W (@1GHz)", "50 W",
                "≤1.35", "螺纹", "外Ø 1.0mm",
                "W 频段毫米波、110 GHz 测试", C
            ),
            ConnectorInfo(
                "0.8mm", "50", "145 GHz", "10 W (@1GHz)", "20 W",
                "≤1.40", "螺纹", "外Ø 0.8mm",
                "亚毫米波前沿研究", C
            ),

            # ==================== 特殊应用 ====================
            ConnectorInfo(
                "F 型", "75", "3 GHz", "100 W (@1GHz)", "200 W",
                "≤1.30", "螺纹", "外Ø 9.5mm",
                "有线电视、卫星电视机顶盒", C
            ),
            ConnectorInfo(
                "MCX", "50", "6 GHz", "150 W (@1GHz)", "150 W",
                "≤1.30", "推入式", "外Ø 3.6mm",
                "GPS、WiFi 模块板端", C
            ),
            ConnectorInfo(
                "MMCX", "50", "6 GHz", "100 W (@1GHz)", "100 W",
                "≤1.30", "推入式", "外Ø 2.8mm",
                "超小型 GPS/蓝牙模组", C
            ),
            ConnectorInfo(
                "QMA", "50", "18 GHz", "900 W (@1GHz)", "2 kW",
                "≤1.15", "推入锁定", "外Ø 1/4″",
                "基站快速安装、替代 SMA", C
            ),
            ConnectorInfo(
                "NEX10", "50", "12 GHz", "1500 W (@1GHz)", "5 kW",
                "≤1.15", "推入锁定", "外Ø 10mm",
                "5G 小基站、新一代替代 4.3-10", C
            ),
            ConnectorInfo(
                "4.3-10", "50", "12 GHz", "2500 W (@1GHz)", "10 kW",
                "≤1.12", "推入锁定", "外Ø 10mm",
                "5G 基站天线、低 PIM 场景", C
            ),
        ]

    # ========== UI 面板 ==========

    def create_input_panel(self) -> QWidget:
        """创建左侧筛选面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("🔍 筛选与控制")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title)

        # 1. 场景筛选
        filter_label = QLabel("按应用场景筛选:")
        layout.addWidget(filter_label)

        self._filter_combo = QComboBox()
        self._filter_combo.addItem("全部连接器", "ALL")
        self._filter_combo.addItem("大功率 (>200W)", "HIGH_POWER")
        self._filter_combo.addItem("通用型 (N/BNC/TNC/SMA)", "GENERAL")
        self._filter_combo.addItem("毫米波精密 (>18GHz)", "PRECISION")
        self._filter_combo.addItem("小型化板端 (SMB/MCX/MMCX)", "MINIATURE")
        self._filter_combo.addItem("5G/基站 (4.3-10/NEX10/QMA)", "BASE_STATION")
        self._filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self._filter_combo)

        # 2. 搜索框
        search_label = QLabel("搜索连接器:")
        layout.addWidget(search_label)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("输入名称 (如 'SMA' 或 '2.92')")
        self._search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self._search_input)

        # 说明
        info = QLabel(
            "数据说明:\n"
            "• CW 功率基于 Southwest Microwave\n"
            "  官方 Power Handling Graph 校准\n"
            "• 条件: 40°C / 海平面 / VSWR 1.0\n"
            "• 功率随频率升高而降低\n"
            "  P(f) = P_ref × √(f_ref / f)\n"
            "• 实际功率因供应商而异\n"
            "• 点选表格行查看降额曲线"
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

        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels([
            "连接器", "阻抗\n(Ω)", "最高频率",
            "CW额定功率", "峰值功率", "VSWR",
            "连接方式", "典型应用"
        ])

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self._table)
        self._update_table()
        
        # 垂直分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self._table)
        
        # 图表区域
        self._chart_container = QWidget()
        chart_layout = QVBoxLayout(self._chart_container)
        chart_layout.setContentsMargins(0, 5, 0, 0)
        
        # 图表画布
        self._fig = Figure(figsize=(5, 3), dpi=100)
        self._canvas = FigureCanvasQTAgg(self._fig)
        chart_layout.addWidget(self._canvas)
        
        # 绘制初始占位提示
        self._draw_placeholder()
        
        splitter.addWidget(self._chart_container)
        splitter.setStretchFactor(0, 6) # 表格占 60%
        splitter.setStretchFactor(1, 4) # 图表占 40%
        
        layout.addWidget(splitter)
        
        return panel

    def _draw_placeholder(self):
        """绘制图表占位提示 (初次打开时显示)"""
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # 主提示文字
        ax.text(0.5, 0.55, "点击上方表格中的连接器",
                ha='center', va='center', fontsize=13,
                color='#718096', fontweight='bold',
            fontfamily=PLOT_FONT_FAMILY)
        ax.text(0.5, 0.42, "查看 CW 功率容量 vs 频率降额曲线",
                ha='center', va='center', fontsize=12,
                color='#A0AEC0',
            fontfamily=PLOT_FONT_FAMILY)
        ax.text(0.5, 0.30, "P(f) = P_ref × √(f_ref / f)",
                ha='center', va='center', fontsize=11,
                color='#CBD5E0', fontstyle='italic')
        
        self._fig.tight_layout()
        self._canvas.draw()

    def _on_selection_changed(self):
        """表格选中行变化"""
        items = self._table.selectedItems()
        if not items:
            return
            
        row = items[0].row()
        name = self._table.item(row, 0).text()
        freq_str = self._table.item(row, 2).text()
        p_avg_str = self._table.item(row, 3).text()
        
        self._plot_power_curve(name, freq_str, p_avg_str)

    def _parse_value(self, s: str) -> float:
        """解析数值字符串 (移除单位等)"""
        import re
        # 提取第一个浮点数
        match = re.search(r"([\d\.]+)", s)
        return float(match.group(1)) if match else 0.0

    def _plot_power_curve(self, name: str, freq_max_str: str, p_avg_str: str):
        """绘制功率-频率曲线"""
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        
        try:
            # 1. 解析最大频率 (GHz)
            f_max = self._parse_value(freq_max_str)
            if f_max <= 0: return

            # 2. 解析基准功率 (W) 及基准频率
            # 默认基准: 1GHz
            f_ref = 1.0 
            p_ref = 0.0
            
            # 解析 "200 W (@1GHz)" 格式
            if "@" in p_avg_str:
                p_part, f_part = p_avg_str.split("@")
                p_ref = self._parse_value(p_part)
                f_ref = self._parse_value(f_part)
            else:
                p_ref = self._parse_value(p_avg_str)
                # 如果没写 @GHz，通常默认为低频或 1GHz，这里假设 1GHz 为基准
                # 特殊情况: 7/16 DIN 等低频大功率可能基准不同，但 1GHz 是通用参考
            
            if p_ref <= 0: return

            # 3. 生成曲线数据 P(f) = P_ref * sqrt(f_ref/f)
            # 频率范围: 0.1 GHz 到 f_max
            x = np.linspace(max(0.1, f_ref/10), f_max, 100)
            y = p_ref * np.sqrt(f_ref / x)
            
            # 4. 绘图
            ax.plot(x, y, color='#2C7BE5', linewidth=2, label='Power Derating')
            ax.fill_between(x, 0, y, color='#2C7BE5', alpha=0.1)
            
            # 标记基准点
            ax.plot(f_ref, p_ref, 'o', color='#E53E3E')
            ax.annotate(f"{p_ref:.0f}W @ {f_ref}GHz", (f_ref, p_ref), 
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, color='#E53E3E')
            
            # 标记最大频率点
            p_end = p_ref * np.sqrt(f_ref / f_max)
            ax.plot(f_max, p_end, 'o', color='#38A169')
            ax.annotate(f"{p_end:.0f}W @ {f_max}GHz", (f_max, p_end),
                        xytext=(-60, 10), textcoords='offset points',
                         fontsize=9, color='#38A169')

            # 设置
            ax.set_title(f"{name} Power Handling vs Frequency", fontsize=10, pad=10)
            ax.set_xlabel("Frequency (GHz)", fontsize=9)
            ax.set_ylabel("Avg Power (W)", fontsize=9)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(loc='upper right', fontsize=8)
            
            # 公式文本 (移除以避免遮挡)
            # eqn = r"$P(f) = P_{ref} \times \sqrt{\frac{f_{ref}}{f}}$"
            # ax.text(0.05, 0.05, eqn, transform=ax.transAxes, fontsize=10, 
            #         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

            # 底部提示
            ax.set_xlabel("Frequency (GHz)\n(Drag to inspect values)", fontsize=9)

            # 保存绘图状态供交互使用
            self._plot_ax = ax
            self._plot_f_ref = f_ref
            self._plot_p_ref = p_ref
            self._plot_f_max = f_max
            self._plot_cursor_line = ax.axvline(x=f_ref, color='gray', linestyle=':', alpha=0.8)
            self._plot_cursor_scatter, = ax.plot([f_ref], [p_ref], 'o', color='orange', alpha=0.8)
            self._plot_cursor_text = ax.text(f_ref, p_ref, "", fontsize=9, 
                                           color='#2D3748', fontweight='bold',
                                           bbox=dict(facecolor='white', alpha=0.9, edgecolor='#CBD5E0', boxstyle='round,pad=0.3'))
            
            # 连接鼠标事件
            self._canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
            
        except Exception as e:
            ax.text(0.5, 0.5, f"Cannot plot: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes)
            
        self._fig.tight_layout()
        self._canvas.draw()

    def _on_mouse_move(self, event):
        """鼠标移动事件 - 更新游标"""
        if not event.inaxes or not hasattr(self, '_plot_ax') or event.inaxes != self._plot_ax:
            return
            
        # 获取当前鼠标 X 坐标 (频率)
        x = event.xdata
        if x is None: return
        
        # 限制范围
        f_min, f_max = 0.1, self._plot_f_max
        x = max(f_min, min(x, f_max))
        
        # 计算对应 Y 坐标 (功率)
        y = self._plot_p_ref * np.sqrt(self._plot_f_ref / x)
        
        # 更新游标位置
        self._plot_cursor_line.set_xdata([x])
        self._plot_cursor_scatter.set_data([x], [y])
        
        # 更新文本位置和内容
        self._plot_cursor_text.set_position((x, y))
        self._plot_cursor_text.set_text(f" {y:.1f}W @ {x:.2f}GHz ")
        
        # 智能调整文本对齐，避免出界
        ha = 'left' if x < (f_max * 0.7) else 'right'
        va = 'bottom' if y < (self._plot_p_ref * 0.8) else 'top'
        self._plot_cursor_text.set_ha(ha)
        self._plot_cursor_text.set_va(va)
        
        self._canvas.draw_idle()

    def _get_category(self, conn: ConnectorInfo) -> str:
        """判断连接器所属类别 (用于筛选)"""
        name = conn.name.upper()
        # 大功率
        if name in ["7/16 DIN", "LC", "SC", "HN", "4.3-10"]:
            return "HIGH_POWER"
        # 通用型
        if any(k in name for k in ["N 型", "BNC", "TNC", "SMA"]) and "SSMA" not in name:
            return "GENERAL"
        # 毫米波精密
        if any(k in name for k in ["3.5MM", "2.92MM", "2.4MM", "1.85MM", "1.35MM", "1.0MM", "0.8MM", "SSMA", "SMP"]):
            return "PRECISION"
        # 小型化板端
        if any(k in name for k in ["SMB", "SMC", "MCX", "MMCX"]):
            return "MINIATURE"
        # 基站
        if any(k in name for k in ["QMA", "NEX10"]):
            return "BASE_STATION"
        # 特殊
        return "GENERAL"

    def _update_table(self, filter_text: str = ""):
        """更新表格"""
        filter_text = filter_text.lower().strip()
        category = self._current_filter

        filtered = []
        for conn in self.connector_data:
            # 类别筛选
            if category != "ALL":
                if self._get_category(conn) != category:
                    continue
            # 文本搜索
            if filter_text:
                searchable = (
                    conn.name.lower() + " " +
                    conn.impedance + " " +
                    conn.freq_max.lower() + " " +
                    conn.coupling.lower() + " " +
                    conn.application.lower()
                )
                if filter_text not in searchable:
                    continue
            filtered.append(conn)

        self._table.setRowCount(len(filtered))
        for row, conn in enumerate(filtered):
            # 连接器名称
            name_item = QTableWidgetItem(conn.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setBackground(QColor(conn.color))
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self._table.setItem(row, 0, name_item)

            # 阻抗
            z_item = QTableWidgetItem(conn.impedance)
            z_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, z_item)

            # 最高频率
            freq_item = QTableWidgetItem(conn.freq_max)
            freq_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, freq_item)

            # 平均功率
            pavg_item = QTableWidgetItem(conn.power_avg)
            pavg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, pavg_item)

            # 峰值功率
            ppk_item = QTableWidgetItem(conn.power_peak)
            ppk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 4, ppk_item)

            # VSWR
            vswr_item = QTableWidgetItem(conn.vswr)
            vswr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 5, vswr_item)

            # 连接方式
            coup_item = QTableWidgetItem(conn.coupling)
            coup_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 6, coup_item)

            # 典型应用
            app_item = QTableWidgetItem(conn.application)
            self._table.setItem(row, 7, app_item)

    # ========== 基类接口 ==========

    def calculate(self):
        """无计算逻辑"""
        pass

    def get_intuition_content(self) -> Optional[str]:
        return None

    def get_math_model_content(self) -> Optional[str]:
        """功率降额计算模型"""
        return """
        <b>📐 功率降额数学模型</b><br><br>

        射频连接器的平均功率容量主要受限于中心导体的焦耳热耗散。
        随频率升高，趋肤效应导致电阻增加，功率容量随之下降。<br><br>

        <b>计算公式:</b><br>
        P(f) = P<sub>ref</sub> &times; &radic;(f<sub>ref</sub> / f)
        <br>
        其中:<br>
        • <b>P(f)</b>: 目标频率 f 下的平均功率容量<br>
        • <b>P<sub>ref</sub></b>: 参考频率下的功率容量 (通常取 1GHz)<br>
        • <b>f<sub>ref</sub></b>: 参考频率 (通常取 1GHz)<br>
        • <b>f</b>: 工作频率<br><br>

        <b>说明:</b><br>
        该模型适用于同轴线和连接器的主模传输模式。
        峰值功率则由电压击穿决定，通常视为常数，但在高海拔处需降额。
        """

    def get_engineering_content(self) -> Optional[str]:
        """连接器选型工程指南"""
        return """
        <b>🏗️ 射频连接器选型指南</b><br>
        <span style="color: #E53E3E; font-size: 12px;">
        数据基于 Southwest Microwave 官方文档</span><br><br>

        <b>1. 频率优先:</b><br>
        • 连接器最高频率必须覆盖系统工作频带<br>
        • 余量建议 ≥20% (如系统 10 GHz，选 ≥12 GHz)<br><br>

        <b>2. 功率降额 (三个维度):</b><br>
        • <b>频率降额:</b> P(f) = P<sub>ref</sub> × √(f<sub>ref</sub>/f)<br>
        • <b>温度降额 (基准 40°C):</b><br>
        &nbsp;&nbsp;0°C → ×1.20 | 80°C → ×0.80<br>
        &nbsp;&nbsp;120°C → ×0.60 | 160°C → ×0.40<br>
        • <b>海拔降额 (基准海平面):</b><br>
        &nbsp;&nbsp;6000m → ×0.80 | 12000m → ×0.60<br>
        &nbsp;&nbsp;18000m → ×0.40 | 21000m → ×0.30<br>
        • <b>组合降额:</b> P = P(f) × DF<sub>temp</sub> × DF<sub>alt</sub><br><br>

        <b>3. 互配兼容:</b><br>
        • SMA ↔ 3.5mm ↔ 2.92mm 机械兼容 (可直连)<br>
        • 2.4mm ↔ 1.85mm 机械兼容<br>
        • N 型 50Ω 和 75Ω 物理可插但阻抗不匹配!<br><br>

        <b>4. 可靠性:</b><br>
        • 螺纹连接 > 卡口 > 推入式 (振动环境)<br>
        • SMA 典型寿命 ~500 次插拔<br>
        • 精密连接器 (3.5mm 等) 需用力矩扳手
        """

    def get_history_content(self) -> Optional[str]:
        """连接器发展历史"""
        return """
        <b>📜 射频连接器发展简史</b><br><br>

        <b>BNC — 二战产物 (1951):</b><br>
        名称来自 Bayonet Neill-Concelman，
        由 Paul Neill (Bell Labs) 和 Carl Concelman 联合设计。
        卡口式连接开创了快速连接的先河。<br><br>

        <b>N 型 — 微波时代基石 (1942):</b><br>
        以发明者 Paul Neill 命名，是第一个真正的
        微波同轴连接器。至今仍是实验室测量的标准。<br><br>

        <b>SMA — 最成功的射频连接器 (1960s):</b><br>
        Sub-Miniature version A，由 Bendix 公司发明。
        全球使用量最大的射频连接器，几乎无处不在。<br><br>

        <b>精密系列 — 毫米波驱动:</b><br>
        3.5mm (Hewlett-Packard, 1970s) → 2.92mm (K, Wiltron 1983)
        → 2.4mm (HP 1988) → 1.85mm (V, Anritsu) → 1.0mm (W, HP 1990s)。<br>
        连接器尺寸与频率上限的关系: f_max ≈ c / (π×d)，
        口径越小频率越高，这也是精密连接器命名用 mm 的原因。
        """

    def get_boundary_content(self) -> Optional[str]:
        return None
