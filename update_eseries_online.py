import json
import os

zh_path = r'e:\AI_project\RF-Antenna-Toolkit\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\RF-Antenna-Toolkit\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f:
    zh = json.load(f)

with open(en_path, 'r', encoding='utf-8') as f:
    en = json.load(f)

# eseries
if 'eseries' not in zh: zh['eseries'] = {}
zh['eseries'].update({
    "desc_e6": "基础容差，适用于早期粗精度元件或大电解电容",
    "desc_e12": "常规容差，多用于普通电容及非关键电路电阻",
    "desc_e24": "【最常用】标准碳膜/厚膜电阻、主流片式电容及电感",
    "desc_e48": "较高精度，主要用于金属膜电阻 (使用3位有效数字)",
    "desc_e96": "【高精常用】精密金属膜/贴片电阻 (1%阻值必须选用此表)",
    "desc_e192": "最高精度，用于仪器仪表级超精细电阻 (0.5%, 0.25%, 0.1%)",
    "lbl_select_standard": "<b>1. 选择容差标准 (E 系列)</b>",
    "lbl_smart_match": "<b>2. 智能就近匹配</b>",
    "lbl_smart_match_desc": "<span style='color:#718096;font-size:12px;'>输入理论计算值，寻找最接近的标准元件</span>",
    "ph_match_input": "例如: 4700 或 3.8",
    "btn_match": "匹配",
    "table_title_e24": "E24 标准标称值基数 (1.0 ~ 9.9)",
    "lbl_tolerance_std": "容差标准:",
    "lbl_sig_figs": "有效数字:",
    "lbl_digits": "位",
    "lbl_typical_app": "典型应用:",
    "table_title_dynamic": "{0} 标准元器件数值速查表 (×0.01 ~ ×1M)",
    "err_invalid_input": "<span style='color:#E53E3E;'>错误: 请输入有效的正数计算值</span>",
    "target_theoretical": "目标理论值:",
    "best_match": "最匹配的",
    "nominal_val": "标称值:",
    "base_val": "基数",
    "deviation_rate": "偏差率:"
})

if 'eseries' not in en: en['eseries'] = {}
en['eseries'].update({
    "desc_e6": "Basic tolerance, early coarse precision parts or large electrolytics",
    "desc_e12": "Normal tolerance, general capacitors and non-critical resistors",
    "desc_e24": "[Most Common] Std carbon/thick film resistors, mainstream caps/inductors",
    "desc_e48": "Higher precision, mainly metal film resistors (3 sig figs)",
    "desc_e96": "[High Precision] Precision metal film/SMD resistors (1% requires this)",
    "desc_e192": "Highest precision, instrument-grade fine resistors (0.5%, 0.25%, 0.1%)",
    "lbl_select_standard": "<b>1. Select Tolerance Standard (E Series)</b>",
    "lbl_smart_match": "<b>2. Smart Nearest Match</b>",
    "lbl_smart_match_desc": "<span style='color:#718096;font-size:12px;'>Enter theoretical calc value to find nearest std component</span>",
    "ph_match_input": "e.g., 4700 or 3.8",
    "btn_match": "Match",
    "table_title_e24": "E24 Std Nominal Master Base (1.0 ~ 9.9)",
    "lbl_tolerance_std": "Tolerance:",
    "lbl_sig_figs": "Sig Figs:",
    "lbl_digits": "digits",
    "lbl_typical_app": "Typical App:",
    "table_title_dynamic": "{0} Component Values Reference Table (×0.01 ~ ×1M)",
    "err_invalid_input": "<span style='color:#E53E3E;'>Error: Please enter a valid positive calculated value</span>",
    "target_theoretical": "Target Calc:",
    "best_match": "Best Match",
    "nominal_val": "Nominal:",
    "base_val": "Base",
    "deviation_rate": "Deviation:"
})

# online_tools
if 'online_tools' not in zh: zh['online_tools'] = {}
zh['online_tools'].update({
    "tool_name": "在线精品推荐",
    "murata_name": "SimSurfing 元件特性计算器",
    "murata_desc": "全球顶级的被动元器件（电容、电感、滤波器、巴伦）S参数、阻抗曲线与频率响应一键在线出图查看系统。",
    "adi_filter_name": "Analog Filter Wizard",
    "adi_filter_desc": "强大的有源及无源滤波器在线合成工具。支持多拓扑（巴特沃斯、切比雪夫等）极点设计，自动选配运放并出具理想/真实响应图。",
    "adisimrf_name": "ADIsimRF 信号链系统管家",
    "adisimrf_desc": "用于计算复杂射频微波信号链的级联增益、噪声系数 (NF)、1dB压缩点 (P1dB) 及 IP3 互调指标的核心在线神器。",
    "ti_power_name": "WEBENCH® Power Designer",
    "ti_power_desc": "射频供电首选方案！输入系统的核心低噪供电需求，自动生成最佳电源拓扑（DC-DC/LDO）、原理图、BOM清单及稳态热仿真图。",
    "qorvo_matchcalc_name": "MatchCalc 射频匹配计算",
    "qorvo_matchcalc_desc": "偏向纯微波实战射频通道的轻量级匹配阻抗计算、微波级联评估平台（史密斯圆图辅助网络综合匹配设计）。",
    "lbl_title": "🌐 精品在线实战工具推荐",
    "lbl_subtitle": "以下皆为精挑细选的 **全球半导体大厂官方无墙** 权威工具，点击卡片即可在本地浏览器安全快速打开：",
    "btn_open": "🚀 浏览器打开工具",
    "footer_disclaimer": "免责声明：以上推荐平台各项权利均属于其原开发公司及半导体厂商。本页面仅提供便捷外链访问。"
})

if 'online_tools' not in en: en['online_tools'] = {}
en['online_tools'].update({
    "tool_name": "Online Tools Hub",
    "murata_name": "SimSurfing Component Calculator",
    "murata_desc": "Top global system for 1-click online viewing of S-parameters, impedance curves, and frequency responses for passive components (caps, inductors, filters, baluns).",
    "adi_filter_name": "Analog Filter Wizard",
    "adi_filter_desc": "Powerful active/passive filter synthesis tool. Supports pole design for multiple topologies (Butterworth, Chebyshev), auto-selects OpAmps & outputs ideal/real responses.",
    "adisimrf_name": "ADIsimRF Signal Chain Manager",
    "adisimrf_desc": "Core online artifact for calculating cascaded gain, NF, P1dB, and IP3 intermodulation specs for complex RF/microwave signal chains.",
    "ti_power_name": "WEBENCH® Power Designer",
    "ti_power_desc": "Top choice for RF power! Enter core low-noise power needs to auto-generate optimal topology (DC-DC/LDO), schematics, BOM, and thermal sims.",
    "qorvo_matchcalc_name": "MatchCalc RF Matching",
    "qorvo_matchcalc_desc": "Lightweight matching impedance calculator and microwave cascade evaluation platform focusing on pure microwave practical RF channels (Smith Chart assisted).",
    "lbl_title": "🌐 Premium Online RF Tools Hub",
    "lbl_subtitle": "Below are handpicked authoritative tools from **global semiconductor giants (no firewall needed)**. Click a card to open securely in your local browser:",
    "btn_open": "🚀 Open Tool in Browser",
    "footer_disclaimer": "Disclaimer: All rights to the recommended platforms belong to their original developers/IC vendors. This page only provides convenient external links."
})

with open(zh_path, 'w', encoding='utf-8') as f:
    json.dump(zh, f, indent=4, ensure_ascii=False)

with open(en_path, 'w', encoding='utf-8') as f:
    json.dump(en, f, indent=4, ensure_ascii=False)

print("Translation dictionaries updated successfully.")
