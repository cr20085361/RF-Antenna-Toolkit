import re
import sys

filepath = r"e:\AI_project\射频天线工具集\ui\tools\rf\impedance_tool.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Import tr
if "from core.i18n import tr" not in content:
    content = content.replace("from core.rf.impedance import", "from core.i18n import tr\nfrom core.rf.impedance import")

# Add static labels
if "self._static_labels = []" not in content:
    content = content.replace("        self.calculator = ImpedanceCalculator()", "        self._static_labels = []\n        self.calculator = ImpedanceCalculator()")

# _create_param_row modification
content = content.replace(
    'layout.addWidget(QLabel(label), row, 0)',
    'lbl_wid = QLabel(label)\n        layout.addWidget(lbl_wid, row, 0)\n        if "coax_d" == param_key or "coax_D" == param_key or "coax_Z" == param_key or \\\n           "ms_W" == param_key or "ms_H" == param_key or "ms_T" == param_key or "ms_Z" == param_key or \\\n           "cpwg_W" == param_key or "cpwg_S" == param_key or "cpwg_H" == param_key or "cpwg_T" == param_key or "cpwg_Z" == param_key:\n            # This is handled dynamically via specific mapping\n            self._static_labels.append((lbl_wid, "impedance", param_key.lower().replace("ms_z", "lbl_z0").replace("coax_z", "lbl_z0").replace("cpwg_z", "lbl_z0"), "text"))'
)
content = content.replace(
    'calc_btn = QPushButton("计算")',
    'calc_btn = QPushButton(tr("impedance", "lbl_calc"))\n            self._static_labels.append((calc_btn, "impedance", "lbl_calc", "text"))'
)


# Mode Selection
content = content.replace(
    'mode_group = QGroupBox("结构模式")',
    'mode_group = QGroupBox(tr("impedance", "group_mode"))\n        self._static_labels.append((mode_group, "impedance", "group_mode", "title"))'
)
content = content.replace(
    'coaxial_radio = QRadioButton("同轴线 (Coaxial)")',
    'coaxial_radio = QRadioButton(tr("impedance", "radio_coax"))\n        self._static_labels.append((coaxial_radio, "impedance", "radio_coax", "text"))'
)
content = content.replace(
    'microstrip_radio = QRadioButton("单微带线 (Microstrip)")',
    'microstrip_radio = QRadioButton(tr("impedance", "radio_ms"))\n        self._static_labels.append((microstrip_radio, "impedance", "radio_ms", "text"))'
)
content = content.replace(
    'cpwg_radio = QRadioButton("共面波导 (CPWG)")',
    'cpwg_radio = QRadioButton(tr("impedance", "radio_cpwg"))\n        self._static_labels.append((cpwg_radio, "impedance", "radio_cpwg", "text"))'
)


# Epsilon R labels
content = re.sub(
    r'layout\.addWidget\(QLabel\("介电常数 εᵣ:"\), row, 0\)',
    'lbl_er = QLabel(tr("impedance", "lbl_er"))\n        self._static_labels.append((lbl_er, "impedance", "lbl_er", "text"))\n        layout.addWidget(lbl_er, row, 0)',
    content
)


# Result Panel
content = content.replace(
    'detail_title = QLabel("📊 详细参数")',
    'detail_title = QLabel(tr("impedance", "title_detail"))\n        self._static_labels.append((detail_title, "impedance", "title_detail", "text"))'
)
content = content.replace(
    'detail_items = [\n            ("effective_er", "有效介电常数 εₑ"),\n            ("velocity", "速度因子"),\n            ("capacitance", "单位长度电容"),\n            ("ratio", "尺寸比例"),\n        ]',
    'detail_items = [\n            ("effective_er", tr("impedance", "detail_er"), "detail_er"),\n            ("velocity", tr("impedance", "detail_vel"), "detail_vel"),\n            ("capacitance", tr("impedance", "detail_cap"), "detail_cap"),\n            ("ratio", tr("impedance", "detail_ratio"), "detail_ratio"),\n        ]'
)
content = content.replace(
    'for i, (key, label) in enumerate(detail_items):',
    'for i, (key, label, tr_key) in enumerate(detail_items):'
)
content = content.replace(
    'name_label = QLabel(f"{label}:")',
    'name_label = QLabel(f"{label}:")\n            self._static_labels.append((name_label, "impedance", tr_key, "text_colon"))'
)
content = content.replace(
    'diagram_title = QLabel("📐 截面示意图")',
    'diagram_title = QLabel(tr("impedance", "title_diagram"))\n        self._static_labels.append((diagram_title, "impedance", "title_diagram", "text"))'
)


# Messages
content = content.replace('"请输入有效的尺寸"', 'tr("impedance", "err_dim")')
content = content.replace('"外径必须大于内径"', 'tr("impedance", "err_d_D")')
content = content.replace('"请输入有效的阻抗和外径"', 'tr("impedance", "err_z_D")')
content = content.replace('"请输入有效的阻抗和内径"', 'tr("impedance", "err_z_d")')
content = content.replace('"请输入有效的阻抗和介质厚度"', 'tr("impedance", "err_z_H")')
content = content.replace('"请输入有效的阻抗和线宽"', 'tr("impedance", "err_z_W")')
content = content.replace('"请输入有效的阻抗和尺寸"', 'tr("impedance", "err_z_dim")')

content = content.replace('f"✅ 验证阻抗: {result.impedance:.2f} Ω"', 'f"{tr(\'impedance\', \'eval_veri\')}{result.impedance:.2f} Ω"')
content = content.replace('"✅ 接近 50Ω 标准阻抗"', 'tr("impedance", "eval_50")')
content = content.replace('"✅ 接近 75Ω 标准阻抗"', 'tr("impedance", "eval_75")')
content = content.replace('"ℹ️ 非标准阻抗值"', 'tr("impedance", "eval_non")')


# KNOWLEDGE CONTENT
content = re.sub(r'def get_intuition_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_intuition_content(self) -> Optional[str]:\n        return tr("impedance", "intuition_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_math_model_content\(self\) -> Optional\[str\]:\n\s+"""(.*?)"""\n\s+return """(.*?)"""', 
                 'def get_math_model_content(self) -> Optional[str]:\n        return tr("impedance", "math_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_engineering_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_engineering_content(self) -> Optional[str]:\n        return tr("impedance", "engineering_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_history_content\(self\) -> Optional\[str\]:\n\s+"""(.*?)"""\n\s+return """(.*?)"""', 
                 'def get_history_content(self) -> Optional[str]:\n        return tr("impedance", "history_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_boundary_content\(self\) -> Optional\[str\]:\n\s+"""(.*?)"""\n\s+return """(.*?)"""', 
                 'def get_boundary_content(self) -> Optional[str]:\n        return tr("impedance", "boundary_content")', content, flags=re.DOTALL)


# Retranslate
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
            elif attr == "text_colon":
                widget.setText(f"{tr(category, key)}:")
                
        # combobox custom edit
        idx0 = self._coax_er_combo.findData(None)
        if idx0 >= 0: self._coax_er_combo.setItemText(idx0, tr("impedance", "lbl_custom"))
        
        idx1 = self._ms_er_combo.findData(None)
        if idx1 >= 0: self._ms_er_combo.setItemText(idx1, tr("impedance", "lbl_custom"))
        
        idx2 = self._cpwg_er_combo.findData(None)
        if idx2 >= 0: self._cpwg_er_combo.setItemText(idx2, tr("impedance", "lbl_custom"))
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated impedance_tool.py")
