
import sys
import numpy as np
import skrf as rf
from matplotlib import pyplot as plt

# Simulate the fix in plotting
try:
    fig, ax = plt.subplots()
    
    # 1. Create a 3D s-parameter array
    s_3d = np.array([[[0.5+0.5j]]])
    
    # 2. Slice to 1D
    s_1d = s_3d[:, 0, 0]
    
    # 3. Plot using matplotlib directly
    ax.plot(s_1d.real, s_1d.imag)
    print("Plotting using ax.plot PASSED")
    
except Exception as e:
    print(f"Plotting FAILED: {e}")
    import traceback
    traceback.print_exc()

# Simulate division by zero fix
try:
    val = 0.0
    val_fixed = val if val > 1e-15 else 1e-15
    z = 1.0 / (1j * 2 * np.pi * 1e9 * val_fixed)
    print(f"Zero value handled. Z={z:.2e}")
except Exception as e:
    print(f"Zero value fix FAILED: {e}")
