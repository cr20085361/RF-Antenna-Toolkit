# -*- coding: utf-8 -*-
"""
相控阵计算工具 UI
"""

import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QComboBox, QPushButton,
    QFrame, QGroupBox, QDoubleSpinBox, QSpinBox,
    QSizePolicy, QSplitter, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

# 设置 Matplotlib 支持显示中文和正常显示负号
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
mpl.rcParams['axes.unicode_minus'] = False

from core.i18n import tr
from ui.base.tool_base import ToolBase
from core.antenna.phased_array_calculator import PhasedArrayCalculator, PhasedArrayParams

class PhasedArrayTool(ToolBase):
    """相控阵计算分析工具"""
    
    tool_name = tr("phased_array.tool_name", "相控阵天线")
    tool_icon = "🎯"
    tool_category = "antenna"
    tool_description = tr("phased.tool_desc", "评估计算二维相控阵天线性能，波束扫描及指标可视化。")
    i18n_title_key = "phasedarray.tool_name"
    i18n_desc_key = "phasedarray.tool_desc"
    
    def __init__(self):
        self.calculator = PhasedArrayCalculator()
        super().__init__()
        # 延迟触发第一次计算
        self._update_calculation()

    def create_input_panel(self) -> QWidget:
        """创建左侧参数控制面板 (实现基类接口)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 快速上手区 (小白一键配置)
        self._grp_preset = QGroupBox(tr("phased.preset_group", "快速预设 (小白推荐)"))
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)
        
        btn_4x4 = QPushButton(tr("phased.btn_4x4", "4x4 基站"))
        btn_8x8 = QPushButton(tr("phased.btn_8x8", "8x8 雷达"))
        btn_16x16 = QPushButton(tr("phased.btn_16x16", "16x16 大型阵"))
        
        btn_4x4.setStyleSheet("padding: 6px;")
        btn_8x8.setStyleSheet("padding: 6px;")
        btn_16x16.setStyleSheet("padding: 6px;")
        
        btn_4x4.clicked.connect(lambda: self._apply_preset(4))
        btn_8x8.clicked.connect(lambda: self._apply_preset(8))
        btn_16x16.clicked.connect(lambda: self._apply_preset(16))
        
        preset_layout.addWidget(btn_4x4)
        preset_layout.addWidget(btn_8x8)
        preset_layout.addWidget(btn_16x16)
        self._grp_preset.setLayout(preset_layout)
        layout.addWidget(self._grp_preset)
        
        # 阵列规模区
        self._grp_array = QGroupBox(tr("phased.hw_size", "阵列硬件规模 (Array Size)"))
        array_layout = QGridLayout()
        
        self.spin_nx = QSpinBox()
        self.spin_nx.setRange(1, 100)
        self.spin_nx.setValue(8)
        self.spin_nx.valueChanged.connect(self._update_calculation)
        
        self.spin_ny = QSpinBox()
        self.spin_ny.setRange(1, 100)
        self.spin_ny.setValue(8)
        self.spin_ny.valueChanged.connect(self._update_calculation)
        
        self.spin_dx = QDoubleSpinBox()
        self.spin_dx.setRange(0.1, 2.0)
        self.spin_dx.setSingleStep(0.1)
        self.spin_dx.setValue(0.5)
        self.spin_dx.setSuffix(" λ")
        self.spin_dx.valueChanged.connect(self._update_calculation)
        
        self.spin_dy = QDoubleSpinBox()
        self.spin_dy.setRange(0.1, 2.0)
        self.spin_dy.setSingleStep(0.1)
        self.spin_dy.setValue(0.5)
        self.spin_dy.setSuffix(" λ")
        self.spin_dy.valueChanged.connect(self._update_calculation)
        
        array_layout.addWidget(QLabel(tr("phased.nx_label", "Nx (横向阵元):")), 0, 0)
        array_layout.addWidget(self.spin_nx, 0, 1)
        array_layout.addWidget(QLabel(tr("phased.ny_label", "Ny (纵向阵元):")), 1, 0)
        array_layout.addWidget(self.spin_ny, 1, 1)
        array_layout.addWidget(QLabel(tr("phased.dx_label", "dx (横向间距):")), 2, 0)
        array_layout.addWidget(self.spin_dx, 2, 1)
        array_layout.addWidget(QLabel(tr("phased.dy_label", "dy (纵向间距):")), 3, 0)
        array_layout.addWidget(self.spin_dy, 3, 1)
        
        self._grp_array.setLayout(array_layout)
        layout.addWidget(self._grp_array)
        
        # 电子扫描控制区 (核心交互区)
        self._grp_scan = QGroupBox(tr("phased.beam_scan", "波束电子扫描 (Beam Steering)"))
        scan_layout = QVBoxLayout()
        
        # 组合滑块与数字标签: Theta (极角/俯仰角)
        theta_header = QHBoxLayout()
        theta_header.addWidget(QLabel(tr("phased.theta_label", "俯仰角 (θ Theta):")))
        self.lbl_theta_val = QLabel("0°")
        self.lbl_theta_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        theta_header.addWidget(self.lbl_theta_val)
        
        self.slider_theta = QSlider(Qt.Orientation.Horizontal)
        self.slider_theta.setRange(0, 90) # 通常扫描 0 到 90 度
        self.slider_theta.setValue(0)
        self.slider_theta.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_theta.setTickInterval(15)
        self.slider_theta.valueChanged.connect(self._on_slider_changed)
        
        # 组合滑块与数字标签: Phi (方位角)
        phi_header = QHBoxLayout()
        phi_header.addWidget(QLabel(tr("phased.phi_label", "方位角 (φ Phi):")))
        self.lbl_phi_val = QLabel("0°")
        self.lbl_phi_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        phi_header.addWidget(self.lbl_phi_val)
        
        self.slider_phi = QSlider(Qt.Orientation.Horizontal)
        self.slider_phi.setRange(0, 360)
        self.slider_phi.setValue(0)
        self.slider_phi.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_phi.setTickInterval(45)
        self.slider_phi.valueChanged.connect(self._on_slider_changed)
        
        scan_layout.addLayout(theta_header)
        scan_layout.addWidget(self.slider_theta)
        scan_layout.addLayout(phi_header)
        scan_layout.addWidget(self.slider_phi)
        
        self._grp_scan.setLayout(scan_layout)
        layout.addWidget(self._grp_scan)
        
        # 高级选项
        self._grp_adv = QGroupBox(tr("phased.adv_setting", "高级加权设置 (Advanced)"))
        adv_layout = QVBoxLayout()
        
        # 窗函数类型
        win_layout = QHBoxLayout()
        win_layout.addWidget(QLabel(tr("phased.win_label", "副瓣抑制窗:")))
        self.combo_window = QComboBox()
        self.combo_window.addItems(["Uniform", "Hanning", "Hamming", "Blackman"])
        self.combo_window.currentIndexChanged.connect(self._update_calculation)
        win_layout.addWidget(self.combo_window)
        
        # 绘制切面选择
        cut_layout = QHBoxLayout()
        cut_layout.addWidget(QLabel(tr("phased.cut_label", "绘制切面:")))
        self.combo_cut = QComboBox()
        # "自动追随Phi波束面" -> 根据扫描角度自动切
        self.combo_cut.addItems([tr("phased.cut_auto", "自动切面 (Follow Beam)"), tr("phased.cut_h", "H平面 (Phi=0°)"), tr("phased.cut_v", "V平面 (Phi=90°)")])
        self.combo_cut.currentIndexChanged.connect(self._update_calculation)
        cut_layout.addWidget(self.combo_cut)
        
        adv_layout.addLayout(win_layout)
        adv_layout.addLayout(cut_layout)
        self._grp_adv.setLayout(adv_layout)
        layout.addWidget(self._grp_adv)
        
        layout.addStretch()
        return panel

    def create_result_panel(self) -> QWidget:
        """创建右侧可视化面板 (Matplotlib + 关键数据提取, 实现基类接口)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. 顶部核心指标看板
        self._grp_dashboard = QGroupBox(tr("phased.res_board", "计算结果大盘"))
        dashboard_layout = QGridLayout()
        
        # 为了醒目，使用较大的字体和颜色
        self.lbl_gain = self._make_dashboard_label()
        self.lbl_hpbw = self._make_dashboard_label()
        self.lbl_sll = self._make_dashboard_label()
        self.lbl_status = self._make_dashboard_label(color="#38A169") # 默认绿色正常
        
        dashboard_layout.addWidget(QLabel(tr("phased.max_gain", "最大增益 / 方向性:")), 0, 0)
        dashboard_layout.addWidget(self.lbl_gain, 0, 1)
        
        dashboard_layout.addWidget(QLabel(tr("phased.hpbw", "波瓣宽度 (HPBW):")), 0, 2)
        dashboard_layout.addWidget(self.lbl_hpbw, 0, 3)
        
        dashboard_layout.addWidget(QLabel(tr("phased.sll", "第一副瓣电平 (SLL):")), 1, 0)
        dashboard_layout.addWidget(self.lbl_sll, 1, 1)
        
        dashboard_layout.addWidget(QLabel(tr("phased.arr_status", "阵列状态:")), 1, 2)
        dashboard_layout.addWidget(self.lbl_status, 1, 3)
        
        self._grp_dashboard.setLayout(dashboard_layout)
        layout.addWidget(self._grp_dashboard)
        
        # 2. 绘图模式切换区
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(15)  # 增加间距防止文字截断
        mode_layout.addWidget(QLabel(tr("phased.plot_mode", "绘图模式(Plot Mode):")))
        self.btn_2d = QRadioButton(tr("phased.mode_2d", "2D 极坐标切面"))
        self.btn_3d = QRadioButton(tr("phased.mode_3d", "3D 立体波束"))
        self.btn_3d.setMinimumWidth(150) # 强制足够大的最小宽度以防止截断
        self.btn_2d.setChecked(True) # 默认 2D
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.btn_2d, 0)
        self.mode_group.addButton(self.btn_3d, 1)
        self.mode_group.buttonClicked.connect(self._update_calculation)
        
        mode_layout.addWidget(self.btn_2d)
        mode_layout.addWidget(self.btn_3d)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # 3. 底部波束大盘绘图区域
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.82, bottom=0.1)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setMinimumSize(450, 450)
        
        # 保存绘图坐标系引用的占位符，由 _update_plot 动态初始化
        self.ax = None
        
        layout.addWidget(self.canvas)
        return panel


    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新 UI 文字"""
        super().retranslate_ui(lang)
        if hasattr(self, '_grp_preset'):
            self._grp_preset.setTitle(tr("phased.preset_group"))
        if hasattr(self, '_grp_array'):
            self._grp_array.setTitle(tr("phased.hw_size"))
        if hasattr(self, '_grp_scan'):
            self._grp_scan.setTitle(tr("phased.beam_scan"))
        if hasattr(self, '_grp_adv'):
            self._grp_adv.setTitle(tr("phased.adv_setting"))
        if hasattr(self, '_grp_dashboard'):
            self._grp_dashboard.setTitle(tr("phased.res_board"))
        if hasattr(self, 'btn_2d'):
            self.btn_2d.setText(tr("phased.mode_2d"))
        if hasattr(self, 'btn_3d'):
            self.btn_3d.setText(tr("phased.mode_3d"))
        # 重新触发计算以刷新图表标题
        if hasattr(self, '_update_calculation'):
            self._update_calculation()

    def _make_dashboard_label(self, color="#2B6CB0") -> QLabel:
        lbl = QLabel("-")
        lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color}; font-family: 'Consolas', monospace;")
        return lbl

    def _apply_preset(self, n: int):
        """应用快速预设参数"""
        self.spin_nx.setValue(n)
        self.spin_ny.setValue(n)
        self.combo_window.setCurrentText("Uniform")
        self.slider_theta.setValue(0)
        self.slider_phi.setValue(0)

    def _on_slider_changed(self):
        """滑块值变更时，实时更新数字并触发计算"""
        t_val = self.slider_theta.value()
        p_val = self.slider_phi.value()
        self.lbl_theta_val.setText(f"{t_val}°")
        self.lbl_phi_val.setText(f"{p_val}°")
        self._update_calculation()

    def _update_calculation(self):
        """读取界面参数，执行计算，并更新图表"""
        try:
            # 1. 获取参数
            params = PhasedArrayParams(
                num_x=self.spin_nx.value(),
                num_y=self.spin_ny.value(),
                spacing_x=self.spin_dx.value(),
                spacing_y=self.spin_dy.value(),
                scan_theta=self.slider_theta.value(),
                scan_phi=self.slider_phi.value(),
                window_type=self.combo_window.currentText()
            )
            
            # 2. 决定计算与绘图模式
            is_3d_mode = self.btn_3d.isChecked()
            
            if is_3d_mode:
                # 3D 模式由于数据量大，降低分辨率到 1.0度 获得更精细连续的曲面
                result = self.calculator.calculate_3d_pattern(params, resolution_deg=1.0)
                # 3D 下我们不定义强切面的 HPBW 和 SLL，将其看板占位
                self.lbl_hpbw.setText("N/A (3D)")
                self.lbl_sll.setText("N/A (3D)")
                self.lbl_gain.setText(f"{result.directivity_dbi:.2f} dBi")
            else:
                # 2D 模式
                cut_option = self.combo_cut.currentText()
                if tr("phased.cut_auto", "自动切面 (Follow Beam)") in cut_option:
                    fixed_phi = params.scan_phi
                elif tr("phased.cut_h", "H平面 (Phi=0°)") in cut_option:
                    fixed_phi = 0.0
                else:
                    fixed_phi = 90.0
                    
                result = self.calculator.calculate_1d_cut(params, fixed_angle=fixed_phi)
                
                # 更新 2D 独有的具体指标看板
                self.lbl_gain.setText(f"{result.directivity_dbi:.2f} dBi")
                if result.hpbw_deg >= 180:
                    self.lbl_hpbw.setText(tr("phased.ultra_wide", "超宽带波束"))
                else:
                    self.lbl_hpbw.setText(f"{result.hpbw_deg:.1f}°")
                self.lbl_sll.setText(f"{result.sll_db:.1f} dB")
            
            # 状态更新 (共有属性)
            if result.is_grating_lobe:
                self.lbl_status.setText(tr("phased.warn_grating", "⚠ 栅瓣出现 (间距过大)"))
                self.lbl_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #E53E3E;")
            else:
                self.lbl_status.setText(tr("phased.status_ok", "✅ 正常扫描"))
                self.lbl_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #38A169;")
                
            # 3. 更新极坐标图形
            self._update_plot(result, is_3d_mode)
            
        except Exception as e:
            # 防止初始化时某些控件未准备好报错
            print(f"Update calculation error: {e}")

    def _update_plot(self, result, is_3d: bool = False):
        """动态重建并更新 Matplotlib 画布"""
        self.fig.clf() # 清除整个图形的挂载子图
        
        # 极小底噪门限
        min_db = -40
        
        if is_3d:
            # ========== 3D Surface 渲染 ==========
            import mpl_toolkits.mplot3d # noqa
            self.ax = self.fig.add_subplot(111, projection='3d')
            
            af_db = result.af_db_grid
            THETA = result.theta_grid
            PHI = result.phi_grid
            
            # 截断数据，并向外平移坐标 (让 3D 波束更像花瓣)
            # R 的定义：增益越高越向外生长。为了美观可以平移至 R >= 0
            af_clipped = np.clip(af_db, min_db, 0)
            R = af_clipped - min_db
            
            # 球面坐标转直角坐标，绘制漂亮的波束花瓣
            X = R * np.sin(THETA) * np.cos(PHI)
            Y = R * np.sin(THETA) * np.sin(PHI)
            Z = R * np.cos(THETA)
            
            # 绘制表面，使用 cmap 做热力涂色
            surf = self.ax.plot_surface(X, Y, Z, cmap='jet', linewidth=0, antialiased=True, alpha=0.9)
            
            # 绘制 3D 坐标轴 (参考 CST 风格: X红, Y绿, Z蓝)
            max_r = np.max(R) if np.max(R) > 0 else 10
            axis_len = max_r * 1.2
            
            # X轴 (红色)
            self.ax.plot([0, axis_len], [0, 0], [0, 0], color='red', linewidth=1.5)
            self.ax.text(axis_len*1.05, 0, 0, 'X (Phi=0°)', color='red', fontweight='bold', fontsize=9)
            
            # Y轴 (绿色)
            self.ax.plot([0, 0], [0, axis_len], [0, 0], color='green', linewidth=1.5)
            self.ax.text(0, axis_len*1.05, 0, 'Y (Phi=90°)', color='green', fontweight='bold', fontsize=9)
            
            # Z轴 (蓝色，天顶角)
            self.ax.plot([0, 0], [0, 0], [0, axis_len], color='blue', linewidth=1.5)
            self.ax.text(0, 0, axis_len*1.05, 'Z (Theta=0°)', color='blue', fontweight='bold', fontsize=9)
            
            # 视觉美化：去掉背景板的框线
            self.ax.xaxis.pane.fill = False
            self.ax.yaxis.pane.fill = False
            self.ax.zaxis.pane.fill = False
            self.ax.grid(False) # 关掉网格不然很乱
            self.ax.set_axis_off() # 彻底隐藏轴线，让主波束悬空漂浮更炫酷
            self.ax.set_title(tr("phased.title_3d", "3D 空间波束 (扫描={0}°)").format(self.slider_theta.value()), pad=20, fontdict={'fontweight':'bold'})
            
        else:
            # ========== 2D Polar 切面渲染 ==========
            self.ax = self.fig.add_subplot(111, polar=True)
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            
            theta_rad = np.radians(result.theta_deg)
            af_db = result.af_db
            
            af_plot = np.clip(af_db, min_db, 0)
            r_plot = af_plot - min_db
            
            self.ax.plot(theta_rad, r_plot, color="#3182CE", linewidth=2.5)
            self.ax.fill(theta_rad, r_plot, color="#3182CE", alpha=0.2)
            
            # 绘制主波束参考线
            if tr("phased.cut_auto", "自动切面 (Follow Beam)") == self.combo_cut.currentText() or np.abs(self.slider_phi.value() - float(result.cut_plane.split('=')[1].split('°')[0])) < 0.1:
               scan_th_rad = np.radians(self.slider_theta.value())
               self.ax.plot([scan_th_rad, scan_th_rad], [0, -min_db], color="#E53E3E", linestyle="--", linewidth=1.5)
            
            self.ax.set_rmin(0)
            self.ax.set_rmax(-min_db)
            
            r_ticks = np.linspace(0, -min_db, 5)
            r_labels = [f"{(r + min_db):.0f}" for r in r_ticks]
            self.ax.set_rticks(r_ticks)
            self.ax.set_yticklabels(r_labels, color="#718096", fontsize=9)
            self.ax.set_xticks(np.radians(np.arange(0, 360, 30)))
            self.ax.grid(True, linestyle=('--'), alpha=0.6)
            self.ax.set_title(tr("phased.title_2d", "阵列放射方向图 | {0}").format(result.cut_plane), pad=20, fontdict={'fontweight':'bold'})
            
        # 刷新画布
        self.canvas.draw()
        
    def get_intuition_content(self) -> str:
        return tr("phased.intuition", """
            <b>🎯 {t_intuition_title}</b><br>
            {t_intuition_1}
            {t_intuition_2}
            {t_intuition_3}<br><br>
            {t_intuition_4}
        """).format(
            t_intuition_title=tr("phased.dd_int_title", "直观比喻：手电筒的光束叠加"),
            t_intuition_1=tr("phased.dd_int_1", "想象手里拿着一排手电筒。如果大家同时点亮并直视前方，光束就会在正前方汇聚，变得极其刺眼（主瓣峰值增益）。"),
            t_intuition_2=tr("phased.dd_int_2", "如果你想让最亮的光柱向左偏，并不需要转动任何手电筒，只需要让左边的手电筒先亮，右边的依次延迟亮起（相位延迟控制）。"),
            t_intuition_3=tr("phased.dd_int_3", "由于光也是电磁波，波峰在左前方交汇，整个阵列射出的能量就如同被“魔法”折弯了一样指向了左侧。"),
            t_intuition_4=tr("phased.dd_int_4", "这就是相控阵雷达（如宙斯盾系统）和 5G Massive MIMO 基站不需要转动天线，却能全空域极速扫描目标的核心奥秘。")
        )
        
    def get_math_model_content(self) -> str:
        return tr("phased.math_model", """
            <b>📐 {t_math_title}</b><br>
            {t_math_1}<br><br>
            {t_math_2}<br><br>
            <div style='font-family: monospace; background-color: #F7FAFC; padding: 10px; border-radius: 4px;'>
            AF(θ, φ) = Σ<sub>m=0</sub><sup>Nx-1</sup> Σ<sub>n=0</sub><sup>Ny-1</sup> W<sub>mn</sub> · e<sup>j(m·Ψx + n·Ψy)</sup>
            </div><br>
            {t_math_3}<br>
            • <b>Ψx</b> = k · dx · (sinθ·cosφ - sinθ₀·cosφ₀)<br>
            • <b>Ψy</b> = k · dy · (sinθ·sinφ - sinθ₀·sinφ₀)<br><br>
            <b>{t_math_k}：</b><br>
            • <b>k = 2π/λ</b>：{t_math_k_v}<br>
            • <b>W<sub>mn</sub></b>：{t_math_w_v}
        """).format(
            t_math_title=tr("phased.dd_math_title", "核心数学公式：阵列因子 (Array Factor)"),
            t_math_1=tr("phased.dd_math_1", "对于一个包含 Nx × Ny 个阵元的矩形平面阵列，根据天线方向图相乘定理 (Pattern Multiplication)，阵列的整体辐射方向图可表示为单一阵元的辐射方向图 (Element Factor) 乘以阵列因子 (AF)。"),
            t_math_2=tr("phased.dd_math_2", "在等间距 (dx, dy) 且主波束目标扫描角度为 (θ₀, φ₀) 的情况下，其归一化阵列因子的核心控制方程如下："),
            t_math_3=tr("phased.dd_math_3", "其中空间相位差项 Ψx 和 Ψy 的展开式为："),
            t_math_k=tr("phased.dd_math_k", "关键参数解析"),
            t_math_k_v=tr("phased.dd_math_k_v", "自由空间波数。"),
            t_math_w_v=tr("phased.dd_math_w_v", "各阵元的复数激励系数（幅相加权窗），用于控制波束形状及抑制副瓣。改变这些幅度权重可实现如切比雪夫 (Chebyshev) 或泰勒 (Taylor) 分布，而改变它们的相位正是我们实现不需要机械转动即可实现波束扫描 (Beam Steering) 的根本手段。")
        )
        
    def get_engineering_content(self) -> str:
        return tr("phased.eng_content", """
            <b>⚙️ {t_eng_title}</b><br>
            1. <b>{t_eng_1_t}</b>：{t_eng_1_v}<br>
            2. <b>{t_eng_2_t}</b>：{t_eng_2_v}<br>
            3. <b>{t_eng_3_t}</b>：{t_eng_3_v}
        """).format(
            t_eng_title=tr("phased.dd_eng_title", "工程边界与避坑：让人头疼的“栅瓣” (Grating Lobes)"),
            t_eng_1_t=tr("phased.dd_eng_1_t", "阵元间距极限"),
            t_eng_1_v=tr("phased.dd_eng_1_v", "为了防止在扫描空间中出现不期望的极大值伪像（即所谓的栅瓣能量泄露），阵元的间距必须满足严格的奈奎斯特空间采样定理。若需实现最大 ±60° 的全空域扫描，阵元间距 d 通常必须被严格限制在<b>半个波长 (0.5λ)</b> 以内。"),
            t_eng_2_t=tr("phased.dd_eng_2_t", "增益衰减坠崖"),
            t_eng_2_v=tr("phased.dd_eng_2_v", "波束扫描并不是没有物理代价的。当波束偏离法线角 θ₀ 时，天线口径的等效投影面积会不可避免地按 cos(θ₀) 规律衰减，导致大角度扫描区域存在巨大的增益损失 (Scan Loss)。"),
            t_eng_3_t=tr("phased.dd_eng_3_t", "热耗与成本"),
            t_eng_3_v=tr("phased.dd_eng_3_v", "实现灵活数字波束成形的代价是极高的硬件复杂度。成百上千个独立可控的阵元，意味着其背后必须支撑同等数量的射频前端组件 (T/R 组件) 和高功耗的移相器/ADC、DAC。整机庞大的功耗、散热管理以及极其苛刻的通道初始相位一致性校准，是目前系统工程界的重中之重。")
        )
        
    def get_history_content(self) -> str:
        return tr("phased.history_content", """
            <b>📜 {t_his_title}</b><br>
            {t_his_1}<br><br>
            {t_his_2}<br>
            {t_his_3}
        """).format(
            t_his_title=tr("phased.dd_his_title", "发展历史：从二战密码到星链 (Starlink)"),
            t_his_1=tr("phased.dd_his_1", "相控阵的概念最早可以追溯到 1905 年诺贝尔奖得主卡尔·布劳恩展示的定向发射。但在二战期间，真正实用的电子扫描雷达由诺贝尔奖得主路易斯·阿尔瓦雷斯研发，用于引导飞机降落。"),
            t_his_2=tr("phased.dd_his_2", "冷战时期，相控阵因为其能瞬间“同时注视”数万个目标且无机械转动惯量的特点，成为了反导预警雷达（如铺路爪 PAVE PAWS）和舰载防空系统（如美军著名的“宙斯盾” SPY-1 雷达）的标配。"),
            t_his_3=tr("phased.dd_his_3", "如今，由于半导体的摩尔定律降本，这一顶级军工技术彻底“飞入寻常百姓家”，成为了 5G 基站及 SpaceX 星链用户终端的核心天线技术。")
        )
        
    def calculate(self):
        """实现基类接口，此处计算已由图表更新逻辑独立处理，返回空字典"""
        return {}
