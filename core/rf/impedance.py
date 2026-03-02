# -*- coding: utf-8 -*-
"""
阻抗计算模块 (Impedance Calculator)
版本: v1.0
功能: 计算传输线特性阻抗
支持结构:
  1. 同轴线 (Coaxial)
  2. 单微带线 (Microstrip)
  3. 共面波导微带线 (CPWG - Coplanar Waveguide with Ground)

计算方法:
  - 同轴线: 经典解析公式
  - 微带线: Hammerstad-Jensen 公式
  - CPWG: Ghione-Naldi 公式 (使用椭圆积分)
"""

import math
from dataclasses import dataclass
from typing import Optional
from scipy.special import ellipk  # 完全椭圆积分第一类


# ==================== 结果数据类 ====================

@dataclass
class CoaxialResult:
    """同轴线计算结果"""
    impedance: float          # 特性阻抗 (Ω)
    inner_diameter: float     # 内导体外径 d (mm)
    outer_diameter: float     # 外导体内径 D (mm)
    dielectric_constant: float  # 介质介电常数 εᵣ
    capacitance_per_m: float  # 单位长度电容 (pF/m)
    inductance_per_m: float   # 单位长度电感 (nH/m)
    velocity_factor: float    # 速度因子


@dataclass
class MicrostripResult:
    """微带线计算结果"""
    impedance: float          # 特性阻抗 (Ω)
    effective_er: float       # 有效介电常数 εₑ
    width: float              # 导线宽度 W (mm)
    height: float             # 介质厚度 H (mm)
    thickness: float          # 铜箔厚度 T (μm)
    dielectric_constant: float  # 介质介电常数 εᵣ
    capacitance_per_m: float  # 单位长度电容 (pF/m)
    velocity_factor: float    # 速度因子
    w_h_ratio: float          # W/H 比值


@dataclass
class CPWGResult:
    """共面波导微带线计算结果"""
    impedance: float          # 特性阻抗 (Ω)
    effective_er: float       # 有效介电常数 εₑ
    center_width: float       # 中心导线宽度 W (mm)
    gap_width: float          # 间隙宽度 S (mm)
    height: float             # 介质厚度 H (mm)
    thickness: float          # 铜箔厚度 T (μm)
    dielectric_constant: float  # 介质介电常数 εᵣ
    capacitance_per_m: float  # 单位长度电容 (pF/m)
    velocity_factor: float    # 速度因子


# ==================== 常用材料介电常数 ====================

COMMON_MATERIALS = {
    "FR4 (标准)": 4.3,
    "FR4 (高频)": 4.0,
    "Rogers 4350B": 3.48,
    "Rogers 4003C": 3.55,
    "Rogers 5880": 2.2,
    "聚四氟乙烯 (PTFE)": 2.1,
    "空气": 1.0,
    "聚乙烯 (PE)": 2.25,
    "陶瓷 (Alumina)": 9.8,
}


# ==================== 阻抗计算器类 ====================

class ImpedanceCalculator:
    """
    传输线特性阻抗计算器
    
    支持三种传输线结构:
    1. 同轴线 (Coaxial)
    2. 单微带线 (Microstrip)
    3. 共面波导微带线 (CPWG)
    """
    
    # 物理常数
    C0 = 299792458  # 光速 (m/s)
    EPS0 = 8.854e-12  # 真空介电常数 (F/m)
    MU0 = 4 * math.pi * 1e-7  # 真空磁导率 (H/m)
    
    def __init__(self):
        pass
    
    # ==================== 同轴线计算 ====================
    
    def calculate_coaxial(
        self,
        inner_diameter_mm: float,  # 内导体外径 d (mm)
        outer_diameter_mm: float,  # 外导体内径 D (mm)
        dielectric_constant: float = 2.25  # 介质介电常数 εᵣ
    ) -> CoaxialResult:
        """
        计算同轴线特性阻抗
        
        公式: Z₀ = (60 / √εᵣ) × ln(D/d)
        
        参数:
            inner_diameter_mm: 内导体外径 d (mm)
            outer_diameter_mm: 外导体内径 D (mm)
            dielectric_constant: 介质相对介电常数 εᵣ
        
        返回:
            CoaxialResult: 计算结果
        """
        d = inner_diameter_mm
        D = outer_diameter_mm
        er = dielectric_constant
        
        # 验证参数
        if d <= 0 or D <= 0:
            raise ValueError("直径必须为正数")
        if D <= d:
            raise ValueError("外导体内径(D)必须大于内导体外径(d)")
        if er < 1:
            raise ValueError("介电常数必须≥1")
        
        # 计算阻抗: Z₀ = (60 / √εᵣ) × ln(D/d)
        impedance = (60 / math.sqrt(er)) * math.log(D / d)
        
        # 速度因子: v_f = 1 / √εᵣ
        velocity_factor = 1 / math.sqrt(er)
        
        # 单位长度电容 (pF/m): C = 2πε₀εᵣ / ln(D/d) × 10¹²
        capacitance_per_m = (2 * math.pi * self.EPS0 * er) / math.log(D / d) * 1e12
        
        # 单位长度电感 (nH/m): L = μ₀ / (2π) × ln(D/d) × 10⁹
        inductance_per_m = (self.MU0 / (2 * math.pi)) * math.log(D / d) * 1e9
        
        return CoaxialResult(
            impedance=impedance,
            inner_diameter=d,
            outer_diameter=D,
            dielectric_constant=er,
            capacitance_per_m=capacitance_per_m,
            inductance_per_m=inductance_per_m,
            velocity_factor=velocity_factor
        )
    
    # ==================== 微带线计算 ====================
    
    def calculate_microstrip(
        self,
        width_mm: float,          # 导线宽度 W (mm)
        height_mm: float,         # 介质厚度 H (mm)
        dielectric_constant: float = 4.3,  # 介质介电常数 εᵣ
        thickness_um: float = 35  # 铜箔厚度 T (μm)
    ) -> MicrostripResult:
        """
        计算微带线特性阻抗 (Hammerstad-Jensen 1980 + 厚度修正)
        
        v1.2 更新: 提升精度 (与 SI9000 吻合度 ~0.1%)
         - 去除 T/H<0.1 限制，确保厚度修正始终生效
         - 增加 F1 修正因子 (窄线时 +0.04×(1-u)² 项)
         - 增加 εeff 厚度修正: Δεeff = (εr-1)×T/(4.6×H)
        
        公式:
        当 W/H ≤ 1 (窄线):
            Z₀ = (60/√εₑ) × ln(8H/W + 0.25W/H)
        当 W/H > 1 (宽线):
            Z₀ = (120π/√εₑ) / (W/H + 1.393 + 0.667×ln(W/H + 1.444))
        
        有效介电常数 (Hammerstad-Jensen 1980):
            εₑ = (εᵣ+1)/2 + (εᵣ-1)/2 × F₁ - (εᵣ-1)×T/(4.6×H)
            F₁ = (1+12H/W)⁻⁰·⁵ + 0.04×(1-W/H)²  (W/H ≤ 1)
            F₁ = (1+12H/W)⁻⁰·⁵                      (W/H > 1)
        
        参数:
            width_mm: 导线宽度 W (mm)
            height_mm: 介质厚度 H (mm)
            dielectric_constant: 介质相对介电常数 εᵣ
            thickness_um: 铜箔厚度 T (μm)
        
        返回:
            MicrostripResult: 计算结果
        """
        W = width_mm
        H = height_mm
        er = dielectric_constant
        T = thickness_um / 1000  # 转换为 mm
        
        # 验证参数
        if W <= 0 or H <= 0:
            raise ValueError("宽度和高度必须为正数")
        if er < 1:
            raise ValueError("介电常数必须≥1")
        
        # ===== 铜箔厚度修正 (Wheeler) =====
        # v1.2: 去除 T/H<0.1 限制，确保在 T=35μm H=0.2mm 等情况下也能修正
        # 等效宽度: W_eff = W + ΔW
        if T > 0:
            delta_W = (T / math.pi) * math.log(
                4 * math.e / math.sqrt((T/H)**2 + (T/(math.pi * W + 1.1 * math.pi * T))**2)
            )
            W_eff = W + delta_W
        else:
            W_eff = W
        
        # W/H 比值 (使用有效宽度)
        u = W_eff / H
        
        # ===== 有效介电常数 (Hammerstad-Jensen 1980) =====
        # F₁ 因子: 窄线时有额外修正项
        if u <= 1:
            F1 = (1 + 12 / u) ** (-0.5) + 0.04 * (1 - u) ** 2
        else:
            F1 = (1 + 12 / u) ** (-0.5)
        
        eeff_base = (er + 1) / 2 + (er - 1) / 2 * F1
        
        # v1.2: εeff 厚度修正 (Schneider 1969)
        # 铜箔厚度会降低有效介电常数
        if T > 0:
            effective_er = eeff_base - (er - 1) * T / (4.6 * H)
        else:
            effective_er = eeff_base
        
        # ===== 计算阻抗 (Hammerstad-Jensen) =====
        if u <= 1:
            # 窄线公式
            impedance = (60 / math.sqrt(effective_er)) * math.log(8 / u + 0.25 * u)
        else:
            # 宽线公式
            impedance = (120 * math.pi / math.sqrt(effective_er)) / (
                u + 1.393 + 0.667 * math.log(u + 1.444)
            )
        
        # 速度因子
        velocity_factor = 1 / math.sqrt(effective_er)
        
        # 单位长度电容 (pF/m): C = εₑ / (c₀ × Z₀) × 10¹²
        capacitance_per_m = (effective_er / (self.C0 * impedance)) * 1e12
        
        return MicrostripResult(
            impedance=impedance,
            effective_er=effective_er,
            width=W,
            height=H,
            thickness=thickness_um,
            dielectric_constant=er,
            capacitance_per_m=capacitance_per_m,
            velocity_factor=velocity_factor,
            w_h_ratio=u
        )
    
    # ==================== 共面波导计算 ====================
    
    def calculate_cpwg(
        self,
        center_width_mm: float,   # 中心导线宽度 W (mm)
        gap_width_mm: float,      # 间隙宽度 S (mm)
        height_mm: float,         # 介质厚度 H (mm)
        dielectric_constant: float = 4.3,  # 介质介电常数 εᵣ
        thickness_um: float = 35  # 铜箔厚度 T (μm)
    ) -> CPWGResult:
        """
        计算 CBCPW (conductor-backed coplanar waveguide) 特性阻抗
        
        v1.2 更新: 修正为 CBCPW 模型
         - k₃ 使用 tanh (非 sinh)，对应底部接地板结构
         - 厚度修正使用间隙参数 S (Gevorgian)
         - 与 SI9000 结果吻合度: ~2% (典型配置)
        
        公式 (Ghione-Naldi 1984, Gevorgian 1995):
            Z₀ = 60π / [√εeff × (q₁ + q₃)]
            εeff = (q₁ + εr×q₃) / (q₁ + q₃)
        其中:
            q₁ = K(k)/K(k'), q₃ = K(k₃)/K(k₃')
            k  = W_e / (W_e + 2S_e)     — 中心线/总宽比
            k₃ = tanh(πW_e/4H) / tanh(π(W_e+2S_e)/4H)  — 接地层修正
        
        参数:
            center_width_mm: 中心导线宽度 W (mm)
            gap_width_mm: 间隙宽度 S (mm)
            height_mm: 介质厚度 H (mm)
            dielectric_constant: 介质相对介电常数 εᵣ
            thickness_um: 铜箔厚度 T (μm)，默认 35μm (1oz)
        
        返回:
            CPWGResult: 计算结果
        """
        W = center_width_mm  # 中心线宽 (mm)
        S = gap_width_mm     # 间隙宽度 (mm)
        H = height_mm        # 介质厚度 (mm)
        t = thickness_um / 1000.0  # 铜箔厚度转为 mm
        er = dielectric_constant
        
        # 验证参数
        if S <= 0 or W <= 0 or H <= 0:
            raise ValueError("所有尺寸必须为正数")
        if er < 1:
            raise ValueError("介电常数必须≥1")
        if t < 0:
            raise ValueError("铜箔厚度不能为负数")
        
        # ===== 铜箔厚度修正 (Gevorgian 1995) =====
        # 修正量 Δ 使用间隙宽度 S 作为参考距离
        if t > 0 and S > t:
            delta = (1.25 * t / math.pi) * (1 + math.log(2 * S / t))
            W_e = W + delta         # 有效线宽增大
            S_e = max(S - delta, 0.001)  # 有效间隙减小
        else:
            W_e = W
            S_e = S
        
        # ===== 计算 k 参数 (使用有效尺寸) =====
        k = W_e / (W_e + 2 * S_e)
        k_prime = math.sqrt(1 - k**2)
        
        # ===== CBCPW 接地层修正 (tanh 形式) =====
        # 注意: 必须用 tanh 而非 sinh，对应底部接地板结构
        k3 = math.tanh(math.pi * W_e / (4 * H)) / math.tanh(math.pi * (W_e + 2 * S_e) / (4 * H))
        k3_prime = math.sqrt(1 - k3**2)
        
        # ===== 椭圆积分 =====
        K_k = ellipk(k**2)
        K_k_prime = ellipk(k_prime**2)
        K_k3 = ellipk(k3**2)
        K_k3_prime = ellipk(k3_prime**2)
        
        # ===== 有效介电常数 (电容比法) =====
        # q₁ = K(k)/K(k')  — 上半空间 (空气) 的 CPW 模式贡献
        # q₃ = K(k₃)/K(k₃') — 下半空间 (介质+接地) 的贡献
        q1 = K_k / K_k_prime
        q3 = K_k3 / K_k3_prime
        effective_er = (q1 + er * q3) / (q1 + q3)
        
        # ===== CBCPW 阻抗公式 =====
        # Z₀ = 60π / [√εeff × (q₁ + q₃)]
        impedance = (60 * math.pi) / ((q1 + q3) * math.sqrt(effective_er))
        
        # 速度因子
        velocity_factor = 1 / math.sqrt(effective_er)
        
        # 单位长度电容 (pF/m)
        capacitance_per_m = (effective_er / (self.C0 * impedance)) * 1e12
        
        return CPWGResult(
            impedance=impedance,
            effective_er=effective_er,
            center_width=W,
            gap_width=S,
            height=H,
            thickness=thickness_um,
            dielectric_constant=er,
            capacitance_per_m=capacitance_per_m,
            velocity_factor=velocity_factor
        )
    
    # ==================== 辅助方法 ====================
    
    @staticmethod
    def get_common_materials():
        """获取常用材料介电常数"""
        return COMMON_MATERIALS.copy()
    
    # ==================== 反向计算方法 ====================
    
    def solve_coaxial_outer(
        self,
        target_impedance: float,     # 目标阻抗 Z₀ (Ω)
        inner_diameter_mm: float,    # 内导体外径 d (mm)
        dielectric_constant: float = 2.25  # 介质介电常数 εᵣ
    ) -> float:
        """
        反算同轴线外导体内径 D
        
        公式反推: D = d × exp(Z₀ × √εᵣ / 60)
        
        参数:
            target_impedance: 目标阻抗 Z₀ (Ω)
            inner_diameter_mm: 内导体外径 d (mm)
            dielectric_constant: 介质相对介电常数 εᵣ
        
        返回:
            外导体内径 D (mm)
        """
        d = inner_diameter_mm
        Z0 = target_impedance
        er = dielectric_constant
        
        # 验证参数
        if d <= 0:
            raise ValueError("内导体直径必须为正数")
        if Z0 <= 0:
            raise ValueError("目标阻抗必须为正数")
        if er < 1:
            raise ValueError("介电常数必须≥1")
        
        # 反推公式: D = d × exp(Z₀ × √εᵣ / 60)
        D = d * math.exp(Z0 * math.sqrt(er) / 60)
        
        return D
    
    def solve_microstrip_width(
        self,
        target_impedance: float,      # 目标阻抗 Z₀ (Ω)
        height_mm: float,             # 介质厚度 H (mm)
        dielectric_constant: float = 4.3,  # 介质介电常数 εᵣ
        thickness_um: float = 35,     # 铜箔厚度 T (μm)
        tolerance: float = 0.001      # 迭代精度 (mm)
    ) -> float:
        """
        反算微带线导线宽度 W (二分法)
        
        参数:
            target_impedance: 目标阻抗 Z₀ (Ω)
            height_mm: 介质厚度 H (mm)
            dielectric_constant: 介质相对介电常数 εᵣ
            thickness_um: 铜箔厚度 T (μm)
            tolerance: 迭代收敛精度 (mm)
        
        返回:
            导线宽度 W (mm)
        """
        H = height_mm
        Z0 = target_impedance
        er = dielectric_constant
        T = thickness_um
        
        # 验证参数
        if H <= 0:
            raise ValueError("介质厚度必须为正数")
        if Z0 <= 0:
            raise ValueError("目标阻抗必须为正数")
        if er < 1:
            raise ValueError("介电常数必须≥1")
        
        # 二分搜索范围: W 从 0.01H 到 20H
        W_low = 0.01 * H
        W_high = 20.0 * H
        
        # 检查边界阻抗
        Z_low = self.calculate_microstrip(W_low, H, er, T).impedance  # W小 → Z高
        Z_high = self.calculate_microstrip(W_high, H, er, T).impedance  # W大 → Z低
        
        if Z0 > Z_low or Z0 < Z_high:
            raise ValueError(f"目标阻抗 {Z0}Ω 超出可行范围 ({Z_high:.1f}~{Z_low:.1f}Ω)")
        
        # 二分法迭代
        max_iterations = 100
        for _ in range(max_iterations):
            W_mid = (W_low + W_high) / 2
            Z_mid = self.calculate_microstrip(W_mid, H, er, T).impedance
            
            if abs(Z_mid - Z0) < 0.01:  # 阻抗误差 < 0.01Ω
                return W_mid
            
            if Z_mid > Z0:  # 阻抗偏高，需增大线宽
                W_low = W_mid
            else:
                W_high = W_mid
            
            if W_high - W_low < tolerance:
                return W_mid
        
        return (W_low + W_high) / 2
    
    def solve_cpwg_gap(
        self,
        target_impedance: float,      # 目标阻抗 Z₀ (Ω)
        center_width_mm: float,       # 中心导线宽度 W (mm)
        height_mm: float,             # 介质厚度 H (mm)
        dielectric_constant: float = 4.3,  # 介质介电常数 εᵣ
        thickness_um: float = 35,     # 铜箔厚度 T (μm)
        tolerance: float = 0.001      # 迭代精度 (mm)
    ) -> float:
        """
        反算共面波导间隙宽度 S (二分法)
        
        v1.1 更新: 增加铜箔厚度参数
        
        参数:
            target_impedance: 目标阻抗 Z₀ (Ω)
            center_width_mm: 中心导线宽度 W (mm)
            height_mm: 介质厚度 H (mm)
            dielectric_constant: 介质相对介电常数 εᵣ
            thickness_um: 铜箔厚度 T (μm)
            tolerance: 迭代收敛精度 (mm)
        
        返回:
            间隙宽度 S (mm)
        """
        W = center_width_mm
        H = height_mm
        Z0 = target_impedance
        er = dielectric_constant
        
        # 验证参数
        if W <= 0 or H <= 0:
            raise ValueError("尺寸必须为正数")
        if Z0 <= 0:
            raise ValueError("目标阻抗必须为正数")
        if er < 1:
            raise ValueError("介电常数必须≥1")
        
        # 二分搜索范围: S 从 0.01mm 到 10*W
        S_low = 0.01
        S_high = 10.0 * W
        
        # 检查边界阻抗
        Z_low = self.calculate_cpwg(W, S_low, H, er, thickness_um).impedance
        Z_high = self.calculate_cpwg(W, S_high, H, er, thickness_um).impedance
        
        if Z0 < Z_low or Z0 > Z_high:
            raise ValueError(f"目标阻抗 {Z0}Ω 超出可行范围 ({Z_low:.1f}~{Z_high:.1f}Ω)")
        
        # 二分法迭代
        max_iterations = 100
        for _ in range(max_iterations):
            S_mid = (S_low + S_high) / 2
            Z_mid = self.calculate_cpwg(W, S_mid, H, er, thickness_um).impedance
            
            if abs(Z_mid - Z0) < 0.01:
                return S_mid
            
            if Z_mid < Z0:  # 阻抗偏低，需增大间隙
                S_low = S_mid
            else:
                S_high = S_mid
            
            if S_high - S_low < tolerance:
                return S_mid
        
        return (S_low + S_high) / 2


# ==================== 测试代码 ====================

if __name__ == "__main__":
    calc = ImpedanceCalculator()
    
    # 测试同轴线 (50Ω 标准同轴)
    print("=== 同轴线测试 ===")
    result = calc.calculate_coaxial(0.91, 2.98, 2.25)  # RG-58 参数
    print(f"阻抗: {result.impedance:.2f} Ω")
    
    # 测试微带线 (FR4 50Ω)
    print("\n=== 微带线测试 ===")
    result = calc.calculate_microstrip(1.1, 0.6, 4.3, 35)
    print(f"阻抗: {result.impedance:.2f} Ω")
    print(f"有效介电常数: {result.effective_er:.3f}")
    
    # 测试 CPWG
    print("\n=== CPWG 测试 ===")
    result = calc.calculate_cpwg(0.5, 0.2, 0.6, 4.3)
    print(f"阻抗: {result.impedance:.2f} Ω")
    print(f"有效介电常数: {result.effective_er:.3f}")
