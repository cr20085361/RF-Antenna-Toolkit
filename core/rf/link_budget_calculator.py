# -*- coding: utf-8 -*-
"""
核心计算逻辑 - 链路预算计算器
Core Logic - Link Budget Calculator

功能:
- 定义射频组件参数 (StageParams)
- 计算级联增益 (Cascade Gain)
- 计算级联噪声系数 (Cascade NF) - Friis公式
- 计算级联 P1dB (Cascade P1dB)
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class StageParams:
    """单级组件参数"""
    name: str = "Stage"
    stage_type: str = "Amplifier" # LNA, Filter, Attenuator, etc.
    gain_db: float = 0.0          # 增益 (dB)
    nf_db: float = 0.0            # 噪声系数 (dB)
    op1db_dbm: float = 100.0      # 输出1dB压缩点 (dBm), 默认给很大表示不压缩
    
    # 辅助属性，不直接输入
    is_active: bool = True        # 是否是有源器件 (影响P1dB计算是否参与)

@dataclass
class StageResult:
    """单级计算结果 (包含级联累积值)"""
    stage_index: int
    params: StageParams
    
    # 单级线性值
    gain_lin: float
    nf_lin: float
    op1db_mw: float
    
    # 级联至此级的累积指标 (从输入到此级输出)
    cascaded_gain_db: float
    cascaded_nf_db: float
    cascaded_op1db_dbm: float
    cascaded_iip1db_dbm: float

class LinkBudgetCalculator:
    """链路预算计算器"""
    
    def calculate_chain(self, stages: List[StageParams]) -> List[StageResult]:
        """
        计算整个链路的级联指标
        
        Args:
            stages: 组件列表
            
        Returns:
            List[StageResult]: 每一级的计算结果
        """
        results = []
        
        # 累积变量
        cum_gain_db = 0.0
        cum_gain_lin = 1.0
        cum_nf_lin = 1.0  # F_total (Linear)
        
        # P1dB 计算较为复杂，需要从后往前反推或者使用累积公式
        # 这里使用通用的倒数求和近似公式 (Worst Case):
        # 1/op1_total_mw = 1/op1_n + 1/(op1_n-1 * gn) + ...
        # 为了方便逐级显示，无论是P1dB还是IP3，通常是计算 "输入到此级为止" 的系统指标
        
        # 我们采用逐级计算 "从头到当前级" 的系统级联指标
        
        for i, stage in enumerate(stages):
            # 1. 基础转换
            g_lin = 10 ** (stage.gain_db / 10.0)
            nf_lin = 10 ** (stage.nf_db / 10.0)
            op1_mw = 10 ** (stage.op1db_dbm / 10.0)
            
            # 2. 级联增益
            # G_sys = G_prev * G_curr
            current_sys_gain_lin = cum_gain_lin * g_lin
            current_sys_gain_db = 10 * math.log10(current_sys_gain_lin) if current_sys_gain_lin > 0 else -999
            
            # 3. 级联噪声系数 (Friis Formula)
            # F_sys = F_prev + (F_curr - 1) / G_prev
            # 注意: 这里 F_prev 是指 "前 i-1 级的级联 NF"
            # Friis 公式展开: F_total = F1 + (F2-1)/G1 + (F3-1)/G1G2 + ...
            # 增量项: (F_curr - 1) / cum_gain_lin (这里的 cum_gain_lin 是前 i 级的总增益... 不对，是前 i-1 级的总增益)
            
            if i == 0:
                cum_nf_lin = nf_lin
            else:
                cum_nf_lin += (nf_lin - 1) / cum_gain_lin
            
            current_sys_nf_db = 10 * math.log10(cum_nf_lin) if cum_nf_lin > 0 else 0
            
            # 4. 级联 P1dB (输出参考)
            # 公式: 1/OP1_sys = 1/OP1_curr + 1/(OP1_prev * G_curr) 
            # 这是一个递推公式，计算截止到当前级的系统 OP1dB
            # 初始值: 第一级 OP1
            
            if i == 0:
                current_sys_op1_mw = op1_mw
            else:
                prev_sys_op1_mw = results[-1].cascaded_op1db_dbm
                prev_sys_op1_mw = 10 ** (prev_sys_op1_mw / 10.0)
                
                # OP1_sys_inv = 1/op1_mw + 1/(prev_sys_op1_mw * g_lin)
                # 只有当器件有压缩特性时才计入 (虽然 passive 器件 P1dB 很高，倒数接近 0，自然忽略)
                term1 = 1.0 / op1_mw
                term2 = 1.0 / (prev_sys_op1_mw * g_lin)
                current_sys_op1_mw = 1.0 / (term1 + term2 + 1e-20) # 避免除零
                
            current_sys_op1_dbm = 10 * math.log10(current_sys_op1_mw) if current_sys_op1_mw > 0 else -100
            
            # IIP1 = OIP1 - Gain
            current_sys_iip1_dbm = current_sys_op1_dbm - current_sys_gain_db
            
            # 创建结果对象
            result = StageResult(
                stage_index=i,
                params=stage,
                gain_lin=g_lin,
                nf_lin=nf_lin,
                op1db_mw=op1_mw,
                cascaded_gain_db=current_sys_gain_db,
                cascaded_nf_db=current_sys_nf_db,
                cascaded_op1db_dbm=current_sys_op1_dbm,
                cascaded_iip1db_dbm=current_sys_iip1_dbm
            )
            results.append(result)
            
            # 更新累积值供下一级使用
            cum_gain_db += stage.gain_db
            cum_gain_lin *= g_lin
            
        return results

    def dbm_to_mw(self, dbm: float) -> float:
        return 10 ** (dbm / 10.0)
    
    def mw_to_dbm(self, mw: float) -> float:
        if mw <= 0: return -999.0
        return 10 * math.log10(mw)
