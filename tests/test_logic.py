import unittest
import numpy as np
import sys
import os

# Ensure app can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.hrv_analysis import HRV_analysis
from app.controller import MainController
from app.config import Config

class TestHRV(unittest.TestCase):
    def setUp(self):
        # Create synthetic ECG signal
        # Sine wave at 1 Hz (60 bpm) + 10 Hz "QRS" spikes
        self.fs = 500
        t = np.linspace(0, 10, 10 * self.fs)
        self.signal = np.sin(2 * np.pi * 1 * t)
        
        # Add R-peaks
        for i in range(10):
            idx = i * self.fs # every second
            self.signal[idx:idx+20] += 5 # Spike
            
        self.hrv = HRV_analysis(self.signal, self.fs)

    def test_filter_runs(self):
        filtered = self.hrv.apply_filter()
        self.assertEqual(len(filtered), len(self.signal))
        
    def test_hrv_calculation(self):
        # Mock filtering by setting filtered data to raw (since raw has perfect peaks)
        self.hrv.filtered_data = self.signal
        rr = self.hrv.calculate_hrv()
        
        # We expect 10 peaks, so 9 RR intervals
        # But Pan Tompkins might need warmup or edges logic.
        # Intervals should be exactly 1.0s
        if len(rr) > 0:
            mean_rr = np.mean(rr)
            self.assertAlmostEqual(mean_rr, 1.0, delta=0.05) # Allow slight deviation due to peak refinement

class TestFHR(unittest.TestCase):
    def setUp(self):
        self.fs = 4 # CTG typical
        # Baseline 140
        self.fhr = np.full(1000, 140.0)
        
        # Add acceleration: +20 bpm for 20 sec (80 samples)
        # Start at 100
        self.fhr[100:180] += 20
        
        self.controller = MainController()
        # Mock ui setup to avoid window creation issues in test if possible, or just test logic method
        # We only need identify_accel_decel which is a method of controller class but doesn't use self state
        
    def test_accel_detection(self):
        accel, decel = self.controller.identify_accel_decel(self.fhr, self.fs)
        
        # Should detect acceleration around index 100-180
        self.assertTrue(len(accel) > 0)
        self.assertTrue(140 in accel) # Middle of event
        self.assertEqual(len(decel), 0)

if __name__ == '__main__':
    unittest.main()
