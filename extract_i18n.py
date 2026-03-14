import re
import os
import json

def extract_tr_calls(file_path):
    # 匹配 tr("key", "default")
    pattern = re.compile(r'tr\(\s*["\']([^"\']+)["\']\s*,\s*["\']((?:[^"\']|\\["\'])*)["\']\)')
    # 匹配 tr("key")
    pattern_single = re.compile(r'tr\(\s*["\']([^"\']+)["\']\s*\)')
    
    results = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for key, val in pattern.findall(content):
        # 处理转义的引号
        val = val.replace('\\"', '"').replace("\\'", "'")
        results[key] = val
        
    for key in pattern_single.findall(content):
        if key not in results:
            results[key] = f"FIXME_{key}"
            
    return results

def sync_module(module_name, file_paths):
    all_kv = {}
    for fp in file_paths:
        all_kv.update(extract_tr_calls(fp))
        
    # 按前缀分组
    module_data = {}
    for k, v in all_kv.items():
        if k.startswith(f"{module_name}."):
            sub_key = k.split('.', 1)[1]
            module_data[sub_key] = v
            
    return module_data

if __name__ == "__main__":
    base = r"e:\AI_Project\RF-Antenna-Toolkit"
    modules = {
        "cascade": [os.path.join(base, "ui/tools/rf/cascade_tool.py")],
        "vswr": [os.path.join(base, "ui/tools/rf/vswr_tool.py")],
        "linkbudget": [os.path.join(base, "ui/tools/rf/link_budget_tool.py")],
        "impedance": [os.path.join(base, "ui/tools/rf/impedance_tool.py")]
    }
    
    final_output = {}
    for mod, paths in modules.items():
        final_output[mod] = sync_module(mod, paths)
        
    with open(os.path.join(base, "i18n_extracted.json"), 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    print("Done! Results saved to i18n_extracted.json")
