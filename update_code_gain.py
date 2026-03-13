import re
import sys

filepath = r"e:\AI_project\射频天线工具集\ui\tools\antenna\gain_tool.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Import tr
if "from core.i18n import tr" not in content:
    content = content.replace("from core.antenna.gain import", "from core.i18n import tr\nfrom core.antenna.gain import")

# Modify __init__
if "self._static_labels = []" not in content:
    content = content.replace(
        "        super().__init__(parent)",
        "        self._static_labels = []\n        super().__init__(parent)"
    )

# INPUT PANEL
content = content.replace(
    'mode_group = QGroupBox("计算模式")',
    'mode_group = QGroupBox(tr("gain.group_mode"))\n        self._static_labels.append((mode_group, "gain", "group_mode", "title"))'
)
content = content.replace(
    'beamwidth_radio = QRadioButton("波束宽度法 (3dB 波宽)")',
    'beamwidth_radio = QRadioButton(tr("gain.radio_bw"))\n        self._static_labels.append((beamwidth_radio, "gain", "radio_bw", "text"))'
)
content = content.replace(
    'aperture_radio = QRadioButton("有效口径法 (面积 & 频率)")',
    'aperture_radio = QRadioButton(tr("gain.radio_aperture"))\n        self._static_labels.append((aperture_radio, "gain", "radio_aperture", "text"))'
)

# BW Mode Area
content = content.replace(
    'bw_layout.addWidget(QLabel("E面 3dB波宽 (度):"), 0, 0)',
    'lbl_bwe = QLabel(tr("gain.lbl_bw_e"))\n        self._static_labels.append((lbl_bwe, "gain", "lbl_bw_e", "text"))\n        bw_layout.addWidget(lbl_bwe, 0, 0)'
)
content = content.replace(
    'bw_layout.addWidget(QLabel("H面 3dB波宽 (度):"), 1, 0)',
    'lbl_bwh = QLabel(tr("gain.lbl_bw_h"))\n        self._static_labels.append((lbl_bwh, "gain", "lbl_bw_h", "text"))\n        bw_layout.addWidget(lbl_bwh, 1, 0)'
)
content = content.replace(
    'bw_layout.addWidget(QLabel("天线效率 η (0-1):"), 2, 0)',
    'lbl_eff1 = QLabel(tr("gain.lbl_eff"))\n        self._static_labels.append((lbl_eff1, "gain", "lbl_eff", "text"))\n        bw_layout.addWidget(lbl_eff1, 2, 0)'
)

# Aperture Mode Area
content = content.replace(
    'aperture_layout.addWidget(QLabel("工作频率:"), 0, 0)',
    'lbl_freq = QLabel(tr("gain.lbl_freq"))\n        self._static_labels.append((lbl_freq, "gain", "lbl_freq", "text"))\n        aperture_layout.addWidget(lbl_freq, 0, 0)'
)
content = content.replace(
    'self._shape_combo.addItems([\n            "矩形口径 (长 × 宽)",\n            "圆形口径 (直径 × 1)"\n        ])',
    'self._shape_combo.addItems([\n            tr("gain.radio_rect"),\n            tr("gain.radio_circ")\n        ])\n        # updated in retranslate_ui'
)
content = content.replace(
    'self._dim1_label = QLabel("物理尺寸1:")',
    'self._dim1_label = QLabel(tr("gain.lbl_dim1"))\n        self._static_labels.append((self._dim1_label, "gain", "lbl_dim1", "text"))'
)
content = content.replace(
    'self._dim2_label = QLabel("物理尺寸2:")',
    'self._dim2_label = QLabel(tr("gain.lbl_dim2"))\n        self._static_labels.append((self._dim2_label, "gain", "lbl_dim2", "text"))'
)
content = content.replace(
    'aperture_layout.addWidget(QLabel("天线效率 η (0-1):"), 4, 0)',
    'lbl_eff2 = QLabel(tr("gain.lbl_eff"))\n        self._static_labels.append((lbl_eff2, "gain", "lbl_eff", "text"))\n        aperture_layout.addWidget(lbl_eff2, 4, 0)'
)

content = content.replace(
    'calc_button = QPushButton("📡 计算增益")',
    'calc_button = QPushButton(tr("gain.btn_calc"))\n        self._static_labels.append((calc_button, "gain", "btn_calc", "text"))'
)

# RESULT PANEL
content = content.replace(
    'quality_title = QLabel("计算结果")',
    'quality_title = QLabel(tr("gain.title_eval"))\n        self._static_labels.append((quality_title, "gain", "title_eval", "text"))'
)
content = content.replace(
    'main_grid.addWidget(QLabel("天线增益 (dBi):"), 0, 0)',
    'lbl_res1 = QLabel(tr("gain.res_main") + ":")\n        self._static_labels.append((lbl_res1, "gain", "res_main", "text_colon"))\n        main_grid.addWidget(lbl_res1, 0, 0)'
)
content = content.replace(
    'main_grid.addWidget(QLabel("线性增益 (倍数):"), 1, 0)',
    'lbl_res2 = QLabel(tr("gain.res_linear") + ":")\n        self._static_labels.append((lbl_res2, "gain", "res_linear", "text_colon"))\n        main_grid.addWidget(lbl_res2, 1, 0)'
)
content = content.replace(
    'detail_title = QLabel("📐 详细参数")',
    'detail_title = QLabel(tr("gain.title_detail"))\n        self._static_labels.append((detail_title, "gain", "title_detail", "text"))'
)

# Note: detail grid dynamic labels
content = content.replace(
    'self._detail1_widget = QLabel("有效口径面积:")',
    'self._detail1_widget = QLabel(tr("gain.detail_aperture") + ":")\n        self._static_labels.append((self._detail1_widget, "gain", "detail_aperture", "text_colon"))'
)
content = content.replace(
    'self._detail2_widget = QLabel("立体角 (波束宽度法):")',
    'self._detail2_widget = QLabel(tr("gain.detail_solid") + ":")\n        self._static_labels.append((self._detail2_widget, "gain", "detail_solid", "text_colon"))'
)
content = content.replace(
    'self._detail3_widget = QLabel("理论最大增益 (效率=100%):")',
    'self._detail3_widget = QLabel(tr("gain.detail_max") + ":")\n        self._static_labels.append((self._detail3_widget, "gain", "detail_max", "text_colon"))'
)

# MESSAGES & ALERTS
content = content.replace('"波束宽度必须在 0 到 360 度之间"', 'tr("gain.err_bw")')
content = content.replace('"效率必须在 0 到 1 之间"', 'tr("gain.err_eff")')
content = content.replace('"请输入有效的正向频率"', 'tr("gain.err_freq")')
content = content.replace('"请输入有效的物理尺寸"', 'tr("gain.err_dim")')
content = content.replace('"输入格式错误"', 'tr("gain.err_inp")')

# KNOWLEDGE CONTENT
content = re.sub(r'def get_intuition_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_intuition_content(self) -> Optional[str]:\n        return tr("gain.intuition_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_math_model_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_math_model_content(self) -> Optional[str]:\n        return tr("gain.math_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_engineering_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_engineering_content(self) -> Optional[str]:\n        return tr("gain.engineering_content")', content, flags=re.DOTALL)

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
                
        self._shape_combo.setItemText(0, tr("gain.radio_rect"))
        self._shape_combo.setItemText(1, tr("gain.radio_circ"))
        
        # update mode
        self._on_mode_changed()
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated gain_tool.py")
