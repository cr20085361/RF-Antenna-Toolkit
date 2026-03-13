import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

if 'range' not in zh: zh['range'] = {}
if 'range' not in en: en['range'] = {}

range_trans = {
    'tool_name': ('收发距离计算', 'Link Range Calculator'),
    'tool_desc': ('基于 Friis 方程计算最远通信距离', 'Calculate maximum communication range based on Friis Transmission Equation'),
    
    'group_tx': ('发射端参数 (Tx)', 'Transmitter Parameters (Tx)'),
    'lbl_tx_power': ('发射功率 Pt (dBm):', 'Transmit Power Pt (dBm):'),
    'lbl_tx_gain': ('发射天线增益 Gt (dBi):', 'Tx Antenna Gain Gt (dBi):'),
    
    'group_rx': ('接收端参数 (Rx)', 'Receiver Parameters (Rx)'),
    'lbl_rx_sens': ('接收灵敏度 Pr_min (dBm):', 'Rx Sensitivity Pr_min (dBm):'),
    'lbl_rx_gain': ('接收天线增益 Gr (dBi):', 'Rx Antenna Gain Gr (dBi):'),
    
    'group_env': ('环境与系统参数', 'Environment & System Parameters'),
    'lbl_freq': ('工作频率 f:', 'Operating Frequency f:'),
    'lbl_loss': ('系统/衰落裕量 L (dB):', 'System/Fade Margin L (dB):'),
    
    'btn_calc': ('📏 计算最远通信距离', '📏 Calculate Max Range'),
    
    'title_eval': ('计算结果', 'Calculation Result'),
    'res_main': ('理论最远距离', 'Theoretical Max Range'),
    'title_detail': ('📐 链路分析拆解', '📐 Link Budget Breakdown'),
    'detail_eirp': ('等效全向辐射功率 (EIRP)', 'EIRP (Equivalent Isotropic Radiated Power)'),
    'detail_allow_loss': ('最大允许路径损耗 (MAPL)', 'Max Allowable Path Loss (MAPL)'),
    'detail_fspl': ('自由空间边界 (无裕量距离)', 'Free Space Limit (0 Margin Range)'),
    
    'err_power': ('发射功率必须为有效数字', 'Transmit power must be a valid number'),
    'err_sens': ('接收增敏度必须为有效数字', 'Receiver sensitivity must be a valid number'),
    'err_gain': ('天线增益格式错误', 'Antenna gain format error'),
    'err_freq': ('频率必须为正数', 'Frequency must be a positive number'),
    'err_loss': ('裕量格式错误', 'Margin format error'),
    'err_format': ('输入格式错误', 'Input format error'),
    
    'intuition_content': (
        '''<b>🔗 什么是最远通信距离？</b><br><br>
        想象两个人在旷野中对话：一个人（发射端 Tx）大声喊叫，另一个人（接收端 Rx）竖起耳朵听。能听清的<b>最远距离</b>取决于四个因素：<br><br>
        1. <b>嗓门有多大</b> (Tx 发射功率 Pt)<br>
        2. <b>有没有用扩音喇叭定向喊</b> (Tx 天线增益 Gt)<br>
        3. <b>有没有用助听器定向听</b> (Rx 天线增益 Gr)<br>
        4. <b>耳朵有多灵敏</b> (Rx 接收灵敏度 Pr_min)<br><br>
        <b>Friis 传输方程</b>就是用来精确计算以上四个条件在电磁波世界中的数学关系！它告诉你：在电磁波扩散衰减到接收机"听不见"之前，信号到底能飞多远。''',
        
        '''<b>🔗 What is the Maximum Communication Range?</b><br><br>
        Imagine two people talking across a vast field: one person (Transmitter Tx) shouts, and the other (Receiver Rx) listens. The <b>maximum distance</b> they can clearly communicate depends on four things:<br><br>
        1. <b>How loudly they shout</b> (Tx Power Pt)<br>
        2. <b>If they use a megaphone to aim their voice</b> (Tx Antenna Gain Gt)<br>
        3. <b>If the listener uses a hearing trumpet to focus sound</b> (Rx Antenna Gain Gr)<br>
        4. <b>How good the listener's hearing is</b> (Rx Sensitivity Pr_min)<br><br>
        The <b>Friis Transmission Equation</b> describes exactly these four factors mapping into the electromagnetic world. It calculates how far the signal can fly before it disperses so much that the receiver can no longer "hear" it.'''
    ),
    'math_content': (
        '''<b>📐 Friis 传输方程 (dB 形式)</b><br><br>
        最远通信距离的核心是计算<b>最大允许路径损耗 (MAPL)</b>。<br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ 链路预算平衡方程</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        P<sub>r</sub> = P<sub>t</sub> + G<sub>t</sub> + G<sub>r</sub> - L<sub>fspl</sub> - L<sub>sys</sub>
        </span><br>
        当接收功率 P<sub>r</sub> 正好等于接收机的底限灵敏度时，距离达到最大。
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>2️⃣ 自由空间路径损耗 (FSPL) 倒推距离</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        FSPL(dB) = 32.44 + 20×log₁₀(d) + 20×log₁₀(f)
        </span><br>
        其中：d 是距离(km)，f 是频率(MHz)。<br><br>
        将方程倒过来求解距离 d：<br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px; font-weight: bold; color: #047857;">
        d = 10 ^ [ (MAPL - 32.44 - 20×log₁₀(f)) / 20 ]
        </span>
        </div>''',
        
        '''<b>📐 Friis Transmission Equation (in dB)</b><br><br>
        The core of max range calculation is finding the <b>Maximum Allowable Path Loss (MAPL)</b>.<br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>1️⃣ Link Budget Balance Equation</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        P<sub>r</sub> = P<sub>t</sub> + G<sub>t</sub> + G<sub>r</sub> - L<sub>fspl</sub> - L<sub>sys</sub>
        </span><br>
        The distance is maximized when the received power P<sub>r</sub> equals exactly the receiver's absolute baseline sensitivity.
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>2️⃣ Back-calculating Distance from FSPL</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        FSPL(dB) = 32.44 + 20×log₁₀(d) + 20×log₁₀(f)
        </span><br>
        Where d is distance in km, and f is frequency in MHz.<br><br>
        Solving for distance d:<br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px; font-weight: bold; color: #047857;">
        d = 10 ^ [ (MAPL - 32.44 - 20×log₁₀(f)) / 20 ]
        </span>
        </div>'''
    ),
    'engineering_content': (
        '''<b>⚠️ 系统衰落裕量 (Fade Margin) 避坑</b><br><br>
        只用纯 Friis 方程算出的距离我们叫"实验室距离"，在真实世界中根本达不到！<br>
        因为真实世界的空气不是纯净的真空，会下雨、有雾气，信号会被树木吸收、被建筑反射抵消。<br><br>
        <table style="margin: 8px 0;">
        <tr><th>应用场景</th><th>推荐保留的衰落裕量 (L)</th></tr>
        <tr><td>视距无遮挡空对空 (无人机)</td><td>10 ~ 15 dB</td></tr>
        <tr><td>开阔郊野/农村</td><td>15 ~ 20 dB</td></tr>
        <tr><td>城市微蜂窝/密集建筑</td><td>25 ~ 35 dB (甚至不用Friis)</td></tr>
        <tr><td>下雨/高教频段 (>10GHz)</td><td>需额外增加降雨衰耗裕量</td></tr>
        </table><br>
        <b>工程经验：</b>如果要扩大通信距离，提升 Rx 端天线增益 (Gr) 是最划算的，因为它不像加大 Pt 那样耗电和发热。''',
        
        '''<b>⚠️ System Fade Margin Pitfalls</b><br><br>
        The distance calculated using *only* the Friis equation without margin is called "lab distance"—you will never achieve it in the real world!<br>
        The real world has rain, fog, foliage absorption, and buildings that cause multi-path cancellation.<br><br>
        <table style="margin: 8px 0;">
        <tr><th>Scenario</th><th>Recommended Fade Margin (L)</th></tr>
        <tr><td>LOS Air-to-Air (UAVs)</td><td>10 ~ 15 dB</td></tr>
        <tr><td>Open Rural/Suburban</td><td>15 ~ 20 dB</td></tr>
        <tr><td>Dense Urban/Indoors</td><td>25 ~ 35 dB (Friis often invalid here)</td></tr>
        <tr><td>Rain / High Freq (>10GHz)</td><td>Require extra Rain Attenuation Margin</td></tr>
        </table><br>
        <b>Pro Tip:</b> If you want to extend communication range, increasing the Rx Antenna Gain (Gr) is often the most cost-effective method since it doesn't radically increase power consumption or heat like boosting Pt does.'''
    ),
    'history_content': (
        '''<b>📜 Friis 与他的传奇方程</b><br><br>
        <b>1946年</b>，贝尔实验室的丹麦裔美国工程师 <b>Harald T. Friis</b> 发表了一篇仅有很短几页的论文《A Note on a Simple Transmission Formula》。<br><br>
        在这之前，工程师们计算无线电收发都需要用到极其复杂、充斥着微积分和场强积分的电磁学方程。Friis 的终极贡献在于：他天才般地引入了<b>"有效接收面积" (Effective Area)</b> 的概念，将复杂的电磁场推导，极简压缩成了我们今天看到的代数加减法（dB形式）！<br><br>
        这篇论文从根本上改变了射频工程师的工作方式，使得不用精通麦克斯韦方程组的普通系统工程师也能快速进行射频链路设计。直到 80 多年后的今天，星链 (Starlink)、5G、深空探测，依然每天在无数次地借用这套极简理论。''',
        
        '''<b>📜 Friis and His Legendary Equation</b><br><br>
        In <b>1946</b>, a Danish-American engineer at Bell Labs, <b>Harald T. Friis</b>, published a remarkably short paper titled "A Note on a Simple Transmission Formula".<br><br>
        Before this, engineers had to use overwhelmingly complex electromagnetic field equations filled with integrals and vector calculus to design a radio link. Friis's ultimate genius was introducing the concept of <b>"Effective Area"</b>. By doing so, he condensed daunting field theory into the simple algebraic additions (in dB) that we use today!<br><br>
        This paper fundamentally revolutionized RF engineering. It enabled system engineers to rapidly design radio links without needing a Ph.D. in Maxwell's equations. Over 80 years later, from 5G to Starlink and deep space probes, Friis's simple formula is still being invoked countless times every single day.'''
    )
}

for k, (ch, eng) in range_trans.items():
    zh['range'][k] = ch
    en['range'][k] = eng

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)

print("Language files updated for range tool.")
