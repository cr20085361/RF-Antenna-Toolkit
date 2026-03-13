import re

files = [
    r"e:\AI_project\射频天线工具集\ui\tools\antenna\wavelength_tool.py",
    r"e:\AI_project\射频天线工具集\ui\tools\antenna\los_tool.py",
    r"e:\AI_project\射频天线工具集\ui\tools\rf\impedance_tool.py"
]

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. replace tr("category", "key") with tr("category.key")
    content = re.sub(r'tr\("([a-z_]+)",\s*"([a-z0-9_]+)"\)', r'tr("\1.\2")', content)
    content = re.sub(r"tr\('([a-z_]+)',\s*'([a-z0-9_]+)'\)", r'tr("\1.\2")', content)
    
    # 2. replace tr(category, key) in retranslate_ui
    content = content.replace("tr(category, key)", 'tr(f"{category}.{key}")')
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Fixed tr(...) calls in all three tool files.")
