"""
批量为所有剩余 RF 工具注入翻译词条
处理: vswr, cascade, attenuator, matching, link_budget
"""
import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

# ===================== VSWR 驻波计算 =====================
zh['vswr'] = {
    'tool_name': '驻波计算',
    'tool_desc': '计算VSWR、回波损耗、反射系数之间的换算关系',
    'intuition_content': '''<b>📡 什么是驻波比 (VSWR)?</b><br><br>
想象你把一根绳子的一端系在墙上，然后向绳子发送一个波。如果绳子和墙的连接不够"完美"（阻抗不匹配），部分波会被反射回来。<br><br>
<b>入射波 + 反射波 = 驻波</b><br><br>
驻波比 (VSWR) 就是衡量你的系统中反射有多严重的一个数：<br>
• <b>VSWR = 1.0</b>：完美匹配，零反射（理想状态）<br>
• <b>VSWR = 2.0</b>：约11%的功率被反射<br>
• <b>VSWR = ∞</b>：全部反射，信号完全打回（开路 / 短路）<br><br>
<b>💡 工程黄金法则：</b>对大多数射频系统，VSWR < 2.0（即回波损耗 > 10dB）就算可接受。''',
    'math_content': '''<b>📐 VSWR 核心换算公式</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>反射系数 Γ (Gamma)：</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
|Γ| = (VSWR - 1) / (VSWR + 1)
</span><br><br>
<b>回波损耗 RL (Return Loss)：</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
RL(dB) = -20 × log₁₀|Γ|
</span><br><br>
<b>反射功率百分比：</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
P_refl = |Γ|² × 100%
</span><br><br>
<b>失配损耗 ML (Mismatch Loss)：</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
ML(dB) = -10 × log₁₀(1 - |Γ|²)
</span>
</div>''',
    'engineering_content': '''<b>⚠️ VSWR 工程参考速查</b><br>
<table style="margin: 8px 0;">
<tr><th>VSWR</th><th>回波损耗(dB)</th><th>反射功率</th><th>评价</th></tr>
<tr><td>1.0</td><td>∞</td><td>0%</td><td>完美匹配</td></tr>
<tr><td>1.2</td><td>20.8</td><td>0.8%</td><td>优秀</td></tr>
<tr><td>1.5</td><td>14.0</td><td>4.0%</td><td>良好</td></tr>
<tr><td>2.0</td><td>9.5</td><td>11.1%</td><td>可接受</td></tr>
<tr><td>3.0</td><td>6.0</td><td>25.0%</td><td>需要改进</td></tr>
<tr><td>5.0</td><td>3.5</td><td>44.4%</td><td>较差</td></tr>
</table>'''
}

en['vswr'] = {
    'tool_name': 'VSWR Calculator',
    'tool_desc': 'Convert between VSWR, Return Loss, and Reflection Coefficient',
    'intuition_content': '''<b>📡 What is VSWR?</b><br><br>
Imagine tying one end of a rope to a wall and sending a wave down it. If the connection isn't "perfect" (impedance mismatch), part of the wave bounces back.<br><br>
<b>Incident Wave + Reflected Wave = Standing Wave</b><br><br>
VSWR (Voltage Standing Wave Ratio) measures how severe reflections are in your system:<br>
• <b>VSWR = 1.0</b>: Perfect match, zero reflection (ideal).<br>
• <b>VSWR = 2.0</b>: About 11% of power reflected.<br>
• <b>VSWR = ∞</b>: Total reflection (open/short circuit).<br><br>
<b>💡 Golden Rule:</b> For most RF systems, VSWR < 2.0 (i.e., Return Loss > 10dB) is acceptable.''',
    'math_content': '''<b>📐 VSWR Core Conversion Formulas</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>Reflection Coefficient Γ (Gamma):</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
|Γ| = (VSWR - 1) / (VSWR + 1)
</span><br><br>
<b>Return Loss RL:</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
RL(dB) = -20 × log₁₀|Γ|
</span><br><br>
<b>Reflected Power Percentage:</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
P_refl = |Γ|² × 100%
</span><br><br>
<b>Mismatch Loss ML:</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
ML(dB) = -10 × log₁₀(1 - |Γ|²)
</span>
</div>''',
    'engineering_content': '''<b>⚠️ VSWR Engineering Reference</b><br>
<table style="margin: 8px 0;">
<tr><th>VSWR</th><th>Return Loss(dB)</th><th>Reflected Power</th><th>Rating</th></tr>
<tr><td>1.0</td><td>∞</td><td>0%</td><td>Perfect</td></tr>
<tr><td>1.2</td><td>20.8</td><td>0.8%</td><td>Excellent</td></tr>
<tr><td>1.5</td><td>14.0</td><td>4.0%</td><td>Good</td></tr>
<tr><td>2.0</td><td>9.5</td><td>11.1%</td><td>Acceptable</td></tr>
<tr><td>3.0</td><td>6.0</td><td>25.0%</td><td>Needs Work</td></tr>
<tr><td>5.0</td><td>3.5</td><td>44.4%</td><td>Poor</td></tr>
</table>'''
}

# ===================== Cascade 级联驻波 =====================
zh['cascade'] = {
    'tool_name': '级联驻波',
    'tool_desc': '计算多级模块级联后的系统总驻波比',
    'intuition_content': '''<b>🔗 什么是级联驻波?</b><br><br>
当你把多个射频模块串联在一起（比如：天线 → 滤波器 → 低噪声放大器 → 混频器），每个连接点都会产生自己的反射。<br><br>
级联驻波计算解决的核心问题是：<b>知道每个模块自己的 VSWR，如何预估整条链路的总 VSWR？</b><br><br>
<b>💡 关键：</b>级联后的总 VSWR 总是比单个模块更差（更大），因为反射在各个连接点之间来回弹跳叠加。最坏情况下各反射同相叠加。''',
    'math_content': '''<b>📐 级联 VSWR 公式</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>最差情况（反射同相叠加）：</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
|Γ_total| = |Γ₁| + |Γ₂| + |Γ₃| + ...
</span><br><br>
<b>然后转换回 VSWR：</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
VSWR_total = (1 + |Γ_total|) / (1 - |Γ_total|)
</span>
</div>
注意：如果级联中存在衰减器或放大器，它们会衰减通过的反射波，从而改善后续级的 VSWR 贡献。''',
    'engineering_content': '''<b>⚠️ 级联 VSWR 工程建议</b><br><br>
• 在高 VSWR 模块之间插入 3~6dB 衰减器可以显著改善系统匹配<br>
• 放大器的反向隔离度也能抑制驻波的反向传播<br>
• 实际中各模块的反射相位几乎不可能完全同相，所以真实的级联 VSWR 通常优于最差值计算<br>
• 对于关键链路，建议用矢量网络分析仪 (VNA) 实测端到端 S₁₁'''
}

en['cascade'] = {
    'tool_name': 'Cascade VSWR',
    'tool_desc': 'Calculate total VSWR for cascaded multi-stage RF modules',
    'intuition_content': '''<b>🔗 What is Cascade VSWR?</b><br><br>
When you chain multiple RF modules together (e.g., Antenna → Filter → LNA → Mixer), each junction creates its own reflections.<br><br>
The key question Cascade VSWR solves: <b>Given each module's individual VSWR, what is the total VSWR of the entire chain?</b><br><br>
<b>💡 Key Insight:</b> The cascaded VSWR is always worse (higher) than any single module, because reflections bounce between junctions and superimpose. The worst case is when all reflections add in-phase.''',
    'math_content': '''<b>📐 Cascade VSWR Formula</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>Worst Case (In-phase Addition):</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
|Γ_total| = |Γ₁| + |Γ₂| + |Γ₃| + ...
</span><br><br>
<b>Convert back to VSWR:</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
VSWR_total = (1 + |Γ_total|) / (1 - |Γ_total|)
</span>
</div>
Note: If the cascade contains attenuators or amplifiers, they attenuate the reflected waves passing through, improving the VSWR contribution of subsequent stages.''',
    'engineering_content': '''<b>⚠️ Cascade VSWR Engineering Tips</b><br><br>
• Insert 3~6dB attenuators between high-VSWR modules to significantly improve system match.<br>
• Amplifier reverse isolation also suppresses backward VSWR propagation.<br>
• In practice, reflection phases are almost never perfectly in-phase, so real cascade VSWR is usually better than worst-case calculations.<br>
• For critical chains, measure end-to-end S₁₁ with a Vector Network Analyzer (VNA).'''
}

# ===================== Attenuator 衰减计算 =====================
zh['attenuator'] = {
    'tool_name': '衰减计算',
    'tool_desc': 'π型/T型衰减器电阻网络计算',
    'intuition_content': '''<b>🔌 什么是衰减器?</b><br><br>
衰减器就像一个"精密音量旋钮"——它在保持信号特性（阻抗匹配、频率响应）不变的同时，按照你指定的 dB 值精确降低信号功率。<br><br>
<b>为什么不能直接用一个电阻串联?</b><br>
因为单个电阻会破坏阻抗匹配，导致信号反射。衰减器用 3 个电阻组成特殊的 π 型或 T 型网络，同时实现精确衰减和完美的阻抗匹配。<br><br>
<b>💡 常见用途：</b><br>
• 改善 VSWR（在高驻波模块之间插入垫片）<br>
• 降低信号电平以保护后级设备<br>
• 实验室测试中精确设定功率电平''',
    'math_content': '''<b>📐 π 型 / T 型衰减器电阻公式</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>π 型衰减器 (50Ω → 50Ω)：</b><br>
R₁ = R₃ = Z₀ × (K + 1) / (K - 1)<br>
R₂ = Z₀ × (K² - 1) / (2K)<br>
其中 K = 10^(dB/20)
</div>
<div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>T 型衰减器 (50Ω → 50Ω)：</b><br>
R₁ = R₃ = Z₀ × (K - 1) / (K + 1)<br>
R₂ = 2 × Z₀ × K / (K² - 1)
</div>''',
    'engineering_content': '''<b>⚠️ 衰减器设计要点</b><br>
• π 型适合 PCB 贴片（接地明确）<br>
• T 型适合同轴连接器封装<br>
• 注意电阻的功率额定值和频率特性<br>
• 高频时寄生参数会导致衰减量偏差'''
}

en['attenuator'] = {
    'tool_name': 'Attenuator Calculator',
    'tool_desc': 'Pi/T-type attenuator resistor network calculation',
    'intuition_content': '''<b>🔌 What is an Attenuator?</b><br><br>
An attenuator is like a "precision volume knob"—it reduces signal power by a precise dB value while maintaining signal integrity (impedance match, frequency response).<br><br>
<b>Why not just use a single series resistor?</b><br>
Because a single resistor would destroy impedance matching, causing signal reflections. Attenuators use 3 resistors in a special Pi or T network to achieve precise attenuation AND perfect impedance matching simultaneously.<br><br>
<b>💡 Common Uses:</b><br>
• Improve VSWR (insert pads between high-VSWR modules)<br>
• Reduce signal level to protect downstream equipment<br>
• Set precise power levels in lab testing''',
    'math_content': '''<b>📐 Pi / T-type Attenuator Resistor Formulas</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>Pi-type Attenuator (50Ω → 50Ω):</b><br>
R₁ = R₃ = Z₀ × (K + 1) / (K - 1)<br>
R₂ = Z₀ × (K² - 1) / (2K)<br>
Where K = 10^(dB/20)
</div>
<div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>T-type Attenuator (50Ω → 50Ω):</b><br>
R₁ = R₃ = Z₀ × (K - 1) / (K + 1)<br>
R₂ = 2 × Z₀ × K / (K² - 1)
</div>''',
    'engineering_content': '''<b>⚠️ Attenuator Design Tips</b><br>
• Pi-type is preferred for PCB SMD layout (clear ground)<br>
• T-type is preferred for coaxial connector packaging<br>
• Mind the power rating and frequency characteristics of resistors<br>
• At high frequencies, parasitic effects can cause attenuation drift'''
}

# ===================== Matching 阻抗匹配 =====================
zh['matching'] = {
    'tool_name': '阻抗匹配',
    'tool_desc': 'L/C 匹配网络设计 (Smith 圆图法)',
    'intuition_content': '''<b>🎯 什么是阻抗匹配?</b><br><br>
阻抗匹配就像给水管接口选择合适的转换接头——如果两根水管口径不同，强行对接会导致水流紊乱（信号反射和功率浪费）。<br><br>
L/C 匹配网络通过电感 (L) 和电容 (C) 的组合，在源阻抗和负载阻抗之间搭建一座"阻抗变换桥"，使得信号认为它看到的两端阻抗是一样的（通常都变换到 50Ω）。<br><br>
<b>💡 Smith 圆图：</b>射频工程师的"地图"，将所有可能的阻抗映射到一个单位圆上，使匹配路径的设计变得直观可视。''',
    'math_content': '''<b>📐 L 型匹配网络公式</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>当 R_L > Z₀ 时（高阻抗到低阻抗）：</b><br>
Q = √(R_L/Z₀ - 1)<br>
X_series = Q × Z₀<br>
X_shunt = R_L / Q
</div>
<div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>当 R_L < Z₀ 时（低阻抗到高阻抗）：</b><br>
Q = √(Z₀/R_L - 1)<br>
X_series = Q × R_L<br>
X_shunt = Z₀ / Q
</div>
其中 X_series 和 X_shunt 可以是电感或电容, 取决于匹配拓扑。''',
    'engineering_content': '''<b>⚠️ 匹配网络选型建议</b><br>
• L 型匹配最简单但带宽窄<br>
• Pi/T 型提供更多自由度（可控 Q 值）<br>
• 实际中还需考虑器件寄生参数<br>
• 宽带匹配可能需要多级级联'''
}

en['matching'] = {
    'tool_name': 'Impedance Matching',
    'tool_desc': 'L/C Matching Network Design (Smith Chart Method)',
    'intuition_content': '''<b>🎯 What is Impedance Matching?</b><br><br>
Impedance matching is like selecting the right pipe adapter—if two pipes have different diameters, forcing a connection causes turbulence (signal reflections and power waste).<br><br>
An L/C matching network uses inductors (L) and capacitors (C) to build an "impedance transformation bridge" between source and load, making the signal "see" the same impedance on both sides (usually transformed to 50Ω).<br><br>
<b>💡 Smith Chart:</b> The RF engineer's "map"—it maps all possible impedances onto a unit circle, making matching path design intuitive and visual.''',
    'math_content': '''<b>📐 L-type Matching Network Formulas</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>When R_L > Z₀ (High to Low Impedance):</b><br>
Q = √(R_L/Z₀ - 1)<br>
X_series = Q × Z₀<br>
X_shunt = R_L / Q
</div>
<div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>When R_L < Z₀ (Low to High Impedance):</b><br>
Q = √(Z₀/R_L - 1)<br>
X_series = Q × R_L<br>
X_shunt = Z₀ / Q
</div>
Where X_series and X_shunt can be either inductor or capacitor, depending on the topology.''',
    'engineering_content': '''<b>⚠️ Matching Network Selection Tips</b><br>
• L-type is simplest but narrow-band.<br>
• Pi/T-type offers more freedom (controllable Q).<br>
• In practice, component parasitics must be considered.<br>
• Wideband matching may require multi-stage cascading.'''
}

# ===================== Link Budget 链路预算 =====================
zh['linkbudget'] = {
    'tool_name': '链路预算',
    'tool_desc': '完整无线通信链路功率预算分析',
    'intuition_content': '''<b>📊 什么是链路预算?</b><br><br>
链路预算就像一笔"能量账"——从发射端到接收端，把所有的功率"收入"和"支出"逐项列清楚：<br><br>
<b>收入（正 dB）：</b>发射功率、天线增益<br>
<b>支出（负 dB）：</b>路径损耗、线缆损耗、衰落裕量<br><br>
最终"账户余额"就是到达接收机的信号功率。如果这个余额高于接收机的灵敏度门限，链路就能正常工作。''',
    'math_content': '''<b>📐 链路预算公式</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>接收功率：</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
P_rx = P_tx + G_tx - L_tx - FSPL + G_rx - L_rx - M
</span><br><br>
<b>链路裕量 = P_rx - P_sensitivity</b><br>
裕量 > 0 → 链路可用
</div>''',
    'engineering_content': '''<b>⚠️ 链路预算注意事项</b><br>
• 一定要预留 10~20dB 衰落裕量<br>
• 高频段 (>6GHz) 需考虑雨衰<br>
• 室内环境需额外增加穿墙损耗<br>
• 注意 EIRP 法规限制'''
}

en['linkbudget'] = {
    'tool_name': 'Link Budget',
    'tool_desc': 'Complete wireless communication link power budget analysis',
    'intuition_content': '''<b>📊 What is a Link Budget?</b><br><br>
A Link Budget is an "energy ledger"—from transmitter to receiver, it itemizes every power "income" and "expense":<br><br>
<b>Income (+dB):</b> Transmit power, Antenna gains<br>
<b>Expense (-dB):</b> Path loss, Cable loss, Fade margin<br><br>
The final "account balance" is the signal power reaching the receiver. If this balance exceeds the receiver's sensitivity threshold, the link works.''',
    'math_content': '''<b>📐 Link Budget Formula</b><br><br>
<div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
<b>Received Power:</b><br>
<span style="font-family: 'Cambria Math', serif; font-size: 14px;">
P_rx = P_tx + G_tx - L_tx - FSPL + G_rx - L_rx - M
</span><br><br>
<b>Link Margin = P_rx - P_sensitivity</b><br>
Margin > 0 → Link is viable.
</div>''',
    'engineering_content': '''<b>⚠️ Link Budget Best Practices</b><br>
• Always reserve 10~20dB fade margin.<br>
• At high frequencies (>6GHz), account for rain attenuation.<br>
• Indoor scenarios require extra wall-penetration loss.<br>
• Mind regulatory EIRP limits.'''
}

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)

print("RF tools (vswr, cascade, attenuator, matching, linkbudget) language entries injected!")
