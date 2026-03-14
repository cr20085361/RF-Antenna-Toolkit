# -*- coding: utf-8 -*-
"""
为所有缺少 retranslate_ui 的工具批量添加修复
支持工具: phased_array_tool, vswr_tool, cascade_tool, attenuator_tool, matching_tool, link_budget_tool
策略: 为每个工具找到 '四维度知识内容' 或 'calculate' 方法前的合适位置，注入 retranslate_ui
"""
import sys, ast
sys.stdout.reconfigure(encoding='utf-8')

TOOLS_TO_FIX = [
    {
        'file': 'ui/tools/antenna/phased_array_tool.py',
        'group_var_keys': [
            ('preset_group', None, 'phased.preset_group'),
            ('array_group', None, 'phased.hw_size'),
            ('scan_group', None, 'phased.beam_scan'),
            ('adv_group', None, 'phased.adv_setting'),
            ('dashboard_group', None, 'phased.res_board'),
        ],
        'radio_keys': [
            ('btn_2d', 'phased.mode_2d'),
            ('btn_3d', 'phased.mode_3d'),
        ],
        'combo_items': [],
        'insert_before_marker': '    def _make_dashboard_label',
        'retranslate_calls': [
            # (widget_attr, tr_key)
            ('self.btn_2d', 'setText', 'phased.mode_2d'),
            ('self.btn_3d', 'setText', 'phased.mode_3d'),
        ],
        'qgroupbox_self_checks': [
            ('self._grp_preset', 'phased.preset_group'),
            ('self._grp_array', 'phased.hw_size'),
            ('self._grp_scan', 'phased.beam_scan'),
            ('self._grp_adv', 'phased.adv_setting'),
            ('self._grp_dashboard', 'phased.res_board'),
        ],
        # local var -> self.xxx renames in create_input_panel/create_result_panel
        'var_renames_input': [
            ('preset_group = QGroupBox', 'self._grp_preset = QGroupBox'),
            ('preset_group.setLayout', 'self._grp_preset.setLayout'),
            ('layout.addWidget(preset_group)', 'layout.addWidget(self._grp_preset)'),
            ('array_group = QGroupBox', 'self._grp_array = QGroupBox'),
            ('array_group.setLayout', 'self._grp_array.setLayout'),
            ('layout.addWidget(array_group)', 'layout.addWidget(self._grp_array)'),
            ('scan_group = QGroupBox', 'self._grp_scan = QGroupBox'),
            ('scan_group.setLayout', 'self._grp_scan.setLayout'),
            ('layout.addWidget(scan_group)', 'layout.addWidget(self._grp_scan)'),
            ('adv_group = QGroupBox', 'self._grp_adv = QGroupBox'),
            ('adv_group.setLayout', 'self._grp_adv.setLayout'),
            ('layout.addWidget(adv_group)', 'layout.addWidget(self._grp_adv)'),
        ],
        'var_renames_result': [
            ('dashboard_group = QGroupBox', 'self._grp_dashboard = QGroupBox'),
            ('dashboard_group.setLayout', 'self._grp_dashboard.setLayout'),
            ('layout.addWidget(dashboard_group)', 'layout.addWidget(self._grp_dashboard)'),
        ],
        'retranslate_extra': '''        # 重新触发计算以刷新图表标题
        if hasattr(self, '_update_calculation'):
            self._update_calculation()
''',
    },
]

SIMPLE_TOOLS = [
    {
        'file': 'ui/tools/rf/vswr_tool.py',
        'insert_before_marker': '    # ==================== 四维度知识内容 ====================',
        'var_renames': [
            ('input_group = QGroupBox', 'self._grp_input = QGroupBox'),
            ('input_layout = QVBoxLayout(input_group)', 'input_layout = QVBoxLayout(self._grp_input)'),
            ('layout.addWidget(input_group)', 'layout.addWidget(self._grp_input)'),
            ('vswr_radio = QRadioButton', 'self._vswr_radio = QRadioButton'),
            ('vswr_radio.setChecked', 'self._vswr_radio.setChecked'),
            ('self._input_type_group.addButton(vswr_radio, 0)', 'self._input_type_group.addButton(self._vswr_radio, 0)'),
            ('input_layout.addWidget(vswr_radio)', 'input_layout.addWidget(self._vswr_radio)'),
            ('power_group = QGroupBox', 'self._grp_power = QGroupBox'),
            ('power_layout = QVBoxLayout(power_group)', 'power_layout = QVBoxLayout(self._grp_power)'),
            ('layout.addWidget(power_group)', 'layout.addWidget(self._grp_power)'),
        ],
        'retranslate_body': '''        if hasattr(self, '_grp_input'):
            self._grp_input.setTitle(tr("vswr.lbl_input_param"))
        if hasattr(self, '_grp_power'):
            self._grp_power.setTitle(tr("vswr.group_power"))
        if hasattr(self, '_vswr_radio'):
            self._vswr_radio.setText(tr("vswr.radio_vswr"))
''',
    },
    {
        'file': 'ui/tools/rf/cascade_tool.py',
        'insert_before_marker': '    # ==================== 四维度知识内容 ====================',
        'var_renames': [
            ('input_mode_group = QGroupBox', 'self._grp_input_mode = QGroupBox'),
            ('input_mode_layout = QVBoxLayout(input_mode_group)', 'input_mode_layout = QVBoxLayout(self._grp_input_mode)'),
            ('layout.addWidget(input_mode_group)', 'layout.addWidget(self._grp_input_mode)'),
            ('stages_group = QGroupBox', 'self._grp_stages = QGroupBox'),
            ('stages_layout = QVBoxLayout(stages_group)', 'stages_layout = QVBoxLayout(self._grp_stages)'),
            ('layout.addWidget(stages_group)', 'layout.addWidget(self._grp_stages)'),
        ],
        'retranslate_body': '''        if hasattr(self, '_grp_input_mode'):
            self._grp_input_mode.setTitle(tr("cascade.group_mode"))
        if hasattr(self, '_grp_stages'):
            self._grp_stages.setTitle(tr("cascade.group_stages"))
''',
    },
    {
        'file': 'ui/tools/rf/attenuator_tool.py',
        'insert_before_marker': '    # ==================== 四维度知识内容 ====================',
        'var_renames': [
            ('topo_group = QGroupBox', 'self._grp_topo = QGroupBox'),
            ('topo_layout = QVBoxLayout(topo_group)', 'topo_layout = QVBoxLayout(self._grp_topo)'),
            ('layout.addWidget(topo_group)', 'layout.addWidget(self._grp_topo)'),
            ('z0_group = QGroupBox', 'self._grp_z0 = QGroupBox'),
            ('z0_layout = QHBoxLayout(z0_group)', 'z0_layout = QHBoxLayout(self._grp_z0)'),
            ('layout.addWidget(z0_group)', 'layout.addWidget(self._grp_z0)'),
            ('atten_group = QGroupBox', 'self._grp_atten = QGroupBox'),
            ('atten_layout = QHBoxLayout(atten_group)', 'atten_layout = QHBoxLayout(self._grp_atten)'),
            ('layout.addWidget(atten_group)', 'layout.addWidget(self._grp_atten)'),
            ('series_group = QGroupBox', 'self._grp_series = QGroupBox'),
            ('series_layout = QVBoxLayout(series_group)', 'series_layout = QVBoxLayout(self._grp_series)'),
            ('layout.addWidget(series_group)', 'layout.addWidget(self._grp_series)'),
        ],
        'retranslate_body': '''        if hasattr(self, '_grp_topo'):
            self._grp_topo.setTitle(tr("attenuator.group_topo"))
        if hasattr(self, '_grp_z0'):
            self._grp_z0.setTitle(tr("attenuator.group_z0"))
        if hasattr(self, '_grp_atten'):
            self._grp_atten.setTitle(tr("attenuator.group_atten"))
        if hasattr(self, '_grp_series'):
            self._grp_series.setTitle(tr("attenuator.group_series"))
''',
    },
    {
        'file': 'ui/tools/rf/matching_tool.py',
        'insert_before_marker': '    # ==================== 四维度知识内容 ====================',
        'var_renames': [
            ('src_group = QGroupBox', 'self._grp_src = QGroupBox'),
            ('src_layout = QGridLayout(src_group)', 'src_layout = QGridLayout(self._grp_src)'),
            ('layout.addWidget(src_group)', 'layout.addWidget(self._grp_src)'),
            ('net_group = QGroupBox', 'self._grp_net = QGroupBox'),
            ('net_layout = QGridLayout(net_group)', 'net_layout = QGridLayout(self._grp_net)'),
            ('layout.addWidget(net_group)', 'layout.addWidget(self._grp_net)'),
            ('ctrl_group = QGroupBox', 'self._grp_ctrl = QGroupBox'),
            ('ctrl_layout = QVBoxLayout(ctrl_group)', 'ctrl_layout = QVBoxLayout(self._grp_ctrl)'),
            ('layout.addWidget(ctrl_group)', 'layout.addWidget(self._grp_ctrl)'),
        ],
        'retranslate_body': '''        if hasattr(self, '_grp_src'):
            self._grp_src.setTitle(tr("matching.group_src_load_impedance"))
        if hasattr(self, '_grp_net'):
            self._grp_net.setTitle(tr("matching.group_matching_network"))
        if hasattr(self, '_grp_ctrl'):
            self._grp_ctrl.setTitle(tr("matching.group_element_params"))
''',
    },
    {
        'file': 'ui/tools/rf/link_budget_tool.py',
        'insert_before_marker': '    # ==================== 四维度知识内容 ====================',
        'var_renames': [
            ('result_group = QGroupBox', 'self._grp_result = QGroupBox'),
            ('result_layout = QVBoxLayout(result_group)', 'result_layout = QVBoxLayout(self._grp_result)'),
            ('layout.addWidget(result_group)', 'layout.addWidget(self._grp_result)'),
            ('link_params_group = QGroupBox', 'self._grp_link = QGroupBox'),
            ('link_params_layout = QVBoxLayout(link_params_group)', 'link_params_layout = QVBoxLayout(self._grp_link)'),
            ('layout.addWidget(link_params_group)', 'layout.addWidget(self._grp_link)'),
            ('tx_group = QGroupBox', 'self._grp_tx = QGroupBox'),
            ('tx_layout = QGridLayout(tx_group)', 'tx_layout = QGridLayout(self._grp_tx)'),
            ('layout.addWidget(tx_group)', 'layout.addWidget(self._grp_tx)'),
            ('rx_group = QGroupBox', 'self._grp_rx = QGroupBox'),
            ('rx_layout = QGridLayout(rx_group)', 'rx_layout = QGridLayout(self._grp_rx)'),
            ('layout.addWidget(rx_group)', 'layout.addWidget(self._grp_rx)'),
            ('ch_group = QGroupBox', 'self._grp_ch = QGroupBox'),
            ('ch_layout = QGridLayout(ch_group)', 'ch_layout = QGridLayout(self._grp_ch)'),
            ('layout.addWidget(ch_group)', 'layout.addWidget(self._grp_ch)'),
            ('res_group = QGroupBox', 'self._grp_res = QGroupBox'),
            ('res_layout = QGridLayout(res_group)', 'res_layout = QGridLayout(self._grp_res)'),
            ('layout.addWidget(res_group)', 'layout.addWidget(self._grp_res)'),
        ],
        'retranslate_body': '''        if hasattr(self, '_grp_result'):
            self._grp_result.setTitle(tr("linkbudget.title_summary"))
        if hasattr(self, '_grp_link'):
            self._grp_link.setTitle(tr("linkbudget.title_link_params"))
        if hasattr(self, '_grp_tx'):
            self._grp_tx.setTitle(tr("linkbudget.title_tx"))
        if hasattr(self, '_grp_rx'):
            self._grp_rx.setTitle(tr("linkbudget.title_rx"))
        if hasattr(self, '_grp_ch'):
            self._grp_ch.setTitle(tr("linkbudget.title_channel"))
        if hasattr(self, '_grp_res'):
            self._grp_res.setTitle(tr("linkbudget.title_link_budget_results"))
''',
    },
]


def process_simple_tool(tool_cfg):
    fpath = tool_cfg['file']
    with open(fpath, encoding='utf-8') as f:
        content = f.read()

    original = content

    # Apply renames
    applied = 0
    for old, new in tool_cfg.get('var_renames', []):
        if old in content:
            content = content.replace(old, new, 1)
            applied += 1

    # Check if retranslate_ui already exists
    if 'def retranslate_ui' in content:
        print(f'[SKIP] {fpath}: already has retranslate_ui')
        if content != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
        return

    # Build retranslate_ui method
    retranslate_method = f'''
    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新 UI 文字"""
        super().retranslate_ui(lang)
{tool_cfg['retranslate_body']}
'''

    marker = tool_cfg['insert_before_marker']
    if marker in content:
        content = content.replace(marker, retranslate_method + marker, 1)
        applied += 1
    else:
        # Alternative: insert before "def calculate"
        alt_marker = '    def calculate('
        if alt_marker in content:
            content = content.replace(alt_marker, retranslate_method + alt_marker, 1)
            applied += 1
        else:
            print(f'[WARN] {fpath}: marker not found, skipping retranslate_ui insertion')
            return

    # Syntax check
    try:
        ast.parse(content)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK] {fpath}: {applied} changes, syntax OK')
    except SyntaxError as e:
        print(f'[FAIL] {fpath}: syntax error - {e}, rolling back')


def process_phased_array_tool():
    fpath = 'ui/tools/antenna/phased_array_tool.py'
    with open(fpath, encoding='utf-8') as f:
        content = f.read()

    if 'def retranslate_ui' in content:
        print(f'[SKIP] {fpath}: already has retranslate_ui')
        return

    applied = 0
    renames = [
        ('preset_group = QGroupBox', 'self._grp_preset = QGroupBox'),
        ('preset_group.setLayout', 'self._grp_preset.setLayout'),
        ('layout.addWidget(preset_group)', 'layout.addWidget(self._grp_preset)'),
        ('array_group = QGroupBox', 'self._grp_array = QGroupBox'),
        ('array_group.setLayout', 'self._grp_array.setLayout'),
        ('layout.addWidget(array_group)', 'layout.addWidget(self._grp_array)'),
        ('scan_group = QGroupBox', 'self._grp_scan = QGroupBox'),
        ('scan_group.setLayout', 'self._grp_scan.setLayout'),
        ('layout.addWidget(scan_group)', 'layout.addWidget(self._grp_scan)'),
        ('adv_group = QGroupBox', 'self._grp_adv = QGroupBox'),
        ('adv_group.setLayout', 'self._grp_adv.setLayout'),
        ('layout.addWidget(adv_group)', 'layout.addWidget(self._grp_adv)'),
        ('dashboard_group = QGroupBox', 'self._grp_dashboard = QGroupBox'),
        ('dashboard_group.setLayout', 'self._grp_dashboard.setLayout'),
        ('layout.addWidget(dashboard_group)', 'layout.addWidget(self._grp_dashboard)'),
    ]
    for old, new in renames:
        if old in content:
            content = content.replace(old, new, 1)
            applied += 1

    retranslate_method = '''
    # ==================== 国际化刷新接口 ====================

    def retranslate_ui(self, lang: str = ""):
        """语言切换时刷新 UI 文字"""
        super().retranslate_ui(lang)
        if hasattr(self, '_grp_preset'):
            self._grp_preset.setTitle(tr("phased.preset_group"))
        if hasattr(self, '_grp_array'):
            self._grp_array.setTitle(tr("phased.hw_size"))
        if hasattr(self, '_grp_scan'):
            self._grp_scan.setTitle(tr("phased.beam_scan"))
        if hasattr(self, '_grp_adv'):
            self._grp_adv.setTitle(tr("phased.adv_setting"))
        if hasattr(self, '_grp_dashboard'):
            self._grp_dashboard.setTitle(tr("phased.res_board"))
        if hasattr(self, 'btn_2d'):
            self.btn_2d.setText(tr("phased.mode_2d"))
        if hasattr(self, 'btn_3d'):
            self.btn_3d.setText(tr("phased.mode_3d"))
        # 重新触发计算以刷新图表标题
        if hasattr(self, '_update_calculation'):
            self._update_calculation()

'''
    marker = '    def _make_dashboard_label'
    if marker in content:
        content = content.replace(marker, retranslate_method + marker, 1)
        applied += 1

    try:
        ast.parse(content)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK] {fpath}: {applied} changes, syntax OK')
    except SyntaxError as e:
        print(f'[FAIL] {fpath}: syntax error - {e}')


if __name__ == '__main__':
    process_phased_array_tool()
    for tool in SIMPLE_TOOLS:
        process_simple_tool(tool)
    print('\nAll done.')
