import re
import sys

filepath = r"e:\AI_project\射频天线工具集\ui\tools\antenna\sensitivity_tool.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Import tr
if "from core.i18n import tr" not in content:
    content = content.replace("from core.antenna.sensitivity import", "from core.i18n import tr\nfrom core.antenna.sensitivity import")

# Add _static_labels list to init
if "self._static_labels = []" not in content:
    content = content.replace(
        "        super().__init__(parent)",
        "        self._static_labels = []\n        super().__init__(parent)"
    )

# INPUT PANEL
content = content.replace(
    'sys_group = QGroupBox("系统参数")',
    'sys_group = QGroupBox(tr("sens.group_sys"))\n        self._static_labels.append((sys_group, "sens", "group_sys", "title"))'
)
content = content.replace(
    'sys_layout.addWidget(QLabel("信号带宽 BW (MHz):"), 0, 0)',
    'lbl_bw = QLabel(tr("sens.lbl_bw"))\n        self._static_labels.append((lbl_bw, "sens", "lbl_bw", "text"))\n        sys_layout.addWidget(lbl_bw, 0, 0)'
)
content = content.replace(
    'sys_layout.addWidget(QLabel("解调要求信噪比 SNR (dB):"), 1, 0)',
    'lbl_snr = QLabel(tr("sens.lbl_snr"))\n        self._static_labels.append((lbl_snr, "sens", "lbl_snr", "text"))\n        sys_layout.addWidget(lbl_snr, 1, 0)'
)

content = content.replace(
    'rf_group = QGroupBox("射频前端参数")',
    'rf_group = QGroupBox(tr("sens.group_rf"))\n        self._static_labels.append((rf_group, "sens", "group_rf", "title"))'
)
content = content.replace(
    'rf_layout.addWidget(QLabel("接收机噪声系数 NF (dB):"), 0, 0)',
    'lbl_nf = QLabel(tr("sens.lbl_nf"))\n        self._static_labels.append((lbl_nf, "sens", "lbl_nf", "text"))\n        rf_layout.addWidget(lbl_nf, 0, 0)'
)
content = content.replace(
    'rf_layout.addWidget(QLabel("馈线/插损 L (dB):"), 1, 0)',
    'lbl_loss = QLabel(tr("sens.lbl_loss"))\n        self._static_labels.append((lbl_loss, "sens", "lbl_loss", "text"))\n        rf_layout.addWidget(lbl_loss, 1, 0)'
)

content = content.replace(
    'calc_button = QPushButton("📶 计算系统灵敏度")',
    'calc_button = QPushButton(tr("sens.btn_calc"))\n        self._static_labels.append((calc_button, "sens", "btn_calc", "text"))'
)

# RESULT PANEL
content = content.replace(
    'quality_title = QLabel("评估结果")',
    'quality_title = QLabel(tr("sens.title_eval"))\n        self._static_labels.append((quality_title, "sens", "title_eval", "text"))'
)

# main result
content = content.replace(
    'main_grid.addWidget(QLabel("系统灵敏度:"), 0, 0)',
    'lbl_res_main = QLabel(tr("sens.res_main") + ":")\n        self._static_labels.append((lbl_res_main, "sens", "res_main", "text_colon"))\n        main_grid.addWidget(lbl_res_main, 0, 0)'
)

content = content.replace(
    'detail_title = QLabel("📐 噪声链路拆解")',
    'detail_title = QLabel(tr("sens.title_detail"))\n        self._static_labels.append((detail_title, "sens", "title_detail", "text"))'
)

# detail items
content = content.replace(
    'self._detail1_widget = QLabel("热噪声基底 (Thermal Noise):")',
    'self._detail1_widget = QLabel(tr("sens.detail_floor") + ":")\n        self._static_labels.append((self._detail1_widget, "sens", "detail_floor", "text_colon"))'
)
content = content.replace(
    'self._detail2_widget = QLabel("级联总噪声系数 (Total NF):")',
    'self._detail2_widget = QLabel(tr("sens.detail_total_nf") + ":")\n        self._static_labels.append((self._detail2_widget, "sens", "detail_total_nf", "text_colon"))'
)
content = content.replace(
    'self._detail3_widget = QLabel("要求信噪比 (Required SNR):")',
    'self._detail3_widget = QLabel(tr("sens.detail_snr") + ":")\n        self._static_labels.append((self._detail3_widget, "sens", "detail_snr", "text_colon"))'
)

# MESSAGES & ALERTS
content = content.replace('"带宽必须为大于0的有效数字"', 'tr("sens.err_bw")')
content = content.replace('"SNR格式错误"', 'tr("sens.err_snr")')
content = content.replace('"噪声系数必须大于等于0"', 'tr("sens.err_nf")')
content = content.replace('"插损必须大于等于0"', 'tr("sens.err_loss")')
content = content.replace('"输入格式错误"', 'tr("sens.err_inp")')

# KNOWLEDGE CONTENT
content = re.sub(r'def get_intuition_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_intuition_content(self) -> Optional[str]:\n        return tr("sens.intuition_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_math_model_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_math_model_content(self) -> Optional[str]:\n        return tr("sens.math_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_engineering_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_engineering_content(self) -> Optional[str]:\n        return tr("sens.engineering_content")', content, flags=re.DOTALL)


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
print("Updated sensitivity_tool.py")
