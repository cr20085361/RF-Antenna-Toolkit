# -*- coding: utf-8 -*-
"""
射频天线工具集 - 视距计算工具
RF Antenna Toolkit - Line-of-Sight Calculator Tool

版本: v1.0.0
功能: 地球曲率视距、仰角计算、双站视距等
"""

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QPixmap

from ui.base.tool_base import ToolBase
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
    tool_name = "视距计算"
    tool_icon = "🌍"
    tool_category = "antenna"
    tool_description = "地球曲率视距与仰角计算"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化视距计算工具"""
        self._calculator = LOSCalculator()
        super().__init__(parent)
    
    def create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 计算模式选择 ====================
        mode_group = QGroupBox("计算模式")
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setSpacing(12)
        
        self._mode_group = QButtonGroup(self)
        
        # 模式1: 地球曲率视距
        horizon_radio = QRadioButton("地球曲率视距 (天线高度→视距)")
        horizon_radio.setChecked(True)
        self._mode_group.addButton(horizon_radio, 0)
        mode_layout.addWidget(horizon_radio)
        
        horizon_layout = QGridLayout()
        horizon_layout.addWidget(QLabel("天线高度 h:"), 0, 0)
        self._antenna_height_input = QLineEdit()
        self._antenna_height_input.setPlaceholderText("高度")
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
        elevation_radio = QRadioButton("目标仰角计算 (反无场景)")
        self._mode_group.addButton(elevation_radio, 1)
        mode_layout.addWidget(elevation_radio)
        
        elevation_layout = QGridLayout()
        
        elevation_layout.addWidget(QLabel("目标距离 d:"), 0, 0)
        self._target_distance_input = QLineEdit()
        self._target_distance_input.setPlaceholderText("距离")
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
        
        elevation_layout.addWidget(QLabel("目标高度 h_target:"), 1, 0)
        self._target_height_input = QLineEdit()
        self._target_height_input.setPlaceholderText("无人机高度")
        self._target_height_input.setValidator(QDoubleValidator(0, 50000, 2))
        self._target_height_input.setText("100")
        self._target_height_input.setEnabled(False)
        self._target_height_input.setMinimumWidth(120)
        elevation_layout.addWidget(self._target_height_input, 1, 1)
        elevation_layout.addWidget(QLabel("m"), 1, 2)
        
        elevation_layout.addWidget(QLabel("雷达高度 h_radar:"), 2, 0)
        self._radar_height_input = QLineEdit()
        self._radar_height_input.setPlaceholderText("雷达位置高度")
        self._radar_height_input.setValidator(QDoubleValidator(0, 10000, 2))
        self._radar_height_input.setText("5")
        self._radar_height_input.setEnabled(False)
        self._radar_height_input.setMinimumWidth(120)
        elevation_layout.addWidget(self._radar_height_input, 2, 1)
        elevation_layout.addWidget(QLabel("m"), 2, 2)
        
        mode_layout.addLayout(elevation_layout)
        
        # 模式3: 双站视距
        two_station_radio = QRadioButton("双站视距 (两站间通视)")
        self._mode_group.addButton(two_station_radio, 2)
        mode_layout.addWidget(two_station_radio)
        
        two_station_layout = QGridLayout()
        
        two_station_layout.addWidget(QLabel("站点A高度 h₁:"), 0, 0)
        self._station1_height_input = QLineEdit()
        self._station1_height_input.setValidator(QDoubleValidator(0, 10000, 2))
        self._station1_height_input.setText("10")
        self._station1_height_input.setEnabled(False)
        self._station1_height_input.setMinimumWidth(120)
        two_station_layout.addWidget(self._station1_height_input, 0, 1)
        two_station_layout.addWidget(QLabel("m"), 0, 2)
        
        two_station_layout.addWidget(QLabel("站点B高度 h₂:"), 1, 0)
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
        atm_layout.addWidget(QLabel("大气条件:"))
        self._atmosphere_combo = QComboBox()
        self._atmosphere_combo.addItems([
            "标准大气 (k=4/3)",
            "干燥/无折射 (k=1)",
            "高湿度 (k=1.5)",
            "超折射 (k=2)"
        ])
        atm_layout.addWidget(self._atmosphere_combo)
        mode_layout.addLayout(atm_layout)
        
        layout.addWidget(mode_group)
        
        # 切换模式
        self._mode_group.buttonClicked.connect(self._on_mode_changed)
        
        # ==================== 计算按钮 ====================
        calc_button = QPushButton("🌍 计算视距")
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
        
        quality_title = QLabel("评估结果")
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
        
        self._main_title = QLabel("🌍 计算结果")
        self._main_title.setObjectName("ResultTitle")
        main_layout.addWidget(self._main_title)
        
        main_grid = QGridLayout()
        main_grid.setSpacing(12)
        
        main_grid.addWidget(QLabel("主要结果:"), 0, 0)
        self._result1_label = QLabel("--")
        self._result1_label.setStyleSheet("font-weight: bold; color: #2C7BE5; font-size: 18px;")
        main_grid.addWidget(self._result1_label, 0, 1)
        
        main_grid.addWidget(QLabel("次要结果:"), 1, 0)
        self._result2_label = QLabel("--")
        main_grid.addWidget(self._result2_label, 1, 1)
        
        main_layout.addLayout(main_grid)
        layout.addWidget(main_card)
        
        # 详细参数
        detail_card = QWidget()
        detail_card.setObjectName("ResultPanel")
        detail_layout = QVBoxLayout(detail_card)
        
        detail_title = QLabel("📐 详细参数")
        detail_title.setObjectName("ResultTitle")
        detail_layout.addWidget(detail_title)
        
        detail_grid = QGridLayout()
        detail_grid.setSpacing(8)
        
        detail_grid.addWidget(QLabel("参数1:"), 0, 0)
        self._detail1_label = QLabel("--")
        detail_grid.addWidget(self._detail1_label, 0, 1)
        
        detail_grid.addWidget(QLabel("参数2:"), 1, 0)
        self._detail2_label = QLabel("--")
        detail_grid.addWidget(self._detail2_label, 1, 1)
        
        detail_grid.addWidget(QLabel("参数3:"), 2, 0)
        self._detail3_label = QLabel("--")
        detail_grid.addWidget(self._detail3_label, 2, 1)
        
        detail_layout.addLayout(detail_grid)
        layout.addWidget(detail_card)
        
        # 计算模型示意图
        diagram_card = QWidget()
        diagram_card.setObjectName("ResultPanel")
        diagram_layout = QVBoxLayout(diagram_card)
        
        diagram_title = QLabel("📊 计算模型示意图")
        diagram_title.setObjectName("ResultTitle")
        diagram_layout.addWidget(diagram_title)
        
        self._diagram_label = QLabel()
        self._diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._diagram_label.setMinimumHeight(300)
        self._diagram_label.setScaledContents(False)
        self._diagram_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px; }")
        
        # 加载默认图片（地球曲率视距）
        from pathlib import Path
        diagram_path = Path(self.get_asset_path("assets/diagrams/horizon_distance.png"))
        if diagram_path.exists():
            pixmap = QPixmap(str(diagram_path))
            scaled_pixmap = pixmap.scaled(400, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._diagram_label.setPixmap(scaled_pixmap)
        else:
            self._diagram_label.setText("示意图暂未加载")
        
        diagram_layout.addWidget(self._diagram_label)
        layout.addWidget(diagram_card)
        
        layout.addStretch()
        
        return panel
    
    def _update_diagram(self, mode_id: int):
        """根据计算模式更新示意图"""
        from pathlib import Path
        
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
                    return {"success": False, "error": "⚠️ 请输入天线高度"}
                
                try:
                    height = float(height_text)
                except ValueError:
                    return {"success": False, "error": "⚠️ 高度格式错误"}
                
                if height < 0:
                    return {"success": False, "error": "⚠️ 高度不能为负值"}
                
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
                    return {"success": False, "error": "⚠️ 请输入目标距离"}
                if not target_h_text:
                    return {"success": False, "error": "⚠️ 请输入目标高度"}
                
                try:
                    distance = float(dist_text)
                    target_h = float(target_h_text)
                    radar_h = float(radar_h_text) if radar_h_text else 0
                except ValueError:
                    return {"success": False, "error": "⚠️ 输入格式错误"}
                
                if distance <= 0:
                    return {"success": False, "error": "⚠️ 目标距离必须为正值"}
                if target_h < 0:
                    return {"success": False, "error": "⚠️ 目标高度不能为负值"}
                
                # 单位转换
                if self._distance_unit.currentText() == "m":
                    distance = distance / 1000
                
                result = self._calculator.calculate_elevation_angle(distance, target_h, radar_h)
                return {"success": True, "result": result, "mode": "elevation"}
                
            else:  # 双站视距
                h1_text = self._station1_height_input.text().strip()
                h2_text = self._station2_height_input.text().strip()
                
                if not h1_text or not h2_text:
                    return {"success": False, "error": "⚠️ 请输入两个站点的高度"}
                
                try:
                    h1 = float(h1_text)
                    h2 = float(h2_text)
                except ValueError:
                    return {"success": False, "error": "⚠️ 高度格式错误"}
                
                if h1 < 0 or h2 < 0:
                    return {"success": False, "error": "⚠️ 高度不能为负值"}
                
                result = self._calculator.calculate_two_station_los(h1, h2, k)
                return {"success": True, "result": result, "mode": "two_station"}
                
        except Exception as e:
            return {"success": False, "error": f"⚠️ 计算错误: {str(e)}"}
    
    def _do_calculate(self):
        """执行计算并更新显示"""
        calc_result = self.calculate()
        
        if calc_result["success"]:
            self._error_label.hide()
            mode = calc_result["mode"]
            
            if mode == "horizon":
                result: HorizonResult = calc_result["result"]
                self._main_title.setText("🌍 地球曲率视距")
                self._result1_label.setText(f"{result.radio_horizon_km:.2f} km")
                self._result2_label.setText(f"光学视距: {result.optical_horizon_km:.2f} km")
                self._quality_label.setText("📡 无线电视距 (考虑大气折射)")
                
                self._detail1_label.setText(f"天线高度: {result.antenna_height_m:.1f} m")
                self._detail2_label.setText(f"折射系数: k = {result.refraction_k:.3f}")
                self._detail3_label.setText(f"视距增益: {(result.radio_horizon_km/result.optical_horizon_km-1)*100:.1f}%")
                
            elif mode == "elevation":
                result: ElevationResult = calc_result["result"]
                self._main_title.setText("🎯 目标仰角")
                self._result1_label.setText(f"{result.corrected_angle_deg:.3f}°")
                self._result2_label.setText(f"几何仰角: {result.geometric_angle_deg:.3f}°")
                self._quality_label.setText(self._calculator.get_elevation_quality(result.corrected_angle_deg))
                
                self._detail1_label.setText(f"目标距离: {result.target_distance_km:.2f} km")
                self._detail2_label.setText(f"目标高度: {result.target_height_m:.1f} m")
                self._detail3_label.setText(f"曲率修正: +{result.earth_curvature_deg:.4f}°")
                
            else:  # two_station
                result: TwoStationResult = calc_result["result"]
                self._main_title.setText("📡 双站视距")
                self._result1_label.setText(f"{result.max_los_distance_km:.2f} km")
                self._result2_label.setText("最大通视距离")
                self._quality_label.setText("🔗 两站间理论最大通视距离")
                
                self._detail1_label.setText(f"站点1视距: {result.station1_horizon_km:.2f} km")
                self._detail2_label.setText(f"站点2视距: {result.station2_horizon_km:.2f} km")
                self._detail3_label.setText(f"高度: {result.station1_height_m:.1f}m / {result.station2_height_m:.1f}m")
                
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
        return """
        <b>🌍 什么是视距？</b><br><br>
        
        由于地球是圆的，站在地面上无法看到无限远。
        无线电波沿直线传播，超出视距后信号会被地球遮挡。<br><br>
        
        <b>🎯 反无人机场景:</b><br>
        低空目标（无人机）的仰角很小，需要准确计算以瞄准目标。
        地球曲率会影响仰角，距离越远影响越大。<br><br>
        
        <b>💡 大气折射:</b><br>
        标准大气条件下，无线电波会略微弯曲，使视距比光学视距远约15%。
        """
    
    def get_math_model_content(self) -> Optional[str]:
        return """
        <b>📐 视距计算公式与推导</b><br><br>
        
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ 无线电视距</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        <b>d = √(2 × R × k × h)</b>
        </span><br>
        • R = 6371 km (地球半径)<br>
        • k = 大气折射系数 (标准: 4/3)<br>
        • h = 天线高度<br><br>
        
        <span style="color: #555; font-size: 12px;">
        <b>▸ 推导:</b> 由勾股定理 (R+h)² = R² + d²<br>
        展开并忽略h²项得: d² ≈ 2Rh<br>
        考虑大气折射: d = √(2kRh)
        </span>
        </div>
        
        <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 10px; margin: 8px 0; border-radius: 6px;">
        <b>2️⃣ 仰角计算 (含地球曲率修正)</b><br><br>
        
        几何仰角: <span style="font-family: serif;">θ<sub>geo</sub> = arctan(Δh / d)</span><br><br>
        
        <b>⚠️ 地球曲率修正:</b><br>
        在距离 d 处，目标"视觉下沉"量:<br>
        <div style="background-color: #FFFBEB; padding: 4px 8px; border-radius: 4px; margin: 4px 0;">
        <b>Δh<sub>drop</sub> = d² / (2R)</b>
        </div>
        
        修正角度: <span style="font-family: serif;">θ<sub>corr</sub> = arctan(Δh<sub>drop</sub>/d)</span><br><br>
        
        <b style="color: #B45309;">最终仰角: θ = θ<sub>geo</sub> + θ<sub>corr</sub></b>
        </div>
        
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>3️⃣ 双站视距</b><br>
        <span style="font-family: 'Cambria Math', serif;">
        d<sub>max</sub> = √(2Rkh₁) + √(2Rkh₂)
        </span><br>
        <span style="color: #555; font-size: 12px;">
        两站最大通视距离 = 各站视距之和
        </span>
        </div>
        """
    
    def get_engineering_content(self) -> Optional[str]:
        return """
        <b>✅ 典型参数参考:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>10m天线</td><td>→ 视距约 13 km</td></tr>
        <tr><td>100m铁塔</td><td>→ 视距约 41 km</td></tr>
        <tr><td>无人机100m@5km</td><td>→ 仰角约 1.15°</td></tr>
        </table><br>
        
        <b>⚠️ 注意事项:</b><br><br>
        
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px;">
        ❌ 低仰角问题
        </span><br>
        • 仰角<1° 地杂波干扰严重<br>
        • 多径效应导致信号衰落<br><br>
        
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px;">
        💡 工程建议
        </span><br>
        • 提高天线架设高度<br>
        • 选择无遮挡的部署位置
        """
    
    def get_history_content(self) -> Optional[str]:
        return """
        <b>📜 视距的故事</b><br><br>
        
        <b>古希腊</b> - 亚里士多德通过观察远航船只
        "船身先消失，桅杆后消失"证明地球是圆的。<br><br>
        
        <b>1917年</b> - 马可尼成功实现跨大西洋无线电通信，
        当时的科学家困惑：无线电波怎么能绕过地球曲率？
        后来发现是电离层反射帮了忙。<br><br>
        
        <b>现代</b> - 反无人机系统需要精确计算低仰角探测能力，
        这正是视距计算的典型应用场景。
        """
