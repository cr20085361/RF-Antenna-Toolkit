import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

if 'wavelength' not in zh: zh['wavelength'] = {}
if 'wavelength' not in en: en['wavelength'] = {}
if 'los' not in zh: zh['los'] = {}
if 'los' not in en: en['los'] = {}

# Wavelength Tool Translations
wl_trans = {
    'tool_name': ('波长计算器', 'Wavelength Calculator'),
    'tool_desc': ('根据频率计算自由空间波长和介质中波长，支持常用介质材料选择', 'Calculate free space and dielectric wavelength from frequency, supporting common dielectric materials'),
    'group_freq': ('频率输入', 'Frequency Input'),
    'lbl_freq': ('频率:', 'Frequency:'),
    'place_freq': ('请输入频率', 'Enter frequency'),
    'group_medium': ('介质设置', 'Medium Settings'),
    'lbl_material': ('材料:', 'Material:'),
    'custom_material': ('自定义', 'Custom'),
    'lbl_epsilon': ('介电常数 εr:', 'Dielectric Constant εr:'),
    'btn_calc': ('📊 计算', '📊 Calculate'),
    'card_free_space': ('自由空间波长 λ₀', 'Free Space Wavelength λ₀'),
    'desc_free_space': ('在真空/空气中的电磁波波长', 'Electromagnetic wavelength in vacuum/air'),
    'card_medium': ('介质波长 λ', 'Dielectric Wavelength λ'),
    'desc_medium': ('在所选介质中的有效波长', 'Effective wavelength in selected medium'),
    'card_quarter': ('四分之一波长 λ/4', 'Quarter Wavelength λ/4'),
    'desc_quarter': ('常用于阻抗匹配段长度', 'Often used for impedance matching sections'),
    'card_half': ('二分之一波长 λ/2', 'Half Wavelength λ/2'),
    'desc_half': ('常用于偶极子天线长度', 'Often used for dipole antenna length'),
    'lbl_error': ('错误', 'Error'),
    
    'intuition_content': (
        '''<b>🌊 什么是电磁波波长？</b><br><br>
        想象往平静的湖面扔一块石头，水波会向外扩散。<b>波长</b>就是<b>相邻两个波峰之间的距离</b>。<br><br>
        电磁波也一样：当电场和磁场以光速振荡传播时，波长就是振荡一个完整周期后电磁波传播的距离。<br><br>
        <b>🔑 关键物理本质：</b><br>
        • 频率越高 → 振荡越快 → 波长越短<br>
        • 介质中光速变慢 → 同样频率下波长变短<br>
        • 波长决定了天线的物理尺寸（天线长度通常是波长的分数）''',
        
        '''<b>🌊 What is Electromagnetic Wavelength?</b><br><br>
        Imagine throwing a stone into a calm lake; ripples spread outward. The <b>wavelength</b> is the <b>distance between two adjacent crests</b>.<br><br>
        The same applies to electromagnetic waves: as electric and magnetic fields oscillate and propagate at the speed of light, wavelength is the distance the wave travels during one complete oscillation cycle.<br><br>
        <b>🔑 Key Physical Intuition:</b><br>
        • Higher frequency → faster oscillation → shorter wavelength<br>
        • Speed of light slows down in a dielectric medium → shorter wavelength for the same frequency<br>
        • Wavelength determines antenna physical size (antenna lengths are typically fractions of a wavelength)'''
    ),
    'math_content': (
        '''<b>📐 基本公式</b><br><br>
        <b>自由空间波长：</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 16px;">
        λ₀ = c / f
        </span><br>
        其中：c = 299,792,458 m/s（真空光速），f = 频率 (Hz)<br><br>
        <b>介质中波长：</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 16px;">
        λ = λ₀ / √εᵣ = c / (f · √εᵣ)
        </span><br>
        其中：εᵣ = 介质相对介电常数<br><br>
        <b>📊 常用分数波长：</b><br>
        • λ/4 = 四分之一波长（阻抗变换、匹配网络）<br>
        • λ/2 = 二分之一波长（偶极子天线、谐振结构）''',
        
        '''<b>📐 Basic Formulas</b><br><br>
        <b>Free Space Wavelength:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 16px;">
        λ₀ = c / f
        </span><br>
        where: c = 299,792,458 m/s (speed of light in vacuum), f = frequency (Hz)<br><br>
        <b>Wavelength in Dielectric Medium:</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 16px;">
        λ = λ₀ / √εᵣ = c / (f · √εᵣ)
        </span><br>
        where: εᵣ = relative permittivity (dielectric constant) of the medium<br><br>
        <b>📊 Common Fractional Wavelengths:</b><br>
        • λ/4 = Quarter wavelength (impedance transformers, matching networks)<br>
        • λ/2 = Half wavelength (dipole antennas, resonant structures)'''
    ),
    'engineering_content': (
        '''<b>✅ 适用范围：</b><br>
        • 远场区电磁波分析（距离 > 2D²/λ）<br>
        • 均匀介质中的传播计算<br>
        • 平面波假设成立的场景<br><br>
        <b>⚠️ 常见错误（避坑指南）：</b><br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 错误1：忽略介质色散
        </span><br>
        高频时εᵣ会随频率变化，不能用静态值<br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 错误2：混淆自由空间波长和介质波长
        </span><br>
        PCB微带线设计必须用介质波长！<br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ 错误3：忽略有效介电常数
        </span><br>
        微带线的有效εᵣ ≠ 基板εᵣ，需用经验公式修正<br><br>
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px; color: #276749;">
        💡 建议：实际设计时预留5-10%调试余量
        </span>''',
        
        '''<b>✅ Scope of Application:</b><br>
        • Far-field electromagnetic wave analysis (distance > 2D²/λ)<br>
        • Propagation calculation in homogeneous media<br>
        • Scenarios where plane wave assumptions hold<br><br>
        <b>⚠️ Common Mistakes (Pitfalls):</b><br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ Mistake 1: Ignoring Dielectric Dispersion
        </span><br>
        At high frequencies, εᵣ changes with frequency; static values shouldn't be used blindly.<br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ Mistake 2: Confusing Free Space & Dielectric Wavelength
        </span><br>
        PCB microstrip designs must use the dielectric wavelength!<br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px; color: #C53030;">
        ❌ Mistake 3: Ignoring Effective Dielectric Constant
        </span><br>
        A microstrip's effective εᵣ is NOT the substrate εᵣ; empirical formula corrections are needed.<br><br>
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px; color: #276749;">
        💡 Recommendation: Leave a 5-10% tuning margin during practical design
        </span>'''
    ),
    'history_content': (
        '''<b>📜 电磁波的发现之旅</b><br><br>
        <b>1865年</b> - 詹姆斯·克拉克·<b>麦克斯韦</b>通过数学推导预言：电磁波以光速传播，光也是电磁波的一种。<br><br>
        <b>1887年</b> - 海因里希·<b>赫兹</b>首次用实验证实了电磁波的存在，成功产生并检测到了无线电波。为纪念他，频率单位被命名为"赫兹(Hz)"。<br><br>
        <i>💭 有趣的是，赫兹当时认为这个发现"没有任何实际用途"。仅仅几年后，马可尼就用它实现了跨大西洋无线通信！</i>''',
        
        '''<b>📜 The Discovery of Electromagnetic Waves</b><br><br>
        <b>1865</b> - James Clerk <b>Maxwell</b> theoretically predicted through mathematical derivation that electromagnetic waves travel at the speed of light, and that light itself is a form of electromagnetic wave.<br><br>
        <b>1887</b> - Heinrich <b>Hertz</b> confirmed the existence of electromagnetic waves experimentally for the first time, successfully generating and detecting radio waves. The unit of frequency is named "Hertz (Hz)" in his honor.<br><br>
        <i>💭 Fun fact: Hertz originally believed his discovery was "of no use whatsoever." Just a few years later, Marconi used it to achieve cross-Atlantic wireless communication!</i>'''
    )
}

# LOS Tool Translations
los_trans = {
    'tool_name': ('视距计算', 'Line-of-Sight Calculator'),
    'tool_desc': ('地球曲率视距与仰角计算', 'Earth curvature LOS and elevation angle calculator'),
    'group_mode': ('计算模式', 'Calculation Mode'),
    'radio_horizon': ('地球曲率视距 (天线高度→视距)', 'Radio Horizon (Antenna Height → LOS)'),
    'lbl_h': ('天线高度 h:', 'Antenna Height h:'),
    'place_h': ('高度', 'Height'),
    'radio_ele': ('目标仰角计算 (反无场景)', 'Target Elevation Angle (C-UAS Scenario)'),
    'lbl_d': ('目标距离 d:', 'Target Distance d:'),
    'place_d': ('距离', 'Distance'),
    'lbl_htarget': ('目标高度 h_target:', 'Target Height h_target:'),
    'place_htarget': ('无人机高度', 'UAV height'),
    'lbl_hradar': ('雷达高度 h_radar:', 'Radar Height h_radar:'),
    'place_hradar': ('雷达位置高度', 'Radar placement height'),
    'radio_two': ('双站视距 (两站间通视)', 'Two-Station LOS (Clearance between two stations)'),
    'lbl_h1': ('站点A高度 h₁:', 'Station A Height h₁:'),
    'lbl_h2': ('站点B高度 h₂:', 'Station B Height h₂:'),
    'lbl_atm': ('大气条件:', 'Atmospheric Conditions:'),
    'atm_1': ('标准大气 (k=4/3)', 'Standard Atmosphere (k=4/3)'),
    'atm_2': ('干燥/无折射 (k=1)', 'Dry / No Refraction (k=1)'),
    'atm_3': ('高湿度 (k=1.5)', 'High Humidity (k=1.5)'),
    'atm_4': ('超折射 (k=2)', 'Super Refraction (k=2)'),
    'btn_calc': ('🌍 计算视距', '🌍 Calculate LOS'),
    
    'title_eval': ('评估结果', 'Evaluation Result'),
    'title_main': ('🌍 计算结果', '🌍 Main Results'),
    'lbl_res1': ('主要结果:', 'Primary Result:'),
    'lbl_res2': ('次要结果:', 'Secondary Result:'),
    'title_detail': ('📐 详细参数', '📐 Detailed Parameters'),
    'lbl_param1': ('参数1:', 'Param 1:'),
    'lbl_param2': ('参数2:', 'Param 2:'),
    'lbl_param3': ('参数3:', 'Param 3:'),
    'title_diagram': ('📊 计算模型示意图', '📊 Calculation Model Diagram'),
    'diagram_placeholder': ('示意图暂未加载', 'Diagram not loaded yet'),
    
    'horizon_opt': ('光学视距:', 'Optical LOS:'),
    'horizon_qual': ('📡 无线电视距 (考虑大气折射)', '📡 Radio LOS (considering atmospheric refraction)'),
    'horizon_d1': ('天线高度:', 'Antenna height:'),
    'horizon_d2': ('折射系数: k =', 'Refraction coefficient: k ='),
    'horizon_d3': ('视距增益:', 'LOS Gain:'),
    
    'ele_geom': ('几何仰角:', 'Geometric Elevation:'),
    'ele_d1': ('目标距离:', 'Target distance:'),
    'ele_d2': ('目标高度:', 'Target height:'),
    'ele_d3': ('曲率修正:', 'Curvature correction:'),
    
    'two_geom': ('最大通视距离', 'Maximum clearance distance'),
    'two_qual': ('🔗 两站间理论最大通视距离', '🔗 Theoretical max LOS distance between two stations'),
    'two_d1': ('站点1视距:', 'Station 1 LOS:'),
    'two_d2': ('站点2视距:', 'Station 2 LOS:'),
    'two_d3': ('高度:', 'Heights:'),
    
    'intuition_content': (
        '''<b>🌍 什么是视距？</b><br><br>
        由于地球是圆的，站在地面上无法看到无限远。
        无线电波沿直线传播，超出视距后信号会被地球遮挡。<br><br>
        <b>🎯 反无人机场景:</b><br>
        低空目标（无人机）的仰角很小，需要准确计算以瞄准目标。
        地球曲率会影响仰角，距离越远影响越大。<br><br>
        <b>💡 大气折射:</b><br>
        标准大气条件下，无线电波会略微弯曲，使视距比光学视距远约15%。''',
        
        '''<b>🌍 What is Line of Sight (LOS)?</b><br><br>
        Because the Earth is spherical, you cannot see infinitely far from the ground. Radio waves propagate in straight lines, and signals beyond the visual horizon are blocked by the Earth's curvature.<br><br>
        <b>🎯 Counter-UAS Scenario:</b><br>
        Low-altitude targets (like UAVs) have very small elevation angles, requiring accurate calculations to aim tracking systems. Earth's curvature affects this angle, and the impact grows with distance.<br><br>
        <b>💡 Atmospheric Refraction:</b><br>
        Under standard atmospheric conditions, radio waves bend slightly downward, increasing the radio horizon by about 15% compared to the optical horizon.'''
    ),
    'math_content': (
        '''<b>📐 视距计算公式与推导</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ 无线电视距</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        <b>d = √(2 × R × k × h)</b>
        </span><br>
        • R = 6371 km (地球半径)<br>
        • k = 大气折射系数 (标准: 4/3)<br>
        • h = 天线高度<br><br>
        <span style="color: #555; font-size: 12px;">
        <b>▸ 推导:</b> 由勾股定理 (R+h)² = R² + d²<br>
        展开并忽略h²项得: d² ≈ 2Rh<br>
        考虑大气折射: d = √(2kRh)
        </span>
        </div>
        <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 10px; margin: 8px 0; border-radius: 6px;">
        <b>2️⃣ 仰角计算 (含地球曲率修正)</b><br><br>
        几何仰角: <span style="font-family: serif;">θ<sub>geo</sub> = arctan(Δh / d)</span><br><br>
        <b>⚠️ 地球曲率修正:</b><br>
        在距离 d 处，目标"视觉下沉"量:<br>
        <div style="background-color: #FFFBEB; padding: 4px 8px; border-radius: 4px; margin: 4px 0;">
        <b>Δh<sub>drop</sub> = d² / (2R)</b>
        </div>
        修正角度: <span style="font-family: serif;">θ<sub>corr</sub> = arctan(Δh<sub>drop</sub>/d)</span><br><br>
        <b style="color: #B45309;">最终仰角: θ = θ<sub>geo</sub> + θ<sub>corr</sub></b>
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>3️⃣ 双站视距</b><br>
        <span style="font-family: 'Cambria Math', serif;">
        d<sub>max</sub> = √(2Rkh₁) + √(2Rkh₂)
        </span><br>
        <span style="color: #555; font-size: 12px;">
        两站最大通视距离 = 各站视距之和
        </span>
        </div>''',
        
        '''<b>📐 LOS Formulas and Derivations</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ Radio Horizon</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        <b>d = √(2 × R × k × h)</b>
        </span><br>
        • R = 6371 km (Earth radius)<br>
        • k = Refraction coefficient (standard: 4/3)<br>
        • h = Antenna height<br><br>
        <span style="color: #555; font-size: 12px;">
        <b>▸ Derivation:</b> From Pythagorean theorem (R+h)² = R² + d²<br>
        Expanded and dropping h² yields: d² ≈ 2Rh<br>
        Adding refraction: d = √(2kRh)
        </span>
        </div>
        <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 10px; margin: 8px 0; border-radius: 6px;">
        <b>2️⃣ Elevation Angle (with Curvature Correction)</b><br><br>
        Geometric elevation: <span style="font-family: serif;">θ<sub>geo</sub> = arctan(Δh / d)</span><br><br>
        <b>⚠️ Earth Curvature Correction:</b><br>
        At distance d, the "visual drop" of the target is:<br>
        <div style="background-color: #FFFBEB; padding: 4px 8px; border-radius: 4px; margin: 4px 0;">
        <b>Δh<sub>drop</sub> = d² / (2R)</b>
        </div>
        Correction angle: <span style="font-family: serif;">θ<sub>corr</sub> = arctan(Δh<sub>drop</sub>/d)</span><br><br>
        <b style="color: #B45309;">Final Elevation: θ = θ<sub>geo</sub> + θ<sub>corr</sub></b>
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>3️⃣ Two-Station LOS</b><br>
        <span style="font-family: 'Cambria Math', serif;">
        d<sub>max</sub> = √(2Rkh₁) + √(2Rkh₂)
        </span><br>
        <span style="color: #555; font-size: 12px;">
        Max clearance distance = Sum of individual horizons
        </span>
        </div>'''
    ),
    'engineering_content': (
        '''<b>✅ 典型参数参考:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>10m天线</td><td>→ 视距约 13 km</td></tr>
        <tr><td>100m铁塔</td><td>→ 视距约 41 km</td></tr>
        <tr><td>无人机100m@5km</td><td>→ 仰角约 1.15°</td></tr>
        </table><br>
        <b>⚠️ 注意事项:</b><br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px;">
        ❌ 低仰角问题
        </span><br>
        • 仰角<1° 地杂波干扰严重<br>
        • 多径效应导致信号衰落<br><br>
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px;">
        💡 工程建议
        </span><br>
        • 提高天线架设高度<br>
        • 选择无遮挡的部署位置''',
        
        '''<b>✅ Typical Parameters Reference:</b><br>
        <table style="margin: 8px 0;">
        <tr><td>10m antenna</td><td>→ LOS ≈ 13 km</td></tr>
        <tr><td>100m tower</td><td>→ LOS ≈ 41 km</td></tr>
        <tr><td>UAV 100m@5km</td><td>→ Elevation ≈ 1.15°</td></tr>
        </table><br>
        <b>⚠️ Attention:</b><br><br>
        <span style="background-color: #FED7D7; padding: 4px 8px; border-radius: 4px;">
        ❌ Low Elevation Issues
        </span><br>
        • Elevation < 1° suffers heavy ground clutter<br>
        • Multipath fading leads to signal degradation<br><br>
        <span style="background-color: #C6F6D5; padding: 4px 8px; border-radius: 4px;">
        💡 Engineering Recommendations
        </span><br>
        • Increase antenna mounting height<br>
        • Choose deployment locations with clear paths'''
    ),
    'history_content': (
        '''<b>📜 视距的故事</b><br><br>
        <b>古希腊</b> - 亚里士多德通过观察远航船只"船身先消失，桅杆后消失"证明地球是圆的。<br><br>
        <b>1917年</b> - 马可尼成功实现跨大西洋无线电通信，当时的科学家困惑：无线电波怎么能绕过地球曲率？后来发现是电离层反射帮了忙。<br><br>
        <b>现代</b> - 反无人机系统需要精确计算低仰角探测能力，这正是视距计算的典型应用场景。''',
        
        '''<b>📜 The Story of Line-of-Sight</b><br><br>
        <b>Ancient Greece</b> - Aristotle proved the Earth was spherical by observing ships sailing away: "the hull disappears first, then the mast."<br><br>
        <b>1917</b> - Marconi successfully achieved cross-Atlantic radio communication. Scientists at the time were baffled: how could radio waves bypass the Earth's curvature? It was later discovered that ionospheric refraction made it possible.<br><br>
        <b>Modern Era</b> - Anti-UAS systems require precise calculations of low-elevation detection capabilities, which is a classic application scenario for LOS calculations.'''
    ),
    'err_h1': ('⚠️ 请输入天线高度', '⚠️ Please enter antenna height'),
    'err_h2': ('⚠️ 高度格式错误', '⚠️ Height format error'),
    'err_h3': ('⚠️ 高度不能为负值', '⚠️ Height cannot be negative'),
    'err_d1': ('⚠️ 请输入目标距离', '⚠️ Please enter target distance'),
    'err_d2': ('⚠️ 请输入目标高度', '⚠️ Please enter target height'),
    'err_fmt': ('⚠️ 输入格式错误', '⚠️ Input format error'),
    'err_d_pos': ('⚠️ 目标距离必须为正值', '⚠️ Target distance must be positive'),
    'err_h_pos': ('⚠️ 目标高度不能为负值', '⚠️ Target height cannot be negative'),
    'err_h_2': ('⚠️ 请输入两个站点的高度', '⚠️ Please enter both station heights'),
    'err_calc': ('⚠️ 计算错误: ', '⚠️ Calc error: ')
}

for k, (ch, eng) in wl_trans.items():
    zh['wavelength'][k] = ch
    en['wavelength'][k] = eng

for k, (ch, eng) in los_trans.items():
    zh['los'][k] = ch
    en['los'][k] = eng

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)
print("Language files updated for wavelength and los.")
