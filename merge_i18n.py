import json
import os

def merge_json(target_path, source_data):
    if not os.path.exists(target_path):
        print(f"Error: {target_path} not found")
        return
        
    with open(target_path, 'r', encoding='utf-8') as f:
        target_data = json.load(f)
        
    for module, keys in source_data.items():
        if module not in target_data:
            target_data[module] = {}
        for key, value in keys.items():
            target_data[module][key] = value

    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(target_data, f, indent=4, ensure_ascii=False)

en_overrides = {
    "linkbudget": {
        "status_excellent": "Link Excellent",
        "status_good": "Link Good",
        "status_fail": "Link Fail",
        "tip_move_left": "Move Left",
        "tip_move_right": "Move Right",
        "tip_remove": "Remove Stage"
    },
    "matching": {
        "title_smith_chart": "Smith Chart",
        "lbl_element_value": "Value",
        "lbl_original": "Original",
        "lbl_load": "Load",
        "lbl_matched": "Matched"
    },
    "impedance": {
        "tool_name": "Impedance Tool"
    },
    "vswr": {
        "math_model": "Math Model",
        "intuition": "Intuition",
        "history_content": "History",
        "eng_content": "Engineering",
        "math_core_formula": "Formula",
        "math_gamma": "Gamma",
        "math_zl": "Zl",
        "math_vswr_gamma": "VSWR-Gamma",
        "math_rl": "Return Loss",
        "math_ml": "Mismatch Loss",
        "eng_ref": "Ref",
        "eng_ref_1": "Pro",
        "eng_ref_2": "Common",
        "eng_ref_3": "Acceptable",
        "eng_ref_4": "Bad",
        "eng_notice": "Notice",
        "eng_err_title": "Cons",
        "eng_err_1": "Heat",
        "eng_err_2": "Efficiency",
        "eng_err_3": "Protect",
        "eng_tip_title": "Tip",
        "eng_tip_desc": "Measure",
        "his_title": "History",
        "his_era1": "1820",
        "his_era1_v": "Fresnel",
        "his_era2": "1888",
        "his_era2_v": "Hertz",
        "his_quote": "Quote",
        "dd_what_is": "What is",
        "dd_desc_1": "Desc",
        "dd_key_concept": "Concept",
        "dd_key_desc": "Desc",
        "dd_vswr_1": "1",
        "dd_vswr_inf": "inf",
        "dd_core": "Core",
        "dd_core_desc": "Desc",
        "err_power_req": "Req Pwr",
        "err_no_comp": "No Comp",
        "err_unknown": "Unknown"
    }
}

# 中文 FIXME
zh_fixes = {
    "impedance": {"tool_name": "阻抗工具"},
    "linkbudget": {
        "tip_move_left": "向左移动",
        "tip_move_right": "向右移动",
        "tip_remove": "删除此级",
        "status_excellent": "链路极佳",
        "status_good": "符合要求",
        "status_fail": "链路中断"
    },
    "vswr": {
        "math_model": "数学模型",
        "intuition": "直观理解",
        "history_content": "历史背景",
        "eng_content": "工程参考",
        "math_core_formula": "核心公式",
        "math_gamma": "反射系数",
        "math_zl": "负载阻抗",
        "math_vswr_gamma": "VSWR-Gamma 关系",
        "math_rl": "回波损耗",
        "math_ml": "失配损耗",
        "eng_ref": "参考",
        "eng_ref_1": "优",
        "eng_ref_2": "良",
        "eng_ref_3": "中",
        "eng_ref_4": "差",
        "eng_notice": "注意",
        "eng_err_title": "后果",
        "eng_err_1": "发热",
        "eng_err_2": "效率",
        "eng_err_3": "保护",
        "eng_tip_title": "提示",
        "eng_tip_desc": "测量",
        "his_title": "历史",
        "his_era1": "1820",
        "his_era1_v": "菲涅尔",
        "his_era2": "1888",
        "his_era2_v": "赫兹",
        "his_quote": "语录",
        "dd_what_is": "什么是",
        "dd_desc_1": "描述",
        "dd_key_concept": "概念",
        "dd_key_desc": "描述",
        "dd_vswr_1": "1",
        "dd_vswr_inf": "inf",
        "dd_core": "核心",
        "dd_core_desc": "描述",
        "err_power_req": "需功率",
        "err_no_comp": "无法补偿",
        "err_unknown": "未知"
    }
}

locales_dir = os.path.join(os.getcwd(), "assets", "locales")
merge_json(os.path.join(locales_dir, "zh_CN.json"), zh_fixes)
merge_json(os.path.join(locales_dir, "en_US.json"), en_overrides)

print("Merged successfully!")
