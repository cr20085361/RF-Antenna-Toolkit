# -*- coding: utf-8 -*-
"""
全局滚轮事件过滤器 (Global Wheel Event Filter)
功能:
- 全局禁用数值输入控件 (QSpinBox, QDoubleSpinBox, QComboBox, QSlider 等) 通过鼠标滚轮直接调整数值，避免用户在滚动页面时误触导致参数被篡改。
- 保证 QScrollArea 等父级滚动容器可以顺畅接收滚轮事件并正常滚动视口。
- 放行 QScrollBar 本身以及 QComboBox 弹出下拉列表内部的正常滚动。
"""

from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractSpinBox,
    QComboBox,
    QSlider,
    QScrollBar,
    QScrollArea
)


class GlobalWheelEventFilter(QObject):
    """
    全局滚轮事件过滤器
    """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel:
            # 1. 滚动条自身必须完全放行
            if isinstance(obj, QScrollBar):
                return False

            # 2. 匹配目标控件（支持自身或作为 SpinBox 等复合控件内部的直接子部件）
            matched_widget = None
            if isinstance(obj, (QAbstractSpinBox, QComboBox, QSlider)):
                matched_widget = obj
            elif obj.parent() and isinstance(obj.parent(), (QAbstractSpinBox, QComboBox, QSlider)):
                matched_widget = obj.parent()

            if matched_widget is not None and not isinstance(matched_widget, QScrollBar):
                # 如果是 QComboBox 且下拉列表当前正处于展开可见状态，放行以便用户在下拉列表中滚动浏览
                if isinstance(matched_widget, QComboBox):
                    view = matched_widget.view()
                    if view and view.isVisible():
                        return False

                # 忽略控件自身的数值变更处理
                event.ignore()

                # 寻找祖先中的 QScrollArea 并将滚轮事件透传给其 viewport，保证页面视口顺滑滚动
                parent_widget = matched_widget.parent()
                while parent_widget is not None:
                    if isinstance(parent_widget, QScrollArea):
                        QApplication.sendEvent(parent_widget.viewport(), event)
                        break
                    parent_widget = parent_widget.parent()

                # 返回 True 拦截事件派发给当前数值控件
                return True

        return super().eventFilter(obj, event)
