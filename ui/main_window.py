# -*- coding: utf-8 -*-
"""
射频天线工具集 - 主窗口
RF Antenna Toolkit - Main Window

版本: v1.0.0
功能: 应用程序主窗口，包含导航栏和工具工作区
"""

import os
import sys
from typing import Dict, Optional, Type

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.widgets.nav_bar import NavBar
from ui.base.tool_base import ToolBase
from ui.tools.antenna.wavelength_tool import WavelengthTool
from ui.tools.antenna.bandwidth_tool import BandwidthTool
from ui.tools.antenna.gain_tool import GainTool
from ui.tools.antenna.los_tool import LOSTool
from ui.tools.antenna.sensitivity_tool import SensitivityTool
from ui.tools.antenna.phased_array_tool import PhasedArrayTool
from ui.tools.antenna.range_tool import RangeTool
from ui.tools.rf.vswr_tool import VSWRTool
from ui.tools.rf.cascade_tool import CascadeTool
from ui.tools.rf.impedance_tool import ImpedanceTool
from ui.tools.rf.attenuator_tool import AttenuatorTool
from ui.tools.rf.matching_tool import MatchingTool
from ui.tools.rf.link_budget_tool import LinkBudgetTool
from ui.tools.reference.band_table_tool import BandTableTool
from ui.tools.reference.waveguide_table_tool import WaveguideTableTool
from ui.tools.reference.connector_table_tool import ConnectorTableTool
from ui.tools.reference.eseries_table_tool import ESeriesTableTool
from ui.tools.reference.online_tools_page import OnlineToolsPage


def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MainWindow(QMainWindow):
    """
    应用程序主窗口
    
    布局结构:
    - 顶部: 标题栏
    - 左侧: 工具导航栏
    - 右侧: 工具工作区 (堆叠窗口)
    """
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 工具注册表 {tool_id: tool_widget}
        self._tools: Dict[str, QWidget] = {}
        
        # 初始化界面
        self._setup_window()
        self._setup_ui()
        self._register_tools()
        self._load_stylesheet()
    
    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("射频天线工具集 v1.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 设置窗口居中
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_ui(self):
        """构建界面"""
        # 中央容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==================== 顶部标题栏 ====================
        header = self._create_header()
        main_layout.addWidget(header)
        
        # ==================== 主体区域 (导航 + 工作区) ====================
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # 左侧导航栏
        self._nav_bar = NavBar()
        self._nav_bar.tool_selected.connect(self._on_tool_selected)
        body_layout.addWidget(self._nav_bar)
        
        # 右侧工作区
        work_area = QWidget()
        work_area.setObjectName("WorkArea")
        work_layout = QVBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        
        # 堆叠窗口 (用于切换不同工具)
        self._tool_stack = QStackedWidget()
        work_layout.addWidget(self._tool_stack)
        
        # 添加欢迎页
        welcome_page = self._create_welcome_page()
        self._tool_stack.addWidget(welcome_page)
        
        body_layout.addWidget(work_area, 1)
        main_layout.addLayout(body_layout, 1)
    
    def _create_header(self) -> QWidget:
        """创建顶部标题栏"""
        header = QWidget()
        header.setObjectName("HeaderWidget")
        header.setFixedHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        
        # 左侧: Logo和标题
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        # 主标题
        title = QLabel("🔧 射频天线工具集")
        title.setObjectName("AppTitle")
        title_layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("RF Antenna Toolkit v1.0 - 专业射频与天线计算工具")
        subtitle.setObjectName("AppSubtitle")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # 右侧: 公司/开发者信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        company_label = QLabel("成都市安泰纳科技有限公司")
        company_label.setStyleSheet("font-size: 12px; color: #718096; font-weight: 500;")
        company_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        info_layout.addWidget(company_label)
        
        dev_label = QLabel("Developer: CR | 625313077@qq.com")
        dev_label.setStyleSheet("font-size: 11px; color: #A0AEC0;")
        dev_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        info_layout.addWidget(dev_label)
        
        layout.addLayout(info_layout)
        
        return header
    
    def _create_welcome_page(self) -> QWidget:
        """创建欢迎页"""
        page = QWidget()
        page.setObjectName("WelcomePage")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 欢迎标题
        title = QLabel("欢迎使用射频天线工具集")
        title.setObjectName("WelcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("请从左侧导航栏选择一个工具开始使用")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # 公司与作者信息 (底部)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        company_label = QLabel("🚀 研发公司: 成都市安泰纳科技有限公司")
        company_label.setStyleSheet("color: #718096; font-size: 14px;")
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        author_label = QLabel("作者: CR | 邮箱: 625313077@qq.com | 版本: v1.0.0")
        author_label.setStyleSheet("color: #A0AEC0; font-size: 13px;")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        copyright_label = QLabel("© 2026 所有权保留")
        copyright_label.setStyleSheet("color: #CBD5E0; font-size: 12px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        info_layout.addWidget(company_label)
        info_layout.addWidget(author_label)
        info_layout.addWidget(copyright_label)
        
        layout.addLayout(info_layout)
        
        return page
    
    def _register_tools(self):
        """注册所有工具"""
        # ==================== 天线工具 ====================
        self._nav_bar.add_category("天线工具", "📡")
        
        # 波长计算器
        self._register_tool(
            "wavelength",
            WavelengthTool,
            "波长计算",
            "📏",
            "频率与波长转换计算"
        )
        
        # 带宽计算器
        self._register_tool(
            "bandwidth",
            BandwidthTool,
            "带宽计算",
            "📶",
            "各种带宽定义转换计算"
        )
        
        # 增益计算器
        self._register_tool(
            "gain",
            GainTool,
            "增益计算",
            "📡",
            "天线增益计算 (波束宽度/口径法)"
        )
        
        # 视距计算器
        self._register_tool(
            "los",
            LOSTool,
            "视距计算",
            "🌍",
            "地球曲率视距与仰角计算"
        )
        
        # 系统灵敏度计算
        self._register_tool(
            "sensitivity",
            SensitivityTool,
            "系统灵敏度计算",
            "📶",
            "无线系统链路总灵敏度评估"
        )
        
        # 相控阵计算
        self._register_tool(
            "phased_array",
            PhasedArrayTool,
            "相控阵计算",
            "🎯",
            "阵列天线扫描与方向图剖析"
        )
        
        # 收发距离计算
        self._register_tool(
            "range",
            RangeTool,
            "收发距离计算",
            "📏",
            "基于 Friis 方程计算最远通信距离"
        )
        
        # ==================== 射频工具 ====================
        self._nav_bar.add_category("射频工具", "📻")
        
        # 驻波计算器
        self._register_tool(
            "vswr",
            VSWRTool,
            "驻波计算",
            "📊",
            "驻波比与反射系数转换"
        )
        
        # 级联驻波计算器
        self._register_tool(
            "cascade",
            CascadeTool,
            "级联驻波",
            "🔗",
            "多组件级联驻波范围计算"
        )
        
        # 阻抗计算器
        self._register_tool(
            "impedance",
            ImpedanceTool,
            "阻抗计算",
            "Ω",
            "传输线特性阻抗计算"
        )
        
        # 后续工具占位 (后续迭代添加)
        # self._register_tool("txline", TxLineTool, "传输线", "〰️", "传输线参数计算")

        # 衰减计算器
        self._register_tool(
            "attenuator",
            AttenuatorTool,
            "衰减计算",
            "📉",
            "T 型/π 型衰减器电阻值计算"
        )

        # 阻抗匹配
        self._register_tool(
            "matching",
            MatchingTool,
            "阻抗匹配",
            "🔧",
            "阻抗匹配网络设计与实时调谐"
        )

        # 链路预算计算
        self._register_tool(
            "link_budget",
            LinkBudgetTool,
            "链路预算",
            "🔗",
            "射频链路级联增益、NF、P1dB 计算"
        )

        # ==================== 参考手册 ====================
        self._nav_bar.add_category("参考手册", "📖")
        
        # 频段参考表
        self._register_tool(
            "band_table",
            BandTableTool,
            "频段分类",
            "📶",
            "无线电频段分类标准对照表"
        )
        
        # 波导法兰参考表
        self._register_tool(
            "waveguide_table",
            WaveguideTableTool,
            "波导法兰",
            "🔧",
            "标准矩形波导结构尺寸与法兰型号速查"
        )
        
        # 射频连接器参考表
        self._register_tool(
            "connector_table", ConnectorTableTool, "连接器选型", "🔌",
            "射频连接器频率范围及功率查阅"
        )
        self._register_tool(
            "eseries_table", ESeriesTableTool, "标称值速查", "🏷️",
            "IEC 60063 元件标准阻值/容差速查"
        )
        self._register_tool(
            "online_tools", OnlineToolsPage, "精品在线工具", "🌐",
            "大厂射频在线仿真与匹配计算神器库"
        )
    
    def _register_tool(
        self,
        tool_id: str,
        tool_class: Type[ToolBase],
        name: str,
        icon: str,
        tooltip: str
    ):
        """
        注册工具
        
        参数:
            tool_id: 工具唯一标识
            tool_class: 工具类
            name: 显示名称
            icon: 图标
            tooltip: 提示文字
        """
        # 创建工具实例
        tool_widget = tool_class()
        
        # 添加到堆叠窗口
        self._tool_stack.addWidget(tool_widget)
        self._tools[tool_id] = tool_widget
        
        # 添加导航按钮
        self._nav_bar.add_tool(tool_id, name, icon, tooltip)
    
    def _on_tool_selected(self, tool_id: str):
        """工具被选中"""
        tool_widget = self._tools.get(tool_id)
        if tool_widget:
            self._tool_stack.setCurrentWidget(tool_widget)
    
    def _load_stylesheet(self):
        """加载样式表"""
        # 使用 resource_path 获取样式表路径
        qss_path = resource_path(os.path.join("ui", "styles", "smartisan.qss"))
        
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"加载样式表失败: {e} (路径: {qss_path})")
