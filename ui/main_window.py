# -*- coding: utf-8 -*-
"""
射频天线工具集 - 主窗口
RF Antenna Toolkit - Main Window

版本: v2.1.0
功能: 应用程序主窗口，包含导航栏和工具工作区
"""

import os
import shutil
import subprocess
import sys
import threading
from typing import Dict, Optional, Type

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget, QSizePolicy, QMessageBox, QFileDialog
)
from PyQt6.QtCore import QObject, Qt, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QDesktopServices, QFont

from core.app_metadata import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    APP_VERSION_LABEL,
    AUTHOR_SIGNATURE,
    COMPANY_NAME,
    COPYRIGHT_TEXT,
    DEVELOPER_SIGNATURE,
)
from core.update_checker import (
    ReleaseInfo,
    UpdateCheckResult,
    check_for_updates,
    download_release_asset,
)
from core.update_settings import UpdateSettings, load_update_settings, save_update_settings
from ui.help.update_settings_dialog import UpdateSettingsDialog
from ui.help.version_features_page import VersionFeaturesPage
from ui.widgets.nav_bar import NavBar
from ui.base.tool_base import ToolBase
from ui.tools.antenna.wavelength_tool import WavelengthTool
from ui.tools.antenna.bandwidth_tool import BandwidthTool
from ui.tools.antenna.gain_tool import GainTool
from ui.tools.antenna.los_tool import LOSTool
from ui.tools.antenna.sensitivity_tool import SensitivityTool
from ui.tools.antenna.phased_array_tool import PhasedArrayTool
from ui.tools.antenna.range_tool import RangeTool
from ui.tools.antenna.farfield_tool import FarFieldTool
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
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        return os.path.join(bundle_dir, relative_path)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)


class UpdateCheckSignals(QObject):
    """后台更新检查信号"""

    finished = pyqtSignal(object, bool, str)


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
        self._extra_pages: Dict[str, QWidget] = {}
        self._update_settings = load_update_settings()
        self._update_check_signals = UpdateCheckSignals(self)
        self._update_check_signals.finished.connect(self._handle_update_check_result)
        self._update_check_in_progress = False
        self._last_prompted_version: Optional[str] = None
        
        # 初始化界面
        self._setup_window()
        self._setup_ui()
        self._register_tools()
        self._register_extra_pages()
        self._load_stylesheet()
        QTimer.singleShot(1800, lambda: self._check_updates(silent=True))
    
    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 设置窗口居中
        screen = self.screen()
        handle = self.windowHandle()
        if screen is None and handle is not None:
            handle_screen = handle.screen()
            if handle_screen is not None:
                screen = handle_screen
        if screen is None:
            screen = QApplication.primaryScreen()

        if screen is not None:
            geometry = screen.geometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def _setup_ui(self):
        """构建界面"""
        self._setup_menu_bar()

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
        self._welcome_page = self._create_welcome_page()
        self._tool_stack.addWidget(self._welcome_page)
        
        body_layout.addWidget(work_area, 1)
        main_layout.addLayout(body_layout, 1)

        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.setSizeGripEnabled(False)

    def _setup_menu_bar(self):
        """创建顶部菜单栏"""
        menu_bar = self.menuBar()
        if menu_bar is None:
            return
        menu_bar.setNativeMenuBar(False)

        help_menu = menu_bar.addMenu("帮助")
        if help_menu is None:
            return

        calculator_action = QAction("🧮", self)
        calculator_action.setToolTip("打开系统计算器")
        calculator_action.setStatusTip("快速打开系统自带计算器")
        calculator_action.triggered.connect(self._open_system_calculator)
        menu_bar.addAction(calculator_action)

        version_action = QAction("版本功能", self)
        version_action.triggered.connect(self._show_version_features_page)
        help_menu.addAction(version_action)

        update_action = QAction("检查更新", self)
        update_action.triggered.connect(lambda: self._check_updates(silent=False))
        help_menu.addAction(update_action)

        update_settings_action = QAction("更新设置", self)
        update_settings_action.triggered.connect(self._show_update_settings_dialog)
        help_menu.addAction(update_settings_action)

        self._version_action = version_action
        self._update_action = update_action
        self._update_settings_action = update_settings_action
        self._calculator_action = calculator_action
    
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
        title = QLabel(f"🔧 {APP_NAME}")
        title.setObjectName("AppTitle")
        title_layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setObjectName("AppSubtitle")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # 右侧: 公司/开发者信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        company_label = QLabel(COMPANY_NAME)
        company_label.setStyleSheet("font-size: 12px; color: #718096; font-weight: 500;")
        company_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        info_layout.addWidget(company_label)
        
        dev_label = QLabel(DEVELOPER_SIGNATURE)
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
        title = QLabel(f"欢迎使用 {APP_NAME}")
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
        
        company_label = QLabel(f"🚀 研发公司: {COMPANY_NAME}")
        company_label.setStyleSheet("color: #718096; font-size: 14px;")
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        author_label = QLabel(f"{AUTHOR_SIGNATURE} | 版本: {APP_VERSION_LABEL}")
        author_label.setStyleSheet("color: #A0AEC0; font-size: 13px;")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        copyright_label = QLabel(COPYRIGHT_TEXT)
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

        # 远场距离计算
        self._register_tool(
            "farfield",
            FarFieldTool,
            "远场计算器",
            "🎯",
            "天线远场测试距离计算 (IEEE 149)"
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
            "标准矩形波导与双脊波导法兰实践速查"
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

    def _register_extra_pages(self):
        """注册非导航页面"""
        self._register_extra_page("version_features", VersionFeaturesPage())

    def _register_extra_page(self, page_id: str, page_widget: QWidget):
        """注册仅通过菜单访问的页面"""
        self._extra_pages[page_id] = page_widget
        self._tool_stack.addWidget(page_widget)
    
    def _register_tool(
        self,
        tool_id: str,
        tool_class: Type[QWidget],
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

    def _show_version_features_page(self):
        """显示版本功能页"""
        page = self._extra_pages.get("version_features")
        if page is None:
            return

        self._nav_bar.clear_selection()
        self._tool_stack.setCurrentWidget(page)

    def _open_system_calculator(self):
        """打开系统自带计算器"""
        commands = []

        if sys.platform.startswith("win"):
            commands.append(["calc.exe"])
        elif sys.platform == "darwin":
            commands.append(["open", "-a", "Calculator"])
        else:
            for program_name in (
                "gnome-calculator",
                "kcalc",
                "mate-calc",
                "galculator",
                "xcalc",
            ):
                if shutil.which(program_name):
                    commands.append([program_name])
                    break

        for command in commands:
            try:
                subprocess.Popen(command)
                status_bar = self.statusBar()
                if status_bar is not None:
                    status_bar.showMessage("系统计算器已打开", 2500)
                return
            except OSError:
                continue

        QMessageBox.warning(
            self,
            "打开计算器失败",
            "未找到可用的系统计算器程序，请确认系统已安装计算器。",
        )

    def _check_updates(self, silent: bool):
        """异步检查 GitHub Release 更新"""
        if self._update_check_in_progress:
            if not silent:
                status_bar = self.statusBar()
                if status_bar is not None:
                    status_bar.showMessage("更新检查正在进行中，请稍候...", 3000)
            return

        self._update_check_in_progress = True
        if not silent:
            status_bar = self.statusBar()
            if status_bar is not None:
                status_bar.showMessage("正在检查 GitHub Release 更新...", 3000)

        thread = threading.Thread(
            target=self._run_update_check,
            args=(silent, self._update_settings),
            daemon=True,
        )
        thread.start()

    def _run_update_check(self, silent: bool, settings: UpdateSettings):
        """后台执行更新检查"""
        try:
            result = check_for_updates(APP_VERSION, settings)
            self._update_check_signals.finished.emit(result, silent, "")
        except Exception as exc:
            self._update_check_signals.finished.emit(None, silent, str(exc))

    def _persist_update_settings(self, settings: UpdateSettings) -> bool:
        """保存更新设置并刷新内存状态"""
        clean_settings = settings.cleaned()
        try:
            save_update_settings(clean_settings)
        except OSError as exc:
            QMessageBox.warning(self, "保存更新设置失败", str(exc))
            return False

        self._update_settings = clean_settings
        return True

    def _show_update_settings_dialog(self):
        """打开更新设置对话框"""
        dialog = UpdateSettingsDialog(self._update_settings, self)
        if not dialog.exec():
            return

        new_settings = dialog.get_settings()
        if not self._persist_update_settings(new_settings):
            return

        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(
                f"更新设置已保存，当前仓库：{new_settings.repository_slug}",
                4000,
            )

    def _handle_update_check_result(
        self,
        result: Optional[UpdateCheckResult],
        silent: bool,
        error_message: str,
    ):
        """处理后台更新检查结果"""
        self._update_check_in_progress = False

        if error_message:
            if not silent:
                QMessageBox.warning(self, "检查更新失败", error_message)
            return

        if result is None:
            return

        if result.state == "update_available" and result.latest_release:
            if silent and self._last_prompted_version == result.latest_release.version:
                return

            self._last_prompted_version = result.latest_release.version
            self._show_update_available_dialog(result.latest_release)
            return

        if result.state == "ignored" and result.latest_release and not silent:
            self._show_ignored_version_dialog(result.latest_release)
            return

        if result.state == "no_matching_asset" and result.latest_release and not silent:
            self._show_no_matching_asset_dialog(result.latest_release, result.asset_patterns)
            return

        if result.state == "up_to_date" and not silent:
            QMessageBox.information(
                self,
                "检查更新",
                f"当前已是最新版本 {APP_VERSION_LABEL}。",
            )
            return

        if result.state == "no_release" and not silent:
            QMessageBox.information(
                self,
                "检查更新",
                "当前 GitHub 仓库尚未发布正式 Release，暂时无法自动获取下载地址。",
            )

    def _show_update_available_dialog(self, release: ReleaseInfo):
        """弹出发现新版本提示"""
        message_box = QMessageBox(self)
        message_box.setWindowTitle("发现新版本")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"检测到新版本 v{release.version}")
        message_box.setInformativeText(
            f"当前版本: {APP_VERSION_LABEL}\n"
            f"最新版本: {release.tag_name}\n"
            f"安装包: {release.asset_name}\n"
            f"发布时间: {release.published_at}\n"
            "可以直接保存安装包到本地，也可以打开 GitHub Release 页面。"
        )
        if release.body:
            message_box.setDetailedText(release.body)

        download_button = message_box.addButton("下载到本地", QMessageBox.ButtonRole.AcceptRole)
        release_page_button = message_box.addButton("打开发布页", QMessageBox.ButtonRole.ActionRole)
        ignore_button = message_box.addButton("忽略此版本", QMessageBox.ButtonRole.DestructiveRole)
        message_box.addButton("稍后", QMessageBox.ButtonRole.RejectRole)
        message_box.exec()

        clicked_button = message_box.clickedButton()
        if clicked_button is download_button:
            self._download_release_asset(release)
        elif clicked_button is release_page_button:
            QDesktopServices.openUrl(QUrl(release.html_url))
        elif clicked_button is ignore_button:
            if self._persist_update_settings(self._update_settings.with_updates(ignored_version=release.version)):
                status_bar = self.statusBar()
                if status_bar is not None:
                    status_bar.showMessage(f"已忽略版本 v{release.version}", 4000)

    def _show_ignored_version_dialog(self, release: ReleaseInfo):
        """提示最新版本已被忽略"""
        message_box = QMessageBox(self)
        message_box.setWindowTitle("检查更新")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"最新版本 v{release.version} 当前已被忽略")
        message_box.setInformativeText(
            "如果要恢复此版本提醒，可直接清除忽略设置后重新检查更新。"
        )
        clear_button = message_box.addButton("恢复此版本提醒", QMessageBox.ButtonRole.ActionRole)
        message_box.addButton("关闭", QMessageBox.ButtonRole.AcceptRole)
        message_box.exec()

        if message_box.clickedButton() is clear_button:
            if self._persist_update_settings(self._update_settings.with_updates(ignored_version="")):
                self._check_updates(silent=False)

    def _show_no_matching_asset_dialog(self, release: ReleaseInfo, asset_patterns: str):
        """提示发现新版本但没有匹配的安装包资产"""
        message_box = QMessageBox(self)
        message_box.setWindowTitle("检查更新")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"检测到新版本 {release.tag_name}，但没有命中安装包资产")
        if asset_patterns:
            message_box.setInformativeText(
                f"当前资产匹配规则：{asset_patterns}\n"
                "请确认 Release 资产命名是否符合规则，或在“更新设置”中调整匹配条件。"
            )
        else:
            message_box.setInformativeText("当前 Release 没有可下载的安装包资产。")
        if release.body:
            message_box.setDetailedText(release.body)

        settings_button = message_box.addButton("打开更新设置", QMessageBox.ButtonRole.ActionRole)
        release_page_button = message_box.addButton("打开发布页", QMessageBox.ButtonRole.ActionRole)
        message_box.addButton("关闭", QMessageBox.ButtonRole.AcceptRole)
        message_box.exec()

        clicked_button = message_box.clickedButton()
        if clicked_button is settings_button:
            self._show_update_settings_dialog()
        elif clicked_button is release_page_button:
            QDesktopServices.openUrl(QUrl(release.html_url))

    def _download_release_asset(self, release: ReleaseInfo):
        """下载更新安装包"""
        suggested_name = release.asset_name or f"{APP_NAME}-{release.version}"
        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存更新安装包",
            suggested_name,
            "所有文件 (*)",
        )
        if not selected_path:
            return

        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(f"正在下载 {release.asset_name} ...")

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            download_release_asset(release, self._update_settings, selected_path)
        except Exception as exc:
            QMessageBox.warning(self, "下载失败", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()

        if status_bar is not None:
            status_bar.showMessage(f"更新包已保存到 {selected_path}", 5000)

        QMessageBox.information(self, "下载完成", f"安装包已保存到：\n{selected_path}")
    
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
