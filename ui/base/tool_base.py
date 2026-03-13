# -*- coding: utf-8 -*-
"""
射频天线工具集 - 工具基类
RF Antenna Toolkit - Tool Base Class

版本: v1.0.0
功能: 定义所有工具的基类，提供标准接口便于扩展
"""

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.i18n import translator, tr


class ToolBase(QWidget):
    """
    工具基类
    
    所有工具都应继承此类，并实现以下方法:
    - create_input_panel(): 创建输入面板 (必须实现)
    - create_result_panel(): 创建结果面板 (必须实现)
    - calculate(): 执行计算 (必须实现)
    
    可选重写:
    - create_theory_panel(): 创建原理说明面板
    - create_visualization(): 创建可视化图表
    """
    
    # 信号: 计算完成
    calculation_completed = pyqtSignal(dict)
    
    # ==================== 工具元信息 (子类需重写) ====================
    tool_name: str = "基础工具"              # 工具名称
    tool_icon: str = "📊"                    # 工具图标 (emoji或图片路径)
    tool_category: str = "other"             # 分类: antenna / rf
    tool_description: str = "工具描述"        # 简短描述
    
    # 国际化支持
    i18n_title_key: str = ""
    i18n_desc_key: str = ""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化工具基类"""
        super().__init__(parent)
        
        # 存储计算结果
        self._result: Dict[str, Any] = {}
        
        # 构建界面
        self._setup_ui()
        
        # 注册国际化回调
        translator.language_changed.connect(self.retranslate_ui)
    
    def _setup_ui(self):
        """构建工具界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 滚动区域内容
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(24, 24, 24, 24)
        scroll_layout.setSpacing(20)
        
        # 工具标题
        title_text = tr(self.i18n_title_key, self.tool_name) if self.i18n_title_key else self.tool_name
        self._title_label = QLabel(f"{self.tool_icon} {title_text}")
        self._title_label.setObjectName("ToolCardTitle")
        scroll_layout.addWidget(self._title_label)
        
        # 工具描述
        desc_text = tr(self.i18n_desc_key, self.tool_description) if self.i18n_desc_key else self.tool_description
        self._desc_label = QLabel(desc_text)
        self._desc_label.setObjectName("ResultDescription")
        self._desc_label.setWordWrap(True)
        scroll_layout.addWidget(self._desc_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #E2E8F0; max-height: 1px;")
        scroll_layout.addWidget(separator)
        
        # 主工作区 (水平布局: 左侧输入 + 右侧结果)
        work_layout = QHBoxLayout()
        work_layout.setSpacing(24)
        
        # 左侧: 输入面板
        input_panel = self.create_input_panel()
        if input_panel:
            input_panel.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Preferred
            )
            work_layout.addWidget(input_panel, 1)
        
        # 右侧: 结果面板
        result_panel = self.create_result_panel()
        if result_panel:
            result_panel.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred
            )
            work_layout.addWidget(result_panel, 2)
        
        scroll_layout.addLayout(work_layout)
        
        # 可视化区域 (可选)
        visualization = self.create_visualization()
        if visualization:
            scroll_layout.addWidget(visualization)
        
        # 知识科普区 - 四维度板块
        knowledge_section = self.create_knowledge_section()
        if knowledge_section:
            scroll_layout.addWidget(knowledge_section)
        
        # 弹性空间
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    # ==================== 基础方法 (子类应重写) ====================
    
    def create_input_panel(self) -> QWidget:
        """
        创建输入面板 (子类必须重写)
        
        返回:
            包含输入控件的QWidget
        """
        raise NotImplementedError("子类必须实现 create_input_panel 方法")
    
    def create_result_panel(self) -> QWidget:
        """
        创建结果显示面板 (子类必须重写)
        
        返回:
            包含结果显示的QWidget
        """
        raise NotImplementedError("子类必须实现 create_result_panel 方法")
    
    def calculate(self) -> Dict[str, Any]:
        """
        执行计算 (子类必须重写)
        
        返回:
            计算结果字典
        """
        raise NotImplementedError("子类必须实现 calculate 方法")
    
    def retranslate_ui(self, lang: str = ""):
        """
        语言切换时刷新 UI 文本 (基类默认实现)
        
        子类可重写以刷新各自特有的控件文字。
        重写时请先调用 super().retranslate_ui(lang)。
        """
        # 刷新工具标题
        if hasattr(self, '_title_label'):
            title_text = tr(self.i18n_title_key, self.tool_name) if self.i18n_title_key else self.tool_name
            self._title_label.setText(f"{self.tool_icon} {title_text}")
        
        # 刷新工具描述
        if hasattr(self, '_desc_label'):
            desc_text = tr(self.i18n_desc_key, self.tool_description) if self.i18n_desc_key else self.tool_description
            self._desc_label.setText(desc_text)
        
        # 刷新知识面板内容
        if hasattr(self, '_knowledge_tabs'):
            content_getters = [
                ('intuition', self.get_intuition_content),
                ('math', self.get_math_model_content),
                ('engineering', self.get_engineering_content),
                ('history', self.get_history_content),
            ]
            tab_labels = {
                'intuition': tr("toolbase.intuition_title"),
                'math': tr("toolbase.math_title"),
                'engineering': tr("toolbase.engineering_title"),
                'history': tr("toolbase.history_title"),
            }
            for i, (key, getter) in enumerate(content_getters):
                content = getter()
                if content and i < self._knowledge_tabs.count():
                    # 更新 tab 标题
                    self._knowledge_tabs.setTabText(i, tab_labels.get(key, key))
                    # 更新 tab 内容
                    widget = self._knowledge_tabs.widget(i)
                    if widget:
                        lbl = widget.findChild(QLabel)
                        if lbl:
                            lbl.setText(content)
    
    # ==================== 知识科普方法 (子类可重写) ====================
    
    def create_knowledge_section(self) -> Optional[QWidget]:
        """
        创建知识科普区 - 四维度板块
        
        子类应重写以下方法提供内容:
        - get_intuition_content(): 直观理解
        - get_math_model_content(): 数学模型
        - get_engineering_content(): 工程边界
        - get_history_content(): 发现历史 (可选)
        
        返回:
            包含四维度知识板块的QWidget
        """
        # 获取各板块内容
        intuition = self.get_intuition_content()
        math_model = self.get_math_model_content()
        engineering = self.get_engineering_content()
        history = self.get_history_content()
        
        # 如果所有内容都为空，不创建知识区
        if not any([intuition, math_model, engineering, history]):
            return None
        
        # 存储知识面板的标签引用用于热翻译刷新
        self._knowledge_labels = {}
        
        # 创建知识容器
        container = QWidget()
        container.setObjectName("KnowledgeContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 区域标题
        self._knowledge_section_title = QLabel(tr("toolbase.knowledge_title", "📚 深入理解"))
        self._knowledge_section_title.setObjectName("KnowledgeSectionTitle")
        layout.addWidget(self._knowledge_section_title)
        
        # 1. 直观理解板块
        if intuition is not None:
            intuition_panel = self._create_knowledge_panel(
                panel_id="IntuitionPanel",
                icon="🎯",
                title=tr("toolbase.intuition_title", "直观理解 · 物理本质"),
                content=intuition,
                key="intuition"
            )
            layout.addWidget(intuition_panel)
        
        # 2. 数学模型板块
        if math_model is not None:
            math_panel = self._create_knowledge_panel(
                panel_id="MathModelPanel",
                icon="📐",
                title=tr("toolbase.math_title", "数学模型 · 精确计算"),
                content=math_model,
                key="math_model"
            )
            layout.addWidget(math_panel)
        
        # 3. 工程边界板块
        if engineering is not None:
            eng_panel = self._create_knowledge_panel(
                panel_id="EngineeringPanel",
                icon="⚙️",
                title=tr("toolbase.engineering_title", "工程边界 · 适用范围与避坑"),
                content=engineering,
                key="engineering"
            )
            layout.addWidget(eng_panel)
        
        # 4. 发现历史板块 (可选)
        if history is not None:
            history_panel = self._create_knowledge_panel(
                panel_id="HistoryPanel",
                icon="📜",
                title=tr("toolbase.history_title", "发现历史 · 趣味故事"),
                content=history,
                key="history"
            )
            layout.addWidget(history_panel)
        
        return container
    
    def _create_knowledge_panel(
        self, 
        panel_id: str, 
        icon: str, 
        title: str, 
        content: str,
        key: str = ""
    ) -> QWidget:
        """创建单个知识板块"""
        panel = QWidget()
        panel.setObjectName(panel_id)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        
        # 标题行
        title_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setObjectName("KnowledgeIcon")
        title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setObjectName("KnowledgeTitle")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 内容
        content_label = QLabel(content)
        content_label.setObjectName("KnowledgeContent")
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(content_label)
        
        if key:
            self._knowledge_labels[key] = {
                'title': title_label,
                'content': content_label
            }
            
        return panel
    
    # ==================== 知识内容方法 (子类重写以提供内容) ====================
    
    def get_intuition_content(self) -> Optional[str]:
        """
        获取直观理解内容 - 图解+物理本质
        
        返回:
            HTML格式的内容字符串，返回None则不显示此板块
        """
        return None
    
    def get_math_model_content(self) -> Optional[str]:
        """
        获取数学计算模型内容 - 准确的物理公式
        
        返回:
            HTML格式的内容字符串，返回None则不显示此板块
        """
        return None
    
    def get_engineering_content(self) -> Optional[str]:
        """
        获取工程边界内容 - 适用范围+常见错误避坑
        
        返回:
            HTML格式的内容字符串，返回None则不显示此板块
        """
        return None
    
    def get_history_content(self) -> Optional[str]:
        """
        获取发现历史内容 - 趣味性内容 (可选)
        
        返回:
            HTML格式的内容字符串，返回None则不显示此板块
        """
        return None
    
    def create_visualization(self) -> Optional[QWidget]:
        """创建可视化图表 (子类可重写)"""
        return None

    def retranslate_ui(self, lang: str):
        """
        重新翻译 UI (国际化刷新接口)
        子类重写此时须先调用 super().retranslate_ui(lang)
        以确保标题、描述文字得到更新。
        """
        if self.i18n_title_key:
            self._title_label.setText(f"{self.tool_icon} {tr(self.i18n_title_key, self.tool_name)}")
        if self.i18n_desc_key:
            self._desc_label.setText(tr(self.i18n_desc_key, self.tool_description))
            
        # 刷新知识面板的内容
        if hasattr(self, '_knowledge_section_title'):
            self._knowledge_section_title.setText(tr("toolbase.knowledge_title", "📚 深入理解"))
            
        if hasattr(self, '_knowledge_labels'):
            if 'intuition' in self._knowledge_labels:
                self._knowledge_labels['intuition']['title'].setText(tr("toolbase.intuition_title", "直观理解 · 物理本质"))
                content = self.get_intuition_content()
                if content: self._knowledge_labels['intuition']['content'].setText(content)
                
            if 'math_model' in self._knowledge_labels:
                self._knowledge_labels['math_model']['title'].setText(tr("toolbase.math_title", "数学模型 · 精确计算"))
                content = self.get_math_model_content()
                if content: self._knowledge_labels['math_model']['content'].setText(content)
                
            if 'engineering' in self._knowledge_labels:
                self._knowledge_labels['engineering']['title'].setText(tr("toolbase.engineering_title", "工程边界 · 适用范围与避坑"))
                content = self.get_engineering_content()
                if content: self._knowledge_labels['engineering']['content'].setText(content)
                
            if 'history' in self._knowledge_labels:
                self._knowledge_labels['history']['title'].setText(tr("toolbase.history_title", "发现历史 · 趣味故事"))
                content = self.get_history_content()
                if content: self._knowledge_labels['history']['content'].setText(content)
    
    def update_result(self, result: Dict[str, Any]):
        """
        更新结果显示
        
        参数:
            result: 计算结果字典
        """
        self._result = result
        self.calculation_completed.emit(result)
    
    # ==================== 辅助方法 ====================
    
    def create_labeled_input(
        self,
        label_text: str,
        input_widget: QWidget,
        unit_text: str = ""
    ) -> QWidget:
        """
        创建带标签的输入控件
        
        参数:
            label_text: 标签文字
            input_widget: 输入控件
            unit_text: 单位文字 (可选)
        
        返回:
            组合后的QWidget
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(6)
        
        # 标签
        label = QLabel(label_text)
        label.setObjectName("InputLabel")
        layout.addWidget(label)
        
        # 输入行 (输入框 + 单位)
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        input_row.addWidget(input_widget)
        
        if unit_text:
            unit_label = QLabel(unit_text)
            unit_label.setObjectName("UnitLabel")
            input_row.addWidget(unit_label)
        
        input_row.addStretch()
        layout.addLayout(input_row)
        
        return container
    
    def create_result_item(
        self,
        title: str,
        value: str,
        unit: str = "",
        description: str = ""
    ) -> QWidget:
        """
        创建结果显示项
        
        参数:
            title: 结果标题
            value: 结果值
            unit: 单位
            description: 描述说明
        
        返回:
            结果显示QWidget
        """
        container = QWidget()
        container.setObjectName("ResultPanel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("ResultTitle")
        layout.addWidget(title_label)
        
        # 值和单位
        value_row = QHBoxLayout()
        value_row.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setObjectName("ResultValue")
        value_row.addWidget(value_label)
        
        if unit:
            unit_label = QLabel(unit)
            unit_label.setObjectName("ResultUnit")
            value_row.addWidget(unit_label)
        
        value_row.addStretch()
        layout.addLayout(value_row)
        
        # 描述
        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("ResultDescription")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        return container
    
    def create_theory_section(self, title: str, content: str) -> QWidget:
        """
        创建原理说明区块
        
        参数:
            title: 标题
            content: 内容
        
        返回:
            原理说明QWidget
        """
        container = QWidget()
        container.setObjectName("TheoryPanel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel(f"💡 {title}")
        title_label.setObjectName("TheoryTitle")
        layout.addWidget(title_label)
        
        # 内容
        content_label = QLabel(content)
        content_label.setObjectName("TheoryContent")
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        return container
        
    def get_asset_path(self, relative_path: str) -> str:
        """
        获取资源文件的绝对路径 (兼容 PyInstaller 运行环境)
        
        参数:
            relative_path: 相对于项目根目录的路径，例如 "assets/diagrams/coaxial.png"
        返回:
            绝对路径字符串
        """
        import os
        import sys
        
        # 1. 如果在 PyInstaller --onedir/--onefile 下运行
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        # 2. 如果是从源码运行
        else:
            # 当前文件位于 ui/base/tool_base.py，向上三层到达项目根目录
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        # 统一路径分隔符
        # 将传入的 forward slashes 转为当前系统的分隔符
        relative_path = os.path.normpath(relative_path)
            
        return os.path.join(base_path, relative_path)
