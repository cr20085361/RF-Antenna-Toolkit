# -*- coding: utf-8 -*-
"""
射频天线工具集 - 视距计算工具
RF Antenna Toolkit - Line-of-Sight Calculator Tool

版本: v2.0.0
功能: 地球曲率视距、仰角计算、双站视距等
"""

from typing import Dict, Any, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QPixmap

from ui.base.tool_base import ToolBase
from core.i18n import tr
from core.antenna.los import LOSCalculator, HorizonResult, ElevationResult, TwoStationResult


class LOSTool(ToolBase):
    """
    视距计算工具
    
    功能:
    - 地球曲率视距: 天线高度对应的无线电/光学视距
    - 目标仰角: 反无场景的仰角计算
    - 双站视距: 两站间最大通视距离
    """
    
    # 工具元信息
    tool_name = tr("los.tool_name", "视距计算")
    tool_icon = "🔭"
    tool_category = "antenna"
    tool_description = "地球曲率视距与仰角计算"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化视距计算工具"""
        self._calculator = LOSCalculator()
        self._static_labels = []
        super().__init__(parent)
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 计算模式选择 ====================
        mode_group = QGroupBox(tr("los.group_mode"))
        self._static_labels.append((mode_group, "los", "group_mode", "title"))
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setSpacing(12)
        
        self._mode_group = QButtonGroup(self)
        
        # 模式1: 地球曲率视距
        horizon_radio = QRadioButton(tr("los.radio_horizon"))
        self._static_labels.append((horizon_radio, "los", "radio_horizon", "text"))
        horizon_radio.setChecked(True)
        self._mode_group.addButton(horizon_radio, 0)
        mode_layout.addWidget(horizon_radio)
        
        horizon_layout = QGridLayout()
        lbl_h = QLabel(tr("los.lbl_h"))
        self._static_labels.append((lbl_h, "los", "lbl_h", "text"))
        horizon_layout.addWidget(lbl_h, 0, 0)
        self._antenna_height_input = QLineEdit()
        self._antenna_height_input.setPlaceholderText(tr("los.place_h"))
        self._static_labels.append((self._antenna_height_input, "los", "place_h", "placeholder"))
        self._antenna_height_input.setValidator(QDoubleValidator(0, 100000, 2))
        self._antenna_height_input.setText("10")
        self._antenna_height_input.setMinimumWidth(120)
        horizon_layout.addWidget(self._antenna_height_input, 0, 1)
        
        self._height_unit = QComboBox()
        self._height_unit.addItems(["m", "ft"])
        self._height_unit.setFixedWidth(60)
        horizon_layout.addWidget(self._height_unit, 0, 2)
        
        mode_layout.addLayout(horizon_layout)
        
        # 模式2: 目标仰角计算 (反无场景)
        elevation_radio = QRadioButton(tr("los.radio_ele"))
        self._static_labels.append((elevation_radio, "los", "radio_ele", "text"))
        self._mode_group.addButton(elevation_radio, 1)
        mode_layout.addWidget(elevation_radio)
        
        elevation_layout = QGridLayout()
        
        lbl_d = QLabel(tr("los.lbl_d"))
        self._static_labels.append((lbl_d, "los", "lbl_d", "text"))
        elevation_layout.addWidget(lbl_d, 0, 0)
        self._target_distance_input = QLineEdit()
        self._target_distance_input.setPlaceholderText(tr("los.place_d"))
        self._static_labels.append((self._target_distance_input, "los", "place_d", "placeholder"))
        self._target_distance_input.setValidator(QDoubleValidator(0.001, 1000, 3))
        self._target_distance_input.setText("5")
        self._target_distance_input.setEnabled(False)
        self._target_distance_input.setMinimumWidth(120)
        elevation_layout.addWidget(self._target_distance_input, 0, 1)
        
        self._distance_unit = QComboBox()
        self._distance_unit.addItems(["km", "m"])
        self._distance_unit.setEnabled(False)
        self._distance_unit.setFixedWidth(60)
        elevation_layout.addWidget(self._distance_unit, 0, 2)
        
        lbl_htarget = QLabel(tr("los.lbl_htarget"))
        self._static_labels.append((lbl_htarget, "los", "lbl_htarget", "text"))
        elevation_layout.addWidget(lbl_htarget, 1, 0)
        self._target_height_input = QLineEdit()
        self._target_height_input.setPlaceholderText(tr("los.place_htarget"))
        self._static_labels.append((self._target_height_input, "los", "place_htarget", "placeholder"))
        self._target_height_input.setValidator(QDoubleValidator(0, 50000, 2))
        self._target_height_input.setText("100")
        self._target_height_input.setEnabled(False)
        self._target_height_input.setMinimumWidth(120)
        elevation_layout.addWidget(self._target_height_input, 1, 1)
        elevation_layout.addWidget(QLabel("m"), 1, 2)
        
        lbl_hradar = QLabel(tr("los.lbl_hradar"))
        self._static_labels.append((lbl_hradar, "los", "lbl_hradar", "text"))
        elevation_layout.addWidget(lbl_hradar, 2, 0)
        self._radar_height_input = QLineEdit()
        self._radar_height_input.setPlaceholderText(tr("los.place_hradar"))
        self._static_labels.append((self._radar_height_input, "los", "place_hradar", "placeholder"))
        self._radar_height_input.setValidator(QDoubleValidator(0, 10000, 2))
        self._radar_height_input.setText("5")
        self._radar_height_input.setEnabled(False)
        self._radar_height_input.setMinimumWidth(120)
        elevation_layout.addWidget(self._radar_height_input, 2, 1)
        elevation_layout.addWidget(QLabel("m"), 2, 2)
        
        mode_layout.addLayout(elevation_layout)
        
        # 模式3: 双站视距
        two_station_radio = QRadioButton(tr("los.radio_two"))
        self._static_labels.append((two_station_radio, "los", "radio_two", "text"))
        self._mode_group.addButton(two_station_radio, 2)
        mode_layout.addWidget(two_station_radio)
        
        two_station_layout = QGridLayout()
        
        lbl_h1 = QLabel(tr("los.lbl_h1"))
        self._static_labels.append((lbl_h1, "los", "lbl_h1", "text"))
        two_station_layout.addWidget(lbl_h1, 0, 0)
        self._station1_height_input = QLineEdit()
        self._station1_height_input.setValidator(QDoubleValidator(0, 10000, 2))
        self._station1_height_input.setText("10")
        self._station1_height_input.setEnabled(False)
        self._station1_height_input.setMinimumWidth(120)
        two_station_layout.addWidget(self._station1_height_input, 0, 1)
        two_station_layout.addWidget(QLabel("m"), 0, 2)
        
        lbl_h2 = QLabel(tr("los.lbl_h2"))
        self._static_labels.append((lbl_h2, "los", "lbl_h2", "text"))
        two_station_layout.addWidget(lbl_h2, 1, 0)
        self._station2_height_input = QLineEdit()
        self._station2_height_input.setValidator(QDoubleValidator(0, 10000, 2))
        self._station2_height_input.setText("100")
        self._station2_height_input.setEnabled(False)
        self._station2_height_input.setMinimumWidth(120)
        two_station_layout.addWidget(self._station2_height_input, 1, 1)
        two_station_layout.addWidget(QLabel("m"), 1, 2)
        
        mode_layout.addLayout(two_station_layout)
        
        # 大气条件
        atm_layout = QHBoxLayout()
        lbl_atm = QLabel(tr("los.lbl_atm"))
        self._static_labels.append((lbl_atm, "los", "lbl_atm", "text"))
        atm_layout.addWidget(lbl_atm)
        self._atmosphere_combo = QComboBox()
        self._atmosphere_combo.addItems([
            tr("los.atm_1"),
            tr("los.atm_2"),
            tr("los.atm_3"),
            tr("los.atm_4")
        ])
        # combobox update in retranslate_ui
        atm_layout.addWidget(self._atmosphere_combo)
        mode_layout.addLayout(atm_layout)
        
        layout.addWidget(mode_group)
        
        # 切换模式
        self._mode_group.buttonClicked.connect(self._on_mode_changed)
        
        # ==================== 计算按钮 ====================
        calc_button = QPushButton(tr("los.btn_calc"))
        self._static_labels.append((calc_button, "los", "btn_calc", "text"))
        calc_button.setObjectName("PrimaryButton")
        calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_button.clicked.connect(self._do_calculate)
        layout.addWidget(calc_button)
        
        layout.addStretch()
        
        return panel
    
    def _on_mode_changed(self, button):
        """模式切换"""
        mode_id = self._mode_group.id(button)
        
        # 模式0: 视距
        self._antenna_height_input.setEnabled(mode_id == 0)
        self._height_unit.setEnabled(mode_id == 0)
        
        # 模式1: 仰角
        self._target_distance_input.setEnabled(mode_id == 1)
        self._distance_unit.setEnabled(mode_id == 1)
        self._target_height_input.setEnabled(mode_id == 1)
        self._radar_height_input.setEnabled(mode_id == 1)
        
        # 模式2: 双站
        self._station1_height_input.setEnabled(mode_id == 2)
        self._station2_height_input.setEnabled(mode_id == 2)
        
        # 更新示意图
        self._update_diagram(mode_id)
    
    def create_result_panel(self) -> QWidget:
        """创建结果面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 错误提示
        self._error_label = QLabel("")
        self._error_label.setObjectName("ErrorLabel")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)
        
        # 评估结果
        quality_card = QWidget()
        quality_card.setObjectName("ResultPanel")
        quality_layout = QVBoxLayout(quality_card)
        
        quality_title = QLabel(tr("los.title_eval"))
        self._static_labels.append((quality_title, "los", "title_eval", "text"))
        quality_title.setObjectName("ResultTitle")
        quality_layout.addWidget(quality_title)
        
        self._quality_label = QLabel("--")
        self._quality_label.setObjectName("ResultValue")
        quality_layout.addWidget(self._quality_label)
        
        layout.addWidget(quality_card)
        
        # 主要结果
        main_card = QWidget()
        main_card.setObjectName("ResultPanel")
        main_layout = QVBoxLayout(main_card)
        
        self._main_title = QLabel(tr("los.title_main"))
        self._static_labels.append((self._main_title, "los", "title_main", "text"))
        self._main_title.setObjectName("ResultTitle")
        main_layout.addWidget(self._main_title)
        
        main_grid = QGridLayout()
        main_grid.setSpacing(12)
        
        lbl_res1 = QLabel(tr("los.lbl_res1"))
        self._static_labels.append((lbl_res1, "los", "lbl_res1", "text"))
        main_grid.addWidget(lbl_res1, 0, 0)
        self._result1_label = QLabel("--")
        self._result1_label.setStyleSheet("font-weight: bold; color: #2C7BE5; font-size: 18px;")
        main_grid.addWidget(self._result1_label, 0, 1)
        
        lbl_res2 = QLabel(tr("los.lbl_res2"))
        self._static_labels.append((lbl_res2, "los", "lbl_res2", "text"))
        main_grid.addWidget(lbl_res2, 1, 0)
        self._result2_label = QLabel("--")
        main_grid.addWidget(self._result2_label, 1, 1)
        
        main_layout.addLayout(main_grid)
        layout.addWidget(main_card)
        
        # 详细参数
        detail_card = QWidget()
        detail_card.setObjectName("ResultPanel")
        detail_layout = QVBoxLayout(detail_card)
        
        detail_title = QLabel(tr("los.title_detail"))
        self._static_labels.append((detail_title, "los", "title_detail", "text"))
        detail_title.setObjectName("ResultTitle")
        detail_layout.addWidget(detail_title)
        
        detail_grid = QGridLayout()
        detail_grid.setSpacing(8)
        
        lbl_param1 = QLabel(tr("los.lbl_param1"))
        self._static_labels.append((lbl_param1, "los", "lbl_param1", "text"))
        self._lbl_param1 = lbl_param1
        detail_grid.addWidget(lbl_param1, 0, 0)
        self._detail1_label = QLabel("--")
        detail_grid.addWidget(self._detail1_label, 0, 1)
        
        lbl_param2 = QLabel(tr("los.lbl_param2"))
        self._static_labels.append((lbl_param2, "los", "lbl_param2", "text"))
        self._lbl_param2 = lbl_param2
        detail_grid.addWidget(lbl_param2, 1, 0)
        self._detail2_label = QLabel("--")
        detail_grid.addWidget(self._detail2_label, 1, 1)
        
        lbl_param3 = QLabel(tr("los.lbl_param3"))
        self._static_labels.append((lbl_param3, "los", "lbl_param3", "text"))
        self._lbl_param3 = lbl_param3
        detail_grid.addWidget(lbl_param3, 2, 0)
        self._detail3_label = QLabel("--")
        detail_grid.addWidget(self._detail3_label, 2, 1)
        
        detail_layout.addLayout(detail_grid)
        layout.addWidget(detail_card)
        
        # 计算模型示意图
        diagram_card = QWidget()
        diagram_card.setObjectName("ResultPanel")
        diagram_layout = QVBoxLayout(diagram_card)
        
        diagram_title = QLabel(tr("los.title_diagram"))
        self._static_labels.append((diagram_title, "los", "title_diagram", "text"))
        diagram_title.setObjectName("ResultTitle")
        diagram_layout.addWidget(diagram_title)
        
        self._diagram_label = QLabel()
        self._diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._diagram_label.setMinimumHeight(300)
        self._diagram_label.setScaledContents(False)
        self._diagram_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px; }")
        
        # 加载默认图片（地球曲率视距）
        diagram_path = Path(self.get_asset_path("assets/diagrams/horizon_distance.png"))
        if diagram_path.exists():
            pixmap = QPixmap(str(diagram_path))
            scaled_pixmap = pixmap.scaled(400, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._diagram_label.setPixmap(scaled_pixmap)
        else:
            self._diagram_label.setText(tr("los.diagram_placeholder"))
        
        diagram_layout.addWidget(self._diagram_label)
        layout.addWidget(diagram_card)
        
        layout.addStretch()
        
        return panel
    
    def _update_diagram(self, mode_id: int):
        """根据计算模式更新示意图"""
        # 根据模式选择对应的示意图
        diagram_files = {
            0: "horizon_distance.png",  # 地球曲率视距
            1: "elevation_angle.png",   # 目标仰角
            2: "two_station.png"        # 双站视距
        }
        
        diagram_filename = diagram_files.get(mode_id, "horizon_distance.png")
        diagram_path = Path(self.get_asset_path(f"assets/diagrams/{diagram_filename}"))
        
        if diagram_path.exists():
            pixmap = QPixmap(str(diagram_path))
            scaled_pixmap = pixmap.scaled(400, 280, Qt.AspectRatioMode.KeepAspectRatio, 
                                          Qt.TransformationMode.SmoothTransformation)
            self._diagram_label.setPixmap(scaled_pixmap)
        else:
            self._diagram_label.setText(f"示意图文件未找到:\n{diagram_filename}")
    
    def _get_refraction_k(self) -> float:
        """获取折射系数"""
        atm_index = self._atmosphere_combo.currentIndex()
        return [4/3, 1.0, 1.5, 2.0][atm_index]
    
    def calculate(self) -> Dict[str, Any]:
        """执行计算"""
        try:
            mode_id = self._mode_group.checkedId()
            k = self._get_refraction_k()
            
            if mode_id == 0:  # 地球曲率视距
                height_text = self._antenna_height_input.text().strip()
                if not height_text:
                    return {"success": False, "error": tr("los.err_h1")}
                
                try:
                    height = float(height_text)
                except ValueError:
                    return {"success": False, "error": tr("los.err_h2")}
                
                if height < 0:
                    return {"success": False, "error": tr("los.err_h3")}
                
                # 单位转换
                if self._height_unit.currentText() == "ft":
                    height = height * 0.3048
                
                result = self._calculator.calculate_radio_horizon(height, k)
                return {"success": True, "result": result, "mode": "horizon"}
                
            elif mode_id == 1:  # 仰角计算
                dist_text = self._target_distance_input.text().strip()
                target_h_text = self._target_height_input.text().strip()
                radar_h_text = self._radar_height_input.text().strip()
                
                if not dist_text:
                    return {"success": False, "error": tr("los.err_d1")}
                if not target_h_text:
                    return {"success": False, "error": tr("los.err_d2")}
                
                try:
                    distance = float(dist_text)
                    target_h = float(target_h_text)
                    radar_h = float(radar_h_text) if radar_h_text else 0
                except ValueError:
                    return {"success": False, "error": tr("los.err_fmt")}
                
                if distance <= 0:
                    return {"success": False, "error": tr("los.err_d_pos")}
                if target_h < 0:
                    return {"success": False, "error": tr("los.err_h_pos")}
                
                # 单位转换
                if self._distance_unit.currentText() == "m":
                    distance = distance / 1000
                
                result = self._calculator.calculate_elevation_angle(distance, target_h, radar_h)
                return {"success": True, "result": result, "mode": "elevation"}
                
            else:  # 双站视距
                h1_text = self._station1_height_input.text().strip()
                h2_text = self._station2_height_input.text().strip()
                
                if not h1_text or not h2_text:
                    return {"success": False, "error": tr("los.err_h_2")}
                
                try:
                    h1 = float(h1_text)
                    h2 = float(h2_text)
                except ValueError:
                    return {"success": False, "error": tr("los.err_h2")}
                
                if h1 < 0 or h2 < 0:
                    return {"success": False, "error": tr("los.err_h3")}
                
                result = self._calculator.calculate_two_station_los(h1, h2, k)
                return {"success": True, "result": result, "mode": "two_station"}
                
        except Exception as e:
            return {"success": False, "error": tr("los.err_calc") + str(e)}
    
    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()
        
        if calc_result["success"]:
            self._error_label.hide()
            mode = calc_result["mode"]
            
            if mode == "horizon":
                result: HorizonResult = calc_result["result"]
                self._main_title.setText(tr("los.radio_horizon"))
                self._result1_label.setText(f"{result.radio_horizon_km:.2f} km")
                self._result2_label.setText(f"{tr('los.horizon_opt')} {result.optical_horizon_km:.2f} km")
                self._quality_label.setText(tr("los.horizon_qual"))
                
                self._lbl_param1.setText(tr("los.horizon_d1")); self._detail1_label.setText(f"{result.antenna_height_m:.1f} m")
                self._lbl_param2.setText(tr("los.horizon_d2")); self._detail2_label.setText(f"{result.refraction_k:.3f}")
                self._lbl_param3.setText(tr("los.horizon_d3")); self._detail3_label.setText(f"{(result.radio_horizon_km/result.optical_horizon_km-1)*100:.1f}%")
                
            elif mode == "elevation":
                result: ElevationResult = calc_result["result"]
                self._main_title.setText(tr("los.radio_ele"))
                self._result1_label.setText(f"{result.corrected_angle_deg:.3f}°")
                self._result2_label.setText(f"{tr('los.ele_geom')} {result.geometric_angle_deg:.3f}°")
                qual = self._calculator.get_elevation_quality(result.corrected_angle_deg)
                qual_map = {"✅ 仰角较大，受地球曲率影响小": "✅ Large angle, small Earth curvature effect", "⚠️ 低仰角，地球曲率修正显著": "⚠️ Low angle, significant Earth curvature effect", "❌ 超出视距或被地球遮挡": "❌ Beyond horizon or Earth blocked"}
                self._quality_label.setText(qual_map.get(qual, qual) if "✅" not in tr("los.tool_name") and "a" in tr("los.tool_name") else qual)
                
                self._lbl_param1.setText(tr("los.ele_d1")); self._detail1_label.setText(f"{result.target_distance_km:.2f} km")
                self._lbl_param2.setText(tr("los.ele_d2")); self._detail2_label.setText(f"{result.target_height_m:.1f} m")
                self._lbl_param3.setText(tr("los.ele_d3")); self._detail3_label.setText(f"{result.earth_curvature_deg:.4f}°")
                
            else:  # two_station
                result: TwoStationResult = calc_result["result"]
                self._main_title.setText(tr("los.radio_two"))
                self._result1_label.setText(f"{result.max_los_distance_km:.2f} km")
                self._result2_label.setText(tr("los.two_geom"))
                self._quality_label.setText(tr("los.two_qual"))
                
                self._lbl_param1.setText(tr("los.two_d1")); self._detail1_label.setText(f"{result.station1_horizon_km:.2f} km")
                self._lbl_param2.setText(tr("los.two_d2")); self._detail2_label.setText(f"{result.station2_horizon_km:.2f} km")
                self._lbl_param3.setText(tr("los.two_d3")); self._detail3_label.setText(f"{result.station1_height_m:.1f}m / {result.station2_height_m:.1f}m")
                
        else:
            self._error_label.setText(calc_result.get("error", "未知错误"))
            self._error_label.show()
            self._result1_label.setText("--")
            self._result2_label.setText("--")
            self._quality_label.setText("--")
            self._detail1_label.setText("--")
            self._detail2_label.setText("--")
            self._detail3_label.setText("--")
    
    # ==================== 四维度知识内容 ====================
    
    def get_intuition_content(self) -> Optional[str]:
        return tr("los.intuition_content")
    
    def get_math_model_content(self) -> Optional[str]:
        return tr("los.math_content")
    
    def get_engineering_content(self) -> Optional[str]:
        return tr("los.engineering_content")
    
    def get_history_content(self) -> Optional[str]:
        return tr("los.history_content")

    def retranslate_ui(self, lang: str = ""):
        super().retranslate_ui(lang)
        if not hasattr(self, '_static_labels'):
            return
        for widget, category, key, attr in self._static_labels:
            if attr == "text":
                widget.setText(tr(f"{category}.{key}"))
            elif attr == "title":
                widget.setTitle(tr(f"{category}.{key}"))
            elif attr == "placeholder":
                widget.setPlaceholderText(tr(f"{category}.{key}"))
                
        # 刷新大气条件下拉框
        if hasattr(self, '_atmosphere_combo'):
            self._atmosphere_combo.setItemText(0, tr("los.atm_1"))
            self._atmosphere_combo.setItemText(1, tr("los.atm_2"))
            self._atmosphere_combo.setItemText(2, tr("los.atm_3"))
            self._atmosphere_combo.setItemText(3, tr("los.atm_4"))
        
        # 刷新当前结果（如果已有结果）
        if self._result1_label.text() != "--":
            self._do_calculate()
