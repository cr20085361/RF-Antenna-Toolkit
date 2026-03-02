
import sys
import os
import os
import unittest
import math

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.rf.link_budget_calculator import LinkBudgetCalculator, StageParams

class TestLinkBudgetCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = LinkBudgetCalculator()

    def test_single_stage(self):
        stage = StageParams(gain_db=10, nf_db=3, op1db_dbm=20)
        results = self.calc.calculate_chain([stage])
        
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0].cascaded_gain_db, 10)
        self.assertAlmostEqual(results[0].cascaded_nf_db, 3)
        self.assertAlmostEqual(results[0].cascaded_op1db_dbm, 20)

    def test_two_stages_gain_nf(self):
        # Stage 1: G=10dB, NF=3dB
        s1 = StageParams(gain_db=10, nf_db=3)
        # Stage 2: G=10dB, NF=3dB
        s2 = StageParams(gain_db=10, nf_db=3)
        
        results = self.calc.calculate_chain([s1, s2])
        
        # Gain = 10 + 10 = 20 dB
        self.assertAlmostEqual(results[1].cascaded_gain_db, 20)
        
        # NF: F_total = F1 + (F2-1)/G1
        # F1 = 10^(3/10) ≈ 1.995
        # G1 = 10^(10/10) = 10
        # F2 = 1.995
        # F_total = 1.995 + (1.995-1)/10 = 1.995 + 0.0995 = 2.0945
        # NF_total_db = 10*log10(2.0945) ≈ 3.21 dB
        
        f1 = 10**(3/10)
        expected_nf_lin = f1 + (f1-1)/10
        expected_nf_db = 10 * math.log10(expected_nf_lin)
        
        self.assertAlmostEqual(results[1].cascaded_nf_db, expected_nf_db, places=2)

    def test_cascade_p1db(self):
        # Stage 1: OP1=20dBm
        s1 = StageParams(gain_db=10, op1db_dbm=20)
        # Stage 2: OP1=20dBm
        s2 = StageParams(gain_db=10, op1db_dbm=20)
        
        results = self.calc.calculate_chain([s1, s2])
        
        # 1/OP1_sys = 1/OP1_2 + 1/(OP1_1 * G2)
        # OP1_1 = 100mW
        # OP1_2 = 100mW
        # G2 = 10
        # 1/OP1_sys = 1/100 + 1/(100*10) = 0.01 + 0.001 = 0.011
        # OP1_sys = 1/0.011 ≈ 90.9 mW
        # OP1_sys_dbm = 10*log10(90.9) ≈ 19.58 dBm
        
        expected_op1_mw = 1.0 / (1/100.0 + 1/(100.0 * 10.0))
        expected_op1_dbm = 10 * math.log10(expected_op1_mw)
        
        self.assertAlmostEqual(results[1].cascaded_op1db_dbm, expected_op1_dbm, places=2)

if __name__ == '__main__':
    unittest.main()
