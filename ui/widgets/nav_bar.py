# -*- coding: utf-8 -*-
"""
射频天线工具集 - 导航栏组件
RF Antenna Toolkit - Navigation Bar Widget

版本: v2.0.0
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

from core.i18n import translator, tr


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
        
        # 用于承载国际化记忆 (id/key, widget, args...) 
        self._i18n_categories = []
        self._i18n_tools = []
        
        # 构建界面
        self._setup_ui()
        
        translator.language_changed.connect(self.retranslate_ui)
    
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
    
    def add_category(self, title: str, icon: str = "", i18n_key: str = ""):
        """
        添加分类标题
        
        参数:
            title: 分类标题默认文字
            icon: 图标 (emoji)
            i18n_key: 国际化词典key (如 "nav.menu_antenna")
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
        final_title = tr(i18n_key, title) if i18n_key else title
        category_label = QLabel(f"{icon} {final_title}" if icon else final_title)
        category_label.setObjectName("CategoryTitle")
        self._content_layout.insertWidget(
            self._content_layout.count() - 1,
            category_label
        )
        
        # 缓存供切换语言时使用
        self._i18n_categories.append((category_label, icon, i18n_key, title))
    
    def add_tool(
        self,
        tool_id: str,
        name: str,
        icon: str = "",
        tooltip: str = "",
        i18n_key: str = ""
    ):
        """
        添加工具按钮
        
        参数:
            tool_id: 工具唯一标识
            name: 工具名称默认值
            icon: 图标 (emoji)
            tooltip: 提示文字
            i18n_key: 国际化词条名称 key
        """
        # 创建按钮
        final_name = tr(i18n_key, name) if i18n_key else name
        button = QPushButton(final_name)
        
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
        
        # 添加到布局
        self._content_layout.insertWidget(
            self._content_layout.count() - 1,
            button
        )
        
        # 缓存数据
        self._tool_buttons[tool_id] = button
        self._i18n_tools.append((button, icon, i18n_key, name, tooltip))
        
    def retranslate_ui(self, lang: str):
        """重新拉取所有已注册导航栏文字的翻译"""
        for label, icon, i18n_key, default_title in self._i18n_categories:
            if i18n_key:
                new_text = tr(i18n_key, default_title)
                label.setText(f"{icon} {new_text}" if icon else new_text)
                
        for btn, icon, i18n_key, default_name, tooltip in self._i18n_tools:
            if i18n_key:
                btn.setText(tr(i18n_key, default_name))
    
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
