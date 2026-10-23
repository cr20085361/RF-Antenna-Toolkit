# -*- coding: utf-8 -*-
"""
射频天线工具集 - 主程序入口
RF Antenna Toolkit - Main Entry Point

版本: v2.2
作者: 射频天线工具集开发团队
功能: 应用程序启动入口

使用方法:
    python main.py
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

from core.app_metadata import APP_NAME, APP_VERSION
from ui.main_window import MainWindow
from ui.widgets.wheel_filter import GlobalWheelEventFilter

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境 """
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        return os.path.join(bundle_dir, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


def build_default_font(point_size: int = 10) -> QFont:
    """选择当前系统可用的默认界面字体"""
    for family in ("Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", "Arial"):
        font = QFont(family, point_size)
        if font.exactMatch():
            return font

    font = QFont()
    font.setPointSize(point_size)
    return font


def main():
    """主函数"""
    # 高DPI支持
    # Qt6默认启用高DPI缩放
    
    # 创建应用程序
    app = QApplication(sys.argv)

    # 全局禁用输入控件滚轮误触修改数值
    wheel_filter = GlobalWheelEventFilter(app)
    app.installEventFilter(wheel_filter)
    
    # 设置应用程序属性
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("RF Antenna Toolkit")
    
    # 设置应用全局图标 (任务栏和窗口角落图标)
    app_icon_path = resource_path(os.path.join("assets", "app.ico"))
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))
    
    # 设置默认字体
    default_font = build_default_font(10)
    app.setFont(default_font)

    # 安装验收模式在隐藏窗口中验证真正发行包，不依赖项目源码或外部解释器。
    if "--verify-installation" in sys.argv:
        import argparse
        from ui.help.installation_check import verify_installation
        parser = argparse.ArgumentParser(description="验证离线安装后的资源与核心功能")
        parser.add_argument("--verify-installation", required=True, metavar="REPORT_JSON")
        arguments = parser.parse_args()
        sys.exit(verify_installation(app, arguments.verify_installation))
    
    # ---------------- 启动画面 (Splash Screen) ----------------
    splash_pixmap_path = resource_path(os.path.join("assets", "splash.png"))
    splash = None
    if os.path.exists(splash_pixmap_path):
        pixmap = QPixmap(splash_pixmap_path)
        splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        splash.show()
        splash.showMessage("正在加载核心组件...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
        app.processEvents() # 确保画面被渲染
        
        # 强制展示一小段时间，彰显专业软件的启动感 (实际生产中这里是加载模型和数据的耗时)
        time.sleep(1.0) 
        splash.showMessage("初始化计算引擎...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
        app.processEvents()
        time.sleep(0.5)

    # 创建主窗口
    window = MainWindow()
    
    if splash:
        splash.finish(window) # 当主窗口就绪后关闭闪屏
    
    window.show()
    
    # 运行事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
