"""发行包的非交互安装验收，版本 2.3。

通过实际安装的程序验证资源、导航、计算和绘图；不发送桌面输入，
不打开可见窗口、不联网，也不修改用户的参数配置。
"""

import json
import math
import platform
import sys
import traceback
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from core.app_metadata import APP_VERSION
from ui.main_window import MainWindow, resource_path


def verify_installation(app, report_path: str) -> int:
    """返回进程退出码并写入机器可读验收报告，失败时保留明确的错误证据。"""
    report = {"version": APP_VERSION, "frozen": bool(getattr(sys, "frozen", False)),
              "platform": platform.platform(), "checks": [], "success": False}
    window = None

    def check(condition: bool, description: str) -> None:
        """不用可被优化移除的断言，任何失败都使验收返回非零退出码。"""
        report["checks"].append({"name": description, "passed": bool(condition)})
        if not condition:
            raise RuntimeError(description)

    try:
        for asset in ("assets/app.ico", "assets/splash.png", "resources/icons/amplifier.svg",
                      "ui/styles/smartisan.qss"):
            check(Path(resource_path(asset)).is_file(), f"资源存在：{asset}")
        check(not QPixmap(resource_path("assets/splash.png")).isNull(), "启动图能够解码")
        check(not QIcon(resource_path("resources/icons/amplifier.svg")).pixmap(32, 32).isNull(),
              "矢量图标能够渲染")

        window = MainWindow()
        # 覆盖尚未执行的自动更新回调，使验收完全独立于网络状态。
        window._check_updates = lambda *args, **kwargs: None
        window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        window.show()
        app.processEvents()
        check("QGroupBox" in window.styleSheet(), "应用主题样式已加载")
        window._nav_bar.select_tool("fh_capture")
        window._on_tool_selected("fh_capture")
        tool = window._tools["fh_capture"]
        check(window._tool_stack.currentWidget() is tool, "导航可进入跳频测向捕获评估")
        result = tool._last_result
        check(result.group_count == 8 and result.switch_count == 8
              and math.isclose(result.scan_s, 44e-6), "默认九元双通道扫描时间为44微秒")
        tool.first_state.setCurrentIndex(1)
        check(math.isclose(tool._last_result.scan_s, 43.5e-6), "首组已就绪时为43.5微秒")
        tool.first_state.setCurrentIndex(0)
        tool.hop_rate.edit.setText("25000")
        check(tool._last_result.status == "insufficient"
              and math.isclose(tool._last_result.actual_margin_s, -4e-6), "25000跳每秒正确报告缺少4微秒")
        tool._draw_current_plot()
        check(bool(tool.figures[0].axes[0].patches), "超时时间轴能够渲染")
        tool.tabs.setCurrentIndex(1)
        check(tool.figures[1].axes[0].get_xscale() == "log", "跳速余量曲线能够渲染")
        tool.acquisition_mode.setCurrentIndex(1)
        check(math.isclose(tool._last_result.params.acquisition_s, 5e-6), "采样点数与采样率换算正常")
        tool.acquisition_mode.setCurrentIndex(0)
        tool.acquisition_time.edit.setText("invalid")
        check(tool._last_result is None and tool.table.rowCount() == 0
              and all(not figure.axes for figure in tool.figures), "无效输入清除旧结果与图表")
        window._show_version_features_page()
        check(window._tool_stack.currentWidget() is window._extra_pages["version_features"],
              "版本功能页面可打开")
        window._on_tool_selected("waveguide_table")
        check(window._tool_stack.currentWidget() is window._tools["waveguide_table"], "波导法兰参考工具可打开")
        report["success"] = True
    except Exception:
        report["error"] = traceback.format_exc()
    finally:
        if window is not None:
            tool = window._tools.get("fh_capture")
            if tool is not None:
                tool._plot_timer.stop()
            window.close()
            window.deleteLater()
            app.processEvents()
        target = Path(report_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if report["success"] else 1
