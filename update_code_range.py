import re
import sys

filepath = r"e:\AI_project\射频天线工具集\ui\tools\antenna\range_tool.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Import tr
if "from core.i18n import tr" not in content:
    content = content.replace("from core.antenna.range_calculator import", "from core.i18n import tr\nfrom core.antenna.range_calculator import")

# Add _static_labels list to init
if "self._static_labels = []" not in content:
    content = content.replace(
        "        super().__init__(parent)",
        "        self._static_labels = []\n        super().__init__(parent)"
    )

# INPUT PANEL
content = content.replace(
    'tx_group = QGroupBox("发射端参数 (Tx)")',
    'tx_group = QGroupBox(tr("range.group_tx"))\n        self._static_labels.append((tx_group, "range", "group_tx", "title"))'
)
content = content.replace(
    'tx_layout.addWidget(QLabel("发射功率 Pt (dBm):"), 0, 0)',
    'lbl_tx_power = QLabel(tr("range.lbl_tx_power"))\n        self._static_labels.append((lbl_tx_power, "range", "lbl_tx_power", "text"))\n        tx_layout.addWidget(lbl_tx_power, 0, 0)'
)
content = content.replace(
    'tx_layout.addWidget(QLabel("发射天线增益 Gt (dBi):"), 1, 0)',
    'lbl_tx_gain = QLabel(tr("range.lbl_tx_gain"))\n        self._static_labels.append((lbl_tx_gain, "range", "lbl_tx_gain", "text"))\n        tx_layout.addWidget(lbl_tx_gain, 1, 0)'
)

content = content.replace(
    'rx_group = QGroupBox("接收端参数 (Rx)")',
    'rx_group = QGroupBox(tr("range.group_rx"))\n        self._static_labels.append((rx_group, "range", "group_rx", "title"))'
)
content = content.replace(
    'rx_layout.addWidget(QLabel("接收灵敏度 Pr_min (dBm):"), 0, 0)',
    'lbl_rx_sens = QLabel(tr("range.lbl_rx_sens"))\n        self._static_labels.append((lbl_rx_sens, "range", "lbl_rx_sens", "text"))\n        rx_layout.addWidget(lbl_rx_sens, 0, 0)'
)
content = content.replace(
    'rx_layout.addWidget(QLabel("接收天线增益 Gr (dBi):"), 1, 0)',
    'lbl_rx_gain = QLabel(tr("range.lbl_rx_gain"))\n        self._static_labels.append((lbl_rx_gain, "range", "lbl_rx_gain", "text"))\n        rx_layout.addWidget(lbl_rx_gain, 1, 0)'
)

content = content.replace(
    'env_group = QGroupBox("环境与系统参数")',
    'env_group = QGroupBox(tr("range.group_env"))\n        self._static_labels.append((env_group, "range", "group_env", "title"))'
)
content = content.replace(
    'env_layout.addWidget(QLabel("工作频率 f:"), 0, 0)',
    'lbl_freq = QLabel(tr("range.lbl_freq"))\n        self._static_labels.append((lbl_freq, "range", "lbl_freq", "text"))\n        env_layout.addWidget(lbl_freq, 0, 0)'
)
content = content.replace(
    'env_layout.addWidget(QLabel("系统/衰落裕量 L (dB):"), 1, 0)',
    'lbl_loss = QLabel(tr("range.lbl_loss"))\n        self._static_labels.append((lbl_loss, "range", "lbl_loss", "text"))\n        env_layout.addWidget(lbl_loss, 1, 0)'
)

content = content.replace(
    'calc_button = QPushButton("📏 计算最远通信距离")',
    'calc_button = QPushButton(tr("range.btn_calc"))\n        self._static_labels.append((calc_button, "range", "btn_calc", "text"))'
)

# RESULT PANEL
content = content.replace(
    'quality_title = QLabel("计算结果")',
    'quality_title = QLabel(tr("range.title_eval"))\n        self._static_labels.append((quality_title, "range", "title_eval", "text"))'
)

# main result
content = content.replace(
    'main_grid.addWidget(QLabel("理论最远距离:"), 0, 0)',
    'lbl_res_main = QLabel(tr("range.res_main") + ":")\n        self._static_labels.append((lbl_res_main, "range", "res_main", "text_colon"))\n        main_grid.addWidget(lbl_res_main, 0, 0)'
)

content = content.replace(
    'detail_title = QLabel("📐 链路分析拆解")',
    'detail_title = QLabel(tr("range.title_detail"))\n        self._static_labels.append((detail_title, "range", "title_detail", "text"))'
)

# detail items
content = content.replace(
    'self._detail1_widget = QLabel("等效全向辐射功率 (EIRP):")',
    'self._detail1_widget = QLabel(tr("range.detail_eirp") + ":")\n        self._static_labels.append((self._detail1_widget, "range", "detail_eirp", "text_colon"))'
)
content = content.replace(
    'self._detail2_widget = QLabel("最大允许路径损耗 (MAPL):")',
    'self._detail2_widget = QLabel(tr("range.detail_allow_loss") + ":")\n        self._static_labels.append((self._detail2_widget, "range", "detail_allow_loss", "text_colon"))'
)
content = content.replace(
    'self._detail3_widget = QLabel("自由空间边界 (无裕量距离):")',
    'self._detail3_widget = QLabel(tr("range.detail_fspl") + ":")\n        self._static_labels.append((self._detail3_widget, "range", "detail_fspl", "text_colon"))'
)


# MESSAGES & ALERTS
content = content.replace('"发射功率必须为有效数字"', 'tr("range.err_power")')
content = content.replace('"接收增敏度必须为有效数字"', 'tr("range.err_sens")')
content = content.replace('"天线增益格式错误"', 'tr("range.err_gain")')
content = content.replace('"频率必须为正数"', 'tr("range.err_freq")')
content = content.replace('"裕量格式错误"', 'tr("range.err_loss")')
content = content.replace('"输入格式错误"', 'tr("range.err_format")')

# KNOWLEDGE CONTENT
content = re.sub(r'def get_intuition_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_intuition_content(self) -> Optional[str]:\n        return tr("range.intuition_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_math_model_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_math_model_content(self) -> Optional[str]:\n        return tr("range.math_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_engineering_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_engineering_content(self) -> Optional[str]:\n        return tr("range.engineering_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_history_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_history_content(self) -> Optional[str]:\n        return tr("range.history_content")', content, flags=re.DOTALL)

# retranslate_ui implementation
if "def retranslate_ui(self, lang: str = \"\"):" not in content:
    content += """
    def retranslate_ui(self, lang: str = ""):
        super().retranslate_ui(lang)
        for widget, category, key, attr in self._static_labels:
            if attr == "text":
                widget.setText(tr(f"{category}.{key}"))
            elif attr == "title":
                widget.setTitle(tr(f"{category}.{key}"))
            elif attr == "placeholder":
                widget.setPlaceholderText(tr(f"{category}.{key}"))
            elif attr == "text_colon":
                widget.setText(tr(f"{category}.{key}") + ":")
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated range_tool.py")
