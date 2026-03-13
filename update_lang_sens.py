import json

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

if 'sens' not in zh: zh['sens'] = {}
if 'sens' not in en: en['sens'] = {}

sens_trans = {
    'tool_name': ('系统灵敏度计算', 'System Sensitivity Calculator'),
    'tool_desc': ('无线通信接收机链路灵敏度与噪声系数评估', 'Evaluate Rx Link Sensitivity and Noise Figure'),
    
    'group_sys': ('系统参数 (System Settings)', 'System Parameters'),
    'lbl_bw': ('信号带宽 BW (MHz):', 'Signal Bandwidth BW (MHz):'),
    'lbl_snr': ('解调要求信噪比 SNR (dB):', 'Required Demodulation SNR (dB):'),
    
    'group_rf': ('射频前端参数 (RF Front-End)', 'RF Front-End Specs'),
    'lbl_nf': ('接收机噪声系数 NF (dB):', 'Receiver Noise Figure NF (dB):'),
    'lbl_loss': ('馈线/插损 L (dB):', 'Cable/Insertion Loss L (dB):'),
    
    'btn_calc': ('📶 计算灵敏度', '📶 Calculate Sensitivity'),
    
    'title_eval': ('计算结果', 'Calculation Result'),
    'res_main': ('系统灵敏度 (Sensitivity)', 'System Sensitivity'),
    'title_detail': ('📐 噪声链路拆解', '📐 Noise Link Breakdown'),
    
    'detail_floor': ('热噪声基底 (Thermal Noise Floor)', 'Thermal Noise Floor'),
    'detail_total_nf': ('级联总噪声系数 (Total NF)', 'Total Cascaded NF'),
    'detail_snr': ('要求信噪比 (Required SNR)', 'Required SNR'),
    
    'err_bw': ('带宽必须为大于0的有效数字', 'Bandwidth must be a positive valid number'),
    'err_snr': ('SNR格式错误', 'SNR format error'),
    'err_nf': ('噪声系数必须大于等于0', 'Noise figure must be ≥ 0'),
    'err_loss': ('插损必须大于等于0', 'Insertion loss must be ≥ 0'),
    'err_inp': ('输入格式错误', 'Input format error'),
    
    'intuition_content': (
        '''<b>📶 什么是接收机灵敏度？</b><br><br>
        想象你在一个嘈杂的派对（<b>热噪声底</b>）上。有人从很远的地方（信号衰减）跟你说话。<br>
        你要能听清他说什么，必须要满足三个条件：<br><br>
        1. <b>房间有多吵</b> (带宽越宽，进来的底噪越多)<br>
        2. <b>你的耳朵是否有点背</b> (接收机自身的噪声系数 NF，也就是机器内部产生的额外噪声)<br>
        3. <b>你要听懂这句话，要求对方的声音必须比环境音高出多少</b> (解调门限 SNR。比如调幅广播需要比较高的SNR，而扩频通信甚至能在噪声以下听懂)。<br><br>
        <b>总灵敏度 (Sensitivity)</b> 就是：为了让你最终在这个系统里能准确"听懂"，对方发出的到达你耳边的<b>最小可接受信号功率</b>。''',
        
        '''<b>📶 What is Receiver Sensitivity?</b><br><br>
        Imagine you are at a very noisy party (<b>Thermal Noise Floor</b>). Someone is talking to you from far away (Signal Attenuation).<br>
        To understand what they are saying, three crucial conditions must be met:<br><br>
        1. <b>How noisy the room is</b> (The wider the bandwidth, the more noise hits your ear).<br>
        2. <b>How good your hearing is</b> (Receiver Noise Figure NF—how much extra noise your own "ear" or circuitry adds).<br>
        3. <b>How loud their voice needs to be *above* the background noise for you to comprehend the words</b> (Required Demodulation SNR).<br><br>
        <b>System Sensitivity</b> is the <b>absolute minimum signal power</b> that must reach your antenna so that, after battling all this noise, the final demodulator can still "understand" the message.'''
    ),
    'math_content': (
        '''<b>📐 灵敏度经典计算公式</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>总灵敏度 P_min (dBm) 公式：</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        P_min = -174 + 10×log₁₀(BW) + NF + SNR_min
        </span><br><br>
        <b>各项物理意义：</b><br>
        • <b>-174 dBm/Hz</b>: 常温(290K)下 1Hz 带宽的理想热噪声底。<br>
        • <b>10×log₁₀(BW)</b>: 带宽造成的噪声增加量 (BW的单位是Hz)。<br>
        • <b>NF</b>: 接收机的噪声系数 (射频前端自身的不完美)。<br>
        • <b>SNR_min</b>: 基带芯片要成功解调所需的最差信噪比。
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>📡 前端插损的影响</b><br>
        注意：天线到第一级 LNA (低噪声放大器) 之间的线缆插入损耗 L，会一比一地恶化系统的总噪声系数（即 <b>NF_total = NF_LNA + L</b>）。<br>
        因此，接收天线到 LNA 的射频线必须<b>越短越好</b>！
        </div>''',
        
        '''<b>📐 Classic Sensitivity Equation</b><br><br>
        <div style="background-color: #EBF5FF; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>Total Sensitivity P_min (dBm):</b><br>
        <span style="font-family: 'Cambria Math', serif; font-size: 14px;">
        P_min = -174 + 10×log₁₀(BW) + NF + SNR_min
        </span><br><br>
        <b>Breakdown:</b><br>
        • <b>-174 dBm/Hz</b>: Thermal noise floor for 1 Hz of bandwidth at room temp (290K).<br>
        • <b>10×log₁₀(BW)</b>: Noise integrated across the full channel bandwidth (BW in Hz).<br>
        • <b>NF</b>: Receiver Noise Figure (the imperfection/extra noise added by the RF front-end).<br>
        • <b>SNR_min</b>: Minimum Signal-to-Noise Ratio required by the baseband chip/demodulator.
        </div>
        <div style="background-color: #F0FDF4; padding: 10px; border-radius: 6px; margin: 8px 0;">
        <b>📡 The Impact of Front-End Loss</b><br>
        Cable/insertion loss (L) *before* the first Low Noise Amplifier (LNA) adds directly to the total Noise Figure dB for dB. (e.g., <b>NF_total = NF_LNA + L</b>).<br>
        Therefore, the RF cable between the antenna and the first LNA must be <b>as short as absolutely possible</b>!
        </div>'''
    ),
    'engineering_content': (
        '''<b>🎛️ 不同通信体制的 SNR 要求参考：</b><br>
        <table style="margin: 8px 0;">
        <tr><th>解调方式 / 系统</th><th>典型要求 SNR (dB)</th></tr>
        <tr><td>LoRa / GPS (扩频增益)</td><td>-15 ~ -25 dB (可以在噪声下!)</td></tr>
        <tr><td>BPSK / QPSK (稳健数字)</td><td>3 ~ 10 dB</td></tr>
        <tr><td>16-QAM (高速数据)</td><td>15 ~ 20 dB</td></tr>
        <tr><td>256-QAM (如Wi-Fi 6)</td><td>30 ~ 35 dB (需要极高信号)</td></tr>
        <tr><td>模拟对讲机 (FM)</td><td>约 12 dB (SINAD门限)</td></tr>
        </table><br>
        <b>⚠️ 提升灵敏度的陷阱：</b><br>
        很多工程师试图拼命降低 LNA 的 NF (比如从 1.5dB 降到 0.8dB，花掉大量成本)，来提升灵敏度。<br>
        其实如果系统外部环境噪声本来就大，这点 NF 的提升完全被淹没。有时候去<b>缩减系统带宽</b>，或者选用<b>更先进的低SNR基带算法</b>，收益要远大得多。''',
        
        '''<b>🎛️ Typical SNR Requirements by Protocol:</b><br>
        <table style="margin: 8px 0;">
        <tr><th>Modulation / System</th><th>Typical Required SNR (dB)</th></tr>
        <tr><td>LoRa / GPS (Spread Spec)</td><td>-15 to -25 dB (Works under the noise!)</td></tr>
        <tr><td>BPSK / QPSK (Robust Data)</td><td>3 ~ 10 dB</td></tr>
        <tr><td>16-QAM (Fast Data)</td><td>15 ~ 20 dB</td></tr>
        <tr><td>256-QAM (e.g. Wi-Fi 6)</td><td>30 ~ 35 dB (Requires massive signal)</td></tr>
        <tr><td>Analog FM Radio</td><td>~ 12 dB (SINAD threshold)</td></tr>
        </table><br>
        <b>⚠️ Sensitivity Improvement Pitfall:</b><br>
        Engineers often burn immense budgets trying to shave the LNA's NF down (e.g., from 1.5dB to 0.8dB).<br>
        However, if the external environmental noise is already huge, this NF improvement is completely washed out. Often, <b>reducing system bandwidth</b> or selecting a <b>better baseband algorithm</b> with lower SNR demands yields much more drastic improvements.'''
    )
}

for k, (ch, eng) in sens_trans.items():
    zh['sens'][k] = ch
    en['sens'][k] = eng

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)

print("Language files updated for sensitivity tool.")
