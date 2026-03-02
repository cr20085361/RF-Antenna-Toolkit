
import sys
import numpy as np
import skrf as rf
from matplotlib import pyplot as plt

# Simulate the fix in plotting
try:
    fig, ax = plt.subplots()
    
    # 1. Create a 3D s-parameter array (1 freq point)
    # shape (1, 1, 1)
    s_3d = np.array([[[0.5+0.5j]]])
    
    print(f"Original shape: {s_3d.shape}")
    
    # 2. Slice to 1D
    s_1d = s_3d[:, 0, 0]
    print(f"Sliced shape: {s_1d.shape}")
    
    # 3. Plot
    rf.plotting.plot_smith(s_1d, ax=ax, grid=False)
    print("Plotting 1D array PASSED")
    
except Exception as e:
    print(f"Plotting FAILED: {e}")
    import traceback
    traceback.print_exc()

# Simulate division by zero fix
try:
    val = 0.0
    # Fix logic:
    val_fixed = val if val > 1e-15 else 1e-15
    z = 1.0 / (1j * 2 * np.pi * 1e9 * val_fixed)
    print(f"Zero value handled. Z={z:.2e}")
except Exception as e:
    print(f"Zero value fix FAILED: {e}")
