import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

if 'gain' not in zh: zh['gain'] = {}
if 'gain' not in en: en['gain'] = {}

gain_trans = {
    'tool_name': ('增益计算', 'Gain Calculator'),
    'tool_desc': ('天线增益计算 (波束宽度法/口径法)', 'Antenna Gain Calculation (Beamwidth/Aperture Method)'),
    'group_mode': ('计算模式', 'Calculation Mode'),
    'radio_bw': ('波束宽度法 (3dB 波宽)', 'Beamwidth Method (3dB Beamwidth)'),
    'radio_aperture': ('有效口径法 (面积 & 频率)', 'Aperture Method (Area & Frequency)'),
    
    'lbl_bw_e': ('E面 3dB波宽 (度):', 'E-plane 3dB BW (deg):'),
    'lbl_bw_h': ('H面 3dB波宽 (度):', 'H-plane 3dB BW (deg):'),
    'lbl_eff': ('天线效率 η (0-1):', 'Antenna Efficiency η (0-1):'),
    
    'lbl_freq': ('工作频率:', 'Operating Frequency:'),
    'lbl_dim1': ('物理尺寸1:', 'Physical Dimension 1:'),
    'lbl_dim2': ('物理尺寸2:', 'Physical Dimension 2:'),
    'radio_rect': ('矩形口径 (长 × 宽)', 'Rectangular Aperture (L × W)'),
    'radio_circ': ('圆形口径 (直径 × 1)', 'Circular Aperture (Diameter × 1)'),
    
    'btn_calc': ('📡 计算增益', '📡 Calculate Gain'),
    
    'title_eval': ('计算结果', 'Calculation Result'),
    'res_main': ('天线增益 (dBi)', 'Antenna Gain (dBi)'),
    'res_linear': ('线性增益 (倍数)', 'Linear Gain (Ratio)'),
    'title_detail': ('📐 详细参数', '📐 Detailed Parameters'),
    'detail_aperture': ('有效口径面积', 'Effective Aperture Area'),
    'detail_solid': ('立体角 (波束宽度法)', 'Solid Angle (Beamwidth)'),
    'detail_max': ('理论最大增益 (效率=100%)', 'Theoretical Max Gain (η=100%)'),
    
    'err_bw': ('波束宽度必须在 0 到 360 度之间', 'Beamwidth must be between 0 and 360 degrees'),
    'err_eff': ('效率必须在 0 到 1 之间', 'Efficiency must be between 0 and 1'),
    'err_freq': ('请输入有效的正向频率', 'Please enter a valid positive frequency'),
    'err_dim': ('请输入有效的物理尺寸', 'Please enter a valid physical dimension'),
    'err_inp': ('输入格式错误', 'Input format error'),
    
    'intuition_content': (
        '''<b>📡 什么是天线增益？</b><br><br>
        想象一个手电筒：灯泡的原始光线是向四面八方发散的（这类似<b>全向点源天线</b>，增益为0 dBi）。<br>
        当你给灯泡加上一个反光碗时，光线被集中到了一个方向，虽然<b>总能量没变</b>，但在这个方向上光变得非!常!亮!。<br><br>
        这就是<b>天线增益</b>的本质：天线本身不\"放大\"能量，它只是一个\"无源能量汇聚器\"，把本来要射向四面八方的电磁波，集中到了你想要的特定方向上。<br><br>
        <b>💡 两个核心结论：</b><br>
        1. 增益越大，波束越\"窄\" (如同聚光手电筒)<br>
        2. 天线的物理面积越大，能捕获和发射的能量越集中，增益也越高''',
        
        '''<b>📡 What is Antenna Gain?</b><br><br>
        Imagine a flashlight: an unshielded bulb emits light in all directions (similar to an <b>isotropic point source</b>, 0 dBi gain).<br>
        When you add a reflector bowl behind the bulb, all that light is concentrated in one direction. The <b>total energy hasn't changed</b>, but the beam becomes intensely bright in that specific direction.<br><br>
        This is the essence of <b>Antenna Gain</b>: An antenna does not "amplify" power; it acts as a "passive energy concentrator," focusing electromagnetic waves that would have gone everywhere into a specific sector.<br><br>
        <b>💡 Two Key Takeaways:</b><br>
        1. Higher gain = Narrower beam (like a laser vs. a floodlight).<br>
        2. Larger physical area = More energy focused/captured = Higher gain.'''
    ),
    'math_content': (
        '''<b>📐 增益计算核心公式</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ 波束宽度法 (近似)</b><br>
        对于方向图近似为单一主瓣的笔形波束天线 (通常适用于增益 > 10dBi):<br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        G = η × (41000 / (θ_E × θ_H))
        </span><br>
        • θ_E, θ_H = E面和H面的 3dB 波束宽度 (单位: 度°)<br>
        • 41000 是一个经验常数 (整个球面的立体角近似为 41253 平方度)
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>2️⃣ 物理口径法 (精确)</b><br>
        对于面状天线 (如抛物面、喇叭天线、微带阵列):<br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        G = η × (4π × A) / λ²
        </span><br>
        • A = 天线的物理面积 (长×宽，或 πr²)<br>
        • λ = 工作波长 (λ = c/f)<br>
        • η = 口径效率 (通常介于 0.5 到 0.8 之间)
        </div>
        <b>📈 dBi 与线性倍数的转换</b><br>
        Gain(dBi) = 10 × log₁₀(线性倍数)<br>
        3 dBi ≈ 2 倍功率, 10 dBi = 10 倍功率, 20 dBi = 100 倍功率''',
        
        '''<b>📐 Core Gain Equations</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ Beamwidth Method (Approximation)</b><br>
        For pencil-beam antennas with a single main lobe (typically > 10dBi):<br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        G = η × (41000 / (θ_E × θ_H))
        </span><br>
        • θ_E, θ_H = 3dB beamwidths in E and H planes (degrees°)<br>
        • 41000 is an empirical constant (a full sphere is roughly 41253 sq. degrees).
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>2️⃣ Physical Aperture Method (Exact)</b><br>
        For aperture antennas (e.g., reflectors, horns, microstrip arrays):<br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        G = η × (4π × A) / λ²
        </span><br>
        • A = Physical area (L×W, or πr²)<br>
        • λ = Wavelength (λ = c/f)<br>
        • η = Aperture efficiency (usually 0.5 to 0.8)
        </div>
        <b>📈 dBi to Linear Conversion</b><br>
        Gain(dBi) = 10 × log₁₀(Linear multiplier)<br>
        3 dBi ≈ 2x power, 10 dBi = 10x power, 20 dBi = 100x power'''
    ),
    'engineering_content': (
        '''<b>🏗️ 常见天线的典型增益与效率 (工程参考)</b><br>
        <table style="margin: 8px 0;">
        <tr><th>天线类型</th><th>典型增益</th><th>典型效率 η</th></tr>
        <tr><td>理想点源 (Isotropic)</td><td>0 dBi</td><td>100% (理论值)</td></tr>
        <tr><td>半波偶极子 (Dipole)</td><td>2.15 dBi</td><td>> 95%</td></tr>
        <tr><td>微带贴片 (Patch)</td><td>5 ~ 8 dBi</td><td>60% ~ 80%</td></tr>
        <tr><td>标准喇叭 (Horn)</td><td>10 ~ 25 dBi</td><td>50% ~ 70%</td></tr>
        <tr><td>抛物面天线 (Reflector)</td><td>20 ~ 45 dBi</td><td>55% ~ 65%</td></tr>
        </table><br>
        <span style="background-color: #FEF3C7; padding: 4px 8px; border-radius: 4px; color: #B45309;">
        <b>⚠️ 避坑指南：波束宽度法的陷阱</b>
        </span><br>
        经常有新手用 "41000/(θE×θH)" 去计算<b>低增益天线</b> (比如偶极子，波宽78°×360°)，结果算出来增益不到2dBi，甚至报错。<br>
        <b>原因：</b>该公式假设极大部分能量集中在一个很窄的圆锥体内。如果你的波束很宽（存在大量的旁瓣或后瓣泄漏），这个公式的误差将极其巨大，仅适用于大阵列或高增益天线估算！''',
        
        '''<b>🏗️ Typical Antennas (Engineering Reference)</b><br>
        <table style="margin: 8px 0;">
        <tr><th>Antenna Type</th><th>Typical Gain</th><th>Typical Eff. η</th></tr>
        <tr><td>Isotropic radiator</td><td>0 dBi</td><td>100% (Theory)</td></tr>
        <tr><td>Half-wave Dipole</td><td>2.15 dBi</td><td>> 95%</td></tr>
        <tr><td>Microstrip Patch</td><td>5 ~ 8 dBi</td><td>60% ~ 80%</td></tr>
        <tr><td>Pyramidal Horn</td><td>10 ~ 25 dBi</td><td>50% ~ 70%</td></tr>
        <tr><td>Parabolic Reflector</td><td>20 ~ 45 dBi</td><td>55% ~ 65%</td></tr>
        </table><br>
        <span style="background-color: #FEF3C7; padding: 4px 8px; border-radius: 4px; color: #B45309;">
        <b>⚠️ Pitfall: Beamwidth Formula Breakdown</b>
        </span><br>
        Beginners often use "41000/(θE×θH)" on <b>low-gain antennas</b> (like dipoles, 78°×360°), getting severe errors or nonsensical results.<br>
        <b>Why?</b> This formula assumes energy is tightly beamed into a single narrow cone. If your beam is wide (significant sidelobes/backlobes exist), this approximation fails miserably. Use it ONLY for high-gain/array estimations!'''
    )
}

for k, (ch, eng) in gain_trans.items():
    zh['gain'][k] = ch
    en['gain'][k] = eng

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)

print("Language files updated for gain tool.")
