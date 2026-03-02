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

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


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
    
    # 设置默认字体
    default_font = QFont("Microsoft YaHei UI", 10)
    app.setFont(default_font)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
