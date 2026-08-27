# -*- coding: utf-8 -*-
"""
应用元数据与版本说明
"""

from dataclasses import dataclass
from typing import List


APP_NAME = "射频天线工具集_CN_v2.2"
APP_VERSION = "2.2"
APP_VERSION_LABEL = "v2.2_CN"
APP_SUBTITLE = "RF Antenna Toolkit_CN_v2.2 - 专业射频与天线计算工具"

COMPANY_NAME = "成都市安泰纳科技有限公司"
DEVELOPER_SIGNATURE = "Developer: CR | 625313077@qq.com"
AUTHOR_SIGNATURE = "作者: CR | 邮箱: 625313077@qq.com"
COPYRIGHT_TEXT = "© 2026 所有权保留"

GITHUB_OWNER = "cr20085361"
GITHUB_REPO = "RF-Antenna-Toolkit"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases"
GITHUB_LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


@dataclass(frozen=True)
class VersionFeatureEntry:
    """版本功能说明"""

    version: str
    title: str
    release_date: str
    highlights: List[str]
    modules: List[str]
    notes: List[str]


VERSION_FEATURES = [
    VersionFeatureEntry(
        version="2.2",
        title="全局防误触、波束角度直输与相控阵时延模型修正",
        release_date="2026-08-28",
        highlights=[
            "全局禁用输入控件（SpinBox, ComboBox, Slider等）鼠标滚轮调节数值，滚轮事件智能透传至页面滚动视口，彻底消除长页面浏览时的误触改值风险。",
            "目标波束指向（Beam Steering）扫描角 θ 与方位角 φ 增加精确数值输入框（QDoubleSpinBox），支持键盘直接键入与 0.1° 高精度滑块双向实时无缝联动。",
            "修正相控阵通道移相与时延计算中的频率联动物理模型：工作频率改变时硬件物理阵元间距锁定不变，实现相邻阵元真时延 Δτ 严格与频率无关，自适应动态换算电长度 d/λ 与相位差 ΔΦ。",
            "同步升级相控阵综合计算工具中的波束扫描输入组件，统一全工具集高精度角度控制体验。"
        ],
        modules=[
            "全局底层 -> 全局滚轮事件过滤器 (GlobalWheelEventFilter)",
            "天线工具 -> 相控阵移相与时延计算器 (BeamformingDelayTool)",
            "天线工具 -> 相控阵综合计算分析 (PhasedArrayTool)"
        ],
        notes=[
            "根据电磁理论，空间电磁波传播真时延 Δτ = (d·sinθ)/c 仅由硬件几何物理间距与空间扫描角决定，与电磁波工作频率无关。v2.2 彻底纠正了旧版本调频反向篡改硬件尺寸的问题。"
        ],
    ),
    VersionFeatureEntry(
        version="2.1",
        title="新增干扰压制计算器与底层优化",
        release_date="2026-04-30",
        highlights=[
            "正式推出“干扰压制计算器”，针对发射机对目标的电磁干扰压制效果进行专业评估。",
            "支持单频点与宽频段双模式评估，宽带模式下引入动态增减频点的参数输入表。",
            "全局数值输入控件接入“智能折算”逻辑，支持 MHz/GHz, dBm/W, m/km 等核心单位的无缝切换与自动数学换算。",
            "修复了大量极端情况下的UI排版对齐与由于滚轮误触引发的数据异常问题。"
        ],
        modules=[
            "天线工具 -> 干扰压制计算器（JammingTool）",
            "基础组件 -> 数值单位控件（ValueUnitWidget）"
        ],
        notes=[
            "宽带模式下的功率单位下拉框支持对表格内的历史频点数据进行批量换算，极大减免了手动敲击计算器的繁琐度。"
        ],
    ),
    VersionFeatureEntry(
        version="2.1.0",
        title="双脊波导完善与私有更新",
        release_date="2026-04-11",
        highlights=[
            "波导法兰工具把结构图与详情卡移到左侧联动区，并补齐 WRD110、WRD180、WRD840 的可绘图几何参数。",
            "双脊速查继续补充更细的法兰兼容备注，WRD110 / WRD180 / WRD840 可直接显示 ridge gap 与 ridge width。",
            "帮助菜单新增更新设置，GitHub Release 更新支持私有仓库令牌、资产名匹配和忽略指定版本。",
            "检查更新只在找到匹配安装包资产时提示，并可直接把命中的安装包保存到本地。",
        ],
        modules=[
            "参考手册中的波导法兰页升级为左侧联动结构展示页。",
            "GitHub 更新配置持久化到本地用户目录，适配私有仓库访问。",
            "更新检查流程新增资产过滤、忽略版本和安装包直存本地。",
        ],
        notes=[
            "WRD110、WRD180、WRD840 的几何值读取自公开 PDF 前视图，最终加工仍建议以原始厂家图纸复核。",
            "私有仓库检查更新需要具备仓库 Metadata / Contents 读取权限的 GitHub 令牌。",
        ],
    ),
    VersionFeatureEntry(
        version="2.0.0",
        title="工具集主框架定版",
        release_date="2026-04-01",
        highlights=[
            "完成射频与天线主工具框架，统一导航、样式和知识板块布局。",
            "补齐链路预算、阻抗匹配、驻波、带宽、增益、相控阵与远场等核心模块。",
            "建立标准波导、连接器、频段与元件标称值等基础参考手册。",
        ],
        modules=[
            "桌面应用主框架与风格主题。",
            "核心射频和天线计算模块。",
            "多类工程参考速查工具。",
        ],
        notes=[
            "作为 v2 主线基座版本，为后续可视化、更新服务和宽带波导扩展提供统一入口。",
        ],
    ),
]


CURRENT_VERSION_FEATURES = VERSION_FEATURES[0]