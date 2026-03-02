# -*- coding: utf-8 -*-
"""
核心计算逻辑 - 二维相控阵天线计算器
Core Logic - 2D Phased Array Calculator

功能:
- 计算 Nx * Ny 二维矩形面阵的阵列因子 (Array Factor)
- 支持等间距 dx, dy
- 幅相加权窗函数生成 (Uniform, Hanning, Hamming, Blackman 等简单加权，后续可扩充 Taylor/Chebyshev)
- 波束电平特征提取 (HPBW, 指向性增益 Directivity, 第一副瓣电平 SLL)
- 一维切面方向图提取 (可指定方位角 Phi 或 俯仰角 Theta 切面)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional

@dataclass
class PhasedArrayParams:
    """相控阵配置参数"""
    num_x: int = 8          # X轴阵元数
    num_y: int = 8          # Y轴阵元数
    spacing_x: float = 0.5  # X轴间距 (相对波长 λ)
    spacing_y: float = 0.5  # Y轴间距 (相对波长 λ)
    scan_theta: float = 0.0 # 扫描俯仰角 (度)
    scan_phi: float = 0.0   # 扫描方位角 (度)
    window_type: str = "Uniform"  # 窗函数类型 (Uniform, Hanning, Hamming, Blackman)
    
@dataclass
class PhasedArrayResult:
    """相控阵计算结果"""
    theta_deg: np.ndarray          # 1D 切面的 Theta 角坐标 (度)
    af_db: np.ndarray              # 1D 切面的归一化阵列因子 (dB)
    
    directivity_dbi: float         # 估算的理论峰值方向性增益 (dBi)
    hpbw_deg: float                # 半波瓣宽度 (度)
    sll_db: float                  # 第一副瓣电平 (相对主瓣, dB. 负数)
    is_grating_lobe: bool          # 是否出现明显的栅瓣
    
    # 元数据
    cut_plane: str                 # 绘制的切面标识，如 "Phi = 0° (Elevation Cut)"


@dataclass
class PhasedArray3DResult:
    """相控阵计算结果 (3D Surface)"""
    theta_grid: np.ndarray     # Theta 网格 (rad, meshgrid)
    phi_grid: np.ndarray       # Phi 网格 (rad, meshgrid)
    af_db_grid: np.ndarray     # 阵列因子网格 (dB)
    directivity_dbi: float     # 估算方向性 (dBi)
    is_grating_lobe: bool      # 是否存在栅瓣


class PhasedArrayCalculator:
    """二维相控阵核心计算引擎 (基于理想各向同性阵元)"""

    def __init__(self):
        pass

    def _generate_weights(self, n: int, window_type: str) -> np.ndarray:
        """生成 1D 的幅相加权窗函数"""
        if n <= 1:
            return np.ones(1)
            
        if window_type == "Hanning":
            w = np.hanning(n)
        elif window_type == "Hamming":
            w = np.hamming(n)
        elif window_type == "Blackman":
            w = np.blackman(n)
        else:
            w = np.ones(n)
            
        # 归一化使得主瓣不丢增益基准 (中心权值为1或平均权值为1均可，这里做均值归一化)
        if np.sum(w) > 0:
            w = w / np.sum(w) * n
        return w

    def calculate_1d_cut(self, params: PhasedArrayParams, cut_type: str = "elevation", fixed_angle: float = 0.0) -> PhasedArrayResult:
        """
        计算一维切面方向图及关键指标。
        
        Args:
            params: 阵列参数
            cut_type: 'elevation' (固定 Phi，扫描 Theta) 或 'azimuth' (固定 Theta=90，扫描 Phi，注意天线坐标系定义)
                     通常对于面阵，最常见的是看主平面 (Phi=0° 和 Phi=90°) 的 Theta 扫描切面。
            fixed_angle: 固定截面的角度值 (度)
        """
        # 将输入角度转为弧度
        th0 = np.radians(params.scan_theta)
        phi0 = np.radians(params.scan_phi)
        
        # 1. 物理位置信息建立
        # 默认天线阵列分布在 X-Y 平面，以原点为中心对称。
        xn = np.arange(params.num_x) * params.spacing_x
        xn = xn - np.mean(xn)
        
        yn = np.arange(params.num_y) * params.spacing_y
        yn = yn - np.mean(yn)
        
        # 2. 幅相衰减权重
        wx = self._generate_weights(params.num_x, params.window_type)
        wy = self._generate_weights(params.num_y, params.window_type)
        
        # 生成2D权重矩阵 (Nx, Ny)
        w_2d = np.outer(wx, wy)
        
        # 3. 目标扫描切面的坐标轴生成
        # 一维切面，我们计算 Theta 从 -90 到 90 度的切面 (或者 0 到 180，看习惯，用 -90 到 90 比较符合雷达直觉)
        theta_1d = np.linspace(-90, 90, 1001)
        theta_rad = np.radians(theta_1d)
        
        # 为了能够在极坐标中连续绘制，我们需要将 -90~0度 映射到对侧的 Phi。
        # 传统的球坐标 Theta 取值是 [0, 180]。
        # 这里的工程直觉处理：正角度表示 Phi = fixed_angle，负角度表示 Phi = fixed_angle + 180
        phi_1d = np.where(theta_rad >= 0, np.radians(fixed_angle), np.radians(fixed_angle + 180))
        theta_rad_abs = np.abs(theta_rad)
        
        # 4. 驱动相位计算 (波束偏转)
        # u0 = sin(th0)*cos(phi0), v0 = sin(th0)*sin(phi0)
        u0 = np.sin(th0) * np.cos(phi0)
        v0 = np.sin(th0) * np.sin(phi0)
        
        # 目标扫描方向的方向余弦空间
        u = np.sin(theta_rad_abs) * np.cos(phi_1d)
        v = np.sin(theta_rad_abs) * np.sin(phi_1d)
        
        # 阵列因子求和计算
        # AF(u, v) = sum( w * exp(j * 2pi * (xn*(u-u0) + yn*(v-v0))) )
        af_linear = np.zeros_like(theta_1d, dtype=complex)
        
        # 矩阵化加速 (对于不是极大规模的面阵循环也可，但张量积极快)
        # xn shape: (Nx,), yn shape: (Ny,)
        # u, v shape: (N_pts,)
        
        # k * d_pos * (dir - dir0)
        # 2*pi 是因为 d 已经是波长倍数
        phase_x = 2 * np.pi * np.outer(xn, (u - u0))  # shape: (Nx, N_pts)
        phase_y = 2 * np.pi * np.outer(yn, (v - v0))  # shape: (Ny, N_pts)
        
        # 计算每轴的一维阵列因子
        # sum_Nx (wx * exp(j * phase_x))
        af_x = np.sum(wx[:, np.newaxis] * np.exp(1j * phase_x), axis=0) # shape: (N_pts,)
        af_y = np.sum(wy[:, np.newaxis] * np.exp(1j * phase_y), axis=0) # shape: (N_pts,)
        
        # 面阵的阵列因子是一维的乘积 (分离定律)
        af_linear = af_x * af_y
        
        # 5. 归一化并取对数 (dB)
        af_abs = np.abs(af_linear)
        max_af = np.max(af_abs)
        if max_af > 0:
            af_norm = af_abs / max_af
        else:
            af_norm = af_abs
            
        # 避免 log10(0)
        af_norm = np.clip(af_norm, 1e-10, 1.0)
        af_db = 20 * np.log10(af_norm)
        
        # ================= 特征提取 =================
        # 找到主瓣峰值索引 (理论上应该是 0dB处，也就是 u=u0, v=v0的地方)
        peak_idx = np.argmax(af_db)
        
        # 提取 HPBW (3dB 波瓣宽度)
        hpbw = self._extract_hpbw(theta_1d, af_db, peak_idx)
        
        # 提取 SLL (第一副瓣电平)
        sll = self._extract_sll(af_db, peak_idx)
        
        # 栅瓣检测 (大于 -5dB 的副瓣视作极强相干或栅瓣)
        is_grating = bool(sll > -5.0 and sll < 0)
        
        # 方向性估算 Directivity (基于孔径面积和效率估算, Kraus公式 D ≈ 4pi * A / lambda^2)
        # 这里给出理想均匀线阵/面阵的简易方向性估算公式: D_max ≈ N * M * D_element (假设单元D=pi)
        # 我们用更通用的面积法: A = (Nx*dx) * (Ny*dy)
        area = (params.num_x * params.spacing_x) * (params.num_y * params.spacing_y)
        # 加权效率估算 (Uniform=1.0, 汉宁等窗在0.4-0.6之间)
        taper_eff_x = (np.sum(wx)**2) / (params.num_x * np.sum(wx**2)) if params.num_x > 0 else 1
        taper_eff_y = (np.sum(wy)**2) / (params.num_y * np.sum(wy**2)) if params.num_y > 0 else 1
        taper_eff = taper_eff_x * taper_eff_y
        
        # Cosine Element Factor 补偿 (方向性在扫描时会下降，即投影面积减小 cos(theta))
        scan_loss = np.cos(th0) if np.cos(th0) > 0.1 else 0.1
        
        # D = 4 * pi * Area * taper_eff * scan_loss (面积单位是lambda^2)
        directivity_linear = 4 * np.pi * area * taper_eff * scan_loss
        
        # 边界保护：阵子数过少时用理论下限 (单振子方向性假设约2.15dBi半波振子)
        min_dir = 10 * np.log10(params.num_x * params.num_y) 
        directivity_dbi = max(10 * np.log10(directivity_linear) if directivity_linear > 0 else 0, min_dir)

        return PhasedArrayResult(
            theta_deg=theta_1d,
            af_db=af_db,
            directivity_dbi=directivity_dbi,
            hpbw_deg=hpbw,
            sll_db=sll,
            is_grating_lobe=is_grating,
            cut_plane=f"Phi = {fixed_angle}° (Elevation Cut)"
        )
        
    def _extract_hpbw(self, angles: np.ndarray, af_db: np.ndarray, peak_idx: int) -> float:
        """从 1D 方向图中提取 3dB 宽度"""
        # 向左寻找第一个跌破 -3dB 的点
        left_idx = peak_idx
        while left_idx > 0 and af_db[left_idx] > -3.0:
            left_idx -= 1
            
        # 向右寻找第一个跌破 -3dB 的点
        right_idx = peak_idx
        while right_idx < len(af_db) - 1 and af_db[right_idx] > -3.0:
            right_idx += 1
            
        width = np.abs(angles[right_idx] - angles[left_idx])
        # 如果波束过宽没有跌下 -3dB，返回 180
        if width == 0 or left_idx == 0 or right_idx == len(af_db) - 1:
            # Maybe broadside dipole or too few elements
            if af_db[0] > -3 and af_db[-1] > -3:
                return 180.0
                
        return float(width)

    def _extract_sll(self, af_db: np.ndarray, peak_idx: int) -> float:
        """简单提取主瓣外的第一副瓣 (或者最高副瓣) 峰值"""
        # 第一步：找到主瓣零点边界 (或者简单粗暴地切掉峰值附近的一段距离)
        # 用一阶导数的符号变化找波谷
        diffs = np.diff(af_db)
        
        # 向右找第一个波谷 (主瓣右侧零点)
        right_null_idx = peak_idx
        while right_null_idx < len(diffs) - 1:
            if diffs[right_null_idx] > 0 and diffs[right_null_idx+1] >= 0:
                # 开始上升了，找到了副瓣的迹象
                break
            right_null_idx += 1
            
        # 向左找第一个波谷 (主瓣左侧零点)
        left_null_idx = peak_idx
        while left_null_idx > 0:
            if diffs[left_null_idx-1] < 0 and diffs[left_null_idx] <= 0:
                # 往回看开始下降，说明到了波谷
                break
            left_null_idx -= 1
            
        # 排除掉主瓣区域，求外侧的最大值就是副瓣
        mask = np.ones(len(af_db), dtype=bool)
        # 保护边界
        if left_null_idx > 0 and right_null_idx < len(af_db):
            mask[left_null_idx:right_null_idx+1] = False
        else:
            # 如果没找到清晰零点，可能是由于分辨率或特殊阵形，排除峰顶3dB区域
            mask[af_db > -3] = False
            
        sidelobes = af_db[mask]
        if len(sidelobes) > 0:
            max_sll = np.max(sidelobes)
            return float(max_sll)
        else:
            return -99.9 # 没有副瓣 (如极少阵元)

    def calculate_3d_pattern(self, params: PhasedArrayParams, resolution_deg: float = 3.0) -> PhasedArray3DResult:
        """
        计算 3D 空间内半球面的阵列因子网格
        
        参数:
            params: 阵列参数
            resolution_deg: 空间网格分辨率 (度)，越小越精细但计算越慢
            
        返回:
            PhasedArray3DResult 对象，包含绘图所需的网格数据
        """
        # 1. 提取参数
        Nx = params.num_x
        Ny = params.num_y
        dx = params.spacing_x
        dy = params.spacing_y
        
        # 将输入角度转为弧度
        th0 = np.radians(params.scan_theta)
        phi0 = np.radians(params.scan_phi)
        
        # 物理位置中心化
        xn = np.arange(Nx) * dx
        xn = xn - np.mean(xn)
        yn = np.arange(Ny) * dy
        yn = yn - np.mean(yn)
        
        # 加权窗函数
        wx = self._generate_weights(Nx, params.window_type)
        wy = self._generate_weights(Ny, params.window_type)
        
        # 2. 生成半球面网格 (Theta 0~90, Phi 0~360)
        theta_1d = np.arange(0, 90 + resolution_deg, resolution_deg)
        phi_1d = np.arange(0, 360 + resolution_deg, resolution_deg) 
        
        THETA, PHI = np.meshgrid(np.radians(theta_1d), np.radians(phi_1d))
        
        # 转换到 uv 空间
        U = np.sin(THETA) * np.cos(PHI)
        V = np.sin(THETA) * np.sin(PHI)
        
        # 主波束指向 (u0, v0)
        u0 = np.sin(th0) * np.cos(phi0)
        v0 = np.sin(th0) * np.sin(phi0)
        
        # 3. 矩阵化阵列因子计算 (利用 np.einsum 进行高效张量乘法)
        # xn.shape: (Nx,), U.shape: (N_phi, N_theta)
        # phase_x: (Nx, N_phi, N_theta)
        phase_x = 2 * np.pi * np.einsum('i,jk->ijk', xn, U - u0)
        phase_y = 2 * np.pi * np.einsum('i,jk->ijk', yn, V - v0)
        
        # 求和 af_x: sum_Nx(wx * exp(j * phase))
        af_x = np.sum(wx[:, np.newaxis, np.newaxis] * np.exp(1j * phase_x), axis=0)
        af_y = np.sum(wy[:, np.newaxis, np.newaxis] * np.exp(1j * phase_y), axis=0)
        
        af_linear = af_x * af_y
        
        # 4. 归一化并转 dB
        af_abs = np.abs(af_linear)
        max_af = np.max(af_abs)
        if max_af > 0:
            af_norm = af_abs / max_af
        else:
            af_norm = af_abs
            
        af_norm = np.clip(af_norm, 1e-10, 1.0)
        af_db = 20 * np.log10(af_norm)
        
        # 5. 指标估算
        area = (Nx * dx) * (Ny * dy)
        taper_eff_x = (np.sum(wx)**2) / (Nx * np.sum(wx**2)) if Nx > 0 else 1
        taper_eff_y = (np.sum(wy)**2) / (Ny * np.sum(wy**2)) if Ny > 0 else 1
        taper_eff = taper_eff_x * taper_eff_y
        scan_loss = np.cos(th0) if np.cos(th0) > 0.1 else 0.1
        
        directivity_linear = 4 * np.pi * area * taper_eff * scan_loss
        min_dir = 10 * np.log10(Nx * Ny) 
        directivity_dbi = max(10 * np.log10(directivity_linear) if directivity_linear > 0 else 0, min_dir)
        
        # 简单的栅瓣过阈检测 (通过检查除主瓣外是否有 > -5dB 的峰值)
        is_grating_lobe = False
        
        # 寻找主波束区 (-3dB)
        # 简单处理：把全图 > -5dB 的独立连通域（或局部极值）当做峰
        # 我们这里用一个简化的距离判定：距离理论满偏向角超过一定电轴距离的地方如果还有强势能量，就是栅瓣
        # 主瓣区域 (用方向余弦距离, radius = 0.5 约等于30度空间角)
        dist_uv = np.sqrt((U - u0)**2 + (V - v0)**2)
        main_beam_mask = dist_uv < 0.35 
        
        # 寻找主瓣外的大于 -5dB 的区域
        sidelobe_region = (af_db > -5.0) & (~main_beam_mask)
        if np.any(sidelobe_region):
            is_grating_lobe = True
            
        return PhasedArray3DResult(
            theta_grid=THETA,
            phi_grid=PHI,
            af_db_grid=af_db,
            directivity_dbi=directivity_dbi,
            is_grating_lobe=is_grating_lobe
        )
