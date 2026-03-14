import json
import sys

zh = json.load(open('assets/locales/zh_CN.json', encoding='utf-8'))
en = json.load(open('assets/locales/en_US.json', encoding='utf-8'))

def count_keys(d):
    count = 0
    for k, v in d.items():
        if isinstance(v, dict):
            count += count_keys(v)
        else:
            count += 1
    return count

zh_count = count_keys(zh)
en_count = count_keys(en)

print(f'zh_CN.json total keys: {zh_count}')
print(f'en_US.json total keys: {en_count}')
print()

all_tools = sorted(set(zh.keys()) | set(en.keys()))
print('=== Per-tool key comparison ===')
all_ok = True
for tool in all_tools:
    zh_keys = set(zh.get(tool, {}).keys())
    en_keys = set(en.get(tool, {}).keys())
    missing_en = zh_keys - en_keys
    missing_zh = en_keys - zh_keys
    total = len(zh_keys | en_keys)
    if missing_en:
        all_ok = False
        print(f'  [{tool}] en_US missing {len(missing_en)}/{total} keys: {sorted(missing_en)[:5]}')
    elif missing_zh:
        all_ok = False
        print(f'  [{tool}] zh_CN missing {len(missing_zh)}/{total} keys: {sorted(missing_zh)[:5]}')
    else:
        print(f'  [{tool}] OK ({total} keys)')

print()
if all_ok:
    print('All tools: bilingual dictionaries are in sync!')
else:
    print('Some tools have key mismatches - see above.')
