import json
import os

def mega_recovery():
    zh_path = r"e:\AI_Project\RF-Antenna-Toolkit\assets\locales\zh_CN.json"
    en_path = r"e:\AI_Project\RF-Antenna-Toolkit\assets\locales\en_US.json"
    
    # 读取原始数据
    try:
        with open(zh_path, 'r', encoding='utf-8') as f: zh_data = json.load(f)
    except: zh_data = {}
    try:
        with open(en_path, 'r', encoding='utf-8') as f: en_data = json.load(f)
    except: en_data = {}

    def cleanup_and_update(mod, zh_updates, en_updates):
        if mod not in zh_data: zh_data[mod] = {}
        if mod not in en_data: en_data[mod] = {}
        
        # 清除旧的简易 Key (防止匹配错误)
        for old_key in ["intuition", "math_model", "eng_content", "history_content"]:
            if old_key in zh_data[mod]: del zh_data[mod][old_key]
            if old_key in en_data[mod]: del en_data[mod][old_key]
            
        zh_data[mod].update(zh_updates)
        en_data[mod].update(en_updates)

    # 1. VSWR 模块
    cleanup_and_update("vswr", {
        "intuition_content": "<b>📡 什么是驻波比 (VSWR)?</b><br><br>想象一根系在墙上的绳子，如果你快速抖动，入射波与墙面反射回来的波会叠加。当两股波相位一致时形成波腹（最高点），相位相反时形成波节（最低点）。<b>驻波比</b>就是这两者电压幅值的比值。<br><br>• <b>1.0 (完美)</b>: 能量全部传输，没有反射。<br>• <b>1.5 (优秀)</b>: 只有 4% 的功率被反射，是大多数工程标准的门限。<br>• <b>2.0 (合格)</b>: 约 11% 的功率反射。功率进一步增大时，反射能量可能烧毁发射机。",
        "math_content": "<b>📐 数学换算模型</b><br><br><b>反射系数 (Γ):</b><br>|Γ| = (VSWR - 1) / (VSWR + 1)<br><br><b>回波损耗 (RL):</b><br>RL = -20 · log₀|Γ| (dB)<br><br><b>反射功率占比:</b><br>P_refl / P_fwd = |Γ|²<br><br><b>失配损耗 (ML):</b><br>ML = -10 · log₀(1 - |Γ|²) (dB)",
        "engineering_content": "<b>⚙️ 工程避坑指南</b><br>1. <b>测量位置</b>: 驻波随电缆长度变化会因为损耗看起来“变好”，所以最真实的驻波应该在天线接口处测量。<br>2. <b>高功率预警</b>: 在高功率系统中（如 100W 以上），即使 VSWR 为 2.0，反射的 11W 能量也足以让接头剧烈发热甚至融化。<br>3. <b>改善技巧</b>: 在源端接入一个 3dB 衰减器，可以强制将回波损耗改善 6dB（牺牲了功率但保护了源）。",
        "history_content": "<b>📜 发现历史</b><br>1887年，<b>海因里希·赫兹</b>在证明电磁波存在的著名实验中，通过在实验室墙壁上覆盖锌板反射电磁波，成功观测到了空间中的波腹与波节。这是人类第一次观测到无线电驻波，并借此测量出了电磁波的波长。"
    }, {
        "intuition_content": "<b>📡 What is VSWR?</b><br><br>Imagine a wave on a rope tied to a wall. Incident and reflected waves interfere to form a 'Standing Wave'. VSWR is the ratio of Voltage Max to Voltage Min.<br><br>• <b>1.0</b>: Perfect match. No reflection.<br>• <b>1.5</b>: Standard for most RF systems (4% power reflected).<br>• <b>2.0</b>: Lower limit of acceptability (11% reflected).",
        "math_content": "<b>📐 Math Models</b><br>|Γ| = (VSWR - 1) / (VSWR + 1)<br>RL = -20 · log₀|Γ|<br>Mismatch Loss = -10 · log₀(1 - |Γ|²)",
        "engineering_content": "<b>⚙️ Engineering Tips</b><br>Measure at the antenna port for true performance. High VSWR in high-power systems causes severe connector heating due to reflected energy.",
        "history_content": "<b>📜 History</b><br>Observed by <b>Heinrich Hertz</b> in 1887. By reflecting radio waves off zinc sheets, he mapped nodes and antinodes, proving the wave nature of light."
    })

    # 2. Range 模块 (核心恢复)
    cleanup_and_update("range", {
        "intuition_content": "<b>🔗 直观理解：电磁波的空间扩散</b><br><br>想象你在平静的湖面投入一颗石子，水波会一圈一圈向外扩散。电磁波在自由空间的传播与此类似，它像一个不断膨胀的理想球体。<br><br>随着距离 <i>d</i> 的增加，这个球体的表面积以 <i>O(d²)</i> 的速度急剧增大，因此分布在单位面积上的能量（功率密度）就会以平方反比规律迅速衰减。这解释了为什么我们增加 6 dB 的发射功率，最远通信距离仅仅只能增加一倍。",
        "math_content": "<b>📐 数学模型：Friis 传输方程</b><br><br>Friis 传输方程是射频链路计算的基石。对数形式（工程常用）：<br><br><b>P_r(dBm) = Pt(dBm) + Gt(dBi) + Gr(dBi) - FSPL(dB)</b><br><br>其中自由空间路损 FSPL = 20·log₁₀(d) + 20·log₁₀(f) + 32.44 (假设 d 为 km, f 为 MHz)。<br>当接收功率 P_r 正好逼近底噪 + 解调信噪比 + 衰落余量的统合极限阈值时，反解出的 d 即为理论最大距离。",
        "engineering_content": "<b>⚙️ 工程边界：理论与现实</b><br><br>1. <b>地球曲率</b>: 直线传播受地球阻挡。实际视距受天线架设高度制约。<br>2. <b>多径干涉</b>: 地面反射波与直达波抵消，产生深度衰落。<br>3. <b>大气余量</b>: 建议设置 10~20dB 的空间衰落余量 (Fade Margin) 以应对雨雪大气的不确定因素。",
        "history_content": "<b>📜 发现历史</b><br>1946 年，贝尔实验室的 <b>Harald T. Friis</b> 发表了《A Note on a Simple Transmission Formula》。他引入了“有效接收面积”的概念，把复杂的 Maxwell 方程组化繁为简，奠定了现代无线电链路预算的基础。"
    }, {
        "intuition_content": "<b>🔗 Visualizing Wave Diffusion</b><br><br>Think of ripples on a pond. EM waves expand as a sphere. As the sphere's area grows with O(d²), power density decays by the inverse-square law.",
        "math_content": "<b>📐 Friis Equation</b><br><br>P_r = Pt + Gt + Gr - FSPL<br>FSPL = 20·log₁₀(d) + 20·log₁₀(f) + 32.44",
        "engineering_content": "<b>⚙️ Reality vs Theory</b><br>Always include 10-20dB Fade Margin for real-world environmental stability.",
        "history_content": "<b>📜 History</b><br>Founded by Harald T. Friis in 1946 at Bell Labs, transforming field theory into manageable dB link budgets."
    })

    # 3. Gain 模块 (Antenna Gain)
    cleanup_and_update("gain", {
        "intuition_content": "<b>📡 什么是天线增益?</b><br><br>天线并不像放大器那样增加总能量。它更像一个手电筒反光罩，把散射向四面八方的光线集中到一个方向上。增益值越大，意味着能量集中的波束越“细长”，照射得越远。",
        "math_content": "<b>📐 计算方法</b><br><br>1. <b>波束宽度法</b>: G ≈ 41253 / (θ_E · θ_H)<br>2. <b>有效面积法</b>: G = 4π · η · A / λ²<br>其中 η 为效率，A 为物理面积。",
        "engineering_content": "<b>⚙️ 工程建议</b><br>高增益天线虽然距离远，但波束极窄，对准困难。在移动端应用中，通常追求中低增益以换取更宽的连接角度。",
        "history_content": "<b>📜 发现历史</b><br>波束定向的概念可以追溯到 1926 年日本工程师<b>八木秀次</b>发明的八木天线。这是人类第一次大规模使用寄生单元提升天线增益并实现波束指向性。"
    }, {
        "intuition_content": "<b>📡 What is Gain?</b><br>Antennas don't create power; they focus it like a lens. Higher gain means a narrower, more focused beam.",
        "math_content": "<b>📐 Models</b><br>Effective Aperture: G = (4πA/λ²) * Efficiency",
        "engineering_content": "<b>⚙️ Tips</b><br>High-gain antennas require precise alignment. Low-gain antennas provide better omnidirectional coverage.",
        "history_content": "<b>📜 History</b><br>The iconic Yagi-Uda antenna (1926) was a pioneer in passive gain enhancement."
    })

    # 4. Attenuator 模块
    cleanup_and_update("attenuator", {
        "intuition_content": "<b>💡 衰减器的物理本质</b><br><br>衰减器是一个精确的耗能网络。它的任务是：1. 按照预定比例降低能量；2. 保证阻抗匹配，让源端察觉不到链路中间的变化。它通常由纯电阻网络组成，将多余的电磁能转化为热能。",
        "math_content": "<b>📐 T/Pi 网络公式</b><br><br>设 A 为功率衰减比 (Linear)，Z₀ 为阻抗：<br>T型串联电阻 R1 = Z₀ · (A-1)/(A+1)<br>Pi型并联电阻 R2 = Z₀ · (A+1)/(A-1)",
        "engineering_content": "<b>⚙️ 工程避坑</b><br>1. <b>功率容量</b>: 衰减掉的能量变成了热，大功率时必须确保电阻封装能散热。<br>2. <b>频率特性</b>: 普通电阻在高频下有寄生电感，微波频段需专用薄膜衰减芯片。",
        "history_content": "<b>📜 简史</b><br>为了平衡长距离电话线的信号强度，贝尔系统在 20 世纪初标准化了电阻衰减方案，奠定了后来分贝 (dB) 单位的基础。"
    }, {
        "intuition_content": "<b>💡 Nature of Attenuators</b><br>Attenuators reduce power by converting EM energy into heat while maintaining port impedance matching.",
        "math_content": "<b>📐 Topology</b><br>T and Pi networks are standard for resistive loss implementation.",
        "engineering_content": "<b>⚙️ Warning</b><br>Check power dissipation ratings. Standard resistors fail at high microwave frequencies due to parasitics.",
        "history_content": "<b>📜 History</b><br>Created to balance signal levels across emerging telephone networks in the early 1900s."
    })

    # 5. Bandwidth 模块
    cleanup_and_update("bandwidth", {
        "intuition_content": "<b>📶 带宽的意义</b><br><br>带宽就像是一条公路的宽度。天线的“路”越宽，能同时跑的高速数据流就越多。通常指天线能维持稳定性能（驻波 < 2.0）的最高频率与最低频率之差。",
        "math_content": "<b>📐 百分比带宽 (FBW)</b><br><br>FBW = (f_high - f_low) / f_center × 100%<br>对于窄带天线，FBW 通常小于 5%；而超宽带 (UWB) 天线可超过 100%。",
        "engineering_content": "<b>⚙️ 性能权衡</b><br>存在物理上的增益带宽积限制：在同样的体积下，想要更宽的带宽，通常会牺牲增益或稳定性（Q值理论极限）。",
        "history_content": "<b>📜 演进</b><br>2002 年 FCC 开放了 3.1-10.6GHz UWB 频段，开启了民用超宽带通信的商业化之路。"
    }, {
        "intuition_content": "<b>📶 Bandwidth Context</b><br>Like road width, more bandwidth enables higher data rates. Defined by the freq range where VSWR < 2.0.",
        "math_content": "<b>📐 Fractional BW</b><br>FBW = (f_H - f_L) / f_C",
        "engineering_content": "<b>⚙️ Trade-offs</b><br>Quality factor (Q) dictates the theoretical limit on gain-bandwidth product.",
        "history_content": "<b>📜 History</b><br>UWB frequency opening in 2002 revolutionized short-range high-speed data transfer."
    })

    # 级联驻波补全
    cleanup_and_update("cascade", {
        "intuition_content": "<b>🔗 级联驻波的叠加效应</b><br><br>多模块串联时，总驻波取决于各级相位。同相叠加时驻波最差，反相抵消时最好。级联计算帮助评估系统的“底线”性能。",
        "math_content": "<b>📐 计算路径</b><br>反射系数模值相加 |Γ_max| = |Γ₁| + |Γ₂|，再换算回 VSWR = (1+|Γ|)/(1-|Γ|)。",
        "engineering_content": "<b>⚙️ 工程对策</b><br>如果系统级联驻波超标，可尝试通过更换转接电缆长度（改变相位）或加入隔离器来改善。",
        "history_content": "<b>📜 背景</b><br>级联失配误差是微波计量的基础，在 20 世纪中期随着 HP (安捷伦) 网络分析仪的发展而成熟。"
    }, {
        "intuition_content": "<b>🔗 Cascade Effect</b><br>Total VSWR depends on phase interference between stages. We calculate the worst-case boundary.",
        "math_content": "<b>📐 Formulas</b><br>|Γ_total| = Σ|Γ_i| for the worst case.",
        "engineering_content": "<b>⚙️ Solutions</b><br>Adjust phase by changing cable length or use isolators to break standing wave ripples.",
        "history_content": "<b>📜 Context</b><br>Essential for VNA error modeling and link budget integrity."
    })

    # 保存文件
    with open(zh_path, 'w', encoding='utf-8') as f:
        json.dump(zh_data, f, ensure_ascii=False, indent=4)
    with open(en_path, 'w', encoding='utf-8') as f:
        json.dump(en_data, f, ensure_ascii=False, indent=4)
    
    print("SUCCESS: Mega Recovery v3.0 Complete. Source Keys aligned and Pro contents injected.")

if __name__ == "__main__":
    mega_recovery()
