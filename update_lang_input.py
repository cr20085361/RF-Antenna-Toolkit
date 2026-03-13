import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

# Input strings
input_trans = {
    'title_aperture': ('天线口径 (最大物理尺寸)', 'Antenna Aperture (Max Dimension)'),
    'radio_direct': ('直接输入 D', 'Direct D'),
    'radio_rect': ('矩形 (长×宽)', 'Rectangular (L×W)'),
    'radio_circ': ('圆形 (直径)', 'Circular (Diameter)'),
    'place_d': ('天线最大物理尺寸', 'Max physical dimension'),
    'lbl_len': ('长 L:', 'Length L:'),
    'place_len': ('矩形长边', 'Longest side'),
    'lbl_wid': ('宽 W:', 'Width W:'),
    'place_wid': ('矩形短边', 'Shortest side'),
    'lbl_unit': ('尺寸单位:', 'Unit:'),
    'title_scan': ('相控阵波束扫描 (可选)', 'Phased Array Scan (Optional)'),
    'lbl_scan': ('扫描角 θ:', 'Scan Angle θ:'),
    'place_scan': ('默认 0 (法线方向)', 'Default 0 (Boresight)'),
}

for k, (ch, eng) in input_trans.items():
    zh['farfield'][k] = ch
    en['farfield'][k] = eng

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)
