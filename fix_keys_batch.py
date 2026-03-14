import os
import re

directories = [
    r"e:\AI_Project\RF-Antenna-Toolkit\ui\tools\rf",
    r"e:\AI_Project\RF-Antenna-Toolkit\ui\tools\antenna"
]

# 重点匹配常见的几种旧 Key 命名
patterns = [
    (re.compile(r'tr\("([a-z_]+)\.intuition"'), r'tr("\1.intuition_content"'),
    (re.compile(r'tr\("([a-z_]+)\.math_model"'), r'tr("\1.math_content"'),
    (re.compile(r'tr\("([a-z_]+)\.eng_content"'), r'tr("\1.engineering_content"'),
    # 兼容带默认值的写法 tr("key", "default")
    (re.compile(r'tr\("([a-z_]+)\.intuition",'), r'tr("\1.intuition_content",'),
    (re.compile(r'tr\("([a-z_]+)\.math_model",'), r'tr("\1.math_content",'),
    (re.compile(r'tr\("([a-z_]+)\.eng_content",'), r'tr("\1.engineering_content",'),
]

def fix_files():
    count = 0
    for directory in directories:
        if not os.path.exists(directory): continue
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                path = os.path.join(directory, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    for pattern, replacement in patterns:
                        new_content = pattern.sub(replacement, new_content)
                    
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Fixed keys in {filename}")
                        count += 1
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    fix_files()
