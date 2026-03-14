"""
全面修复所有工具中遗漏的变量赋值行 NameError
策略: 扫描所有工具，找到 QLayout(xxx_group) 中 xxx_group 未定义的情况并修复
"""
import ast
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

TOOL_FIXES = {
    'ui/tools/rf/cascade_tool.py': [
        # ('QHBoxLayout(input_mode_group)', 'QHBoxLayout(self._grp_input_mode)'),  # just fix the layout call
    ],
}

# More reliable: for each tool file, scan for pattern "QXLayout(xxx)" where xxx is not self.xxx
# and xxx is replaced somewhere in the file to self._grp_xxx

def fix_layout_refs(fpath, old_var, new_var):
    """Replace QXLayout(old_var) with QXLayout(new_var)"""
    with open(fpath, encoding='utf-8') as f:
        content = f.read()
    
    # Replace patterns like QHBoxLayout(old_var), QVBoxLayout(old_var), QGridLayout(old_var)
    patterns = [
        f'QHBoxLayout({old_var})',
        f'QVBoxLayout({old_var})',
        f'QGridLayout({old_var})',
        f'{old_var}.setLayout(',
        f'addWidget({old_var})',
        f'{old_var}.setTitle(',
    ]
    changes = 0
    for p in patterns:
        if p in content:
            new_p = p.replace(old_var, new_var)
            content = content.replace(p, new_p)
            changes += 1
    
    if changes > 0:
        try:
            ast.parse(content)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'[OK] {fpath.split("/")[-1]}: fixed {changes} refs of {old_var} -> {new_var}')
        except SyntaxError as e:
            print(f'[FAIL] {fpath.split("/")[-1]}: syntax error {e}')
    else:
        print(f'[SKIP] {fpath.split("/")[-1]}: no refs to {old_var} found')

# cascade_tool: input_mode_group -> self._grp_input_mode
# (the assignment line was fixed, but layout ref QHBoxLayout(input_mode_group) wasn't fixed)
fix_layout_refs('ui/tools/rf/cascade_tool.py', 'input_mode_group', 'self._grp_input_mode')

# Also check attenuator_tool for similar issues
# - topo_layout = QVBoxLayout(topo_group) -> but the script looks for QVBoxLayout(topo_group)
# Verify each file's layout constructors match what we renamed
FILES_TO_CHECK = [
    ('ui/tools/rf/vswr_tool.py', [
        ('input_group', 'self._grp_input'),
        ('power_group', 'self._grp_power'),
    ]),
    ('ui/tools/rf/attenuator_tool.py', [
        ('topo_group', 'self._grp_topo'),
        ('z0_group', 'self._grp_z0'),
        ('atten_group', 'self._grp_atten'),
        ('series_group', 'self._grp_series'),
    ]),
    ('ui/tools/rf/matching_tool.py', [
        ('src_group', 'self._grp_src'),
        ('net_group', 'self._grp_net'),
        ('ctrl_group', 'self._grp_ctrl'),
    ]),
    ('ui/tools/rf/link_budget_tool.py', [
        ('result_group', 'self._grp_result'),
        ('link_params_group', 'self._grp_link'),
        ('tx_group', 'self._grp_tx'),
        ('rx_group', 'self._grp_rx'),
        ('ch_group', 'self._grp_ch'),
        ('res_group', 'self._grp_res'),
    ]),
    ('ui/tools/antenna/phased_array_tool.py', [
        ('preset_group', 'self._grp_preset'),
        ('array_group', 'self._grp_array'),
        ('scan_group', 'self._grp_scan'),
        ('adv_group', 'self._grp_adv'),
        ('dashboard_group', 'self._grp_dashboard'),
    ]),
]

print('\n--- Checking remaining layout references ---')
for fpath, var_pairs in FILES_TO_CHECK:
    with open(fpath, encoding='utf-8') as f:
        content = f.read()
    for old_var, new_var in var_pairs:
        # Check if old_var still appears in layout constructor calls
        layout_patterns = [
            f'QHBoxLayout({old_var})',
            f'QVBoxLayout({old_var})',
            f'QGridLayout({old_var})',
        ]
        for p in layout_patterns:
            if p in content:
                print(f'  [NEED FIX] {fpath.split("/")[-1]}: {p}')
                fix_layout_refs(fpath, old_var, new_var)
                break
