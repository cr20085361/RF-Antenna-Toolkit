# -*- coding: utf-8 -*-
"""
射频天线工具集 - 主程序入口
RF Antenna Toolkit - Main Entry Point

版本: v1.0.0
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

from ui.main_window import MainWindow

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def main():
    """主函数"""
    # 高DPI支持
    # Qt6默认启用高DPI缩放
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("射频天线工具集")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RF Antenna Toolkit")
    
    # 设置应用全局图标 (任务栏和窗口角落图标)
    app_icon_path = resource_path(os.path.join("assets", "app.ico"))
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))
    
    # 设置默认字体
    default_font = QFont("Microsoft YaHei UI", 10)
    app.setFont(default_font)
    
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
