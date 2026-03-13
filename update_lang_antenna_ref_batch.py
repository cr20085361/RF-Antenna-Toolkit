"""
批量为天线工具和参考手册工具注入翻译词条
处理: bandwidth, phased_array, band_table, connector, eseries, waveguide
"""
import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

# ===================== Bandwidth 带宽计算 =====================
zh['bandwidth'] = {
    'tool_name': '带宽计算',
    'tool_desc': '天线带宽计算与Q值分析',
    'intuition_content': '''<b>📶 什么是天线带宽?</b><br><br>
天线带宽是指在满足某些性能指标（通常是 VSWR < 2.0）的条件下，天线可以正常工作的频率范围。<br><br>
<b>💡 Q值与带宽的关系：</b><br>
• Q值越高 → 天线在谐振频率处表现越好，但带宽越<b>窄</b><br>
• Q值越低 → 带宽越<b>宽</b>，但效率可能下降<br><br>
这就像调钢琴——调得越精准（高Q），它只对特定音高产生共鸣；调得"松"一些（低Q），更多频率都能响应。''',
    'math_content': '''<b>📐 带宽与Q值公式</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px;">
<b>分数带宽 FBW：</b><br>
FBW = (f_upper - f_lower) / f_center × 100%<br><br>
<b>Q 值与分数带宽的关系：</b><br>
Q = f_center / (f_upper - f_lower) = 1 / FBW<br><br>
<b>VSWR 带宽判据：</b><br>
VSWR < 2.0 (即 |S₁₁| < -10dB)
</div>''',
    'engineering_content': '''<b>⚠️ 天线带宽参考</b><br>
<table style="margin: 8px 0;">
<tr><th>天线类型</th><th>典型带宽</th></tr>
<tr><td>微带贴片</td><td>1% ~ 5%</td></tr>
<tr><td>偶极子/单极子</td><td>10% ~ 20%</td></tr>
<tr><td>螺旋天线</td><td>50% ~ 70%</td></tr>
<tr><td>对数周期天线</td><td>> 100% (超宽带)</td></tr>
</table>'''
}

en['bandwidth'] = {
    'tool_name': 'Bandwidth Calculator',
    'tool_desc': 'Antenna bandwidth calculation and Q-factor analysis',
    'intuition_content': '''<b>📶 What is Antenna Bandwidth?</b><br><br>
Antenna bandwidth is the frequency range over which the antenna meets certain performance criteria (usually VSWR < 2.0).<br><br>
<b>💡 Q-factor and Bandwidth Relationship:</b><br>
• Higher Q → Better performance at resonance, but <b>narrower</b> bandwidth.<br>
• Lower Q → <b>Wider</b> bandwidth, but efficiency may decrease.<br><br>
Think of tuning a piano—a precisely tuned string (high Q) resonates only at one exact pitch; a "loose" string (low Q) responds to a broader range of frequencies.''',
    'math_content': '''<b>📐 Bandwidth & Q-factor Formulas</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px;">
<b>Fractional Bandwidth FBW:</b><br>
FBW = (f_upper - f_lower) / f_center × 100%<br><br>
<b>Q-factor vs. Fractional Bandwidth:</b><br>
Q = f_center / (f_upper - f_lower) = 1 / FBW<br><br>
<b>VSWR Bandwidth Criterion:</b><br>
VSWR < 2.0 (i.e., |S₁₁| < -10dB)
</div>''',
    'engineering_content': '''<b>⚠️ Antenna Bandwidth Reference</b><br>
<table style="margin: 8px 0;">
<tr><th>Antenna Type</th><th>Typical BW</th></tr>
<tr><td>Microstrip Patch</td><td>1% ~ 5%</td></tr>
<tr><td>Dipole/Monopole</td><td>10% ~ 20%</td></tr>
<tr><td>Helix Antenna</td><td>50% ~ 70%</td></tr>
<tr><td>Log-Periodic</td><td>> 100% (Ultra-wideband)</td></tr>
</table>'''
}

# ===================== Phased Array 相控阵计算 =====================
zh['phasedarray'] = {
    'tool_name': '相控阵计算',
    'tool_desc': '线性阵列方向图、波束扫描与栅瓣分析',
    'intuition_content': '''<b>📡 什么是相控阵?</b><br><br>
想象一排扬声器排列在舞台上。如果所有扬声器<b>同时</b>发声，声音笔直地向前传播。<br>
但如果你让最左边的扬声器先发声，然后依次让右边的发声（加入"时间差"），声音就会<b>偏转到一侧</b>。<br><br>
这就是<b>相控阵天线</b>的核心原理！通过给每个天线单元施加不同的相位（等效于时间差），就能让整个阵列的波束<b>电子化扫描</b>到任意角度——不需要机械旋转。<br><br>
<b>💡 核心优势：</b>波束切换速度可达微秒级，比机械扫描快百万倍！''',
    'math_content': '''<b>📐 相控阵核心公式</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px;">
<b>阵列因子 AF：</b><br>
AF(θ) = Σ exp[j·n·(kd·sinθ + β)]<br>
k = 2π/λ, d = 间距, β = 相移<br><br>
<b>波束指向角：</b><br>
θ₀ = arcsin(-β / (k·d))<br><br>
<b>栅瓣条件（必须避免）：</b><br>
d < λ / (1 + |sinθ₀|)
</div>''',
    'engineering_content': '''<b>⚠️ 相控阵设计要点</b><br>
• 阵元间距 d < λ/2 可以在全空间无栅瓣<br>
• 大角度扫描时增益下降约 cos(θ) 倍<br>
• 互耦效应在实际设计中影响显著<br>
• 数字波束赋形 (DBF) 比模拟移相器更灵活'''
}

en['phasedarray'] = {
    'tool_name': 'Phased Array Calc',
    'tool_desc': 'Linear array pattern, beam steering, and grating lobe analysis',
    'intuition_content': '''<b>📡 What is a Phased Array?</b><br><br>
Imagine a row of speakers on a stage. If all speakers fire <b>simultaneously</b>, the sound travels straight forward.<br>
But if you make the leftmost speaker fire first, then each one to the right fires slightly later (adding a "time delay"), the sound <b>steers to one side</b>.<br><br>
This is the core principle of <b>Phased Array Antennas</b>! By applying different phases (equivalent to time delays) to each element, the entire array beam can <b>electronically scan</b> to any angle—no mechanical rotation needed.<br><br>
<b>💡 Key Advantage:</b> Beam switching speed reaches microseconds—a million times faster than mechanical scanning!''',
    'math_content': '''<b>📐 Phased Array Core Formulas</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px;">
<b>Array Factor AF:</b><br>
AF(θ) = Σ exp[j·n·(kd·sinθ + β)]<br>
k = 2π/λ, d = spacing, β = phase shift<br><br>
<b>Beam Steering Angle:</b><br>
θ₀ = arcsin(-β / (k·d))<br><br>
<b>Grating Lobe Condition (must avoid):</b><br>
d < λ / (1 + |sinθ₀|)
</div>''',
    'engineering_content': '''<b>⚠️ Phased Array Design Tips</b><br>
• Element spacing d < λ/2 eliminates grating lobes at all scan angles.<br>
• At large scan angles, gain drops by approximately cos(θ).<br>
• Mutual coupling effects are significant in practical designs.<br>
• Digital beamforming (DBF) is more flexible than analog phase shifters.'''
}

# ===================== Band Table 频段速查 =====================
zh['bandtable'] = {
    'tool_name': '频段分类',
    'tool_desc': 'IEEE/ITU 标准频段划分参考速查',
    'intuition_content': '''<b>📻 频段划分：给无线电波归类</b><br><br>
就像可见光从红到紫按波长分类一样，从几 kHz 到上百 GHz 的无线电波也需要"分门别类"以方便工程师交流。<br><br>
<b>IEEE 频段：</b>源自二战时雷达研究，用字母命名（S/C/X/Ku...），至今仍广泛用于军事和雷达领域。<br>
<b>ITU 频段：</b>国际电信联盟的标准编号系统，面向通信应用。''',
    'engineering_content': '''<b>📡 常用频段速查</b><br>
<table style="margin: 8px 0;">
<tr><th>IEEE名称</th><th>频率范围</th><th>典型应用</th></tr>
<tr><td>L</td><td>1-2 GHz</td><td>GPS、手机</td></tr>
<tr><td>S</td><td>2-4 GHz</td><td>WiFi 2.4G、气象雷达</td></tr>
<tr><td>C</td><td>4-8 GHz</td><td>WiFi 5G、卫星通信</td></tr>
<tr><td>X</td><td>8-12 GHz</td><td>军用雷达、SAR</td></tr>
<tr><td>Ku</td><td>12-18 GHz</td><td>卫星直播 (DBS)</td></tr>
<tr><td>Ka</td><td>26-40 GHz</td><td>5G毫米波、卫星宽带</td></tr>
</table>'''
}

en['bandtable'] = {
    'tool_name': 'Frequency Bands',
    'tool_desc': 'IEEE/ITU standard frequency band reference lookup',
    'intuition_content': '''<b>📻 Frequency Bands: Classifying Radio Waves</b><br><br>
Just as visible light is classified from red to violet by wavelength, radio waves from a few kHz to hundreds of GHz are categorized to help engineers communicate.<br><br>
<b>IEEE Bands:</b> Originated from WWII radar research, using letter designations (S/C/X/Ku...), still widely used in military and radar domains.<br>
<b>ITU Bands:</b> International Telecommunication Union's standard numbering system, oriented toward communications.''',
    'engineering_content': '''<b>📡 Frequency Band Quick Reference</b><br>
<table style="margin: 8px 0;">
<tr><th>IEEE Band</th><th>Freq Range</th><th>Typical Applications</th></tr>
<tr><td>L</td><td>1-2 GHz</td><td>GPS, Cellular</td></tr>
<tr><td>S</td><td>2-4 GHz</td><td>WiFi 2.4G, Weather Radar</td></tr>
<tr><td>C</td><td>4-8 GHz</td><td>WiFi 5G, Satellite</td></tr>
<tr><td>X</td><td>8-12 GHz</td><td>Military Radar, SAR</td></tr>
<tr><td>Ku</td><td>12-18 GHz</td><td>Satellite DBS</td></tr>
<tr><td>Ka</td><td>26-40 GHz</td><td>5G mmWave, Satellite BB</td></tr>
</table>'''
}

# ===================== Connector Table 连接器选型 =====================
zh['connector'] = {
    'tool_name': '连接器选型',
    'tool_desc': '常用射频连接器参数对比与选型指南',
    'intuition_content': '''<b>🔌 射频连接器：信号链的薄弱环节</b><br><br>
连接器是射频系统中最容易被忽视但影响最大的环节。一个不合适的连接器可能导致：<br>
• 信号反射（VSWR恶化）<br>
• 功率容量不足（发热甚至烧毁）<br>
• 频率响应不够（高频截止）<br><br>
<b>💡 选型三要素：</b>频率范围、功率容量、接口阻抗（50Ω / 75Ω）''',
    'engineering_content': '''<b>📊 常用连接器速查</b><br>
<table style="margin: 8px 0;">
<tr><th>型号</th><th>频率上限</th><th>特征</th></tr>
<tr><td>SMA</td><td>18 GHz</td><td>最通用，螺纹连接</td></tr>
<tr><td>N</td><td>11 GHz</td><td>大功率，户外防水</td></tr>
<tr><td>BNC</td><td>4 GHz</td><td>快速卡扣，实验室</td></tr>
<tr><td>2.92mm (K)</td><td>40 GHz</td><td>毫米波精密连接</td></tr>
<tr><td>1.85mm (V)</td><td>65 GHz</td><td>高频测量</td></tr>
</table>'''
}

en['connector'] = {
    'tool_name': 'RF Connectors',
    'tool_desc': 'Common RF connector parameter comparison and selection guide',
    'intuition_content': '''<b>🔌 RF Connectors: The Weakest Link in the Signal Chain</b><br><br>
Connectors are the most overlooked yet most impactful part of an RF system. A wrong connector choice can cause:<br>
• Signal reflections (degraded VSWR)<br>
• Insufficient power handling (overheating/burn damage)<br>
• Frequency response limitations (high-frequency cutoff)<br><br>
<b>💡 Three Selection Criteria:</b> Frequency range, Power rating, Impedance (50Ω / 75Ω)''',
    'engineering_content': '''<b>📊 Connector Quick Reference</b><br>
<table style="margin: 8px 0;">
<tr><th>Type</th><th>Max Freq</th><th>Features</th></tr>
<tr><td>SMA</td><td>18 GHz</td><td>Most common, threaded</td></tr>
<tr><td>N</td><td>11 GHz</td><td>High power, weather-proof</td></tr>
<tr><td>BNC</td><td>4 GHz</td><td>Quick bayonet, lab use</td></tr>
<tr><td>2.92mm (K)</td><td>40 GHz</td><td>mmWave precision</td></tr>
<tr><td>1.85mm (V)</td><td>65 GHz</td><td>High-freq measurement</td></tr>
</table>'''
}

# ===================== ESeries Table E系列标准值 =====================
zh['eseries'] = {
    'tool_name': 'E系列标称值速查',
    'tool_desc': '电阻/电容 E6/E12/E24/E48/E96 标准标称值速查',
    'intuition_content': '''<b>📐 什么是E系列标准值?</b><br><br>
为什么电阻不能做成任意阻值？因为制造工艺有精度限制。E 系列就是按照一定规则从 1~10 之间选出一组"代表值"，使得任意阻值都能用这些标准值近似。<br><br>
E12 意味着每 10 倍量程有 12 个标准值（精度 ±10%）<br>
E96 意味着每 10 倍量程有 96 个标准值（精度 ±1%）''',
    'engineering_content': '''<b>📊 E系列速查</b><br>
<table style="margin: 8px 0;">
<tr><th>系列</th><th>精度</th><th>值数/10倍</th></tr>
<tr><td>E6</td><td>±20%</td><td>6</td></tr>
<tr><td>E12</td><td>±10%</td><td>12</td></tr>
<tr><td>E24</td><td>±5%</td><td>24</td></tr>
<tr><td>E48</td><td>±2%</td><td>48</td></tr>
<tr><td>E96</td><td>±1%</td><td>96</td></tr>
</table>'''
}

en['eseries'] = {
    'tool_name': 'E-Series Lookup',
    'tool_desc': 'Resistor/Capacitor E6/E12/E24/E48/E96 standard value lookup',
    'intuition_content': '''<b>📐 What are E-Series Standard Values?</b><br><br>
Why can't resistors be manufactured in any arbitrary value? Because manufacturing tolerances are limited. The E-series selects a set of "representative values" between 1 and 10

, so any value can be approximated by these standards.<br><br>
E12 means 12 standard values per decade (±10% tolerance).<br>
E96 means 96 standard values per decade (±1% tolerance).''',
    'engineering_content': '''<b>📊 E-Series Quick Reference</b><br>
<table style="margin: 8px 0;">
<tr><th>Series</th><th>Tolerance</th><th>Values/Decade</th></tr>
<tr><td>E6</td><td>±20%</td><td>6</td></tr>
<tr><td>E12</td><td>±10%</td><td>12</td></tr>
<tr><td>E24</td><td>±5%</td><td>24</td></tr>
<tr><td>E48</td><td>±2%</td><td>48</td></tr>
<tr><td>E96</td><td>±1%</td><td>96</td></tr>
</table>'''
}

# ===================== Waveguide Table 波导法兰 =====================
zh['waveguide'] = {
    'tool_name': '波导法兰',
    'tool_desc': '标准波导型号/截止频率/法兰尺寸速查',
    'intuition_content': '''<b>📺 什么是波导?</b><br><br>
在低频，我们用同轴线传输信号。但当频率升高到微波/毫米波段时，同轴线的损耗急剧增大。这时候就需要用<b>波导</b>——一种中空的金属管，让电磁波在里面"跑"。<br><br>
波导的截面尺寸决定了它能传输的最低频率（截止频率）。尺寸越大，截止频率越低。<br><br>
<b>法兰 (Flange):</b> 波导管的"接口"标准，就像水管的法兰接头一样。''',
    'engineering_content': '''<b>📊 常用波导速查</b><br>
<table style="margin: 8px 0;">
<tr><th>EIA编号</th><th>频率范围</th><th>常见应用</th></tr>
<tr><td>WR-284</td><td>2.60-3.95 GHz</td><td>S波段雷达</td></tr>
<tr><td>WR-137</td><td>5.85-8.20 GHz</td><td>C波段通信</td></tr>
<tr><td>WR-90</td><td>8.20-12.4 GHz</td><td>X波段雷达</td></tr>
<tr><td>WR-42</td><td>18.0-26.5 GHz</td><td>K波段</td></tr>
<tr><td>WR-28</td><td>26.5-40.0 GHz</td><td>Ka波段5G</td></tr>
</table>'''
}

en['waveguide'] = {
    'tool_name': 'Waveguide Flanges',
    'tool_desc': 'Standard waveguide designation/cutoff frequency/flange size reference',
    'intuition_content': '''<b>📺 What is a Waveguide?</b><br><br>
At low frequencies, we use coaxial cables to transmit signals. But as frequency rises into microwave/mmWave ranges, coaxial loss skyrockets. That's when we use <b>waveguides</b>—hollow metal tubes that let EM waves "run" inside.<br><br>
A waveguide's cross-section size determines the lowest frequency it can transmit (cutoff frequency). Larger cross-section = lower cutoff.<br><br>
<b>Flanges:</b> The "connector standard" for waveguide tubes—like pipe flanges in plumbing.''',
    'engineering_content': '''<b>📊 Common Waveguide Reference</b><br>
<table style="margin: 8px 0;">
<tr><th>EIA ID</th><th>Freq Range</th><th>Typical Use</th></tr>
<tr><td>WR-284</td><td>2.60-3.95 GHz</td><td>S-band Radar</td></tr>
<tr><td>WR-137</td><td>5.85-8.20 GHz</td><td>C-band Comms</td></tr>
<tr><td>WR-90</td><td>8.20-12.4 GHz</td><td>X-band Radar</td></tr>
<tr><td>WR-42</td><td>18.0-26.5 GHz</td><td>K-band</td></tr>
<tr><td>WR-28</td><td>26.5-40.0 GHz</td><td>Ka-band 5G</td></tr>
</table>'''
}

# ===================== Online Tools 在线工具导航 =====================
zh['onlinetools'] = {
    'tool_name': '精品在线工具',
    'tool_desc': '国内外射频/微波在线工具推荐导航'
}

en['onlinetools'] = {
    'tool_name': 'Online Tools',
    'tool_desc': 'Curated RF/Microwave online tool recommendations'
}

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)

print("Antenna + Reference tools language entries injected!")
