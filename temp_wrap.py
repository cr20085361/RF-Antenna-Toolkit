import re
import os

file_path = r"e:\AI_Project\RF-Antenna-Toolkit\ui\tools\reference\band_table_tool.py"
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace _init_data inner strings
def rep_bandinfo(m):
    name, start, end, l, app, col = m.groups()
    app = app.strip()
    # Generate an i18n key e.g. "bandtable.app_hf" or similar based on name
    safe_name = re.sub(r'[^A-Za-z0-9]', '_', name).lower()
    return f'BandInfo("{name}", "{start}", "{end}", "{l}", tr("bandtable.app_{safe_name}", "{app}"), {col})'

text = re.sub(r'BandInfo\(\"([^\"]+)\",\s*\"([^\"]+)\",\s*\"([^\"]+)\",\s*\"([^\"]+)\",\s*\"([^\"]+)\",\s*([^\)]+)\)', rep_bandinfo, text)

# Replace other GUI text
text = text.replace('QLabel("🔍 筛选与控制")', 'QLabel(tr("band_table.lbl_filter_ctrl", "🔍 筛选与控制"))')
text = text.replace('self._standard_combo.addItem("IEEE (雷达/射频常用)", "IEEE")', 'self._standard_combo.addItem(tr("band_table.std_ieee", "IEEE (雷达/射频常用)"), "IEEE")')
text = text.replace('self._standard_combo.addItem("ITU (国际电联/波段号)", "ITU")', 'self._standard_combo.addItem(tr("band_table.std_itu", "ITU (国际电联/波段号)"), "ITU")')
text = text.replace('self._standard_combo.addItem("NATO (北约/军事)", "NATO")', 'self._standard_combo.addItem(tr("band_table.std_nato", "NATO (北约/军事)"), "NATO")')
text = text.replace('self._standard_combo.addItem("手机通信 (5G/4G/3G/2G)", "CELL")', 'self._standard_combo.addItem(tr("band_table.std_cell", "手机通信 (5G/4G/3G/2G)"), "CELL")')
text = text.replace('self._standard_combo.addItem("卫星导航 (GNSS)", "GNSS")', 'self._standard_combo.addItem(tr("band_table.std_gnss", "卫星导航 (GNSS)"), "GNSS")')
text = text.replace('self._standard_combo.addItem("业余无线电 (Ham)", "HAM")', 'self._standard_combo.addItem(tr("band_table.std_ham", "业余无线电 (Ham)"), "HAM")')
text = text.replace('self._standard_combo.addItem("中国/通用工业习惯", "CN")', 'self._standard_combo.addItem(tr("band_table.std_cn", "中国/通用工业习惯"), "CN")')

text = text.replace('QLabel("搜索频段:")', 'QLabel(tr("band_table.lbl_search", "搜索频段:"))')
text = text.replace('setPlaceholderText("输入名称或频率 (如 \'S\' 或 \'2.4\')")', 'setPlaceholderText(tr("band_table.plh_search", "输入名称或频率 (如 \'S\' 或 \'2.4\')"))')

info_zh = "提示: 不同标准中相同的字母可能代表完全不同的频段。\\n例如 'K' 频段:\\n• IEEE: 18-27 GHz\\n• NATO: 20-40 GHz"
text = text.replace('QLabel(\n            "' + info_zh.replace('\\n', '\n') + '"\n        )', f'QLabel(tr("band_table.lbl_tip", "{info_zh}"))')
text = text.replace('QLabel(\n            "提示: 不同标准中相同的字母可能代表完全不同的频段。\\n例如 \'K\' 频段:\\n• IEEE: 18-27 GHz\\n• NATO: 20-40 GHz"\n        )', f'QLabel(tr("band_table.lbl_tip", "{info_zh}"))')
text = text.replace('QLabel("提示: 不同标准中相同的字母可能代表完全不同的频段。\\n例如 \'K\' 频段:\\n• IEEE: 18-27 GHz\\n• NATO: 20-40 GHz")', f'QLabel(tr("band_table.lbl_tip", "{info_zh}"))')

text = text.replace('["频段名称", "频率范围", "波长范围", "典型应用"]', '[tr("band_table.col_band", "频段名称"), tr("band_table.col_freq_range", "频率范围"), tr("band_table.col_lambda", "波长范围"), tr("band_table.col_app", "典型应用")]')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated band_table_tool.py")
