import unittest
import numpy as np
import os
import sys
import pandas as pd
from PyQt5.QtCore import QCoreApplication

# Ensure app can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.workers import FileLoadWorker
from app.config import Config

class TestFileLoadWorker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Needed for QThread usage
        if not QCoreApplication.instance():
            cls.app = QCoreApplication([])

    def setUp(self):
        # Create a temporary short CSV file
        self.filename = "test_short_signal.csv"
        self.fs = 100
        self.duration = 10 # 10 seconds, definitely < 300s
        t = np.arange(0, self.duration, 1/self.fs)
        # Create signal + time columns
        df = pd.DataFrame({
            'time': t,
            'signal': np.sin(2 * np.pi * 1 * t)
        })
        df.to_csv(self.filename, index=False)
        self.worker = None

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            
    def test_expansion_logic_hrv(self):
        # Mode HRV
        self.worker = FileLoadWorker(self.filename, mode="HRV", fs=self.fs)
        
        # We need to capture the emitted signal
        self.result = None
        def on_finished(t, s, f, u, fs):
             self.result = (t, s, f, u, fs)
        
        self.worker.finished.connect(on_finished)
        self.worker.run() # Execute directly
        
        # Verify
        self.assertIsNotNone(self.result)
        time, signal, fhr, uc, fs = self.result
        
        # Check duration
        total_duration = time[-1] - time[0]
        min_duration = Config().MIN_SIMULATION_DURATION_SEC
        
        # It won't be exactly min_duration, but at least min_duration
        # Actually it's repeated enough times to cover min_duration
        self.assertGreaterEqual(total_duration, min_duration - 1) 
        self.assertGreater(len(signal), self.duration * self.fs) 
        
        # Check continuity of time
        diffs = np.diff(time)
        dt = 1.0/self.fs
        # Max gap shouldn't be much larger than dt
        # With np.tile, we reconstructed time.
        self.assertTrue(np.allclose(diffs, dt, atol=1e-3))
        
        print(f"Original Duration: {self.duration}s. Expanded: {total_duration:.2f}s.")

if __name__ == '__main__':
    unittest.main()
