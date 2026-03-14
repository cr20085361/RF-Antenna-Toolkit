# -*- coding: utf-8 -*-
# fix_retranslate.py - 安全地为 bandwidth_tool.py 添加 retranslate_ui
# 使用行号定位+替换，避免中文匹配问题

import sys
sys.stdout.reconfigure(encoding='utf-8')

def fix_bandwidth_tool():
    fpath = 'ui/tools/antenna/bandwidth_tool.py'
    with open(fpath, encoding='utf-8') as f:
        lines = f.readlines()

    # 找关键行号
    def find_line(pattern, start=0):
        for i, line in enumerate(lines[start:], start):
            if pattern in line:
                return i
        return -1

    changes = []

    # 1. input_group = QGroupBox -> self._input_group = QGroupBox
    idx = find_line('input_group = QGroupBox(tr(')
    if idx >= 0:
        lines[idx] = lines[idx].replace('input_group = QGroupBox', 'self._input_group = QGroupBox', 1)
        changes.append(f'line {idx+1}: input_group -> self._input_group')
    # input_layout = QVBoxLayout(input_group)
    idx = find_line('input_layout = QVBoxLayout(input_group)')
    if idx >= 0:
        lines[idx] = lines[idx].replace('QVBoxLayout(input_group)', 'QVBoxLayout(self._input_group)', 1)
        changes.append(f'line {idx+1}: VBoxLayout(input_group)')
    # layout.addWidget(input_group) 
    idx = find_line('layout.addWidget(input_group)')
    if idx >= 0:
        lines[idx] = lines[idx].replace('layout.addWidget(input_group)', 'layout.addWidget(self._input_group)', 1)
        changes.append(f'line {idx+1}: addWidget(input_group)')

    # 2. range_radio -> self._range_radio
    idx = find_line('range_radio = QRadioButton(tr(')
    if idx >= 0:
        lines[idx] = lines[idx].replace('range_radio = QRadioButton', 'self._range_radio = QRadioButton', 1)
        changes.append(f'line {idx+1}: range_radio -> self._range_radio')
    for pattern in ['range_radio.setChecked', 'addButton(range_radio', 'addWidget(range_radio']:
        idx = find_line(pattern)
        if idx >= 0:
            lines[idx] = lines[idx].replace('range_radio', 'self._range_radio', 1)

    # 3. center_bw_radio -> self._center_bw_radio
    idx = find_line('center_bw_radio = QRadioButton')
    if idx >= 0:
        lines[idx] = lines[idx].replace('center_bw_radio = QRadioButton', 'self._center_bw_radio = QRadioButton', 1)
        changes.append(f'line {idx+1}: center_bw_radio -> self._center_bw_radio')
    for pattern in ['addButton(center_bw_radio', 'addWidget(center_bw_radio']:
        idx = find_line(pattern)
        if idx >= 0:
            lines[idx] = lines[idx].replace('center_bw_radio', 'self._center_bw_radio', 1)

    # 4. center_fbw_radio -> self._center_fbw_radio
    idx = find_line('center_fbw_radio = QRadioButton')
    if idx >= 0:
        lines[idx] = lines[idx].replace('center_fbw_radio = QRadioButton', 'self._center_fbw_radio = QRadioButton', 1)
        changes.append(f'line {idx+1}: center_fbw_radio -> self._center_fbw_radio')
    for pattern in ['addButton(center_fbw_radio', 'addWidget(center_fbw_radio']:
        idx = find_line(pattern)
        if idx >= 0:
            lines[idx] = lines[idx].replace('center_fbw_radio', 'self._center_fbw_radio', 1)

    # 5. calc_button -> self._calc_button
    idx = find_line('calc_button = QPushButton(tr(')
    if idx >= 0:
        lines[idx] = lines[idx].replace('calc_button = QPushButton', 'self._calc_button = QPushButton', 1)
        changes.append(f'line {idx+1}: calc_button -> self._calc_button')
    for pattern in ['calc_button.setObjectName', 'calc_button.setCursor', 'calc_button.clicked', 'addWidget(calc_button']:
        idx = find_line(pattern)
        if idx >= 0:
            lines[idx] = lines[idx].replace('calc_button', 'self._calc_button', 1)

    # 6. quality_title -> self._quality_title_lbl
    idx = find_line('quality_title = QLabel(tr("bandwidth.quality_eval')
    if idx >= 0:
        lines[idx] = lines[idx].replace('quality_title = QLabel', 'self._quality_title_lbl = QLabel', 1)
        changes.append(f'line {idx+1}: quality_title -> self._quality_title_lbl')
    for pattern in ['quality_title.setObjectName', 'quality_layout.addWidget(quality_title']:
        idx = find_line(pattern)
        if idx >= 0:
            lines[idx] = lines[idx].replace('quality_title', 'self._quality_title_lbl', 1)

    # 7. freq_title -> self._freq_params_lbl
    idx = find_line('freq_title = QLabel(tr("bandwidth.freq_params')
    if idx >= 0:
        lines[idx] = lines[idx].replace('freq_title = QLabel', 'self._freq_params_lbl = QLabel', 1)
        changes.append(f'line {idx+1}: freq_title -> self._freq_params_lbl')
    for pattern in ['freq_title.setObjectName', 'freq_layout.addWidget(freq_title']:
        idx = find_line(pattern)
        if idx >= 0:
            lines[idx] = lines[idx].replace('freq_title', 'self._freq_params_lbl', 1)

    # 8. freq grid: QLabel(tr("bandwidth.lbl_*")) -> save refs
    idx = find_line('"bandwidth.lbl_center_freq"')
    if idx >= 0:
        original = lines[idx]
        indent = len(original) - len(original.lstrip())
        spaces = ' ' * indent
        lines[idx] = f'{spaces}self._lbl_center_freq = QLabel(tr("bandwidth.lbl_center_freq"))\n{spaces}freq_grid.addWidget(self._lbl_center_freq, 0, 0)\n'
        changes.append(f'line {idx+1}: lbl_center_freq saved')

    idx = find_line('"bandwidth.lbl_lower_freq"')
    if idx >= 0:
        original = lines[idx]
        indent = len(original) - len(original.lstrip())
        spaces = ' ' * indent
        lines[idx] = f'{spaces}self._lbl_lower_freq = QLabel(tr("bandwidth.lbl_lower_freq"))\n{spaces}freq_grid.addWidget(self._lbl_lower_freq, 1, 0)\n'
        changes.append(f'line {idx+1}: lbl_lower_freq saved')

    idx = find_line('"bandwidth.lbl_upper_freq"')
    if idx >= 0:
        original = lines[idx]
        indent = len(original) - len(original.lstrip())
        spaces = ' ' * indent
        lines[idx] = f'{spaces}self._lbl_upper_freq = QLabel(tr("bandwidth.lbl_upper_freq"))\n{spaces}freq_grid.addWidget(self._lbl_upper_freq, 1, 2)\n'
        changes.append(f'line {idx+1}: lbl_upper_freq saved')

    # 9. In create_result_panel, init result_title_labels before results_grid
    idx = find_line('# 带宽指标结果网格')
    if idx >= 0:
        indent = '        '
        init_code = (
            f'{indent}# 结果卡片标题引用字典 (用于 retranslate_ui)\n'
            f'{indent}self._result_title_keys = {{\n'
            f'{indent}    "abs_bw": "bandwidth.res_abs_bw",\n'
            f'{indent}    "fbw": "bandwidth.res_fbw",\n'
            f'{indent}    "octave": "bandwidth.res_octave",\n'
            f'{indent}    "q_factor": "bandwidth.res_q_factor",\n'
            f'{indent}}}\n'
            f'{indent}self._result_title_labels = {{}}\n'
        )
        lines.insert(idx, init_code)
        changes.append(f'line {idx+1}: inserted result_title_labels init')

    # 10. In _create_result_card: add title_label to dict after addWidget
    idx = find_line('title_label.setObjectName("ResultTitle")')
    if idx >= 0:
        # Look for the next addWidget line
        next_idx = find_line('layout.addWidget(title_label)', idx)
        if next_idx >= 0:
            indent = ' ' * 8
            lines.insert(next_idx + 1, f'{indent}if hasattr(self, "_result_title_labels"):\n{indent}    self._result_title_labels[key] = title_label\n')
            changes.append(f'line {next_idx+2}: inserted result_title_labels[key] = title_label')

    # 11. Insert retranslate_ui before "四维度知识内容"
    idx = find_line('# ==================== 四维度知识内容 ====================')
    if idx >= 0:
        retranslate = '''
    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新所有 UI 文字"""
        super().retranslate_ui(lang)
        # 输入面板
        if hasattr(self, '_input_group'):
            self._input_group.setTitle(tr("bandwidth.input_method"))
        if hasattr(self, '_range_radio'):
            self._range_radio.setText(tr("bandwidth.method_range"))
        if hasattr(self, '_center_bw_radio'):
            self._center_bw_radio.setText(tr("bandwidth.method_center_bw"))
        if hasattr(self, '_center_fbw_radio'):
            self._center_fbw_radio.setText(tr("bandwidth.method_center_fbw"))
        if hasattr(self, '_lower_freq_input'):
            self._lower_freq_input.setPlaceholderText(tr("bandwidth.lower_freq"))
        if hasattr(self, '_upper_freq_input'):
            self._upper_freq_input.setPlaceholderText(tr("bandwidth.upper_freq"))
        if hasattr(self, '_center_freq_input'):
            self._center_freq_input.setPlaceholderText(tr("bandwidth.center_freq"))
        if hasattr(self, '_center_freq2_input'):
            self._center_freq2_input.setPlaceholderText(tr("bandwidth.center_freq"))
        if hasattr(self, '_abs_bw_input'):
            self._abs_bw_input.setPlaceholderText(tr("bandwidth.abs_bw"))
        if hasattr(self, '_fbw_input'):
            self._fbw_input.setPlaceholderText(tr("bandwidth.fbw_0_200"))
        if hasattr(self, '_calc_button'):
            self._calc_button.setText(tr("bandwidth.btn_calculate"))
        # 结果面板
        if hasattr(self, '_quality_title_lbl'):
            self._quality_title_lbl.setText(tr("bandwidth.quality_eval"))
        if hasattr(self, '_freq_params_lbl'):
            self._freq_params_lbl.setText(tr("bandwidth.freq_params"))
        if hasattr(self, '_lbl_center_freq'):
            self._lbl_center_freq.setText(tr("bandwidth.lbl_center_freq"))
        if hasattr(self, '_lbl_lower_freq'):
            self._lbl_lower_freq.setText(tr("bandwidth.lbl_lower_freq"))
        if hasattr(self, '_lbl_upper_freq'):
            self._lbl_upper_freq.setText(tr("bandwidth.lbl_upper_freq"))
        # 结果卡片标题
        if hasattr(self, '_result_title_labels') and hasattr(self, '_result_title_keys'):
            for key, i18n_key in self._result_title_keys.items():
                if key in self._result_title_labels:
                    self._result_title_labels[key].setText(tr(i18n_key))

'''
        lines.insert(idx, retranslate)
        changes.append(f'line {idx+1}: inserted retranslate_ui method')

    for c in changes:
        print(f'[+] {c}')

    new_content = ''.join(lines)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'\nTotal {len(changes)} changes applied. File saved.')

    import ast
    try:
        ast.parse(new_content)
        print('Syntax check: OK')
    except SyntaxError as e:
        print(f'Syntax check: FAILED - {e}')


if __name__ == '__main__':
    fix_bandwidth_tool()
