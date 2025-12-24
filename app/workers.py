from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import numpy as np
from app.hrv_analysis import HRV_analysis
from app.logger import get_logger
from app.config import Config

logger = get_logger(__name__)

class FileLoadWorker(QThread):
    finished = pyqtSignal(object, object, object, object, float) # time, signal, fhr, uc, fs
    error = pyqtSignal(str)

    def __init__(self, filepath, mode, fs=None):
        super().__init__()
        self.filepath = filepath
        self.mode = mode
        self.fs = fs

    def run(self):
        try:
            data = pd.read_csv(self.filepath)
            columns = [c.lower() for c in data.columns]
            
            time = None
            signal = None
            fhr = None
            uc = None
            calculated_fs = self.fs

            if self.mode == "HRV":
                # Robust column detection for ECG
                if 'time' in columns:
                    time = data.iloc[:, columns.index('time')].values
                else:
                    # Attempt to guess time if 1st column looks like it, or generate it
                    try:
                         # Heursitic: if col 0 is monotonic increasing, it's likely time
                         if data.iloc[:, 0].is_monotonic_increasing:
                             time = data.iloc[:, 0].values
                    except:
                        pass

                # Signal detection
                potential_signal_cols = ['signal', 'ecg', 'val', 'value', 'v', 'lead']
                signal_idx = -1
                for col in potential_signal_cols:
                    if col in columns:
                        signal_idx = columns.index(col)
                        break
                
                if signal_idx == -1:
                    # Fallback: 2nd column if exists, else 1st if no time
                    if len(columns) >= 2:
                        signal_idx = 1
                    else:
                        signal_idx = 0
                
                signal = data.iloc[:, signal_idx].values

                # Calculate FS if time is available
                # PRIORITIZE calculated FS from time column over the default/input FS
                if time is not None and len(time) > 1:
                    try:
                        # Median diff to be robust against dropped samples
                        diffs = np.diff(time)
                        # Remove zeroes or negative diffs just in case
                        valid_diffs = diffs[diffs > 0]
                        if len(valid_diffs) > 0:
                            median_diff = np.median(valid_diffs)
                            if median_diff > 0:
                                new_fs = 1.0 / median_diff
                                logger.info(f"Calculated FS from data: {new_fs} (Input was: {calculated_fs})")
                                calculated_fs = new_fs
                    except Exception as e:
                        logger.warning(f"Could not calculate FS from time: {e}")

            else: # FHR Mode
                # FHR column detection is stricter as per requirements but we can be nice
                if 'time' in columns:
                    time = data.iloc[:, columns.index('time')].values
                
                if 'fhr' in columns:
                    fhr = data.iloc[:, columns.index('fhr')].values
                
                if 'uc' in columns:
                    uc = data.iloc[:, columns.index('uc')].values
                
                if fhr is None:
                    raise ValueError("FHR column not found in CSV")

                # Calculate FS if time is available
                # PRIORITIZE calculated FS from time column over the default/input FS
                if time is not None and len(time) > 1:
                    try:
                        # Median diff to be robust against dropped samples
                        diffs = np.diff(time)
                        # Remove zeroes or negative diffs just in case
                        valid_diffs = diffs[diffs > 0]
                        if len(valid_diffs) > 0:
                            median_diff = np.median(valid_diffs)
                            if median_diff > 0:
                                new_fs = 1.0 / median_diff
                                logger.info(f"Calculated FS from data: {new_fs} (Input was: {calculated_fs})")
                                calculated_fs = new_fs
                    except Exception as e:
                        logger.warning(f"Could not calculate FS from time: {e}")

            if calculated_fs is None:
                calculated_fs = Config().FS # Default fallback

            # --- Data Expansion for Simulation ---
            # Ensure we have a minimum duration for simulation (e.g. 5 mins)
            min_duration = Config().MIN_SIMULATION_DURATION_SEC
            
            # Determine current duration
            current_duration = 0
            current_len = 0
            if signal is not None:
                current_len = len(signal)
            elif fhr is not None:
                current_len = len(fhr)
            
            if current_len > 0 and calculated_fs > 0:
                current_duration = current_len / calculated_fs

            if current_duration > 0 and current_duration < min_duration:
                repeats = int(np.ceil(min_duration / current_duration))
                logger.info(f"Expanding data: Duration {current_duration:.1f}s < {min_duration}s. Repeating {repeats} times.")
                
                if self.mode == "HRV" and signal is not None:
                    signal = np.tile(signal, repeats)
                    # For time, we need to extend it continuously
                    # If we had original time, use it to find dt, else use fs
                    dt = 1.0 / calculated_fs
                    if time is not None and len(time) > 1:
                        dt = np.median(np.diff(time))
                    
                    # Generate new time array
                    new_len = len(signal)
                    time = np.arange(new_len) * dt
                    if time is None and new_len > 0: # Should be covered but safe check
                         time = np.arange(new_len) / calculated_fs

                elif self.mode != "HRV" and fhr is not None:
                    # Tile FHR and UC
                    fhr = np.tile(fhr, repeats)
                    if uc is not None:
                        uc = np.tile(uc, repeats)
                    
                    # Extend time
                    dt = 1.0 / calculated_fs
                    if time is not None and len(time) > 1:
                        dt = np.median(np.diff(time))
                    
                    new_len = len(fhr)
                    time = np.arange(new_len) * dt

            self.finished.emit(time, signal, fhr, uc, calculated_fs)

        except Exception as e:
            logger.error(f"Error loading file: {e}")
            self.error.emit(str(e))

class AnalysisWorker(QThread):
    finished_hrv = pyqtSignal(object, object, object, object, str) # filtered, peak_times, hrv_data, summary_dict, summary_text
    finished_fhr = pyqtSignal() # Simplify for now, maybe just done signal
    error = pyqtSignal(str)

    def __init__(self, mode, data, fs, hrv_analyser=None):
        super().__init__()
        self.mode = mode
        self.data = data
        self.fs = fs
        self.hrv_analyser = hrv_analyser # Or initialize here

    def run(self):
        try:
            if self.mode == "HRV":
                if self.hrv_analyser is None:
                    # logger.info("Initializing HRV Analysis...")
                    self.hrv_analyser = HRV_analysis(self.data, self.fs)
                
                # These operations can be slow
                # logger.info("Applying Filter...")
                filtered_y_data = self.hrv_analyser.apply_filter(
                    lowcut=Config().FILTER['LOWCUT'],
                    highcut=Config().FILTER['HIGHCUT'],
                    order=Config().FILTER['ORDER']
                )
                # logger.info("Calculating HRV...")
                hrv_data = self.hrv_analyser.calculate_hrv()
                peak_times = self.hrv_analyser.get_peak_times()
                # logger.info("Summarizing HRV...")
                summary_dict, summary_text = self.hrv_analyser.summarize_hrv()
                
                # logger.info(f"Analysis Finished. Dict keys: {summary_dict.keys()}")
                
                self.finished_hrv.emit(filtered_y_data, peak_times, hrv_data, summary_dict, summary_text)
            
            else:
                # FHR analysis is usually fast but good to be consistent
                # Logic for FHR heavy lifting if any (currently in controller, should verify)
                pass # Sent mostly for consistency if we move logic here

        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            self.error.emit(str(e))
