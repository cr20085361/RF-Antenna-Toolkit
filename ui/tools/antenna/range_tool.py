# -*- coding: utf-8 -*-
"""
射频天线工具集 - 收发距离计算工具
RF Antenna Toolkit - Range Calculator Tool

版本: v2.0.0
功能: 根据 Friis 传输方程计算最远通信距离并可视化
"""

from typing import Dict, Any, Optional
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.base.tool_base import ToolBase
from core.i18n import tr
from core.antenna.range_calculator import RangeCalculator, RangeParams, RangeResult


class RangeTool(ToolBase):
    """
    收发距离计算工具 UI 界面
    """
    
    # 工具元信息
    tool_name = tr("range.tool_name", "收发距离计算")
    tool_icon = "📏"
    tool_category = "antenna"
    tool_description = tr("range.tool_desc", "基于 Friis 方程计算最大通信距离")
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化"""
        self._calculator = RangeCalculator()
        self._result_labels: Dict[str, QLabel] = {}
        
        self._static_labels = []
        super().__init__(parent)
        
        # 初始化默认值并计算一次
        self._on_input_changed()

    def create_input_panel(self) -> QWidget:
        """创建左侧输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 1. 链路参数输入框 (QGroupBox)
        param_group = QGroupBox(tr("range.rf_params", "射频链路参数"))
        param_layout = QGridLayout(param_group)
        param_layout.setSpacing(12)
        param_layout.setColumnStretch(1, 1) # 让中间的输入框占据更多伸展空间
        
        # 共用的浮点验证器
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        
        # 辅助函数: 创建统一的输入框
        def create_line_edit(text: str) -> QLineEdit:
            edit = QLineEdit()
            edit.setValidator(validator)
            edit.setText(text)
            edit.setMinimumWidth(80) # 防止数值被截断
            return edit

        # 行 0: 发射功率
        param_layout.addWidget(QLabel(tr("range.tx_power", "发射功率 (Pt):")), 0, 0)
        self.edit_tx_power = create_line_edit("30.0")
        param_layout.addWidget(self.edit_tx_power, 0, 1)
        param_layout.addWidget(QLabel("dBm"), 0, 2)
        
        # 行 1: 发射天线增益
        param_layout.addWidget(QLabel(tr("range.tx_gain", "发射天线增益 (Gt):")), 1, 0)
        self.edit_tx_gain = create_line_edit("10.0")
        param_layout.addWidget(self.edit_tx_gain, 1, 1)
        param_layout.addWidget(QLabel("dBi"), 1, 2)
        
        # 行 2: 接收天线增益
        param_layout.addWidget(QLabel(tr("range.rx_gain", "接收天线增益 (Gr):")), 2, 0)
        self.edit_rx_gain = create_line_edit("10.0")
        param_layout.addWidget(self.edit_rx_gain, 2, 1)
        param_layout.addWidget(QLabel("dBi"), 2, 2)
        
        # 行 3: 频率设置
        param_layout.addWidget(QLabel(tr("range.work_freq", "工作频率 (f):")), 3, 0)
        self.edit_freq = create_line_edit("1000")
        param_layout.addWidget(self.edit_freq, 3, 1)
        
        self.combo_freq_unit = QComboBox()
        self.combo_freq_unit.addItems(["MHz", "GHz"])
        self.combo_freq_unit.setMaximumWidth(70) # 限制单位选择框过长
        param_layout.addWidget(self.combo_freq_unit, 3, 2)
        
        # 行 4: 接收底噪/灵敏度
        param_layout.addWidget(QLabel(tr("range.rx_sens", "接收灵敏度底噪 (Rmin):")), 4, 0)
        self.edit_rx_sens = create_line_edit("-90.0")
        param_layout.addWidget(self.edit_rx_sens, 4, 1)
        param_layout.addWidget(QLabel("dBm"), 4, 2)

        # 行 5: 解调信噪比
        param_layout.addWidget(QLabel(tr("range.snr_req", "解调信噪比 (SNR):")), 5, 0)
        self.edit_snr_req = create_line_edit("0.0")
        self.edit_snr_req.setToolTip(tr("range.tt_snr", "目标解调所需的最小信噪比"))
        param_layout.addWidget(self.edit_snr_req, 5, 1)
        param_layout.addWidget(QLabel("dB"), 5, 2)
        
        # 行 6: 空间衰落余量
        param_layout.addWidget(QLabel(tr("range.fade_margin", "空间衰落余量 (Margin):")), 6, 0)
        self.edit_fade_margin = create_line_edit("0.0")
        self.edit_fade_margin.setToolTip(tr("range.tt_margin", "抵抗多径、雨衰等波动的余量预留"))
        param_layout.addWidget(self.edit_fade_margin, 6, 1)
        param_layout.addWidget(QLabel("dB"), 6, 2)
        
        # 行 7: 附加损耗
        param_layout.addWidget(QLabel(tr("range.extra_loss", "固定附加损耗 (L_extra):")), 7, 0)
        self.edit_extra_loss = create_line_edit("0.0")
        param_layout.addWidget(self.edit_extra_loss, 7, 1)
        param_layout.addWidget(QLabel("dB"), 7, 2)
        
        layout.addWidget(param_group)
        
        # 信号连接
        self.edit_tx_power.textChanged.connect(self._on_input_changed)
        self.edit_tx_gain.textChanged.connect(self._on_input_changed)
        self.edit_rx_gain.textChanged.connect(self._on_input_changed)
        self.edit_freq.textChanged.connect(self._on_input_changed)
        self.combo_freq_unit.currentIndexChanged.connect(self._on_input_changed)
        self.edit_rx_sens.textChanged.connect(self._on_input_changed)
        self.edit_snr_req.textChanged.connect(self._on_input_changed)
        self.edit_fade_margin.textChanged.connect(self._on_input_changed)
        self.edit_extra_loss.textChanged.connect(self._on_input_changed)
        
        layout.addStretch()
        return panel

    def create_result_panel(self) -> QWidget:
        """创建右侧结果面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # ==================== 计算结果卡片 ====================
        result_group = QGroupBox(tr("range.calc_res", "计算结果"))
        result_layout = QVBoxLayout(result_group)
        result_layout.setSpacing(12)
        
        # 1. 极限通信距离
        self._create_result_card(
            result_layout,
            "max_range",
            tr("range.max_dist", "最远通信距离 (D_max):"),
            tr("range.max_dist_desc", "理论最大的视距通信距离，受地球曲率及障碍物限制")
        )
        
        # 2. 自由空间路损
        self._create_result_card(
            result_layout,
            "fspl",
            tr("range.fspl_max", "自由空间路径损耗 (FSPL_max):"),
            tr("range.fspl_desc", "电磁波在真空中扩散至最大通信距离时的理论衰减量")
        )
        
        # 3. 等效全向辐射功率 EIRP
        self._create_result_card(
            result_layout,
            "eirp",
            tr("range.eirp", "等效全向辐射功率 (EIRP):"),
            tr("range.eirp_desc", "发射端的等效辐射功率 (Pt + Gt)，用于管制标准合规评估")
        )
        
        layout.addWidget(result_group)
        
        # 底部图表区域 (随距离的接收功率衰减)
        chart_group = QGroupBox(tr("range.chart_title", "链路衰减曲线 (Pr vs Distance)"))
        chart_layout = QVBoxLayout(chart_group)
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        chart_layout.addWidget(self.canvas)
        layout.addWidget(chart_group, 1) # 占比伸展
        
        return panel

    def _create_result_card(self, parent_layout: QVBoxLayout, key: str, title: str, description: str):
        """创建单个结果卡片"""
        card = QFrame()
        card.setObjectName(f"ResultCard_{key}")
        card.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        
        # 标题栏: 名称 + 结果数值
        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #4A5568; font-weight: bold; border: none; background: transparent;")
        
        value_label = QLabel("--")
        value_label.setObjectName(f"ResultValue_{key}")
        value_label.setStyleSheet("color: #2B6CB0; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self._result_labels[key] = value_label
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(value_label)
        layout.addLayout(header_layout)
        
        # 描述说明
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #718096; font-size: 12px; border: none; background: transparent;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        parent_layout.addWidget(card)

    def _get_input_params(self) -> Optional[RangeParams]:
        """获取并验证输入参数"""
        try:
            tx_power = float(self.edit_tx_power.text())
            tx_gain = float(self.edit_tx_gain.text())
            rx_gain = float(self.edit_rx_gain.text())
            
            freq_raw = float(self.edit_freq.text())
            if self.combo_freq_unit.currentText() == "GHz":
                freq_mhz = freq_raw * 1000.0
            else:
                freq_mhz = freq_raw
            
            if freq_mhz <= 0: return None
                
            rx_sens = float(self.edit_rx_sens.text())
            snr_req = float(self.edit_snr_req.text())
            fade_margin = float(self.edit_fade_margin.text())
            extra_loss = float(self.edit_extra_loss.text())

            return RangeParams(
                tx_power_dbm=tx_power,
                tx_gain_dbi=tx_gain,
                rx_gain_dbi=rx_gain,
                freq_mhz=freq_mhz,
                rx_sensitivity_dbm=rx_sens,
                snr_req_db=snr_req,
                fade_margin_db=fade_margin,
                extra_loss_db=extra_loss
            )
        except ValueError:
            return None

    def calculate(self) -> Dict[str, Any]:
        """执行计算并返回结果字典 (满足 ToolBase 约束)"""
        params = self._get_input_params()
        if not params:
            return {}
            
        result = self._calculator.calculate_max_range(params)
        
        # 生成画图数据
        max_dist = min(result.max_range_km * 1.5, result.max_range_km + 10) # X 轴范围: (大于最大距离一点)
        if max_dist < 1.0:
            # 极近距离，用米表示
            d_m = np.linspace(0.1, result.max_range_km * 1000 * 1.5, 100)
            d_km = d_m / 1000.0
            d_plot = d_m
            x_label = "Distance (m)"
        else:
            d_km = np.linspace(0.01, max_dist, 100)
            d_plot = d_km
            x_label = "Distance (km)"
            
        pr_list = self._calculator.calculate_pr_at_distance(params, list(d_km))
        
        # 返回绘制所需的数据字典
        return {
            "result": result,
            "params": params,
            "plot_data": {
                "d_plot": d_plot,
                "pr_list": np.array(pr_list),
                "d_max_plot": result.max_range_km * 1000.0 if result.max_range_km < 1.0 else result.max_range_km,
                "sens_dbm": params.rx_sensitivity_dbm + params.snr_req_db + params.fade_margin_db,
                "x_label": x_label
            }
        }

    def _on_input_changed(self):
        """输入改变时触发计算和更新"""
        data = self.calculate()
        if not data:
            self._result_labels["max_range"].setText(tr("range.err_invalid", "计算错误 (输入非法)"))
            self._result_labels["fspl"].setText("--")
            self._result_labels["eirp"].setText("--")
            return
            
        result: RangeResult = data["result"]
        
        # 更新文本
        self._result_labels["max_range"].setText(f"<span style='color: #E53E3E; font-size: 18px;'>{result.max_range_formatted}</span>")
        self._result_labels["fspl"].setText(f"{result.fspl_db:.2f} dB")
        self._result_labels["eirp"].setText(f"{result.eirp_dbm:.2f} dBm")
        
        # 更新图表
        self._update_plot(data["plot_data"])

    def _update_plot(self, plot_data: dict):
        """更新 Matplotlib 衰减图"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        d_plot = plot_data["d_plot"]
        pr_list = plot_data["pr_list"]
        sens_dbm = plot_data["sens_dbm"]
        d_max = plot_data["d_max_plot"]
        x_label = plot_data["x_label"]
        
        # 画功率随距离曲线
        ax.plot(d_plot, pr_list, label=tr("range.pr", "Received Power (Pr)"), color="#3182CE", linewidth=2)
        
        # 画灵敏度阈值虚线
        ax.axhline(y=sens_dbm, color="#E53E3E", linestyle="--", label=tr("range.rx_sens_line", "Rx Sensitivity (Rmin)"))
        
        # 画最大距离垂直截顶线
        ax.vlines(x=d_max, ymin=min(pr_list) - 10, ymax=sens_dbm, color="#DD6B20", linestyle=":")
        ax.plot(d_max, sens_dbm, 'ro') # 焦点打红点
        
        # 如果超出图最大值太近，重新设置y轴限制避免被压扁
        min_pr = min(pr_list)
        ax.set_ylim([min(sens_dbm - 10, min_pr), max(pr_list) + 5])
        
        ax.set_xlabel(x_label)
        ax.set_ylabel("Power (dBm)")
        ax.set_title(tr("range.att_profile", "Link Budget Attenuation Profile"), fontsize=10)
        ax.grid(True, linestyle= "--", alpha=0.5)
        ax.legend(loc="upper right", fontsize=8)
        
        self.fig.tight_layout()
        self.canvas.draw()

    # ==================== 知识区内容 ====================
    
    def get_intuition_content(self) -> str:
        return tr("range.intuition_content", """
        <h3>{t_int_title}</h3>
        <p>{t_int_1}</p>
        <p>{t_int_2}</p>
        <p>{t_int_3}</p>
        """).format(
            t_int_title=tr("range.dd_int_title", "直观理解：电磁波的空间扩散"),
            t_int_1=tr("range.dd_int_1", "想象你在平静的湖面投入一颗石子，水波会一圈一圈向外扩散。电磁波在自由空间的传播与此类似，它像一个不断膨胀的理想球体。"),
            t_int_2=tr("range.dd_int_2", "随着距离 <i>d</i> 的增加，这个球体的表面积以 <i>O(d²)</i> 的速度急剧增大，因此分布在单位面积上的能量（功率密度）就会以平方反比规律迅速衰减。"),
            t_int_3=tr("range.dd_int_3", "这解释了为什么我们增加 6 dB 的发射功率，最远通信距离仅仅只能增加一倍。")
        )

    def get_math_model_content(self) -> str:
        return tr("range.math_content", """
        <h3>{t_math_title}</h3>
        <p>{t_math_1}</p>
        <p>{t_math_2}</p>
        <ul>
            <li>P<sub>r</sub>(dBm) = Pt(dBm) + Gt(dBi) + Gr(dBi) - FSPL(dB)</li>
            <li>{t_math_fspl} FSPL(dB) = 20·log<sub>10</sub>(d) + 20·log<sub>10</sub>(f) + 32.44</li>
            <li style='list-style-type: none;'>({t_math_unit})</li>
        </ul>
        <p>{t_math_3} <b>[{t_math_lim}]</b> {t_math_4}</p>
        """).format(
            t_math_title=tr("range.dd_math_title", "数学模型：Friis 传输方程"),
            t_math_1=tr("range.dd_math_1", "Friis 传输方程是射频链路计算的基石："),
            t_math_2=tr("range.dd_math_2", "对数形式（工程常用）："),
            t_math_fspl=tr("range.dd_math_fspl", "自由空间路损"),
            t_math_unit=tr("range.dd_math_unit", "假设 d 单位为 km, f 单位为 MHz"),
            t_math_3=tr("range.dd_math_3", "当接收功率 P<sub>r</sub> 正好逼近"),
            t_math_lim=tr("range.dd_math_lim", "底噪 + 解调信噪比 + 衰落余量"),
            t_math_4=tr("range.dd_math_4", "的统合极限阈值时，反解得到的 d 即为理论最大极限通信距离。")
        )

    def get_engineering_content(self) -> str:
        return tr("range.engineering_content", """
        <h3>{t_eng_title}</h3>
        <p>{t_eng_1}</p>
        <ul>
            <li><b>{t_eng_e_title}：</b>{t_eng_e_desc}</li>
            <li><b>{t_eng_m_title}：</b>{t_eng_m_desc}</li>
            <li><b>{t_eng_a_title}：</b>{t_eng_a_desc}</li>
            <li><b>{t_eng_r_title}：</b>{t_eng_r_desc}</li>
        </ul>
        <p>{t_eng_final_1} <b>{t_eng_margin}</b> {t_eng_final_2}</p>
        """).format(
            t_eng_title=tr("range.dd_eng_title", "工程边界：理论与现实的差异"),
            t_eng_1=tr("range.dd_eng_1", "虽然 Friis 方程能计算出极限距离，但在实际工程中几乎无法达到："),
            t_eng_e_title=tr("range.dd_eng_e_t", "地球曲率阻挡"),
            t_eng_e_desc=tr("range.dd_eng_e_d", "对于微波频段（直线传播），如果天线高度不够，信号会被地球表面遮挡。实际视距更取决于架设高度。"),
            t_eng_m_title=tr("range.dd_eng_m_t", "多径干涉"),
            t_eng_m_desc=tr("range.dd_eng_m_d", "地面反射波与直达波干涉，会产生严重的深度衰落现象。"),
            t_eng_a_title=tr("range.dd_eng_a_t", "大气衰减"),
            t_eng_a_desc=tr("range.dd_eng_a_d", "空气中的氧气 (~60GHz) 和水蒸气 (~24GHz) 会吸收部分微波。"),
            t_eng_r_title=tr("range.dd_eng_r_t", "雨衰"),
            t_eng_r_desc=tr("range.dd_eng_r_d", "在 K 频段 (比如卫星通信) 以上，雨滴会导致显著的额外衰减。"),
            t_eng_final_1=tr("range.dd_eng_f1", "工程师正是利用设置"),
            t_eng_margin=tr("range.dd_eng_margin", "空间衰落余量 (Fade Margin)"),
            t_eng_final_2=tr("range.dd_eng_f2", "(通常 10 ~ 20 dB) 以抵抗上述这些现实环境的不稳定因素从而保障稳定通讯。")
        )

    def get_history_content(self) -> str:
        return tr("range.history_content", """
        <h3>{t_his_title}</h3>
        <p>{t_his_1} <b>Harald T. Friis</b> {t_his_2}</p>
        <p>{t_his_3}</p>
        """).format(
            t_his_title=tr("range.dd_his_title", "发现历史：Harald T. Friis 的贡献"),
            t_his_1=tr("range.dd_his_1", "1946 年，贝尔实验室的工程师"),
            t_his_2=tr("range.dd_his_2", "发表了划时代的论文《A Note on a Simple Transmission Formula》。"),
            t_his_3=tr("range.dd_his_3", "在此之前，无线电工程师们被迫使用极其繁琐和容易出错的电磁场积分来计算收发天线之间的能量耦合。Friis 敏锐地引入了“有效接收面积 (Effective Area)”这一优雅的宏观物理量，把微观复杂的 Maxwell 方程组化繁为简，彻底颠覆并奠定了现代无线电链路预算的基础，让无线通信进入了可以被快速、精准量化的工程时代。")
        )

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
            elif attr == "text_colon":
                widget.setText(tr(f"{category}.{key}") + ":")
