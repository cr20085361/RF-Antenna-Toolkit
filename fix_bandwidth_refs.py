"""
修复 bandwidth_tool.py 中补丁遗漏的变量赋值行
"""
import sys, ast
sys.stdout.reconfigure(encoding='utf-8')

fpath = 'ui/tools/antenna/bandwidth_tool.py'
with open(fpath, encoding='utf-8') as f:
    lines = f.readlines()

def find_line(pattern, start=0):
    for i, line in enumerate(lines[start:], start):
        if pattern in line:
            return i
    return -1

changes = []

# Fix 1: line 61: input_group = QGroupBox -> self._input_group = QGroupBox
idx = find_line('input_group = QGroupBox(')
if idx >= 0:
    lines[idx] = lines[idx].replace('input_group = QGroupBox(', 'self._input_group = QGroupBox(', 1)
    changes.append(f'line {idx+1}: fixed input_group -> self._input_group')

# Fix 2: line 69: range_radio = QRadioButton -> self._range_radio = QRadioButton
idx = find_line('range_radio = QRadioButton(')
if idx >= 0:
    lines[idx] = lines[idx].replace('range_radio = QRadioButton(', 'self._range_radio = QRadioButton(', 1)
    changes.append(f'line {idx+1}: fixed range_radio -> self._range_radio')

# Fix: range_radio.setChecked should be self._range_radio.setChecked (already done, but verify)
idx = find_line('range_radio.setChecked(')
if idx >= 0:
    lines[idx] = lines[idx].replace('range_radio.setChecked(', 'self._range_radio.setChecked(', 1)
    changes.append(f'line {idx+1}: fixed range_radio.setChecked')

# Fix: center_bw_radio = QRadioButton (if not yet fixed)
idx = find_line('center_bw_radio = QRadioButton(')
if idx >= 0:
    lines[idx] = lines[idx].replace('center_bw_radio = QRadioButton(', 'self._center_bw_radio = QRadioButton(', 1)
    changes.append(f'line {idx+1}: fixed center_bw_radio -> self._center_bw_radio')

# Fix: center_fbw_radio = QRadioButton
idx = find_line('center_fbw_radio = QRadioButton(')
if idx >= 0:
    lines[idx] = lines[idx].replace('center_fbw_radio = QRadioButton(', 'self._center_fbw_radio = QRadioButton(', 1)
    changes.append(f'line {idx+1}: fixed center_fbw_radio -> self._center_fbw_radio')

# Fix: calc_button = QPushButton
idx = find_line('calc_button = QPushButton(')
if idx >= 0:
    lines[idx] = lines[idx].replace('calc_button = QPushButton(', 'self._calc_button = QPushButton(', 1)
    changes.append(f'line {idx+1}: fixed calc_button -> self._calc_button')

# Fix calc_button.* -> self._calc_button.*
for pattern in ['calc_button.setObjectName(', 'calc_button.setCursor(', 'calc_button.clicked.connect(']:
    idx = find_line(pattern)
    if idx >= 0:
        old = pattern.split('.')[0] + '.'
        lines[idx] = lines[idx].replace(old, 'self._calc_button.', 1)
        changes.append(f'line {idx+1}: fixed {pattern[:30]}')

# Fix: addWidget(calc_button)
idx = find_line('addWidget(calc_button)')
if idx >= 0:
    lines[idx] = lines[idx].replace('addWidget(calc_button)', 'addWidget(self._calc_button)', 1)
    changes.append(f'line {idx+1}: fixed addWidget(calc_button)')

# Fix quality_title = QLabel -> self._quality_title_lbl = QLabel
idx = find_line('quality_title = QLabel(tr(')
if idx >= 0:
    lines[idx] = lines[idx].replace('quality_title = QLabel(', 'self._quality_title_lbl = QLabel(', 1)
    changes.append(f'line {idx+1}: fixed quality_title -> self._quality_title_lbl')

for pattern in ['quality_title.setObjectName(', 'quality_layout.addWidget(quality_title']:
    idx = find_line(pattern)
    if idx >= 0:
        lines[idx] = lines[idx].replace('quality_title', 'self._quality_title_lbl', 1)
        changes.append(f'line {idx+1}: fixed quality_title ref')

# Fix freq_title = QLabel -> self._freq_params_lbl = QLabel
idx = find_line('freq_title = QLabel(tr(')
if idx >= 0:
    lines[idx] = lines[idx].replace('freq_title = QLabel(', 'self._freq_params_lbl = QLabel(', 1)
    changes.append(f'line {idx+1}: fixed freq_title -> self._freq_params_lbl')

for pattern in ['freq_title.setObjectName(', 'freq_layout.addWidget(freq_title']:
    idx = find_line(pattern)
    if idx >= 0:
        lines[idx] = lines[idx].replace('freq_title', 'self._freq_params_lbl', 1)
        changes.append(f'line {idx+1}: fixed freq_title ref')

for c in changes:
    print(f'[+] {c}')

content = ''.join(lines)
try:
    ast.parse(content)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'\n[OK] {len(changes)} fixes applied, syntax OK')
except SyntaxError as e:
    print(f'\n[FAIL] syntax error: {e}')
