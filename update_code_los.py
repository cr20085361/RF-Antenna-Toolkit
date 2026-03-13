import re
import sys

filepath = r"e:\AI_project\射频天线工具集\ui\tools\antenna\los_tool.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Import tr
if "from core.i18n import tr" not in content:
    content = content.replace("from core.antenna.los import", "from core.i18n import tr\nfrom core.antenna.los import")

# Modify __init__
if "self._static_labels = []" not in content:
    content = content.replace(
        "        super().__init__(parent)",
        "        self._static_labels = []\n        super().__init__(parent)"
    )

# INPUT PANEL
content = content.replace(
    'mode_group = QGroupBox("计算模式")',
    'mode_group = QGroupBox(tr("los", "group_mode"))\n        self._static_labels.append((mode_group, "los", "group_mode", "title"))'
)
content = content.replace(
    'horizon_radio = QRadioButton("地球曲率视距 (天线高度→视距)")',
    'horizon_radio = QRadioButton(tr("los", "radio_horizon"))\n        self._static_labels.append((horizon_radio, "los", "radio_horizon", "text"))'
)
content = content.replace(
    'horizon_layout.addWidget(QLabel("天线高度 h:"), 0, 0)',
    'lbl_h = QLabel(tr("los", "lbl_h"))\n        self._static_labels.append((lbl_h, "los", "lbl_h", "text"))\n        horizon_layout.addWidget(lbl_h, 0, 0)'
)
content = content.replace(
    'self._antenna_height_input.setPlaceholderText("高度")',
    'self._antenna_height_input.setPlaceholderText(tr("los", "place_h"))\n        self._static_labels.append((self._antenna_height_input, "los", "place_h", "placeholder"))'
)

content = content.replace(
    'elevation_radio = QRadioButton("目标仰角计算 (反无场景)")',
    'elevation_radio = QRadioButton(tr("los", "radio_ele"))\n        self._static_labels.append((elevation_radio, "los", "radio_ele", "text"))'
)
content = content.replace(
    'elevation_layout.addWidget(QLabel("目标距离 d:"), 0, 0)',
    'lbl_d = QLabel(tr("los", "lbl_d"))\n        self._static_labels.append((lbl_d, "los", "lbl_d", "text"))\n        elevation_layout.addWidget(lbl_d, 0, 0)'
)
content = content.replace(
    'self._target_distance_input.setPlaceholderText("距离")',
    'self._target_distance_input.setPlaceholderText(tr("los", "place_d"))\n        self._static_labels.append((self._target_distance_input, "los", "place_d", "placeholder"))'
)
content = content.replace(
    'elevation_layout.addWidget(QLabel("目标高度 h_target:"), 1, 0)',
    'lbl_htarget = QLabel(tr("los", "lbl_htarget"))\n        self._static_labels.append((lbl_htarget, "los", "lbl_htarget", "text"))\n        elevation_layout.addWidget(lbl_htarget, 1, 0)'
)
content = content.replace(
    'self._target_height_input.setPlaceholderText("无人机高度")',
    'self._target_height_input.setPlaceholderText(tr("los", "place_htarget"))\n        self._static_labels.append((self._target_height_input, "los", "place_htarget", "placeholder"))'
)
content = content.replace(
    'elevation_layout.addWidget(QLabel("雷达高度 h_radar:"), 2, 0)',
    'lbl_hradar = QLabel(tr("los", "lbl_hradar"))\n        self._static_labels.append((lbl_hradar, "los", "lbl_hradar", "text"))\n        elevation_layout.addWidget(lbl_hradar, 2, 0)'
)
content = content.replace(
    'self._radar_height_input.setPlaceholderText("雷达位置高度")',
    'self._radar_height_input.setPlaceholderText(tr("los", "place_hradar"))\n        self._static_labels.append((self._radar_height_input, "los", "place_hradar", "placeholder"))'
)

content = content.replace(
    'two_station_radio = QRadioButton("双站视距 (两站间通视)")',
    'two_station_radio = QRadioButton(tr("los", "radio_two"))\n        self._static_labels.append((two_station_radio, "los", "radio_two", "text"))'
)
content = content.replace(
    'two_station_layout.addWidget(QLabel("站点A高度 h₁:"), 0, 0)',
    'lbl_h1 = QLabel(tr("los", "lbl_h1"))\n        self._static_labels.append((lbl_h1, "los", "lbl_h1", "text"))\n        two_station_layout.addWidget(lbl_h1, 0, 0)'
)
content = content.replace(
    'two_station_layout.addWidget(QLabel("站点B高度 h₂:"), 1, 0)',
    'lbl_h2 = QLabel(tr("los", "lbl_h2"))\n        self._static_labels.append((lbl_h2, "los", "lbl_h2", "text"))\n        two_station_layout.addWidget(lbl_h2, 1, 0)'
)

content = content.replace(
    'atm_layout.addWidget(QLabel("大气条件:"))',
    'lbl_atm = QLabel(tr("los", "lbl_atm"))\n        self._static_labels.append((lbl_atm, "los", "lbl_atm", "text"))\n        atm_layout.addWidget(lbl_atm)'
)
content = content.replace(
    'self._atmosphere_combo.addItems([\n            "标准大气 (k=4/3)",\n            "干燥/无折射 (k=1)",\n            "高湿度 (k=1.5)",\n            "超折射 (k=2)"\n        ])',
    'self._atmosphere_combo.addItems([\n            tr("los", "atm_1"),\n            tr("los", "atm_2"),\n            tr("los", "atm_3"),\n            tr("los", "atm_4")\n        ])\n        # combobox update in retranslate_ui'
)
content = content.replace(
    'calc_button = QPushButton("🌍 计算视距")',
    'calc_button = QPushButton(tr("los", "btn_calc"))\n        self._static_labels.append((calc_button, "los", "btn_calc", "text"))'
)

# RESULT PANEL
content = content.replace(
    'quality_title = QLabel("评估结果")',
    'quality_title = QLabel(tr("los", "title_eval"))\n        self._static_labels.append((quality_title, "los", "title_eval", "text"))'
)
content = content.replace(
    'self._main_title = QLabel("🌍 计算结果")',
    'self._main_title = QLabel(tr("los", "title_main"))\n        self._static_labels.append((self._main_title, "los", "title_main", "text"))'
)
content = content.replace(
    'main_grid.addWidget(QLabel("主要结果:"), 0, 0)',
    'lbl_res1 = QLabel(tr("los", "lbl_res1"))\n        self._static_labels.append((lbl_res1, "los", "lbl_res1", "text"))\n        main_grid.addWidget(lbl_res1, 0, 0)'
)
content = content.replace(
    'main_grid.addWidget(QLabel("次要结果:"), 1, 0)',
    'lbl_res2 = QLabel(tr("los", "lbl_res2"))\n        self._static_labels.append((lbl_res2, "los", "lbl_res2", "text"))\n        main_grid.addWidget(lbl_res2, 1, 0)'
)
content = content.replace(
    'detail_title = QLabel("📐 详细参数")',
    'detail_title = QLabel(tr("los", "title_detail"))\n        self._static_labels.append((detail_title, "los", "title_detail", "text"))'
)
content = content.replace(
    'detail_grid.addWidget(QLabel("参数1:"), 0, 0)',
    'lbl_param1 = QLabel(tr("los", "lbl_param1"))\n        self._static_labels.append((lbl_param1, "los", "lbl_param1", "text"))\n        self._lbl_param1 = lbl_param1\n        detail_grid.addWidget(lbl_param1, 0, 0)'
)
content = content.replace(
    'detail_grid.addWidget(QLabel("参数2:"), 1, 0)',
    'lbl_param2 = QLabel(tr("los", "lbl_param2"))\n        self._static_labels.append((lbl_param2, "los", "lbl_param2", "text"))\n        self._lbl_param2 = lbl_param2\n        detail_grid.addWidget(lbl_param2, 1, 0)'
)
content = content.replace(
    'detail_grid.addWidget(QLabel("参数3:"), 2, 0)',
    'lbl_param3 = QLabel(tr("los", "lbl_param3"))\n        self._static_labels.append((lbl_param3, "los", "lbl_param3", "text"))\n        self._lbl_param3 = lbl_param3\n        detail_grid.addWidget(lbl_param3, 2, 0)'
)
content = content.replace(
    'diagram_title = QLabel("📊 计算模型示意图")',
    'diagram_title = QLabel(tr("los", "title_diagram"))\n        self._static_labels.append((diagram_title, "los", "title_diagram", "text"))'
)
content = content.replace(
    'self._diagram_label.setText("示意图暂未加载")',
    'self._diagram_label.setText(tr("los", "diagram_placeholder"))'
)

# KNOWLEDGE CONTENT
content = re.sub(r'def get_intuition_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_intuition_content(self) -> Optional[str]:\n        return tr("los", "intuition_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_math_model_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_math_model_content(self) -> Optional[str]:\n        return tr("los", "math_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_engineering_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_engineering_content(self) -> Optional[str]:\n        return tr("los", "engineering_content")', content, flags=re.DOTALL)
content = re.sub(r'def get_history_content\(self\) -> Optional\[str\]:\n\s+return """(.*?)"""', 
                 'def get_history_content(self) -> Optional[str]:\n        return tr("los", "history_content")', content, flags=re.DOTALL)


# Error messages replace in 'calculate'
content = content.replace('"⚠️ 请输入天线高度"', 'tr("los", "err_h1")')
content = content.replace('"⚠️ 高度格式错误"', 'tr("los", "err_h2")')
content = content.replace('"⚠️ 高度不能为负值"', 'tr("los", "err_h3")')
content = content.replace('"⚠️ 请输入目标距离"', 'tr("los", "err_d1")')
content = content.replace('"⚠️ 请输入目标高度"', 'tr("los", "err_d2")')
content = content.replace('"⚠️ 输入格式错误"', 'tr("los", "err_fmt")')
content = content.replace('"⚠️ 目标距离必须为正值"', 'tr("los", "err_d_pos")')
content = content.replace('"⚠️ 目标高度不能为负值"', 'tr("los", "err_h_pos")')
content = content.replace('"⚠️ 请输入两个站点的高度"', 'tr("los", "err_h_2")')
content = re.sub(r'f"⚠️ 计算错误: \{str\(e\)\}"', r'f"{tr(\'los\', \'err_calc\')}{str(e)}"', content)

# Calculation results UI mapping - very tricky manually, I will dynamically set text in _do_calculate using tr
content = content.replace(
    'self._main_title.setText("🌍 地球曲率视距")',
    'self._main_title.setText(tr("los", "radio_horizon"))'
)
content = content.replace(
    'self._result2_label.setText(f"光学视距: {result.optical_horizon_km:.2f} km")',
    'self._result2_label.setText(f"{tr(\'los\', \'horizon_opt\')} {result.optical_horizon_km:.2f} km")'
)
content = content.replace(
    'self._quality_label.setText("📡 无线电视距 (考虑大气折射)")',
    'self._quality_label.setText(tr("los", "horizon_qual"))'
)
content = content.replace(
    'self._detail1_label.setText(f"天线高度: {result.antenna_height_m:.1f} m")',
    'self._lbl_param1.setText(tr("los", "horizon_d1")); self._detail1_label.setText(f"{result.antenna_height_m:.1f} m")'
)
content = content.replace(
    'self._detail2_label.setText(f"折射系数: k = {result.refraction_k:.3f}")',
    'self._lbl_param2.setText(tr("los", "horizon_d2")); self._detail2_label.setText(f"{result.refraction_k:.3f}")'
)
content = content.replace(
    'self._detail3_label.setText(f"视距增益: {(result.radio_horizon_km/result.optical_horizon_km-1)*100:.1f}%")',
    'self._lbl_param3.setText(tr("los", "horizon_d3")); self._detail3_label.setText(f"{(result.radio_horizon_km/result.optical_horizon_km-1)*100:.1f}%")'
)

# Elevation mode
content = content.replace(
    'self._main_title.setText("🎯 目标仰角")',
    'self._main_title.setText(tr("los", "radio_ele"))'
)
content = content.replace(
    'self._result2_label.setText(f"几何仰角: {result.geometric_angle_deg:.3f}°")',
    'self._result2_label.setText(f"{tr(\'los\', \'ele_geom\')} {result.geometric_angle_deg:.3f}°")'
)
content = content.replace(
    'self._detail1_label.setText(f"目标距离: {result.target_distance_km:.2f} km")',
    'self._lbl_param1.setText(tr("los", "ele_d1")); self._detail1_label.setText(f"{result.target_distance_km:.2f} km")'
)
content = content.replace(
    'self._detail2_label.setText(f"目标高度: {result.target_height_m:.1f} m")',
    'self._lbl_param2.setText(tr("los", "ele_d2")); self._detail2_label.setText(f"{result.target_height_m:.1f} m")'
)
content = content.replace(
    'self._detail3_label.setText(f"曲率修正: +{result.earth_curvature_deg:.4f}°")',
    'self._lbl_param3.setText(tr("los", "ele_d3")); self._detail3_label.setText(f"{result.earth_curvature_deg:.4f}°")'
)
# Note: self._quality_label.setText(self._calculator.get_elevation_quality(result.corrected_angle_deg)) 
# -> this function returns a hardcoded string! Need to check the calculator core or wrap translation.
content = content.replace(
    'self._quality_label.setText(self._calculator.get_elevation_quality(result.corrected_angle_deg))',
    'qual = self._calculator.get_elevation_quality(result.corrected_angle_deg)\n                qual_map = {"✅ 仰角较大，受地球曲率影响小": "✅ Large angle, small Earth curvature effect", "⚠️ 低仰角，地球曲率修正显著": "⚠️ Low angle, significant Earth curvature effect", "❌ 超出视距或被地球遮挡": "❌ Beyond horizon or Earth blocked"}\n                self._quality_label.setText(qual_map.get(qual, qual) if "✅" not in tr("los", "tool_name") and "a" in tr("los", "tool_name") else qual)'
)

# Two station mode
content = content.replace(
    'self._main_title.setText("📡 双站视距")',
    'self._main_title.setText(tr("los", "radio_two"))'
)
content = content.replace(
    'self._result2_label.setText("最大通视距离")',
    'self._result2_label.setText(tr("los", "two_geom"))'
)
content = content.replace(
    'self._quality_label.setText("🔗 两站间理论最大通视距离")',
    'self._quality_label.setText(tr("los", "two_qual"))'
)
content = content.replace(
    'self._detail1_label.setText(f"站点1视距: {result.station1_horizon_km:.2f} km")',
    'self._lbl_param1.setText(tr("los", "two_d1")); self._detail1_label.setText(f"{result.station1_horizon_km:.2f} km")'
)
content = content.replace(
    'self._detail2_label.setText(f"站点2视距: {result.station2_horizon_km:.2f} km")',
    'self._lbl_param2.setText(tr("los", "two_d2")); self._detail2_label.setText(f"{result.station2_horizon_km:.2f} km")'
)
content = content.replace(
    'self._detail3_label.setText(f"高度: {result.station1_height_m:.1f}m / {result.station2_height_m:.1f}m")',
    'self._lbl_param3.setText(tr("los", "two_d3")); self._detail3_label.setText(f"{result.station1_height_m:.1f}m / {result.station2_height_m:.1f}m")'
)


# retranslate_ui implementation
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
                
        self._atmosphere_combo.setItemText(0, tr("los", "atm_1"))
        self._atmosphere_combo.setItemText(1, tr("los", "atm_2"))
        self._atmosphere_combo.setItemText(2, tr("los", "atm_3"))
        self._atmosphere_combo.setItemText(3, tr("los", "atm_4"))
        
        # re-trigger translation on active results area
        if self._result1_label.text() != "--":
            self._do_calculate()
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated los_tool.py")
