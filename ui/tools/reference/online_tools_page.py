# -*- coding: utf-8 -*-
"""
精品在线工具推荐页面
汇集行业内顶级、无需翻墙的半导体原厂射频在路线工具，一键唤醒默认浏览器打开。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QCursor

class ToolCard(QFrame):
    """独立的工具展示卡片组件"""
    def __init__(self, title, company, desc, url, brand_color, parent=None):
        super().__init__(parent)
        self.url = url
        self.brand_color = brand_color
        
        # 卡片基础样式设置
        self.setObjectName("ToolCard")
        # 通过 QSS 实现卡片的圆角、背景、悬停效果等
        self.setStyleSheet(f"""
            #ToolCard {{
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }}
            #ToolCard:hover {{
                border: 1px solid {brand_color};
                background-color: #F8FAFC;
            }}
        """)
        
        # 卡片布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        # 顶部：原厂短名方块 + 工具名称
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # 类似 Logo 的色彩块
        logo_lbl = QLabel(company[:2].upper())
        logo_lbl.setFixedSize(32, 32)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet(f"""
            background-color: {brand_color}15; /* 15 是透明度 hex */
            color: {brand_color};
            font-weight: 900;
            font-size: 14px;
            font-family: Arial, sans-serif;
            border-radius: 6px;
        """)
        header_layout.addWidget(logo_lbl)
        
        # 标题组合
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        
        main_title = QLabel(title)
        main_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1A202C;")
        main_title.setWordWrap(True)
        title_box.addWidget(main_title)
        
        sub_title = QLabel(company)
        sub_title.setStyleSheet("font-size: 11px; color: #A0AEC0; font-weight: 500;")
        title_box.addWidget(sub_title)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #EDF2F7; max-height: 1px;")
        layout.addWidget(line)
        
        # 中间：工具说明描述
        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #4A5568; font-size: 13px; line-height: 1.4;")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        desc_lbl.setMinimumHeight(60) # 保持卡片高度一致
        layout.addWidget(desc_lbl)
        
        layout.addStretch()
        
        # 底部：跳转按钮
        btn = QPushButton("🚀 浏览器打开工具")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {brand_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {brand_color}E0; /* 悬浮稍暗 */
            }}
        """)
        btn.clicked.connect(self._open_url)
        layout.addWidget(btn)
        
    def _open_url(self):
        """调用系统默认浏览器打开链接"""
        QDesktopServices.openUrl(QUrl(self.url))

class OnlineToolsPage(QWidget):
    """在线精品工具推荐的主页面"""
    
    # 推荐工具数据大盘
    TOOLS_DATA = [
        {
            "brand": "Murata",
            "name": "SimSurfing 元件特性计算器",
            "desc": "全球顶级的被动元器件（电容、电感、滤波器、巴伦）S参数、阻抗曲线与频率响应一键在线出图查看系统。",
            "url": "https://ds.murata.com/simsurfing/index.html?lcid=zh-cn#_pt_link=https%3A%2F%2Fwww.murata.com.cn%2Fzh-cn%2Fproducts%2Fconnectivitymodule%3Fgad_source%3D1%26gad_campaignid%3D21768348886%26gbraid%3D0AAAAApU99OPdIg_HrQhJmtPnnXSHDTqnw%26gclid%3DCj0KCQiA8KTNBhD_ARIsAOvp6DJpUlEjWdp2QxJjwIljYrAfXRdHsjuWpKu1DbreG7E5lvLHdeCIxd8aAsHoEALw_wcB_s_62acf7fc.f59637b7-afa9-41a3-94f1-792e5357a63a.89786f7f-44ca-431c-8096-cd8a43a3ef0a.1.2.1..1772774308679",
            "color": "#E50020" # 村田红
        },
        {
            "brand": "ADI",
            "name": "Analog Filter Wizard",
            "desc": "强大的有源及无源滤波器在线合成工具。支持多拓扑（巴特沃斯、切比雪夫等）极点设计，自动选配运放并出具理想/真实响应图。",
            "url": "https://tools.analog.com/en/filterwizard/",
            "color": "#00A1E0" # ADI 蓝
        },
        {
            "brand": "ADI",
            "name": "ADIsimRF 信号链系统管家",
            "desc": "用于计算复杂射频微波信号链的级联增益、噪声系数 (NF)、1dB压缩点 (P1dB) 及 IP3 互调指标的核心在线神器。",
            "url": "https://www.analog.com/cn/design-center/adisimrf.html",
            "color": "#00A1E0"
        },
        {
            "brand": "TI",
            "name": "WEBENCH® Power Designer",
            "desc": "射频供电首选方案！输入系统的核心低噪供电需求，自动生成最佳电源拓扑（DC-DC/LDO）、原理图、BOM清单及稳态热仿真图。",
            "url": "https://webench.ti.com/power-designer/",
            "color": "#CC0000" # TI 红
        },
        {
            "brand": "Qorvo",
            "name": "MatchCalc 射频匹配计算",
            "desc": "偏向纯微波实战射频通道的轻量级匹配阻抗计算、微波级联评估平台（史密斯圆图辅助网络综合匹配设计）。",
            "url": "https://www.qorvo.com/design-hub/design-tools/matchcalc",
            "color": "#0E2B58" # Qorvo 藏青蓝
        }
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tool_id = "online_tools_hub"
        self.tool_name = "在线精品推荐"
        self.tool_icon = "🌐"
        
        self._setup_ui()
        
    def _setup_ui(self):
        # 类似 ToolBase，但我们自己写布局不需要分左右栏
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 滚动外壳
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # 页面标题头
        header = QLabel("🌐 精品在线实战工具推荐")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A202C;")
        layout.addWidget(header)
        
        sub_desc = QLabel("以下皆为精挑细选的 **全球半导体大厂官方无墙** 权威工具，点击卡片即可在本地浏览器安全快速打开：")
        sub_desc.setStyleSheet("color: #718096; font-size: 14px; margin-bottom: 10px;")
        sub_desc.setWordWrap(True)
        layout.addWidget(sub_desc)
        
        # 动态生成卡片网格布局
        grid = QGridLayout()
        grid.setSpacing(24) # 卡片间距更现代
        
        # 计算行与列 (一排2个或3个，这里我们固定一行排 2 个比较宽松适宜)
        cols = 2
        for i, t_data in enumerate(self.TOOLS_DATA):
            r = i // cols
            c = i % cols
            
            card = ToolCard(
                title=t_data["name"],
                company=t_data["brand"],
                desc=t_data["desc"],
                url=t_data["url"],
                brand_color=t_data["color"]
            )
            grid.addWidget(card, r, c)
            
        layout.addLayout(grid)
        
        # 免责声明底部占位
        layout.addStretch()
        footer = QLabel("免责声明：以上推荐平台各项权利均属于其原开发公司及半导体厂商。本页面仅提供便捷外链访问。")
        footer.setStyleSheet("color: #CBD5E0; font-size: 12px; margin-top: 40px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
