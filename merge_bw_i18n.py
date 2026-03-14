import json
import os

def merge_json(target_path, source_data):
    if not os.path.exists(target_path):
        print(f"Error: {target_path} not found")
        return
        
    with open(target_path, 'r', encoding='utf-8') as f:
        target_data = json.load(f)
        
    for module, keys in source_data.items():
        if module not in target_data:
            target_data[module] = {}
        for key, value in keys.items():
            # 强化逻辑：支持深层嵌套
            if "." in key:
                parts = key.split(".")
                curr = target_data[module]
                for p in parts[:-1]:
                    if p not in curr: curr[p] = {}
                    curr = curr[p]
                curr[parts[-1]] = value
            else:
                target_data[module][key] = value

    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(target_data, f, indent=4, ensure_ascii=False)

# --- 带宽工具 知识库内容 ---
bw_zh = {
    "bandwidth": {
        "intuition": """<b>📶 什么是带宽？</b><br><br>带宽描述天线或系统能有效工作的<b>频率范围</b>。就像收音机调频一样，天线只能在特定频率范围内正常接收/发射信号。<br><br><b>🎯 常见带宽定义:</b><br>• <b>绝对带宽</b>: f_high - f_low (Hz)<br>• <b>分数带宽</b>: BW / f_center × 100%<br>• <b>倍频程</b>: log₂(f_high / f_low)<br><br><b>💡 核心理解:</b> 分数带宽更能反映天线的宽带特性，因为同样100MHz带宽在1GHz和10GHz意义完全不同。""",
        "math_model": """<b>📐 带宽公式</b><br><br><b>绝对带宽:</b><br>BW = f_H - f_L<br><br><b>中心频率:</b><br>f_c = (f_H + f_L) / 2<br><br><b>分数带宽 (Fractional BW):</b><br>FBW = BW / f_c × 100%<br><br><b>倍频程带宽:</b><br>Octave = log₂(f_H / f_L)<br><br><b>Q值:</b><br>Q = f_c / BW""",
        "eng_content": """<b>✅ 带宽分类参考:</b><br>• FBW < 1% → 极窄带<br>• FBW 1~5% → 窄带天线<br>• FBW 5~20% → 中等带宽<br>• FBW 20~50% → 宽带天线<br>• FBW > 100% → 超宽带 (UWB)<br><br><b>⚠️ 注意事项:</b> 带宽定义可能基于 -3dB / -10dB / VSWR<2:1 等标准。""",
        "history_content": """<b>📜 带宽的演进</b><br><br><b>1900s</b> - 早期火花机带宽极宽且干扰重。<br><b>1920s</b> - 调谐电路实现窄带通信。<br><b>2002</b> - FCC批准UWB技术，开启超宽带时代。"""
    }
}

bw_en = {
    "bandwidth": {
        "intuition": """<b>📶 What is Bandwidth?</b><br><br>Bandwidth describes the <b>frequency range</b> within which an antenna or system can operate effectively. Much like tuning a radio, an antenna only receives or transmits signals properly within a specific range.<br><br><b>🎯 Common Definitions:</b><br>• <b>Absolute BW</b>: f_high - f_low (Hz)<br>• <b>Fractional BW</b>: BW / f_center × 100%<br>• <b>Octave BW</b>: log₂(f_high / f_low)<br><br><b>💡 Core Insight:</b> Fractional BW better represents wideband characteristics, as 100MHz BW means very different things at 1GHz vs. 10GHz.""",
        "math_model": """<b>📐 Bandwidth Formulas</b><br><br><b>Absolute BW:</b><br>BW = f_H - f_L<br><br><b>Center Frequency:</b><br>f_c = (f_H + f_L) / 2<br><br><b>Fractional BW:</b><br>FBW = BW / f_c × 100%<br><br><b>Octave BW:</b><br>log₂(f_H / f_L)<br><br><b>Q Factor:</b><br>Q = f_c / BW""",
        "eng_content": """<b>✅ BW Classification:</b><br>• FBW < 1% → Ultra-narrow<br>• FBW 1~5% → Narrowband<br>• FBW 5~20% → Moderate<br>• FBW 20~50% → Wideband<br>• FBW > 100% → UWB<br><br><b>⚠️ Note:</b> BW can be defined by -3dB, -10dB, or VSWR < 2:1. Always check the criteria.""",
        "history_content": """<b>📜 Evolution of BW</b><br><br><b>Early 1900s</b> - Spark transmitters had huge BW but caused interference.<br><b>1920s</b> - Tuning circuits enabled narrowband comms.<br><b>2002</b> - FCC approved UWB, launching the ultra-wideband era."""
    }
}

locales_dir = os.path.join(os.getcwd(), "assets", "locales")
merge_json(os.path.join(locales_dir, "zh_CN.json"), bw_zh)
merge_json(os.path.join(locales_dir, "en_US.json"), bw_en)

print("Bandwidth i18n merged successfully!")
