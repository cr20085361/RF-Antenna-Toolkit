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

    # ------------------ Antenna Gain 模块 (全量补齐) ------------------
    ensure_module(zh_data, "gain")
    ensure_module(en_data, "gain")
    zh_data["gain"].update({
        "tool_name": "天线增益", "tool_desc": "根据波束宽度或口径计算天线增益",
        "calc_method": "计算方法选择", "method_beamwidth": "波束宽度法 (3dB波束角)",
        "theta_e": "E面 θ_E:", "placeholder_theta": "E面波束角", "theta_h": "H面 θ_H:", "placeholder_theta_h": "H面波束角",
        "constant_k": "公式常数 K:", "const_ieee": "41253 (IEEE标准)", "const_uniform": "32400 (均匀口径)", "const_typical": "26000 (典型值)",
        "method_aperture": "口径效率法", "aperture_shape": "口径形状:", "shape_circ": "⚪ 圆形 (抛物面等)", "shape_rect": "▭ 矩形 (喇叭天线等)",
        "radio_circ": "⚪ 圆形 (抛物面等)", "radio_rect": "▭ 矩形 (喇叭天线等)",
        "aperture_diameter": "口径直径 D:", "ph_diameter": "直径尺寸", "aperture_width": "口径宽度 W:", "ph_width": "宽度尺寸",
        "aperture_height": "口径高度 H:", "ph_height": "高度尺寸", "work_freq": "工作频率 f:", "ph_freq": "频率值",
        "aperture_efficiency": "口径效率 η:", "hint_circ": "(圆形典型0.55)", "hint_rect": "(矩形典型0.60)",
        "method_convert": "增益单位转换", "ph_gain_val": "增益值", "linear_val": "线性值", "btn_calc": "计算增益",
        "type_eval": "天线类型评估", "res_gain": "📡 增益计算结果", "res_dbi": "增益 (dBi):", "res_dbd": "增益 (dBd):",
        "res_linear": "线性增益 (Ratio):", "res_est_beam": "📐 估算波束宽度 (对称假设)", "est_res": "≈ {0:.1f}° × {1:.1f}°",
        "err_no_e": "⚠️ 请输入E面波束宽度", "err_no_h": "⚠️ 请输入H面波束宽度", "err_format_beam": "⚠️ 波束角格式错误",
        "err_beam_positive": "⚠️ 波束宽度必须为正值", "err_beam_too_large": "⚠️ 波束宽度不能超过180°",
        "err_no_freq": "⚠️ 请输入工作频率", "err_no_eff": "⚠️ 请输入口径效率", "err_format_fe": "⚠️ 频率/效率格式错误",
        "err_freq_positive": "⚠️ 频率必须为正值", "err_eff_range": "⚠️ 效率必须在(0,1]之间",
        "err_no_dia": "⚠️ 请输入口径直径", "err_format_dia": "⚠️ 直径格式错误", "err_dia_positive": "⚠️ 直径必须为正值",
        "err_no_w": "⚠️ 请输入口径宽度", "err_no_h_dim": "⚠️ 请输入口径高度", "err_format_dim": "⚠️ 尺寸格式错误",
        "err_w_positive": "⚠️ 宽度必须为正值", "err_h_positive": "⚠️ 高度必须为正值",
        "err_no_gain": "⚠️ 请输入增益值", "err_format_gain": "⚠️ 增益值格式错误", "err_linear_positive": "⚠️ 线性增益必须为正值",
        "err_calc": "⚠️ 计算错误: {0}", "err_unknown": "未知错误",
        "dd_what_is": "什么是天线增益？", "dd_desc_1": "天线增益描述天线在特定方向上聚焦能量的能力。",
        "dd_key_concept": "关键概念", "dd_dbi_desc": "相对于理想全向天线的增益 (Isotropic)",
        "dd_dbd_desc": "相对于半波偶极子的增益 (Dipole)", "dd_core": "核心理解",
        "dd_core_desc": "天线并不\"放大\"信号，而是通过方向性重新分配能量。",
        "dd_formula": "增益计算模型", "dd_method_beam": "波束宽度法", "dd_beam_desc": "注: θ 为 -3dB 半功率波束宽度",
        "dd_method_apt": "口径效率法", "dd_apt_desc": "其中 η 为效率, D 为等效直径",
        "dd_unit_conv": "单位转换关系", "dd_ref_title": "典型天线增益参考", "dd_dipole": "半波偶极子",
        "dd_yagi": "八木天线", "dd_horn": "标准喇叭天线", "dd_para": "大口径抛物面",
        "dd_notice": "工程注意事项", "dd_err_title": "常见误区", "dd_err_1": "近似公式存在 1-2dB 误差",
        "dd_err_2": "常数 K 随天线类型变化需校准", "dd_tip_title": "设计小贴士", "dd_tip_1": "提高效率 η 是提升增益最经济的手段。"
    })
    en_data["gain"].update({
        "tool_name": "Antenna Gain", "tool_desc": "Calculate gain from beamwidth or aperture",
        "calc_method": "Calculation Method", "method_beamwidth": "Beamwidth Method (3dB BW)",
        "theta_e": "E-plane θ_E:", "placeholder_theta": "E-plane BW", "theta_h": "H-plane θ_H:", "placeholder_theta_h": "H-plane BW",
        "constant_k": "Constant K:", "const_ieee": "41253 (IEEE Std)", "const_uniform": "32400 (Uniform)", "const_typical": "26000 (Typical)",
        "method_aperture": "Aperture Method", "aperture_shape": "Aperture Shape:", "shape_circ": "⚪ Circular (Parabolic)", "shape_rect": "▭ Rectangular (Horn)",
        "radio_circ": "⚪ Circular (Parabolic)", "radio_rect": "▭ Rectangular (Horn)",
        "aperture_diameter": "Diameter D:", "ph_diameter": "Size D", "aperture_width": "Width W:", "ph_width": "Size W",
        "aperture_height": "Height H:", "ph_height": "Size H", "work_freq": "Frequency f:", "ph_freq": "Freq value",
        "aperture_efficiency": "Efficiency η:", "hint_circ": "(Circ Typ 0.55)", "hint_rect": "(Rect Typ 0.60)",
        "method_convert": "Gain Conversion", "ph_gain_val": "Gain Val", "linear_val": "Linear", "btn_calc": "Calculate Gain",
        "type_eval": "Antenna Type Evaluation", "res_gain": "📡 Gain Results", "res_dbi": "Gain (dBi):", "res_dbd": "Gain (dBd):",
        "res_linear": "Linear Gain:", "res_est_beam": "📐 Est. Beamwidth (Symm)", "est_res": "≈ {0:.1f}° × {1:.1f}°",
        "err_no_e": "⚠️ Enter E-plane BW", "err_no_h": "⚠️ Enter H-plane BW", "err_format_beam": "⚠️ Invalid BW format",
        "err_beam_positive": "⚠️ BW must be positive", "err_beam_too_large": "⚠️ BW cannot exceed 180°",
        "err_no_freq": "⚠️ Enter Frequency", "err_no_eff": "⚠️ Enter Efficiency", "err_format_fe": "⚠️ Invalid Freq/Eff",
        "err_freq_positive": "⚠️ Freq must be positive", "err_eff_range": "⚠️ Eff must be (0,1]",
        "err_no_dia": "⚠️ Enter Diameter", "err_format_dia": "⚠️ Invalid Diameter", "err_dia_positive": "⚠️ Dia must be positive",
        "err_no_w": "⚠️ Enter Width", "err_no_h_dim": "⚠️ Enter Height", "err_format_dim": "⚠️ Invalid Dim",
        "err_w_positive": "⚠️ Width must be positive", "err_h_positive": "⚠️ Height must be positive",
        "err_no_gain": "⚠️ Enter Gain value", "err_format_gain": "⚠️ Invalid Gain format", "err_linear_positive": "⚠️ Linear must be positive",
        "err_calc": "⚠️ Calc Error: {0}", "err_unknown": "Unknown Error",
        "dd_what_is": "What is Antenna Gain?", "dd_desc_1": "Gain describes the antenna's ability to focus energy.",
        "dd_key_concept": "Key Concepts", "dd_dbi_desc": "Gain rel. to Isotropic source",
        "dd_dbd_desc": "Gain rel. to Half-wave Dipole", "dd_core": "Core Insight",
        "dd_core_desc": "Antennas do not boost power; they redistribute it directionally.",
        "dd_formula": "Calculations", "dd_method_beam": "Beamwidth Method", "dd_beam_desc": "Note: θ is the -3dB beamwidth",
        "dd_method_apt": "Aperture Method", "dd_apt_desc": "η is efficiency, D is effective diameter",
        "dd_unit_conv": "Unit Relations", "dd_ref_title": "Typical Gain Values", "dd_dipole": "Dipole",
        "dd_yagi": "Yagi-Uda", "dd_horn": "Standard Horn", "dd_para": "Large Reflector",
        "dd_notice": "Engineering Notes", "dd_err_title": "Common Pitfalls", "dd_err_1": "Approximation has ~1-2dB error",
        "dd_err_2": "Constant K varies by type", "dd_tip_title": "Design Tip", "dd_tip_1": "Boosting η is the cheapest way to gain."
    })

    # ------------------ Wavelength 模块 (全量补齐) ------------------
    ensure_module(zh_data, "wavelength")
    ensure_module(en_data, "wavelength")
    zh_data["wavelength"].update({
        "tool_name": "波长计算", "tool_desc": "频率与波长互转及传播速度分析",
        "lbl_input_group": "输入参数", "lbl_freq": "频率 f:", "lbl_wave": "波长 λ:",
        "lbl_velocity": "相速度 vₚ:", "lbl_medium": "传播介提示:", "opt_v_c": "真空/空气 (c)",
        "opt_v_custom": "自定义系数", "ph_freq": "频率", "ph_wave": "波长", "ph_vel": "速度 (c)",
        "res_title": "波长分析结果", "res_lambda": "λ =", "res_f": "f =", "res_velocity": "速度 =",
        "err_no_input": "⚠️ 请输入频率或波长中的一个", "err_format": "⚠️ 格式错误", "err_positive": "⚠️ 输入必须为正值",
        "err_vel_range": "⚠️ 相速度不能超过光速 c", "err_calc": "⚠️ 计算错误: {0}",
        "dd_what_is": "什么是波长？", "dd_formula": "波长公式", "dd_eng": "工程意义",
        "dd_history": "发现简史"
    })
    en_data["wavelength"].update({
        "tool_name": "Wavelength", "tool_desc": "Frequency to wavelength conversion",
        "lbl_input_group": "Parameters", "lbl_freq": "Frequency f:", "lbl_wave": "Wavelength λ:",
        "lbl_velocity": "Velocity vₚ:", "lbl_medium": "Medium:", "opt_v_c": "Free Space (c)",
        "opt_v_custom": "Custom Factor", "ph_freq": "Freq", "ph_wave": "Lambda", "ph_vel": "Vel (c)",
        "res_title": "Wavelength Results", "res_lambda": "λ =", "res_f": "f =", "res_velocity": "Vel =",
        "err_no_input": "⚠️ Enter freq or wavelength", "err_format": "⚠️ Invalid format", "err_positive": "⚠️ Must be positive",
        "err_vel_range": "⚠️ Vel cannot exceed c", "err_calc": "⚠️ Calc Error: {0}",
        "dd_what_is": "What is Wavelength?", "dd_formula": "Formula", "dd_eng": "Engineering",
        "dd_history": "History"
    })

    # ------------------ LOS 模块 (全量补齐) ------------------
    ensure_module(zh_data, "los")
    ensure_module(en_data, "los")
    zh_data["los"].update({
        "tool_name": "视距计算", "tool_desc": "计算无线电在地平线上的传播极限视距",
        "lbl_height_input": "端点高度设置", "lbl_h1": "发射端高度 h1:", "lbl_h2": "接收端高度 h2:",
        "lbl_k_factor": "等效地球半径 K:", "hint_k_std": "(标准大气 K=4/3)", "hint_k_custom": "自定义系数",
        "res_title": "视距分析结果", "res_los": "视距距离:", "res_optical": "几何视距:",
        "err_h_positive": "⚠️ 高度必须为正值", "err_calc": "⚠️ 计算错误",
        "dd_what_is": "什么是视距？", "dd_formula": "计算模型", "dd_eng": "工程对策"
    })
    en_data["los"].update({
        "tool_name": "Line of Sight", "tool_desc": "Radio horizon and LOS limit",
        "lbl_height_input": "Height Settings", "lbl_h1": "TX Height h1:", "lbl_h2": "RX Height h2:",
        "lbl_k_factor": "Earth Refraction K:", "hint_k_std": "(Standard K=4/3)", "hint_k_custom": "Custom Factor",
        "res_title": "LOS Results", "res_los": "Radio LOS:", "res_optical": "Optical LOS:",
        "err_h_positive": "⚠️ Height must be > 0", "err_calc": "⚠️ Calc Error",
        "dd_what_is": "What is LOS?", "dd_formula": "Calculation", "dd_eng": "Engineering"
    })

    # ------------------ 统一模块资源注入 ------------------
    ensure_module(zh_data, "bandwidth")
    zh_data["bandwidth"].update({"intuition_content": "<b>💡 什么是天线带宽？</b>", "math_content": "<b>📐 带宽计算模型</b>", "engineering_content": "<b>⚙️ 工程选型指南</b>", "history_content": "<b>📜 频率管理的历史</b>"})
    ensure_module(en_data, "bandwidth")
    en_data["bandwidth"].update({"intuition_content": "<b>💡 What is Antenna Bandwidth?</b>", "math_content": "<b>📐 Math Models</b>", "engineering_content": "<b>⚙️ Engineering Guide</b>", "history_content": "<b>📜 History</b>"})
    
    ensure_module(zh_data, "vswr")
    zh_data["vswr"].update({"intuition":"驻波叠加面","math_model":"VSWR公式","eng_content":"工程参考","history_content":"发现历史"})
    ensure_module(en_data, "vswr")
    en_data["vswr"].update({"intuition":"Standing Wave","math_model":"VSWR Formula","eng_content":"Engineering","history_content":"History"})
    
    ensure_module(zh_data, "attenuator")
    zh_data["attenuator"].update({"intuition":"衰减器本质","math_model":"计算公式","eng_content":"设计指南","history_content":"发展简史"})
    ensure_module(en_data, "attenuator")
    en_data["attenuator"].update({"intuition":"Essence","math_model":"Formulas","eng_content":"Design","history_content":"History"})

    ensure_module(zh_data, "cascade")
    zh_data["cascade"].update({"intuition":"级联驻波","math_model":"级联模型","eng_content":"典型场景","history_content":"故事","rl_perfect":">100dB","err_calc":"错误","err_unknown":"未知"})
    ensure_module(en_data, "cascade")
    en_data["cascade"].update({"intuition":"Cascade VSWR","math_model":"Models","eng_content":"Scenarios","history_content":"Story","rl_perfect":">100dB","err_calc":"Error","err_unknown":"Unknown"})

    ensure_module(zh_data, "matching")
    zh_data["matching"].update({"intuition_content":"阻抗匹配","math_content":"数学基础","engineering_content":"避坑指南","history_content":"历史"})
    ensure_module(en_data, "matching")
    en_data["matching"].update({"intuition_content":"Matching","math_content":"Math","engineering_content":"Engineering","history_content":"History"})

    ensure_module(zh_data, "linkbudget")
    zh_data["linkbudget"].update({"intuition_content":"链路预算","math_content":"弗里斯公式","engineering_content":"经验参考","history_content":"背景"})
    ensure_module(en_data, "linkbudget")
    en_data["linkbudget"].update({"intuition_content":"Link Budget","math_content":"Friis","engineering_content":"Engineering","history_content":"Background"})

    # ------------------ 保存结果 ------------------
    with open(zh_path, 'w', encoding='utf-8') as f:
        json.dump(zh_data, f, ensure_ascii=False, indent=4)
    with open(en_path, 'w', encoding='utf-8') as f:
        json.dump(en_data, f, ensure_ascii=False, indent=4)
    
    print("Success: Final Mega i18n merged for all antenna and RF tools.")

if __name__ == "__main__":
    merge_deep_dive()
