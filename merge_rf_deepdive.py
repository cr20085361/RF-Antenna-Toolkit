import json
import os

def merge_deep_dive():
    zh_path = r"e:\AI_Project\RF-Antenna-Toolkit\assets\locales\zh_CN.json"
    en_path = r"e:\AI_Project\RF-Antenna-Toolkit\assets\locales\en_US.json"
    
    with open(zh_path, 'r', encoding='utf-8') as f:
        zh_data = json.load(f)
    with open(en_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    def ensure_module(data, module):
        if module not in data: data[module] = {}

    # ------------------ Bandwidth 模块 (漏掉的大头) ------------------
    ensure_module(zh_data, "bandwidth")
    ensure_module(en_data, "bandwidth")
    zh_data["bandwidth"].update({
        "intuition_content": "<b>💡 什么是天线带宽？</b><br><br>带宽就像是高速公路的“宽度”：它定义了天线能高效传输信号的频率范围。",
        "math_content": "<b>📐 带宽计算模型</b><br><br><b>1. 百分比带宽 (FBW):</b><br>BW = (fH - fL) / fc * 100%",
        "engineering_content": "<b>⚙️ 工程选型指南</b><br><br>对于移动通信（4G/5G），通常需要 10% 以上的相对带宽。",
        "history_content": "<b>📜 频率管理的历史</b><br><br>早期无线电并没有带宽的概念。随着 1912 年《无线电法案》的颁布，频谱成为了资源。"
    })
    en_data["bandwidth"].update({
        "intuition_content": "<b>💡 What is Antenna Bandwidth?</b><br><br>Bandwidth is like the \"width\" of a highway: it defines the frequency range.",
        "math_content": "<b>📐 Math Models</b><br><br>FBW = (fH - fL) / fc * 100%",
        "engineering_content": "<b>⚙️ Engineering Guide</b><br><br>Mobile comms (4G/5G) typically require > 10% FBW.",
        "history_content": "<b>📜 History</b><br><br>Early radio lacked bandwidth concepts until the Radio Act of 1912."
    })

    # ------------------ VSWR 模块 ------------------
    ensure_module(zh_data, "vswr")
    ensure_module(en_data, "vswr")
    zh_data["vswr"].update({
        "intuition": "<b>🌊 什么是驻波？</b><br>反射波与入射波叠加形成的面。",
        "math_model": "<b>📐 核心公式</b><br>VSWR = (1 + |Γ|) / (1 - |Γ|)",
        "eng_content": "<b>✅ 工程参考</b><br>VSWR < 1.5 是良好匹配的标准。",
        "history_content": "<b>📜 发现历史</b><br>赫兹于 1888 年验证了电磁驻波。"
    })
    en_data["vswr"].update({
        "intuition": "<b>🌊 What is VSWR?</b><br>Overlay of incident and reflected waves.",
        "math_model": "<b>📐 Formulas</b><br>VSWR = (1 + |Γ|) / (1 - |Γ|)",
        "eng_content": "<b>✅ Engineering</b><br>VSWR < 1.5 is the standard for good matching.",
        "history_content": "<b>📜 History</b><br>Hertz verified standing waves in 1888."
    })

    # ------------------ Attenuator 模块 ------------------
    ensure_module(zh_data, "attenuator")
    ensure_module(en_data, "attenuator")
    zh_data["attenuator"].update({
        "intuition": "<b>💡 衰减器本质</b><br>基于电阻网络降低信号电平。",
        "math_model": "<b>📐 计算公式</b><br>K = 10^(dB/20)",
        "eng_content": "<b>⚙️ 设计指南</b><br>选择合适的 E24/E96 阻值系列。",
        "history_content": "<b>📜 发展简史</b><br>从电报时代的电阻盒演变而来。"
    })
    en_data["attenuator"].update({
        "intuition": "<b>💡 Essence</b><br>Reduce signal levels via resistor networks.",
        "math_model": "<b>📐 Formulas</b><br>K = 10^(dB/20)",
        "eng_content": "<b>⚙️ Design</b><br>Choose appropriate E24/E96 series.",
        "history_content": "<b>📜 History</b><br>Evolved from telegraph-era resistor boxes."
    })

    # ------------------ Cascade 模块 ------------------
    ensure_module(zh_data, "cascade")
    ensure_module(en_data, "cascade")
    zh_data["cascade"].update({
        "intuition": "<b>💡 级联驻波</b><br>相位不确定导致驻波在一定范围内变动。",
        "math_model": "<b>📐 级联模型</b><br>|Γ|max = |Γ1| + |Γ2|",
        "eng_content": "<b>✅ 典型场景</b><br>设计应按最差情况考虑。",
        "history_content": "<b>📜 故事</b><br>1930 年代传输线理论的成熟。",
        "rl_perfect": "> 100 dB (近似完美)", "err_calc": "⚠️ 计算错误: {err}", "err_unknown": "未知错误"
    })
    en_data["cascade"].update({
        "intuition": "<b>💡 Cascade VSWR</b><br>Phase uncertainty causes VSWR range.",
        "math_model": "<b>📐 Models</b><br>|Γ|max = |Γ1| + |Γ2|",
        "eng_content": "<b>✅ Scenarios</b><br>Always design for the worst-case.",
        "history_content": "<b>📜 Story</b><br>Transmission line theory matured in 1930s.",
        "rl_perfect": "> 100 dB (Perfect)", "err_calc": "⚠️ Calc Error: {err}", "err_unknown": "Unknown Error"
    })

    # ------------------ Matching 模块 ------------------
    ensure_module(zh_data, "matching")
    ensure_module(en_data, "matching")
    zh_data["matching"].update({
        "intuition_content": "<b>💡 阻抗匹配</b><br>消除反射，实现能量最大化传输。",
        "math_content": "<b>📐 数学基础</b><br>共轭匹配: Zs = Zl*",
        "engineering_content": "<b>⚙️ 避坑指南</b><br>优先使用电容，注意 Q 值权衡。",
        "history_content": "<b>📜 历史</b><br>史密斯圆图的伟大贡献。",
        "btn_load_touchstone": "导入 Touchstone (.s1p/.s2p)"
    })
    en_data["matching"].update({
        "intuition_content": "<b>💡 Matching</b><br>Eliminate reflections for max power.",
        "math_content": "<b>📐 Math</b><br>Conjugate match: Zs = Zl*",
        "engineering_content": "<b>⚙️ Engineering</b><br>Prioritize caps, balance Q-factor.",
        "history_content": "<b>📜 History</b><br>Great contribution of the Smith Chart.",
        "btn_load_touchstone": "Import Touchstone"
    })

    # ------------------ Link Budget 模块 ------------------
    ensure_module(zh_data, "linkbudget")
    ensure_module(en_data, "linkbudget")
    zh_data["linkbudget"].update({
        "intuition_content": "<b>📡 链路预算</b><br>计算信号从发射端到接收端的收支明细。",
        "math_content": "<b>📐 弗里斯公式</b><br>Prx = Ptx + Gtx + Grx - Loss",
        "engineering_content": "<b>⚙️ 经验参考</b><br>必须留有足够的衰落余量。",
        "history_content": "<b>📜 背景</b><br>弗里斯于 1946 年提出。"
    })
    en_data["linkbudget"].update({
        "intuition_content": "<b>📡 Link Budget</b><br>Calculate the balance of signal from TX to RX.",
        "math_content": "<b>📐 Friis Equation</b><br>Prx = Ptx + Gtx + Grx - Loss",
        "engineering_content": "<b>⚙️ Engineering</b><br>Ensure sufficient fade margin.",
        "history_content": "<b>📜 Background</b><br>Proposed by Friis in 1946."
    })

    # ------------------ Impedance 模块 ------------------
    ensure_module(zh_data, "impedance")
    ensure_module(en_data, "impedance")
    zh_data["impedance"].update({
        "tool_name": "特性阻抗", "tool_desc": "各种传输线结构的特性阻抗计算",
        "group_mode": "结构模式选择", "radio_coax": "同轴线 (Coaxial)", "radio_ms": "微带线 (Microstrip)", "radio_cpwg": "共面波导 (CPWG)",
        "lbl_er": "介电常数 εᵣ:", "lbl_calc": "计算", "lbl_z0": "阻抗 Z₀",
        "title_detail": "详细推导参数", "detail_er": "有效介电常数", "detail_vel": "传播速度", "detail_cap": "单位长度电容", "detail_ratio": "尺寸比值",
        "title_diagram": "截面示意图", "err_dim": "尺寸必须大于0", "err_z_dim": "输入必须有效", "eval_veri": "验证: Z₀ = ",
        "err_d_D": "外径必须大于内径", "err_z_D": "目标阻抗和外径必须大于0", "err_z_d": "目标阻抗和内径必须大于0",
        "err_z_H": "目标阻抗和介质厚度必须大于0", "err_z_W": "目标阻抗和线宽必须大于0",
        "intuition": "<b>⚡ 什么是特性阻抗？</b><br>传输线特有的波动阻抗值。",
        "math_model": "<b>📐 基础模型</b><br>Z₀ = √(L/C)",
        "eng_content": "<b>⚙️ 工程常用值</b><br>50 Ω 是最常用的射频标准。",
        "history_content": "<b>📜 阻抗标准由来</b><br>30Ω 功率和 77Ω 损耗的折中。"
    })
    en_data["impedance"].update({
        "tool_name": "Impedance", "tool_desc": "Char. impedance calculator",
        "group_mode": "Structure Mode", "radio_coax": "Coaxial", "radio_ms": "Microstrip", "radio_cpwg": "CPWG",
        "lbl_er": "Dielectric εᵣ:", "lbl_calc": "Calc", "lbl_z0": "Impedance Z₀",
        "title_detail": "Details", "detail_er": "Eff. Er", "detail_vel": "Velocity", "detail_cap": "Cap/m", "detail_ratio": "Ratio",
        "title_diagram": "Diagram", "err_dim": "Dim > 0", "err_z_dim": "Invalid input", "eval_veri": "Veri: Z₀ = ",
        "err_d_D": "D must be > d", "err_z_D": "Z and D must be > 0", "err_z_d": "Z and d must be > 0",
        "err_z_H": "Z and H must be > 0", "err_z_W": "Z and W must be > 0",
        "intuition": "<b>⚡ What is Z₀?</b><br>Specific wave impedance of a line.",
        "math_model": "<b>📐 Model</b><br>Z₀ = √(L/C)",
        "eng_content": "<b>⚙️ Engineering</b><br>50 Ω is standard in RF.",
        "history_content": "<b>📜 Standard Origins</b><br>Compromise between 30Ω and 77Ω."
    })

    # ------------------ Waveguide 模块 ------------------
    ensure_module(zh_data, "waveguide")
    ensure_module(en_data, "waveguide")
    zh_data["waveguide"].update({
        "tool_name": "波导法兰", "tool_desc": "标准波导及法兰速查",
        "lbl_filter_control": "🔍 筛选与控制", "lbl_filter_ieee_band": "按 IEEE 频段筛选:",
        "opt_all_bands": "全部频段", "opt_band_suffix": "频段",
        "lbl_search_waveguide": "搜索波导:", "ph_search_waveguide": "输入 WR 编号或频率",
        "lbl_table_info_title": "表格数据说明:", "lbl_table_info_eia": "• 依据 EIA RS-261",
        "lbl_table_info_mil": "• 依据 MIL-DTL-3922", "lbl_table_info_multi_flange": "• 适配多种法兰",
        "lbl_table_info_cover_choke": "  Cover/Choke 型号", "lbl_table_info_no_std_flange": "• '—' 无标准法兰",
        "lbl_table_info_custom_flange": "  通常为非标",
        "tbl_col_wr": "WR 编号", "tbl_col_iec": "IEC", "tbl_col_dim": "尺寸 (mm)",
        "tbl_col_fc": "截止频率", "tbl_col_freq_range": "工作频段", "tbl_col_ieee_band": "IEEE 频段",
        "tbl_col_cover_flange": "Cover 法兰", "tbl_col_choke_flange": "Choke 法兰",
        "eng_title": "选型指南", "eng_basic_principles": "基本原则", "eng_bp_1": "单模传输原则", "eng_bp_2": "带宽推荐",
        "eng_bp_3": "截止频率公式", "eng_bp_4": "长宽比", "eng_std_ratio": "标准比",
        "eng_flange_selection": "法兰选型", "eng_flat_flange": "平法兰", "eng_flat_desc": "结构简单",
        "eng_choke_flange": "扼流法兰", "eng_choke_desc": "扼流结构", "eng_pair_usage": "配对建议",
        "eng_multi_stds": "多重标准", "eng_mil_std": "美军标", "eng_iec_std": "国际标",
        "eng_cprf": "CPRF标", "eng_cmr": "CMR标", "eng_common_pitfalls": "常见误区",
        "eng_cp_1": "命名陷阱", "eng_cp_2": "对准精度", "eng_cp_3": "定位销需求",
        "his_title": "历史背景", "his_theory": "理论定义", "his_theory_desc": "瑞利勋爵的贡献",
        "his_experiment": "实验验证", "his_exp_desc": "贝尔实验室实验", "his_ww2": "二战爆发",
        "his_ww2_desc": "雷达技术推动", "his_flange_stds": "法兰标准演进", "his_flange_desc": "UG 系列由来",
        "eng_content": "<b>🏗️ {t_eng_title}</b>", "history_content": "<b>📜 {t_history_title}</b>"
    })
    en_data["waveguide"].update({
        "tool_name": "WG Table", "tool_desc": "Waveguide reference",
        "lbl_filter_control": "🔍 Control", "lbl_filter_ieee_band": "Filter Band:",
        "opt_all_bands": "All", "opt_band_suffix": "Band",
        "lbl_search_waveguide": "Search:", "ph_search_waveguide": "Search WR#...",
        "lbl_table_info_title": "Info:", "lbl_table_info_eia": "• EIA RS-261",
        "lbl_table_info_mil": "• MIL-DTL-3922", "lbl_table_info_multi_flange": "• Multi flanges",
        "lbl_table_info_cover_choke": "  Cover/Choke lists", "lbl_table_info_no_std_flange": "• '—' No std",
        "lbl_table_info_custom_flange": "  Custom usage",
        "tbl_col_wr": "WR No.", "tbl_col_iec": "IEC", "tbl_col_dim": "Dim (mm)",
        "tbl_col_fc": "Cutoff", "tbl_col_freq_range": "Range", "tbl_col_ieee_band": "Band",
        "tbl_col_cover_flange": "Cover", "tbl_col_choke_flange": "Choke",
        "eng_title": "Engineering", "eng_basic_principles": "Principles", "eng_bp_1": "Single mode", "eng_bp_2": "Bandwidth",
        "eng_bp_3": "Formula", "eng_bp_4": "Aspect ratio", "eng_std_ratio": "Ratio",
        "eng_flange_selection": "Flanges", "eng_flat_flange": "Flat", "eng_flat_desc": "Regular",
        "eng_choke_flange": "Choke", "eng_choke_desc": "With groove", "eng_pair_usage": "Pairing",
        "eng_multi_stds": "Standards", "eng_mil_std": "MIL", "eng_iec_std": "IEC",
        "eng_cprf": "CPRF", "eng_cmr": "CMR", "eng_common_pitfalls": "Pitfalls",
        "eng_cp_1": "Naming", "eng_cp_2": "Alignment", "eng_cp_3": "Locating pins",
        "his_title": "History", "his_theory": "Theory", "his_theory_desc": "Lord Rayleigh",
        "his_experiment": "Experiment", "his_exp_desc": "Bell Labs", "his_ww2": "WWII",
        "his_ww2_desc": "Radar push", "his_flange_stds": "Evolution", "his_flange_desc": "UG Background",
        "eng_content": "<b>🏗️ {t_eng_title}</b>", "history_content": "<b>📜 {t_history_title}</b>"
    })

    # ------------------ E-Series 模块 ------------------
    ensure_module(zh_data, "eseries")
    ensure_module(en_data, "eseries")
    zh_data["eseries"].update({
        "math_content": "<b>📐 数学基础</b><br>基于 10 的 n 次方根对数间距。",
        "history_content": "<b>📜 历史</b><br>由 Vitold Belevitch 在 1952 年提出。"
    })
    en_data["eseries"].update({
        "math_content": "<b>📐 Mathematics</b><br>Logarithmic spacing based on roots of 10.",
        "history_content": "<b>📜 History</b><br>Proposed by Belevitch in 1952."
    })

    with open(zh_path, 'w', encoding='utf-8') as f:
        json.dump(zh_data, f, ensure_ascii=False, indent=4)
    with open(en_path, 'w', encoding='utf-8') as f:
        json.dump(en_data, f, ensure_ascii=False, indent=4)
    
    print("Success: Mega i18n merged.")

if __name__ == "__main__":
    merge_deep_dive()
