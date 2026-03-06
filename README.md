<div align="center">

# 📡 射频天线工具集 (RF Antenna Toolkit)

**一款专为射频与天线工程师打造的桌面端辅助计算与可视化软件。**<br>
基于 Python 和 PyQt6 开发，旨在集成本专业常用的繁杂计算公式与工程查表，提供直观、高效、现代化的科学计算体验。

</div >

---

## ✨ 核心功能特性

本工具集涵盖**天线计算**、**射频微波网络**及**常用参考字典**三大核心模块，旨在覆盖日常研发测试中的高频需求痛点。

### 1. 📡 天线分析工具 (Antenna Tools)
针对自由空间电波传播与天线辐射特性的专项计算：
*   **收发距离反演 (Range Calculator)**：基于 Friis 传输方程，结合接收机解调信噪比 (SNR) 要求与空间衰落余量 (Fade Margin) 的极致链路预算，附带损耗截点可视化图表。
*   **相控阵综合计算 (Phased Array)**：支持均匀直线阵 (ULA) 和均匀平面阵 (UPA) 的方向图综合计算；可动态调节波束指向角、扫描角及阵元间距，实时预警“栅瓣”出现区域。
*   **传播视距评估 (Line of Sight)**：充分考量真实的地球有效曲率参数与菲涅尔区 (Fresnel Zone) 杂物遮挡现象，计算电波传播视距及基站天线架设高度门槛。
*   **增益双向评估 (Gain Estimator)**：支持波束宽度经验法则与口径孔径效率法双向推算真实增益，并提供 dBi / dBd 单位互转。
*   **系统灵敏度解析 (Receiver Sensitivity)**：基于底噪 KTBF 理论与系统噪声系数 (NF)，量化最小可察觉信号阈值。
*   **波长/频率对照 (Wavelength)**：真空与不同介质常数下的波段特征计算。

### 2. ⚡ 射频网络工具 (RF Microwave Tools)
有源与无源微波器件的链路串联分析与参数剥离：
*   **可视化链路预算 (Cascaded Link Budget)**：零代码完成多级放大器 (LNA/PA)、衰减器、滤波器、混频器级联链路的搭建，自动结算末端输出功率状态（带系统拓扑可视化）。
*   **史密斯圆图阻抗匹配 (Impedance Matching)**：支持 L 型 (LC) 集总参数元器件与微带线分布参数匹配网络设计运算，告别圆图手动标点计算。
*   **微波传输线阻抗计算 (Line Impedance)**：提取微带线 (Microstrip)、共面波导 (CPWG)、同轴线 (Coaxial) 截面物理结构特征至特征阻抗的准确演算。
*   **驻波/回波互换 (VSWR & Return Loss)**：反射系数 (Γ)、回波损耗 (RL)、电压驻波比 (VSWR)、失配传输损耗四元同步转化，带通圆投影。
*   **级联驻波极限评估 (Cascaded VSWR)**：多端口器件级联时的恶劣波动极限求值。
*   **T / π 型衰减网络计算 (Attenuator Networks)**：快速求解固定衰减值所需架构的电阻阻值分布。

### 3. 📖 工程师参考手册 (Reference Tables)
内置免断网日常高频查询：
*   **IEEE/ITU 频段字典**：标准命名频段界限说明。
*   **微波同轴连接器指南**：涵盖常用型号（SMA, 2.92mm, 3.5mm, N等）的耐压、截止频率上限一览，并自带考虑海拔与温度的最恶劣实战**降额功率基准运算**。
*   **常用波导管 (Waveguides) 手册**：国际 EIA WG标准（WR系列）与国标管径对比、截至频率查表。
*   **标称值速查 (E-Series RLC)**：遵循 IEC 60063 规范，囊括 E6 至 E192 系列全精度级别的标准电阻、电容、电感值正反向双维度检索台。
*   **🌐 精品在线工具推荐**：打破本地局限，现代化网格卡片式收录村田(Murata) SimSurfing、ADI 等业界顶级半导体原厂的在线微波/电源仿真系统，自带全屏系统浏览器唤醒。

---

## 🚀 快速开始与编译指南

### 环境依赖
本项目要求您的操作系统中拥有 Python 3.9+ 环境。

*   **Python**: >= 3.9
*   **GUI 框架**: PyQt6
*   **科学计算与绘图**: NumPy, Matplotlib

### 源码运行步骤

1. **克隆项目到本地**
   ```bash
   git clone https://github.com/cr20085361/RF-Antenna-Toolkit.git
   cd RF-Antenna-Toolkit
   ```

2. **创建虚拟环境并安装依赖**
   ```bash
   python -m venv .venv
   # Windows 激活
   .venv\Scripts\activate
   # 如果是 MacOS/Linux 则是 source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **启动应用程序**
   ```bash
   python main.py
   ```

### 独立执行文件打包 (Windows Desktop App)
本项目完美兼顾了纯净的 Python 开发调试生态，并通过 `PyInstaller` 搭载专属的暗蓝矢量天线图标 (`app.ico`) 与启动缓冲画面 (`splash.png`)，实现了**一次编译，脱离环境全局可运行**的设计准则。

```bash
# 激活独立虚拟环境，避免全量库污染
.\.venv\Scripts\activate

# 执行强制打包流程 (参考 .agents/workflows/build_exe.md 指南)
python -m PyInstaller -y RFAntennaToolkit.spec
```
编译成功后，完整的免安装绿色版或标准分发版本体存放于根目录下的 `dist/RFAntennaToolkit/` 目录中。

---

## 💡 界面与体验 (UI & User Experience)

> 工具采用**类锤子科技 (Smartisan OS) 拟物极简风与数据扁平化兼顾的主题 (Smartisan.qss)** 开发，注重输入输出的视觉对齐、下拉伸缩、状态留白以及核心数值的亮色凸显。旨在让“冰冷的数据表和工程计算”带有一些愉悦的操作感知体验。

同时，每个专项工具右下角均附带详细的**工程领域四维知识**：
*   **🎯 直观理解**：一句大白话解释用途。
*   **🧮 数学模型**：标准代数物理方程。
*   **🛠️ 工程边界**：实际操作中的折损妥协提示（如预留衰落余量、考虑插损漏电）。
*   **📜 发现历史**：人物与公式的背景轶闻。

---
**Enjoy Your Engineering Journey!**
