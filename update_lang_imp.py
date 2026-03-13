import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

if 'impedance' not in zh: zh['impedance'] = {}
if 'impedance' not in en: en['impedance'] = {}

imp_trans = {
    'tool_name': ('阻抗计算', 'Impedance Calculator'),
    'tool_desc': ('计算传输线特性阻抗 (同轴线/微带线/CPWG)', 'Calculate characteristic impedance of Coaxial, Microstrip, and CPWG'),
    'group_mode': ('结构模式', 'Structure Mode'),
    'radio_coax': ('同轴线 (Coaxial)', 'Coaxial Line'),
    'radio_ms': ('单微带线 (Microstrip)', 'Microstrip Line'),
    'radio_cpwg': ('共面波导 (CPWG)', 'Coplanar Waveguide (CPWG)'),
    
    'lbl_calc': ('计算', 'Calculate'),
    'lbl_custom': ('自定义', 'Custom'),
    'lbl_er': ('介电常数 εᵣ:', 'Dielectric Constant εᵣ:'),
    'lbl_z0': ('阻抗 Z₀:', 'Impedance Z₀:'),
    
    'coax_d': ('内导体外径 d:', 'Inner Conductor OD d:'),
    'coax_D': ('外导体内径 D:', 'Outer Conductor ID D:'),
    
    'ms_w': ('导线宽度 W:', 'Trace Width W:'),
    'ms_h': ('介质厚度 H:', 'Substrate Thickness H:'),
    'ms_t': ('铜箔厚度 T:', 'Trace Thickness T:'),
    
    'cpwg_w': ('中心线宽 W:', 'Center Trace Width W:'),
    'cpwg_s': ('间隙宽度 S:', 'Gap Width S:'),
    
    'title_eval': ('评估结果', 'Evaluation Result'),
    'title_detail': ('📊 详细参数', '📊 Detailed Parameters'),
    'detail_er': ('有效介电常数 εₑ', 'Effective Dielectric Constant εₑ'),
    'detail_vel': ('速度因子', 'Velocity Factor'),
    'detail_cap': ('单位长度电容', 'Capacitance per Unit Length'),
    'detail_ratio': ('尺寸比例', 'Dimension Ratio'),
    
    'title_diagram': ('📐 截面示意图', '📐 Cross Section Diagram'),
    'diagram_placeholder': ('截面示意图', 'Cross section placeholder'),
    
    'eval_veri': ('✅ 验证阻抗: ', '✅ Verified Impedance: '),
    'eval_50': ('✅ 接近 50Ω 标准阻抗', '✅ Near 50Ω Standard Impedance'),
    'eval_75': ('✅ 接近 75Ω 标准阻抗', '✅ Near 75Ω Standard Impedance'),
    'eval_non': ('ℹ️ 非标准阻抗值', 'ℹ️ Non-standard Impedance Value'),
    
    'err_dim': ('请输入有效的尺寸', 'Please enter valid dimensions'),
    'err_d_D': ('外径必须大于内径', 'Outer diameter must be greater than inner diameter'),
    'err_z_D': ('请输入有效的阻抗和外径', 'Please enter valid impedance and outer diameter'),
    'err_z_d': ('请输入有效的阻抗和内径', 'Please enter valid impedance and inner diameter'),
    'err_z_H': ('请输入有效的阻抗和介质厚度', 'Please enter valid impedance and substrate thickness'),
    'err_z_W': ('请输入有效的阻抗和线宽', 'Please enter valid impedance and trace width'),
    'err_z_dim': ('请输入有效的阻抗和尺寸', 'Please enter valid impedance and dimensions'),
    'err_er': ('无效的介电常数: ', 'Invalid dielectric constant: '),
    
    'intuition_content': (
        '''<b>📡 什么是特性阻抗？</b><br><br>
        特性阻抗 Z₀ 是传输线的固有属性，描述信号在传输线中传播时的电压/电流比。<br><br>
        <b>🎯 为什么重要？</b><br>
        • 阻抗匹配：源/负载阻抗与传输线阻抗不匹配会导致信号反射<br>
        • 50Ω 和 75Ω 是常用标准阻抗<br>
        • 高频信号对阻抗匹配更敏感<br><br>
        <b>💡 常见应用：</b><br>
        • 50Ω：射频系统、仪器设备<br>
        • 75Ω：视频信号、有线电视''',
        
        '''<b>📡 What is Characteristic Impedance?</b><br><br>
        Characteristic impedance Z₀ is an inherent property of a transmission line, describing the voltage-to-current ratio as a signal propagates through it.<br><br>
        <b>🎯 Why is it important?</b><br>
        • Impedance Matching: Mismatches between source/load and the line cause signal reflections.<br>
        • 50Ω and 75Ω are the most common standard impedances.<br>
        • High-frequency signals are much more sensitive to impedance mismatches.<br><br>
        <b>💡 Common Applications:</b><br>
        • 50Ω: RF systems, test & measurement instruments.<br>
        • 75Ω: Video signals, Cable TV (CATV).'''
    ),
    'math_content': (
        '''<b>📐 阻抗计算公式 (v1.2)</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ 同轴线</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 13px;">
        Z₀ = (60 / √εᵣ) × ln(D/d)
        </span><br>
        • D = 外导体内径, d = 内导体外径<br>
        • 速度因子: v_f = 1 / √εᵣ
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>2️⃣ 微带线 (Hammerstad-Jensen 1980)</b><br>
        <span style="font-family: serif; font-size: 12px;">
        窄线 (u≤1): Z₀ = (60/√εₑ) × ln(8/u + u/4)<br>
        宽线 (u>1): Z₀ = (120π/√εₑ) / (u + 1.393 + 0.667×ln(u + 1.444))
        </span><br><br>
        <b>有效介电常数:</b><br>
        <span style="font-family: serif; font-size: 12px;">
        εₑ = (εᵣ+1)/2 + (εᵣ-1)/2 × F₁ − (εᵣ-1)×T/(4.6H)
        </span><br>
        • u = W_eff/H (有效宽厚比)<br>
        • F₁ = (1+12/u)⁻⁰·⁵ + 0.04(1−u)² 当 u≤1<br>
        • F₁ = (1+12/u)⁻⁰·⁵ 当 u>1
        </div>
        <div style="background-color: #FEF3C7; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>3️⃣ CBCPW (Ghione-Naldi 1984 + Gevorgian 1995)</b><br>
        <span style="font-family: serif; font-size: 13px;">
        Z₀ = 60π / [√εₑ × (q₁ + q₃)]
        </span><br><br>
        <b>电容比法有效介电常数:</b><br>
        <span style="font-family: serif; font-size: 12px;">
        εₑ = (q₁ + εᵣ×q₃) / (q₁ + q₃)
        </span><br>
        • q₁ = K(k)/K(k') — 空气层贡献<br>
        • q₃ = K(k₃)/K(k₃') — 接地层贡献<br>
        • k = W/(W+2S), k₃ = tanh(πW/4H)/tanh(π(W+2S)/4H)<br>
        • K(x) = 完全椭圆积分第一类
        </div>''',
        
        '''<b>📐 Impedance Calculation Formulas (v1.2)</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ Coaxial Line</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 13px;">
        Z₀ = (60 / √εᵣ) × ln(D/d)
        </span><br>
        • D = Outer Conductor ID, d = Inner Conductor OD<br>
        • Velocity factor: v_f = 1 / √εᵣ
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>2️⃣ Microstrip (Hammerstad-Jensen 1980)</b><br>
        <span style="font-family: serif; font-size: 12px;">
        Narrow (u≤1): Z₀ = (60/√εₑ) × ln(8/u + u/4)<br>
        Wide (u>1): Z₀ = (120π/√εₑ) / (u + 1.393 + 0.667×ln(u + 1.444))
        </span><br><br>
        <b>Effective Dielectric Constant:</b><br>
        <span style="font-family: serif; font-size: 12px;">
        εₑ = (εᵣ+1)/2 + (εᵣ-1)/2 × F₁ − (εᵣ-1)×T/(4.6H)
        </span><br>
        • u = W_eff/H (Effective Width-to-Height Ratio)<br>
        • F₁ = (1+12/u)⁻⁰·⁵ + 0.04(1−u)² for u≤1<br>
        • F₁ = (1+12/u)⁻⁰·⁵ for u>1
        </div>
        <div style="background-color: #FEF3C7; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>3️⃣ CBCPW (Ghione-Naldi 1984 + Gevorgian 1995)</b><br>
        <span style="font-family: serif; font-size: 13px;">
        Z₀ = 60π / [√εₑ × (q₁ + q₃)]
        </span><br><br>
        <b>Effective Dielectric via Capacitance Ratio:</b><br>
        <span style="font-family: serif; font-size: 12px;">
        εₑ = (q₁ + εᵣ×q₃) / (q₁ + q₃)
        </span><br>
        • q₁ = K(k)/K(k') — Air layer contribution<br>
        • q₃ = K(k₃)/K(k₃') — Ground plane contribution<br>
        • k = W/(W+2S), k₃ = tanh(πW/4H)/tanh(π(W+2S)/4H)<br>
        • K(x) = Complete Elliptic Integral of the First Kind
        </div>'''
    ),
    'engineering_content': (
        '''<b>✅ 50Ω 微带线参考尺寸 (FR4 εᵣ=4.3):</b><br>
        <table style="margin: 8px 0;">
        <tr><td>H = 0.4mm</td><td>→ W ≈ 0.76mm</td></tr>
        <tr><td>H = 0.6mm</td><td>→ W ≈ 1.14mm</td></tr>
        <tr><td>H = 0.8mm</td><td>→ W ≈ 1.52mm</td></tr>
        <tr><td>H = 1.0mm</td><td>→ W ≈ 1.90mm</td></tr>
        </table>
        <b>⚠️ 设计注意事项:</b><br>
        • 铜箔厚度会略微影响阻抗（1oz ≈ 35μm）<br>
        • 高频时需考虑介质损耗（Df）<br>
        • CPWG 比微带线抗干扰性更好''',
        
        '''<b>✅ 50Ω Microstrip Reference Specs (FR4 εᵣ=4.3):</b><br>
        <table style="margin: 8px 0;">
        <tr><td>H = 0.4mm</td><td>→ W ≈ 0.76mm</td></tr>
        <tr><td>H = 0.6mm</td><td>→ W ≈ 1.14mm</td></tr>
        <tr><td>H = 0.8mm</td><td>→ W ≈ 1.52mm</td></tr>
        <tr><td>H = 1.0mm</td><td>→ W ≈ 1.90mm</td></tr>
        </table>
        <b>⚠️ Design Considerations:</b><br>
        • Trace thickness slightly impacts impedance (1oz ≈ 35μm).<br>
        • Dielectric loss tangent (Df) must be considered at high frequencies.<br>
        • CPWG offers better isolation and interference resistance than standard microstrip.'''
    ),
    'boundary_content': (
        '''<b>⚠️ 公式适用范围:</b><br><br>
        <b>微带线 (Hammerstad-Jensen 1980):</b><br>
        • 适用: 0.05 ≤ W/H ≤ 20<br>
        • 频率 < 30 GHz (准静态近似)<br>
        • 含铜箔厚度修正 (Wheeler + Schneider)<br>
        • 与 SI9000 吻合度: ~0.1%<br><br>
        <b>CBCPW (Ghione-Naldi 1984):</b><br>
        • 适用: 底部有接地层的共面波导<br>
        • W/(W+2S) 在 0.2~0.8 范围精度最高<br>
        • 含 Gevorgian 铜箔厚度修正<br>
        • 使用 tanh 接地层修正 (非 sinh)<br>
        • 与 SI9000 吻合度: ~2%<br><br>
        <b>精度说明:</b><br>
        v1.2 公式经过与 SI9000 对照验证。<br>
        如需更高精度，建议使用全波仿真 (HFSS 等)。''',
        
        '''<b>⚠️ Formula Applicable Range:</b><br><br>
        <b>Microstrip (Hammerstad-Jensen 1980):</b><br>
        • Valid for: 0.05 ≤ W/H ≤ 20<br>
        • Frequencies < 30 GHz (Quasi-static approximation)<br>
        • Includes trace thickness correction (Wheeler + Schneider)<br>
        • Agreement with SI9000: ~0.1%<br><br>
        <b>CBCPW (Ghione-Naldi 1984):</b><br>
        • Valid for: Coplanar waveguides with bottom ground capability<br>
        • Best accuracy when W/(W+2S) is between 0.2 and 0.8<br>
        • Includes Gevorgian trace thickness correction<br>
        • Uses `tanh` ground plane correction (not `sinh`)<br>
        • Agreement with SI9000: ~2%<br><br>
        <b>Accuracy Note:</b><br>
        v1.2 formulas have been cross-verified against SI9000.<br>
        For even higher precision, full-wave 3D EM simulation (e.g., HFSS) is recommended.'''
    ),
    'history_content': (
        '''<b>📜 传输线理论简史</b><br><br>
        <div style="background-color: #F5F0FF; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🔬 1855 — 开尔文困境</b><br>
        威廉·汤姆森 (后来的开尔文勋爵) 在分析跨大西洋海底电报线缆时，首次建立了传输线的数学模型...
        </div>
        <div style="background-color: #FFF5F0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>⚡ 1886 — 赫兹的验证</b><br>
        赫兹用一对平行导线传输电磁波，实验验证了麦克斯韦方程，这可以说是最早的传输线阻抗测量。
        </div>
        <div style="background-color: #F0F8FF; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>📡 为什么是 50Ω？</b><br>
        同轴线的功率容量在 30Ω 时最大，而衰减在 77Ω 时最小。50Ω 是两者的几何平均值 (√30×77 ≈ 48Ω)，成为射频系统的"黄金标准"。
        </div>
        <div style="background-color: #FFFFF0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🏗️ 微带线革命 (1950s)</b><br>
        由 ITT 实验室发明，使 PCB 制作微波电路成为可能。Hammerstad 和 Jensen 1980 年公式至今仍是工业基石。
        </div>
        <div style="background-color: #F0FFF0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🌊 共面波导 (1969)</b><br>
        C.P. Wen 首次提出 CPW。信号线和接地同面，大大简化 MMIC 制造工艺。
        </div>''',
        
        '''<b>📜 Brief History of Transmission Line Theory</b><br><br>
        <div style="background-color: #F5F0FF; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🔬 1855 — Lord Kelvin's Dilemma</b><br>
        William Thomson (Lord Kelvin) established the first mathematical models for transmission lines while investigating the cross-Atlantic telegraph cable distortion, realizing the essence of impedance matching.
        </div>
        <div style="background-color: #FFF5F0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>⚡ 1886 — Hertz's Validation</b><br>
        Hertz transmitted EM waves through parallel wires to prove Maxwell's equations. Observing standing waves was basically the first empirical impedance measurement!
        </div>
        <div style="background-color: #F0F8FF; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>📡 Why 50Ω?</b><br>
        Coaxial lines hit peak power handling near 30Ω and minimum attenuation near 77Ω. 50Ω was born as a sweet-spot compromise (geometric mean √30×77 ≈ 48Ω), becoming the RF standard.
        </div>
        <div style="background-color: #FFFFF0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🏗️ Microstrip Revolution (1950s)</b><br>
        Invented by ITT labs, making PCB-based microwave circuits a reality instead of bulky waveguides. Hammerstad and Jensen's 1980 formulations remain the bedrock of industry solvers.
        </div>
        <div style="background-color: #F0FFF0; padding: 10px; border-radius: 6px; margin: 6px 0;">
        <b>🌊 Coplanar Waveguide (1969)</b><br>
        C.P. Wen introduced CPW. Keeping both the signal and ground traces on the same layer greatly simplified MMIC (Monolithic Microwave IC) manufacturing.
        </div>'''
    )
}

for k, (ch, eng) in imp_trans.items():
    zh['impedance'][k] = ch
    en['impedance'][k] = eng

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)

print("Language files updated for impedance tool.")
