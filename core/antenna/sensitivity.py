
import math

class SystemSensitivity:
    """系统灵敏度计算逻辑"""
    
    @staticmethod
    def calculate_antenna_factor(freq_mhz: float, gain_dbi: float) -> float:
        """
        计算天线系数 (Antenna Factor)
        
        Formula:
            AF (dB/m) = 20*log10(f_MHz) - Gain(dBi) - 29.77
        
        Args:
            freq_mhz: 频率 (MHz)
            gain_dbi: 天线增益 (dBi)
            
        Returns:
            AF (dB/m)
        """
        if freq_mhz <= 0:
            return 0.0
        return 20 * math.log10(freq_mhz) - gain_dbi - 29.77

    @staticmethod
    def calculate_field_strength(freq_mhz: float, rx_sens_dbm: float, 
                                 gain_dbi: float, cable_loss_db: float) -> float:
        """
        计算系统灵敏度 (场强)
        
        Formula: 
            E (dBuV/m) = P_rx (dBm) + Loss (dB) + AF (dB/m) + 107
        """
        if freq_mhz <= 0:
            return 0.0
            
        af = SystemSensitivity.calculate_antenna_factor(freq_mhz, gain_dbi)
        p_ant = rx_sens_dbm + cable_loss_db # Power at antenna port required for sensitivity
        
        e_dbuv = p_ant + af + 107
        return e_dbuv

    @staticmethod
    def dbuv_to_uv(dbuv: float) -> float:
        """dBuV/m 转 uV/m"""
        return 10 ** (dbuv / 20.0)

    @staticmethod
    def calculate_rx_sensitivity(bw_khz: float, nf_db: float, snr_min_db: float) -> float:
        """
        计算接收机灵敏度 (dBm)
        S = N_floor + NF + SNR
        N_floor = -174 + 10*log10(BW_Hz)
        """
        if bw_khz <= 0:
            return -174.0 # 理论底噪极限
        
        bw_hz = bw_khz * 1000
        n_floor = -174 + 10 * math.log10(bw_hz)
        return n_floor + nf_db + snr_min_db
