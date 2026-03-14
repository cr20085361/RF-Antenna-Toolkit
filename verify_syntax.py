import ast
import sys
sys.stdout.reconfigure(encoding='utf-8')

tools = [
    'ui/tools/antenna/bandwidth_tool.py',
    'ui/tools/antenna/phased_array_tool.py',
    'ui/tools/antenna/gain_tool.py',
    'ui/tools/antenna/range_tool.py',
    'ui/tools/antenna/sensitivity_tool.py',
    'ui/tools/antenna/los_tool.py',
    'ui/tools/antenna/wavelength_tool.py',
    'ui/tools/rf/vswr_tool.py',
    'ui/tools/rf/cascade_tool.py',
    'ui/tools/rf/attenuator_tool.py',
    'ui/tools/rf/matching_tool.py',
    'ui/tools/rf/link_budget_tool.py',
    'ui/tools/rf/impedance_tool.py',
]
all_ok = True
for fpath in tools:
    with open(fpath, encoding='utf-8') as f:
        src = f.read()
    has_ret = 'def retranslate_ui' in src
    try:
        ast.parse(src)
        status = 'OK'
    except SyntaxError as e:
        status = f'SYNTAX_ERR:{e.lineno}'
        all_ok = False
    fname = fpath.split('/')[-1]
    print(f'[{status}] {fname} | retranslate_ui={has_ret}')

print()
print('All OK!' if all_ok else 'Some files have issues!')
