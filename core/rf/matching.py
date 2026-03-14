# -*- coding: utf-8 -*-
"""
射频天线工具集 - 阻抗匹配核心模块
RF Antenna Toolkit - Impedance Matching Core

版本: v2.0.0
功能: 
    - 封装 scikit-rf 进行射频网络计算
    - 管理匹配网络拓扑 (LC梯形网络)
    - 计算匹配后的 S 参数
"""

import skrf as rf
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Union
import os

# 元件类型常量
ELEMENT_SERIES_R = "SERIES_R"
ELEMENT_SERIES_L = "SERIES_L"
ELEMENT_SERIES_C = "SERIES_C"
ELEMENT_SHUNT_R = "SHUNT_R"
ELEMENT_SHUNT_L = "SHUNT_L"
ELEMENT_SHUNT_C = "SHUNT_C"

@dataclass
class MatchingElement:
    """匹配网络元件"""
    id: int
    type: str           # 元件类型
    value: float        # 元件值 (Ohms, Henrys, Farads)
    enabled: bool = True
    
    @property
    def description(self) -> str:
        """元件描述"""
        unit = ""
        val_str = ""
        
        if "R" in self.type:
            unit = "Ω"
            val_str = f"{self.value:.2f}"
        elif "L" in self.type:
            unit = "nH"
            val_str = f"{self.value * 1e9:.2f}"
        elif "C" in self.type:
            unit = "pF"
            val_str = f"{self.value * 1e12:.2f}"
            
        topo = "串联" if "SERIES" in self.type else "并联"
        comp = "电阻" if "R" in self.type else ("电感" if "L" in self.type else "电容")
        
        return f"{topo} {comp}: {val_str} {unit}"

class MatchingCalculator:
    """
    阻抗匹配计算引擎
    """
    
    def __init__(self):
        self._load_network: Optional[rf.Network] = None
        self._elements: List[MatchingElement] = []
        self._z0 = 50.0
        
    def load_touchstone(self, filepath: str) -> bool:
        """加载 Touchstone 文件 (.s1p, .s2p)"""
        try:
            net = rf.Network(filepath)
            # 如果是 2 端口，默认取 S11 (假设 Port 2 匹配)
            # 或者将其转换为 1 端口网络?
            # 通常匹配是对 S11 进行的。
            if net.nports == 2:
                # 简单起见，取 port 1，假设 port 2 接匹配负载
                # 或者让用户选择? 暂时默认 s11
                # skrf 的 subnetwork 可以提取
                net = net.s11
            
            # 确保 Z0 统一
            if abs(net.z0[0,0] - self._z0) > 1e-6:
                net.renormalize(self._z0)
                
            self._load_network = net
            return True
        except Exception as e:
            print(f"Failed to load touchstone: {e}")
            return False
            
    def set_single_point(self, freq_hz: float, z_complex: complex):
        """设置单点阻抗目标"""
        f = rf.Frequency(freq_hz, freq_hz, 1, unit='hz')
        s = rf.z2s(np.array([[[z_complex]]]), z0=self._z0)
        self._load_network = rf.Network(frequency=f, s=s, z0=self._z0)
        self._load_network.name = "SinglePoint"

    def set_custom_range(self, center_freq: float, bw_hz: float, z_center: complex):
        """
        设置自定义频率范围负载
        根据中心频率的阻抗，生成 R-L 或 R-C 模型在带宽内的响应
        """
        if bw_hz <= 0:
            self.set_single_point(center_freq, z_center)
            return

        f_start = max(1, center_freq - bw_hz / 2)
        f_stop = center_freq + bw_hz / 2
        freqs = np.linspace(f_start, f_stop, 101)
        f_obj = rf.Frequency.from_f(freqs, unit='hz')
        
        # 计算等效元件模型
        R = z_center.real
        X = z_center.imag
        w_c = 2 * np.pi * center_freq
        w = 2 * np.pi * freqs
        
        Z_array = np.zeros(len(freqs), dtype=complex)
        
        # 简单的 R + jX 模型
        # 如果 X > 0, 视为电感 L = X / w_c
        # 如果 X < 0, 视为电容 C = -1 / (w_c * X)
        if abs(X) < 1e-9:
            Z_array[:] = R
        elif X > 0:
            L = X / w_c
            Z_array = R + 1j * w * L
        else:
            C = -1 / (w_c * X)
            with np.errstate(divide='ignore'):
                 Xc = -1.0 / (w * C)
            Z_array = R + 1j * Xc
            
        s = rf.z2s(Z_array.reshape(-1, 1, 1), z0=self._z0)
        self._load_network = rf.Network(frequency=f_obj, s=s, z0=self._z0)
        self._load_network.name = "CustomRange"
        
    def add_element(self, type: str, value: float) -> int:
        """添加元件"""
        # 生成 ID
        new_id = 1
        if self._elements:
            new_id = max(e.id for e in self._elements) + 1
            
        elem = MatchingElement(new_id, type, value)
        self._elements.append(elem)
        return new_id
        
    def remove_element(self, index: int):
        """移除元件"""
        if 0 <= index < len(self._elements):
            self._elements.pop(index)
            
    def update_element_value(self, index: int, value: float):
        """更新元件值"""
        if 0 <= index < len(self._elements):
            self._elements[index].value = value
            
    def move_element(self, from_idx: int, to_idx: int):
        """移动元件顺序"""
        if 0 <= from_idx < len(self._elements) and 0 <= to_idx < len(self._elements):
            elem = self._elements.pop(from_idx)
            self._elements.insert(to_idx, elem)

    def calculate_matched_network(self) -> Optional[rf.Network]:
        """
        计算匹配后的网络
        
        Math:
            Total = Element_N ** ... ** Element_1 ** Load
            注意顺序：
            通常匹配网络是插入在 Source 和 Load 之间。
            如果是 Source -> MatchNet -> Load
            我们关心的是 Input Impedance (从 Source 看进去)。
            
            S parameter 级联 (T矩阵):
            InputZ = MatchNet ** Load
            
            MatchNet 由元件级联而成。
            元件顺序：
            index 0 是最靠近 Load 的元件? 还是最靠近 Source 的?
            通常 UI 列表中，顶部是 Port 1 (Source)，底部是 Port 2 (Load)。
            
            设列表顺序为从 Source 到 Load。
            MaskNet = Elem[0] ** Elem[1] ** ...
            Total = MatchNet ** Load
        """
        if self._load_network is None:
            return None
            
        if not self._elements:
            return self._load_network
            
        # 1. 构建匹配网络
        freq = self._load_network.frequency
        matched_net = self._load_network
        
        # 遍历元件 (从紧邻 Load 的元件开始，即列表的最后一个? 
        # 还是列表第一个元件连接 Load?
        # 约定：UI 列表顺序 0 -> N，0 连接 Source，N 连接 Load。
        # 因此，我们需要先级联元件，再级联 Load。
        # 或者：反向遍历，先将 Load 与最后一个元件级联，再与倒数第二个...
        # Load_new = Elem_N ** Load
        # Load_new_2 = Elem_N-1 ** Load_new
        # ...
        
        # 使用反向遍历，模拟从 Load 向 Source 逐步添加元件
        for i in range(len(self._elements) - 1, -1, -1):
            elem = self._elements[i]
            if not elem.enabled:
                continue
                
            elem_net = self._create_element_network(elem, freq)
            if elem_net:
                matched_net = elem_net ** matched_net
                
        return matched_net
        
    def _create_element_network(self, elem: MatchingElement, freq: rf.Frequency) -> rf.Network:
        """创建单个元件的 2-port 网络"""
        w = freq.w
        n = len(w)
        
        # ABCD 矩阵初始化
        # Shape: (N, 2, 2)
        a = np.zeros((n, 2, 2), dtype=complex)
        
        # 预设单位矩阵
        # [[1, 0], [0, 1]] 实际上是 [[1, 0], [0, 1]]
        # 也就是直通. 
        # 但我们需要根据元件填值
        
        if "SERIES" in elem.type:
            # 串联阻抗 Z
            # ABCD = [[1, Z], [0, 1]]
            Z = np.zeros(n, dtype=complex)
            
            if elem.type == ELEMENT_SERIES_R:
                Z[:] = elem.value
            elif elem.type == ELEMENT_SERIES_L:
                Z[:] = 1j * w * elem.value
            elif elem.type == ELEMENT_SERIES_C:
                # 避免除零
                with np.errstate(divide='ignore'):
                    # 若 C=0 -> Z=infinity (Open). 使用极小电容模拟
                    val = elem.value if elem.value > 1e-15 else 1e-15
                    Z[:] = 1.0 / (1j * w * val)
                Z[w==0] = 1e9 # DC 阻断
            
            a[:, 0, 0] = 1
            a[:, 0, 1] = Z
            a[:, 1, 0] = 0
            a[:, 1, 1] = 1
            
        elif "SHUNT" in elem.type:
            # 并联导纳 Y
            # ABCD = [[1, 0], [Y, 1]]
            Y = np.zeros(n, dtype=complex)
            
            if elem.type == ELEMENT_SHUNT_R:
                if elem.value < 1e-6:
                    Y[:] = 1e9 # 短路
                else:
                    Y[:] = 1.0 / elem.value
            elif elem.type == ELEMENT_SHUNT_L:
                with np.errstate(divide='ignore'):
                    # 若 L=0 -> Y=infinity (Short). 使用极小电感模拟
                    val = elem.value if elem.value > 1e-15 else 1e-15
                    Y[:] = 1.0 / (1j * w * val)
                Y[w==0] = 1e9 # DC 短路
            elif elem.type == ELEMENT_SHUNT_C:
                Y[:] = 1j * w * elem.value
                
            a[:, 0, 0] = 1
            a[:, 0, 1] = 0
            a[:, 1, 0] = Y
            a[:, 1, 1] = 1
            
        # 创建网络
        net = rf.Network(frequency=freq, a=a)
        net.name = elem.description
        return net
