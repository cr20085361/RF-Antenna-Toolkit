import re
import sys

filepath = r"e:\AI_project\射频天线工具集\ui\tools\antenna\wavelength_tool.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Import tr
if "from core.i18n import tr" not in content:
    content = content.replace("from core.constants import", "from core.i18n import tr\nfrom core.constants import")

# Modify __init__
content = content.replace(
    "        self._result_labels: Dict[str, QLabel] = {}",
    "        self._result_labels: Dict[str, QLabel] = {}\n        self._static_labels = []"
)

# Modify create_input_panel
content = content.replace(
    'freq_group = QGroupBox("频率输入")',
    'freq_group = QGroupBox(tr("wavelength", "group_freq"))\n        self._static_labels.append((freq_group, "wavelength", "group_freq", "title"))'
)
content = content.replace(
    'freq_label = QLabel("频率:")',
    'freq_label = QLabel(tr("wavelength", "lbl_freq"))\n        self._static_labels.append((freq_label, "wavelength", "lbl_freq", "text"))'
)
content = content.replace(
    'self._freq_input.setPlaceholderText("请输入频率")',
    'self._freq_input.setPlaceholderText(tr("wavelength", "place_freq"))\n        self._static_labels.append((self._freq_input, "wavelength", "place_freq", "placeholder"))'
)

content = content.replace(
    'medium_group = QGroupBox("介质设置")',
    'medium_group = QGroupBox(tr("wavelength", "group_medium"))\n        self._static_labels.append((medium_group, "wavelength", "group_medium", "title"))'
)
content = content.replace(
    'material_label = QLabel("材料:")',
    'material_label = QLabel(tr("wavelength", "lbl_material"))\n        self._static_labels.append((material_label, "wavelength", "lbl_material", "text"))'
)

# QComboBox custom item
content = content.replace(
    'self._material_combo.addItem("自定义")',
    'self._material_combo.addItem(tr("wavelength", "custom_material"))\n        # combobox update in retranslate_ui if strictly needed, here we simplify'
)
content = content.replace(
    'if material == "自定义":',
    'if material == tr("wavelength", "custom_material") or material == "自定义" or material == "Custom":'
)


content = content.replace(
    'epsilon_label = QLabel("介电常数 εr:")',
    'epsilon_label = QLabel(tr("wavelength", "lbl_epsilon"))\n        self._static_labels.append((epsilon_label, "wavelength", "lbl_epsilon", "text"))'
)
content = content.replace(
    'calc_button = QPushButton("📊 计算")',
    'calc_button = QPushButton(tr("wavelength", "btn_calc"))\n        self._static_labels.append((calc_button, "wavelength", "btn_calc", "text"))'
)

# Modify create_result_panel
content = content.replace(
    '_create_result_card(\n            "free_space",\n            "自由空间波长 λ₀",\n            "在真空/空气中的电磁波波长"\n        )',
    '_create_result_card(\n            "free_space",\n            tr("wavelength", "card_free_space"),\n            tr("wavelength", "desc_free_space"),\n            "card_free_space",\n            "desc_free_space"\n        )'
)
content = content.replace(
    '_create_result_card(\n            "medium",\n            "介质波长 λ",\n            "在所选介质中的有效波长"\n        )',
    '_create_result_card(\n            "medium",\n            tr("wavelength", "card_medium"),\n            tr("wavelength", "desc_medium"),\n            "card_medium",\n            "desc_medium"\n        )'
)
content = content.replace(
    '_create_result_card(\n            "quarter",\n            "四分之一波长 λ/4",\n            "常用于阻抗匹配段长度"\n        )',
    '_create_result_card(\n            "quarter",\n            tr("wavelength", "card_quarter"),\n            tr("wavelength", "desc_quarter"),\n            "card_quarter",\n            "desc_quarter"\n        )'
)
content = content.replace(
    '_create_result_card(\n            "half",\n            "二分之一波长 λ/2",\n            "常用于偶极子天线长度"\n        )',
    '_create_result_card(\n            "half",\n            tr("wavelength", "card_half"),\n            tr("wavelength", "desc_half"),\n            "card_half",\n            "desc_half"\n        )'
)

# Modify _create_result_card definition
content = content.replace(
    'def _create_result_card(\n        self,\n        key: str,\n        title: str,\n        description: str\n    ) -> QWidget:',
    'def _create_result_card(\n        self,\n        key: str,\n        title: str,\n        description: str,\n        title_key: str = "",\n        desc_key: str = ""\n    ) -> QWidget:'
)
content = content.replace(
    'title_label = QLabel(title)\n        title_label.setObjectName("ResultTitle")\n        layout.addWidget(title_label)',
    'title_label = QLabel(title)\n        title_label.setObjectName("ResultTitle")\n        layout.addWidget(title_label)\n        if title_key:\n            self._static_labels.append((title_label, "wavelength", title_key, "text"))'
)
content = content.replace(
    'desc_label = QLabel(description)\n        desc_label.setObjectName("ResultDescription")\n        desc_label.setWordWrap(True)\n        layout.addWidget(desc_label)',
    'desc_label = QLabel(description)\n        desc_label.setObjectName("ResultDescription")\n        desc_label.setWordWrap(True)\n        layout.addWidget(desc_label)\n        if desc_key:\n            self._static_labels.append((desc_label, "wavelength", desc_key, "text"))'
)

# Error messages
content = content.replace(
    'self._result_labels[key].setText("错误")',
    'self._result_labels[key].setText(tr("wavelength", "lbl_error"))'
)

# Knowledge Content
content = re.sub(r'def get_intuition_content\(self\) -> Optional\[str\]:\n\s+"""直观理解 - 物理本质"""\n\s+return """(.*?)"""', 
                 'def get_intuition_content(self) -> Optional[str]:\n        return tr("wavelength", "intuition_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_math_model_content\(self\) -> Optional\[str\]:\n\s+"""数学模型 - 精确公式"""\n\s+return """(.*?)"""', 
                 'def get_math_model_content(self) -> Optional[str]:\n        return tr("wavelength", "math_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_engineering_content\(self\) -> Optional\[str\]:\n\s+"""工程边界 - 适用范围与避坑"""\n\s+return """(.*?)"""', 
                 'def get_engineering_content(self) -> Optional[str]:\n        return tr("wavelength", "engineering_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_history_content\(self\) -> Optional\[str\]:\n\s+"""发现历史 - 趣味故事"""\n\s+return """(.*?)"""', 
                 'def get_history_content(self) -> Optional[str]:\n        return tr("wavelength", "history_content")', content, flags=re.DOTALL)


# Add retranslate_ui
if "def retranslate_ui(self):" not in content:
    content += """
    def retranslate_ui(self):
        super().retranslate_ui()
        for widget, category, key, attr in self._static_labels:
            if attr == "text":
                widget.setText(tr(category, key))
            elif attr == "title":
                widget.setTitle(tr(category, key))
            elif attr == "placeholder":
                widget.setPlaceholderText(tr(category, key))
                
        # Custom material option update in combobox
        idx = self._material_combo.findData(None)
        if idx < 0:
            idx = self._material_combo.count() - 1
        current_idx = self._material_combo.currentIndex()
        self._material_combo.setItemText(idx, tr("wavelength", "custom_material"))
        
        # Default error updating requires re-calculation or simply let it be
"""


with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated wavelength_tool.py")
