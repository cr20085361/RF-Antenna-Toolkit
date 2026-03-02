
import sys
import numpy as np
import skrf as rf
from matplotlib import pyplot as plt

try:
    fig, ax = plt.subplots()
    s_1d = np.array([0.5+0.5j])
    
    print("Testing plot_smith without grid argument...")
    rf.plotting.plot_smith(s_1d, ax=ax)
    print("PASSED")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
