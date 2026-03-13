import json
import os

zh_path = r'e:\AI_project\射频天线工具集\assets\locales\zh_CN.json'
en_path = r'e:\AI_project\射频天线工具集\assets\locales\en_US.json'

with open(zh_path, 'r', encoding='utf-8') as f: zh = json.load(f)
with open(en_path, 'r', encoding='utf-8') as f: en = json.load(f)

# Static strings for Far-Field Result Grid
grid_trans = {
    'lbl_ratio': ('D/λ 比值:', 'D/λ Ratio:'),
    'lbl_size_class': ('电尺寸分类:', 'Size Class:'),
    'lbl_dominant': ('主导判据:', 'Dominant:'),
    
    'lbl_rnf': ('反应性近场 R_nf:', 'Reactive Near-field:'),
    'lbl_radnf': ('辐射近场/菲涅尔区:', 'Radiative/Fresnel Zone:'),
    'lbl_ffz': ('远场/夫琅禾费区:', 'Far-field/Fraunhofer:'),
    
    'lbl_crit_phase': ('相位判据 (2D²/λ):', 'Phase Crit. (2D²/λ):'),
    'lbl_crit_5l': ('场衰减判据 (5λ):', 'Amp Decay (5λ):'),
    'lbl_crit_10l': ('保守场衰减 (10λ):', 'Conserv. Decay (10λ):'),
    'lbl_crit_5d': ('最小距离 (5D):', 'Minimum Dist (5D):'),
    
    'lbl_echo_wl': ('波长 λ:', 'Wavelength λ:'),
    'lbl_echo_d': ('口径 D:', 'Aperture D:'),
    'lbl_echo_deff': ('有效口径 D_eff:', 'Effective D_eff:')
}

for k, (ch, eng) in grid_trans.items():
    zh['farfield'][k] = ch
    en['farfield'][k] = eng

with open(zh_path, 'w', encoding='utf-8') as f: json.dump(zh, f, indent=4, ensure_ascii=False)
with open(en_path, 'w', encoding='utf-8') as f: json.dump(en, f, indent=4, ensure_ascii=False)
print("Language files updated successfully.")
