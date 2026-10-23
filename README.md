<div align="center">

# 📡 射频天线工具集_CN_v2.3 (RF Antenna Toolkit_CN_v2.3)

**一款专为射频与天线工程师打造的桌面端辅助计算与可视化软件。**<br>
基于 Python 和 PyQt6 开发，旨在集成本专业常用的繁杂计算公式与工程查表，提供直观、高效、现代化的科学计算体验。

</div >

---

## ✨ 核心功能特性

本工具集涵盖**天线计算**、**射频微波网络**及**常用参考字典**三大核心模块，旨在覆盖日常研发测试中的高频需求痛点。

### 1. 📡 天线分析工具 (Antenna Tools)
针对自由空间电波传播与天线辐射特性的专项计算：
*   **跳频测向捕获评估**：针对固定参考通道阵列，计算单跳整阵采集时间、实际与设计余量、跳速上限及最迟启动时间。支持采样点数换算、逐组时间轴与跳速余量曲线；仅评估时序可行性，不预测实际捕获概率或测向精度。
*   **收发距离反演 (Range Calculator)**：基于 Friis 传输方程，结合接收机解调信噪比 (SNR) 要求与空间衰落余量 (Fade Margin) 的极致链路预算，附带损耗截点可视化图表。
*   **相控阵综合计算 (Phased Array)**：支持均匀直线阵 (ULA) 和均匀平面阵 (UPA) 的方向图综合计算；可动态调节波束指向角、扫描角及阵元间距，实时预警“栅瓣”出现区域。
*   **相控阵移相与时延 (Beamforming Delay)**：面向通道级硬件波束赋形配置，计算 ULA/UPA 在指定扫描角下的相邻相位差、真时延 (TTD)，支持 4~8 bit 移相器量化与寄存器码字生成，提供全通道配置表导出与宽带波束斜视 (Beam Squint) 评估。
*   **传播视距评估 (Line of Sight)**：充分考量真实的地球有效曲率参数与菲涅尔区 (Fresnel Zone) 杂物遮挡现象，计算电波传播视距及基站天线架设高度门槛。
*   **增益双向评估 (Gain Estimator)**：支持波束宽度经验法则与口径孔径效率法双向推算真实增益，并提供 dBi / dBd 单位互转。
*   **系统灵敏度解析 (Receiver Sensitivity)**：基于底噪 KTBF 理论与系统噪声系数 (NF)，量化最小可察觉信号阈值。
*   **干扰压制计算器 (Jamming Calculator)**：专门评估发射机对远端目标（如通信/雷达设备）的电磁干扰压制效果。支持单频点和宽频段评估模式，具备链路空间损耗反演、发射功率要求与安全距离的精准推算能力。
*   **波长/频率对照 (Wavelength)**：真空与不同介质常数下的波段特征计算。
*   **远场距离计算器 (Far-Field Calculator)**：遵循 IEEE 149 / 3GPP 标准，支持电大/电小天线多判据融合，完整输出反应性近场、辐射近场边界，自带相控阵扫描角修正。

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
*   **常用波导管 (Waveguides) 手册**：国际 EIA WG标准（WR系列）与国标管径对比、截至频率查表，并补充常见双脊波导（WRD系列）的 ridge gap、典型过渡 WR、法兰兼容备注和可点击截面尺寸示意图。
*   **标称值速查 (E-Series RLC)**：遵循 IEC 60063 规范，囊括 E6 至 E192 系列全精度级别的标准电阻、电容、电感值正反向双维度检索台。
*   **🌐 精品在线工具推荐**：打破本地局限，现代化网格卡片式收录村田(Murata) SimSurfing、ADI 等业界顶级半导体原厂的在线微波/电源仿真系统，自带全屏系统浏览器唤醒。
*   **帮助与版本服务**：界面顶部新增“帮助 -> 版本功能 / 检查更新 / 更新设置”，支持查看当前版本能力说明、按资产名规则检查安装包，并适配 GitHub 私有仓库令牌。

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
   py -3 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   Windows 下不必先执行 `.venv\Scripts\Activate.ps1`，这样可以避开 PowerShell 执行策略导致的首次运行报错。
   也可以直接双击项目根目录的 `run_app.bat`，它会在首次运行时自动创建虚拟环境、安装依赖并启动应用。

3. **启动应用程序**
   ```bash
   .\.venv\Scripts\python.exe main.py
   ```

### 应用内检查更新

应用顶部菜单提供 `帮助 -> 检查更新`，默认会在启动后静默检查一次 GitHub Releases。

如果你使用的是公开仓库，通常只需发布正式 Release 并上传安装包资产即可。

如果你使用的是私有仓库，建议先打开 `帮助 -> 更新设置`，配置以下项目：

1. GitHub 仓库 Owner 和 Repo。
2. 具备仓库读取权限的 GitHub Token。
3. 安装包资产名匹配规则，例如 `RF-Antenna-Toolkit-Setup-*.exe`、`*.msi` 或 `portable`。
4. 如某一版暂不想提醒，可在“忽略版本”里填写对应版本号。

要让应用内更新真正命中安装包资产，请按以下方式发布版本：

1. 在 GitHub 仓库创建语义化 tag，例如 `v2.3`。
2. 基于该 tag 创建正式 Release，而不是仅推送 tag。
3. 在 Release 中上传安装包、压缩包或可执行文件资产。
4. 让资产名与应用中的匹配规则一致，例如 `RF-Antenna-Toolkit-Setup-v2.3.exe`。
5. 保持 Release tag 与应用内版本号一致，便于版本比较。

私有仓库推荐使用 GitHub Fine-grained Personal Access Token：

1. 打开 GitHub `Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens`。
2. 选择 `Generate new token`，仓库访问范围选 `Only select repositories`，并勾选你的私有仓库。
3. 在 `Repository permissions` 中至少授予 `Metadata: Read-only` 和 `Contents: Read-only`。
4. 生成后复制 token，粘贴到应用的 `帮助 -> 更新设置 -> 访问令牌`。

应用只会在检测到“版本更新 + 命中资产名规则”的情况下弹出提示，并支持直接把命中的安装包保存到本地。

### 独立执行文件打包 (Windows Desktop App)
本项目完美兼顾了纯净的 Python 开发调试生态，并通过 `PyInstaller` 搭载专属的暗蓝矢量天线图标 (`app.ico`) 与启动缓冲画面 (`splash.png`)，实现了**一次编译，脱离环境全局可运行**的设计准则。

```bash
# 执行强制打包流程 (参考 .agents/workflows/build_exe.md 指南)
.\.venv\Scripts\python.exe build_exe.py
```
编译成功后，完整的免安装绿色版或标准分发版本体存放于根目录下的 `dist/RFAntennaToolkit/` 目录中。
如需配合应用内更新，建议将这里产出的安装包或压缩包同步上传到对应 GitHub Release 的 Assets。

本版打包已额外覆盖以下资源，避免发布后出现“界面能启动但图片、样式或波导截面图缺失”的问题：

1. `assets/` 下的启动图、图标和工程示意图。
2. `resources/` 下的 SVG 图标资源。
3. `ui/assets/` 和 `ui/styles/` 下的界面图片与 QSS。
4. `scikit-rf` 运行时依赖的子模块与数据文件。

### Inno Setup 打包前预检

在执行 `installer_setup.iss` 之前，建议按下面顺序完成预检：

1. 先运行 `python -m pytest`，确认所有回归逻辑通过。
2. 运行 `build_exe.py`，确认 `dist/RFAntennaToolkit/` 已生成。
3. 核对 `dist/RFAntennaToolkit/` 内是否包含 `assets/`、`resources/`、`ui/styles/`、`ui/assets/`。
4. 从项目根目录外直接启动 `dist/RFAntennaToolkit/RFAntennaToolkit.exe`，确认样式、波导截面图、帮助菜单、更新设置页面均正常显示。
5. 预检通过后，再使用 Inno Setup 打开 `installer_setup.iss` 生成安装包。

当前 Inno 脚本已经同步到 `v2.3`，默认输出安装包名称为 `RFAntennaToolkit_CN_v2_Setup_v2.3.exe`。
安装包包含 Python、Qt 与计算依赖，可离线安装和使用；应用内检查更新及外部参考链接需要网络。安装器支持为当前用户安装或管理员安装，命令行可用 `/CURRENTUSER` 选择当前用户模式。

构建脚本会在 Windows 编译期间隔离外部工具的动态库搜索路径，防止 Poppler 等工具的同名 `icuuc.dll` 被误收集进 Qt 发行包。请使用 `build_exe.py` 构建，而不是从混有其他软件路径的终端直接运行旧的打包命令。

安装后也可以直接使用发行 EXE 进行非交互验收，无需 Python 或项目源码：

```powershell
& "安装目录\RFAntennaToolkit.exe" --verify-installation "验收报告目录\installation-report.json"
```

该命令在隐藏窗口中检查资源解码、跳频工具导航、44 μs与43.5 μs手算基准、超时判定、图表、输入失效清理及参考页，并写入 JSON。报告中 `frozen: true` 表示检查运行于独立发行包；只有 `success: true` 且进程退出码为0才算通过。

### Git 同步与忽略项

如果需要把当前版本同步到 GitHub，建议只提交源码、配置与文档，不提交本地构建产物。当前仓库已经忽略以下内容：

1. `.venv/` 等虚拟环境目录。
2. `build/`、`dist/`、`Output/` 等构建和安装输出目录。
3. `*.exe`、`*.msi`、`*.zip`、`*.7z` 等发布产物。
4. `tmp_*.png`、`tmp_pdf_render/` 等临时验证文件。

本次分支备注可使用：`版本 v2.3: 新增跳频测向捕获时间预算、逐组时间轴与知识说明`。

### 跳频测向捕获评估：使用与验证

在“天线工具 → 跳频测向捕获评估”中输入阵元数、相干通道数、切换时间、每组有效采集时间与目标跳速。阵元和通道总数都包含一路固定参考。第一版界面支持 2～256 个阵元，各组内通道同时采样，所有数据必须来自同一跳的一个连续有效窗口。

九元双通道默认需要八组采集。首组也需切换时，500 ns 切换加每组 5 μs 采集得到 `8 × 0.5 + 8 × 5 = 44 μs`，理想时序上限约 22,727 跳/秒。首组已接通且稳定时只计七次切换，总计 43.5 μs。以上仅为教学示例，不代表任何设备实测指标。

“更多时间开销”可填写每跳不可用时间、启动延迟、额外稳定、组间阻塞、预留余量与后处理。输入尚未在其他项计入的净时间；隐藏面板中的参数仍参与预算。后处理仅增加结果延迟，不要求信号继续存在；阻塞下一组采集的处理则应计入组间等待。零启动延迟只代表有效窗口开始时立即启动的最佳情况。

跳速与跳周期可互换，采样时间也可由每通道点数与有效采样率换算。点选分组表或时间条可查看对应阵元及采样时间；越过有效窗口的阶段标红。下方知识区解释跳频与调频、接收带宽、共同相位参考、跨跳限制及一手参考资料。时间足够只是必要条件，带宽、信噪比、校准、多径与连续处理吞吐仍需另行验证。

本次开发使用独立环境，避免覆盖可能已失效的旧 `.venv`。可用 Python 3.12 建立环境后运行：

```powershell
python -m venv env/fh-capture
.\env\fh-capture\Scripts\python.exe -m pip install -r requirements.txt pytest
$env:QT_QPA_PLATFORM = "offscreen"
.\env\fh-capture\Scripts\python.exe -m pytest -q
Remove-Item Env:QT_QPA_PLATFORM
.\env\fh-capture\Scripts\python.exe main.py
```

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
