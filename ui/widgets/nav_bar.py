# -*- coding: utf-8 -*-
"""
射频天线工具集 - 导航栏组件
RF Antenna Toolkit - Navigation Bar Widget

版本: v1.0.0
功能: 左侧工具导航栏，支持分类显示和工具切换
"""

from typing import Dict, List, Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QFrame, QButtonGroup,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont


class NavBar(QWidget):
    """
    导航栏组件
    
    显示工具分类和工具列表，支持:
    - 分类标题
    - 工具按钮 (可选中状态)
    - 点击切换工具
    """
    
    # 信号: 工具被选中 (tool_id)
    tool_selected = pyqtSignal(str)
    
    def _create_emoji_icon(self, emoji: str, size: int = 24) -> QIcon:
        """
        将 Emoji 绘制为图标，确保宽度一致
        """
        if not emoji:
            return QIcon()
            
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # 调整字体大小
        font = painter.font()
        font.setPixelSize(int(size * 0.75)) # 略微缩小以适应
        # font.setFamily("Segoe UI Emoji") # 可选：指定 Emoji 字体
        painter.setFont(font)
        
        # 居中绘制
        rect = pixmap.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        
        return QIcon(pixmap)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化导航栏"""
        super().__init__(parent)
        
        self.setObjectName("NavBar")
        
        # 存储工具按钮
        self._tool_buttons: Dict[str, QPushButton] = {}
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        
        # 构建界面
        self._setup_ui()
    
    def _setup_ui(self):
        """构建导航栏界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 滚动内容
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 8, 0, 8)
        self._content_layout.setSpacing(0)
        self._content_layout.addStretch()
        
        scroll_area.setWidget(self._content)
        main_layout.addWidget(scroll_area)
    
    def add_category(self, title: str, icon: str = ""):
        """
        添加分类标题
        
        参数:
            title: 分类标题
            icon: 图标 (emoji)
        """
        # 如果不是第一个分类，添加分隔线
        if self._content_layout.count() > 1:
            separator = QFrame()
            separator.setObjectName("NavSeparator")
            separator.setFrameShape(QFrame.Shape.HLine)
            self._content_layout.insertWidget(
                self._content_layout.count() - 1,
                separator
            )
        
        # 分类标题
        category_label = QLabel(f"{icon} {title}" if icon else title)
        category_label.setObjectName("CategoryTitle")
        self._content_layout.insertWidget(
            self._content_layout.count() - 1,
            category_label
        )
    
    def add_tool(
        self,
        tool_id: str,
        name: str,
        icon: str = "",
        tooltip: str = ""
    ):
        """
        添加工具按钮
        
        参数:
            tool_id: 工具唯一标识
            name: 工具名称
            icon: 图标 (emoji)
            tooltip: 提示文字
        """
        # 创建按钮
        button = QPushButton(name)
        
        # 设置图标 (使用 Emoji 生成固定宽度的图标)
        if icon:
            icon_obj = self._create_emoji_icon(icon)
            button.setIcon(icon_obj)
            button.setIconSize(QSize(20, 20))
        button.setObjectName("ToolButton")
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if tooltip:
            button.setToolTip(tooltip)
        
        # 点击事件
        button.clicked.connect(lambda checked, tid=tool_id: self._on_tool_clicked(tid))
        
        # 添加到按钮组
        self._button_group.addButton(button)
        self._tool_buttons[tool_id] = button
        
        # 添加到布局
        self._content_layout.insertWidget(
            self._content_layout.count() - 1,
            button
        )
    
    def _on_tool_clicked(self, tool_id: str):
        """工具按钮点击事件"""
        self.tool_selected.emit(tool_id)
    
    def select_tool(self, tool_id: str):
        """
        选中指定工具
        
        参数:
            tool_id: 工具标识
        """
        button = self._tool_buttons.get(tool_id)
        if button:
            button.setChecked(True)
    
    def get_selected_tool(self) -> Optional[str]:
        """
        获取当前选中的工具ID
        
        返回:
            工具ID，如果没有选中则返回None
        """
        for tool_id, button in self._tool_buttons.items():
            if button.isChecked():
                return tool_id
        return None

    def clear_selection(self):
        """清除当前工具选中状态，用于显示菜单页等非导航页面"""
        self._button_group.setExclusive(False)
        for button in self._tool_buttons.values():
            button.setChecked(False)
        self._button_group.setExclusive(True)
