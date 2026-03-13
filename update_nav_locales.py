import json
import os

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

nav_entries = {
    # Antenna Tools
    "tool_wavelength": ("波长计算", "Wavelength"),
    "tool_bandwidth": ("带宽计算", "Bandwidth"),
    "tool_gain": ("增益计算", "Gain Calc"),
    "tool_los": ("视距计算", "Line-of-Sight"),
    "tool_sensitivity": ("系统灵敏度计算", "Sensitivity"),
    "tool_phased_array": ("相控阵计算", "Phased Array"),
    "tool_range": ("收发距离计算", "Link Range"),
    
    # RF Tools
    "tool_vswr": ("驻波计算", "VSWR Calc"),
    "tool_cascade": ("级联驻波", "Cascade VSWR"),
    "tool_impedance": ("阻抗计算", "Impedance"),
    "tool_attenuator": ("衰减计算", "Attenuator"),
    "tool_matching": ("阻抗匹配", "Matching"),
    "tool_link_budget": ("链路预算", "Link Budget"),
    
    # Reference
    "tool_band_table": ("频段分类", "Freq Bands"),
    "tool_waveguide_table": ("波导法兰", "Waveguide"),
    "tool_connector_table": ("连接器选型", "Connector"),
    "tool_eseries_table": ("标称值速查", "E-Series"),
    "tool_online_tools": ("精品在线工具", "Online Tools")
}

for k, (zh_str, en_str) in nav_entries.items():
    zh['nav'][k] = zh_str
    en['nav'][k] = en_str

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)

print("Updated nav items in loclaes JSON!")
