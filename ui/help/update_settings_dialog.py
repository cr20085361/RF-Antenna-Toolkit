# -*- coding: utf-8 -*-
"""
更新设置对话框
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.update_settings import UpdateSettings, get_update_settings_path


class UpdateSettingsDialog(QDialog):
    """配置 GitHub 更新检查参数"""

    def __init__(self, settings: UpdateSettings, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("更新设置")
        self.setMinimumWidth(620)
        self._initial_settings = settings.cleaned()
        self._setup_ui()
        self._load_settings(self._initial_settings)

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(14)

        intro = QLabel(
            "用于配置 GitHub Release 更新源。私有仓库请填写具备仓库读取权限的令牌；"
            "资产名规则支持通配符或关键字，多个规则可用换行、分号或逗号分隔。"
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #4A5568; line-height: 1.7;")
        root_layout.addWidget(intro)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(12)

        self._owner_input = QLineEdit()
        self._owner_input.setPlaceholderText("GitHub owner，例如 cr20085361")
        form_layout.addRow("仓库 Owner", self._owner_input)

        self._repo_input = QLineEdit()
        self._repo_input.setPlaceholderText("GitHub repo，例如 RF-Antenna-Toolkit")
        form_layout.addRow("仓库 Repo", self._repo_input)

        token_widget = QWidget()
        token_layout = QHBoxLayout(token_widget)
        token_layout.setContentsMargins(0, 0, 0, 0)
        token_layout.setSpacing(8)

        self._token_input = QLineEdit()
        self._token_input.setPlaceholderText("私有仓库可填写 GitHub fine-grained token")
        self._token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token_layout.addWidget(self._token_input, 1)

        self._token_toggle = QPushButton("显示")
        self._token_toggle.setObjectName("SecondaryButton")
        self._token_toggle.clicked.connect(self._toggle_token_visibility)
        token_layout.addWidget(self._token_toggle)
        form_layout.addRow("访问令牌", token_widget)

        self._asset_patterns_input = QPlainTextEdit()
        self._asset_patterns_input.setPlaceholderText(
            "示例：\nRF-Antenna-Toolkit-Setup-*.exe\nportable\n*.msi"
        )
        self._asset_patterns_input.setFixedHeight(96)
        form_layout.addRow("资产名匹配", self._asset_patterns_input)

        self._ignored_version_input = QLineEdit()
        self._ignored_version_input.setPlaceholderText("例如 2.1.1 或 v2.1.1")
        form_layout.addRow("忽略版本", self._ignored_version_input)

        root_layout.addLayout(form_layout)

        path_label = QLabel(f"配置文件位置：{get_update_settings_path()}")
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        path_label.setStyleSheet("font-size: 12px; color: #718096;")
        root_layout.addWidget(path_label)

        note_label = QLabel(
            "说明：当前实现仅在检测到匹配的安装包资产时弹出更新提示。"
            "忽略版本后，仍可在此对话框内清空该值重新提醒。"
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-size: 12px; color: #718096; line-height: 1.7;")
        root_layout.addWidget(note_label)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        clear_ignore_button = button_box.addButton("清空忽略版本", QDialogButtonBox.ButtonRole.ActionRole)
        if clear_ignore_button is not None:
            clear_ignore_button.clicked.connect(lambda: self._ignored_version_input.clear())
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        root_layout.addWidget(button_box)

    def _load_settings(self, settings: UpdateSettings):
        self._owner_input.setText(settings.owner)
        self._repo_input.setText(settings.repo)
        self._token_input.setText(settings.token)
        self._asset_patterns_input.setPlainText(settings.asset_name_patterns)
        self._ignored_version_input.setText(settings.ignored_version)

    def _toggle_token_visibility(self):
        is_hidden = self._token_input.echoMode() == QLineEdit.EchoMode.Password
        self._token_input.setEchoMode(
            QLineEdit.EchoMode.Normal if is_hidden else QLineEdit.EchoMode.Password
        )
        self._token_toggle.setText("隐藏" if is_hidden else "显示")

    def get_settings(self) -> UpdateSettings:
        return UpdateSettings(
            owner=self._owner_input.text(),
            repo=self._repo_input.text(),
            token=self._token_input.text(),
            asset_name_patterns=self._asset_patterns_input.toPlainText(),
            ignored_version=self._ignored_version_input.text(),
        ).cleaned()

    def accept(self):
        settings = self.get_settings()
        if not settings.owner or not settings.repo:
            QMessageBox.warning(self, "更新设置", "仓库 Owner 和 Repo 不能为空。")
            return
        super().accept()