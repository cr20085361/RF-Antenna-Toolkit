"""
为所有 11 个剩余工具注入 i18n keys 和 retranslate_ui 方法
"""
import re, os

tools = {
    r"e:\AI_project\射频天线工具集\ui\tools\antenna\bandwidth_tool.py": ("bandwidth", "BandwidthTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\antenna\phased_array_tool.py": ("phasedarray", "PhasedArrayTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\reference\band_table_tool.py": ("bandtable", "BandTableTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\reference\connector_table_tool.py": ("connector", "ConnectorTableTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\reference\eseries_table_tool.py": ("eseries", "ESeriesTableTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\reference\waveguide_table_tool.py": ("waveguide", "WaveguideTableTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\rf\attenuator_tool.py": ("attenuator", "AttenuatorTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\rf\cascade_tool.py": ("cascade", "CascadeTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\rf\link_budget_tool.py": ("linkbudget", "LinkBudgetTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\rf\matching_tool.py": ("matching", "MatchingTool"),
    r"e:\AI_project\射频天线工具集\ui\tools\rf\vswr_tool.py": ("vswr", "VSWRTool"),
}

for fpath, (i18n_key, class_name) in tools.items():
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    modified = False
    
    # 1. Add "from core.i18n import tr" if missing
    if "from core.i18n import" not in content:
        # Find the last import line from the tool's own imports
        content = re.sub(
            r'(from ui\.base\.tool_base import ToolBase)',
            r'from core.i18n import tr\n\1',
            content
        )
        modified = True
    
    # 2. Add i18n_title_key and i18n_desc_key class attributes
    if "i18n_title_key" not in content:
        # Find tool_description line and add after it
        desc_pattern = r'(    tool_description\s*[:=].*?\n)'
        match = re.search(desc_pattern, content)
        if match:
            insert_pos = match.end()
            i18n_attrs = f'    i18n_title_key = "{i18n_key}.tool_name"\n    i18n_desc_key = "{i18n_key}.tool_desc"\n'
            content = content[:insert_pos] + i18n_attrs + content[insert_pos:]
            modified = True
    
    # 3. Replace get_intuition_content / get_math_model_content / etc. to use tr()
    for method_name, content_key in [
        ('get_intuition_content', 'intuition_content'),
        ('get_math_model_content', 'math_content'),
        ('get_engineering_content', 'engineering_content'),
        ('get_history_content', 'history_content'),
    ]:
        # Pattern: def method(self) -> Optional[str]:  followed by return """..."""
        pattern = rf'(def {method_name}\(self\)[^:]*:\s*\n)\s+return\s+""".*?"""'
        replacement = rf'\1        return tr("{i18n_key}.{content_key}")'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if new_content != content:
            content = new_content
            modified = True
    
    if modified:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {os.path.basename(fpath)} ({i18n_key})")
    else:
        print(f"Skipped (no changes needed): {os.path.basename(fpath)}")

print("\nAll 11 tools processed!")
