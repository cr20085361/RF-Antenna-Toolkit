# -*- coding: utf-8 -*-
import sys, ast
sys.stdout.reconfigure(encoding='utf-8')

fpath = 'ui/tools/rf/matching_tool.py'
with open(fpath, encoding='utf-8') as f:
    content = f.read()

renames = [
    ('src_group = QGroupBox', 'self._grp_src = QGroupBox'),
    ('src_layout = QGridLayout(src_group)', 'src_layout = QGridLayout(self._grp_src)'),
    ('layout.addWidget(src_group)', 'layout.addWidget(self._grp_src)'),
    ('net_group = QGroupBox', 'self._grp_net = QGroupBox'),
    ('net_layout = QGridLayout(net_group)', 'net_layout = QGridLayout(self._grp_net)'),
    ('layout.addWidget(net_group)', 'layout.addWidget(self._grp_net)'),
    ('ctrl_group = QGroupBox', 'self._grp_ctrl = QGroupBox'),
    ('ctrl_layout = QVBoxLayout(ctrl_group)', 'ctrl_layout = QVBoxLayout(self._grp_ctrl)'),
    ('layout.addWidget(ctrl_group)', 'layout.addWidget(self._grp_ctrl)'),
]
applied = 0
for old, new in renames:
    if old in content:
        content = content.replace(old, new, 1)
        applied += 1
        print(f'Renamed: {old[:50]}')

retranslate_method = (
    '\n'
    '    # ==================== 国际化刷新接口 ====================\n'
    '\n'
    '    def retranslate_ui(self, lang: str = ""):\n'
    '        """语言切换时刷新 UI 文字"""\n'
    '        super().retranslate_ui(lang)\n'
    '        if hasattr(self, "_grp_src"):\n'
    '            self._grp_src.setTitle(tr("matching.group_src_load_impedance"))\n'
    '        if hasattr(self, "_grp_net"):\n'
    '            self._grp_net.setTitle(tr("matching.group_matching_network"))\n'
    '        if hasattr(self, "_grp_ctrl"):\n'
    '            self._grp_ctrl.setTitle(tr("matching.group_element_params"))\n'
    '\n'
)

marker = '    # 知识面板 (简略)'
if marker in content:
    content = content.replace(marker, retranslate_method + marker, 1)
    applied += 1
    print('Inserted at marker: 知识面板')
else:
    marker2 = '    def get_intuition_content'
    if marker2 in content:
        content = content.replace(marker2, retranslate_method + marker2, 1)
        applied += 1
        print('Inserted before get_intuition_content')

try:
    ast.parse(content)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'[OK] matching_tool.py: {applied} changes, syntax OK')
except SyntaxError as e:
    print(f'[FAIL] syntax error: {e}')
