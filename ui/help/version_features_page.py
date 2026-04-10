# -*- coding: utf-8 -*-
"""
版本功能页面
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from core.app_metadata import (
    APP_NAME,
    APP_VERSION_LABEL,
    CURRENT_VERSION_FEATURES,
    GITHUB_RELEASES_URL,
    VERSION_FEATURES,
    VersionFeatureEntry,
)


class VersionFeaturesPage(QWidget):
    """展示当前版本与历史版本功能说明"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("VersionFeaturesPage")
        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        content_layout.addWidget(self._create_hero_card())

        for entry in VERSION_FEATURES:
            content_layout.addWidget(self._create_version_card(entry))

        content_layout.addStretch()

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area)

    def _create_hero_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("InfoHeroCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(10)

        title = QLabel("版本功能")
        title.setObjectName("InfoPageTitle")
        layout.addWidget(title)

        subtitle = QLabel(
            f"当前应用 {APP_NAME}，运行版本 {APP_VERSION_LABEL}。"
            f"本页汇总当前版本重点能力、关键模块变更以及发布节奏。"
        )
        subtitle.setObjectName("InfoPageSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        current = QLabel(
            f"当前主版本主题：{CURRENT_VERSION_FEATURES.title}<br>"
            f"更新来源：GitHub Releases，发布页：<a href=\"{GITHUB_RELEASES_URL}\">{GITHUB_RELEASES_URL}</a>"
        )
        current.setObjectName("InfoCardBody")
        current.setWordWrap(True)
        current.setOpenExternalLinks(True)
        current.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(current)

        return card

    def _create_version_card(self, entry: VersionFeatureEntry) -> QFrame:
        card = QFrame()
        card.setObjectName("InfoCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)

        meta = QLabel(f"v{entry.version} | {entry.release_date}")
        meta.setObjectName("InfoCardMeta")
        layout.addWidget(meta)

        title = QLabel(entry.title)
        title.setObjectName("InfoCardTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_text_block("本版亮点", entry.highlights))
        layout.addWidget(self._build_text_block("覆盖模块", entry.modules))
        layout.addWidget(self._build_text_block("工程备注", entry.notes))

        return card

    def _build_text_block(self, heading: str, lines: list[str]) -> QLabel:
        label = QLabel(
            f"<b>{heading}</b><br>" + "<br>".join(f"• {line}" for line in lines)
        )
        label.setObjectName("InfoCardBody")
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        return label