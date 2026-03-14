import os
import json
import re
from typing import Set, Dict

def get_i18n_keys(json_path: str) -> Set[str]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    keys = set()
    def flatten(d, prefix=''):
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                flatten(v, full_key)
            else:
                keys.add(full_key)
    flatten(data)
    return keys

def scan_python_files(root_dir: str) -> Dict[str, Set[str]]:
    tr_pattern = re.compile(r'tr\(\s*["\']([^"\']+)["\']')
    found_keys = {}
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = tr_pattern.findall(content)
                        if matches:
                            found_keys[path] = set(matches)
                except Exception:
                    pass
    return found_keys

def verify():
    base_path = r"e:\AI_Project\RF-Antenna-Toolkit"
    zh_path = os.path.join(base_path, "assets", "locales", "zh_CN.json")
    en_path = os.path.join(base_path, "assets", "locales", "en_US.json")
    
    print(f"Loading resources...")
    zh_keys = get_i18n_keys(zh_path)
    en_keys = get_i18n_keys(en_path)
    
    print(f"Scanning Python files in {base_path}...")
    file_to_keys = scan_python_files(os.path.join(base_path, "ui"))
    
    missing_count = 0
    for path, keys in file_to_keys.items():
        rel_path = os.path.relpath(path, base_path)
        missing_zh = keys - zh_keys
        missing_en = keys - en_keys
        
        if missing_zh or missing_en:
            print(f"\n[!] {rel_path}")
            if missing_zh:
                print(f"  Missing in zh_CN: {missing_zh}")
            if missing_en:
                print(f"  Missing in en_US: {missing_en}")
            missing_count += len(missing_zh | missing_en)

    if missing_count == 0:
        print("\n[OK] All translation keys are properly defined in JSON files!")
    else:
        print(f"\n[FAIL] Found {missing_count} missing translation keys.")

if __name__ == "__main__":
    verify()
