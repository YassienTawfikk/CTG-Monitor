import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
import numpy as np
from scipy.signal import savgol_filter

from app.ui.design import Ui_MainWindow
from app.hrv_analysis import HRV_analysis
from app.config import Config
from app.logger import setup_logging, get_logger
from app.workers import FileLoadWorker, AnalysisWorker
import os


class MainController:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        
        setup_logging()
        self.logger = get_logger(__name__)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        
        self.file_worker = None
        self.analysis_worker = None

        # Connect signals to slots
        self.setupConnections()
        
        # Simulation State
        self.simulation_timer = QtCore.QTimer()
        self.simulation_timer.timeout.connect(self.update_simulation)
        self.is_simulating = False
        self.current_index = 0
        self.playback_speed = 1.0
        self.data_fs = 500 # Default, will be updated on load
        
        # Connect simulation controls
        self.ui.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.ui.stop_button.clicked.connect(self.stop_simulation)
        # self.ui.speed_combo.currentIndexChanged.connect(self.change_speed) # REMOVED
        self.ui.speed_button_group.buttonClicked[int].connect(self.change_speed)
        
        # Init speed buttons for default mode (HRV - assuming starts in HRV)
        # Access via group ID
        btn0 = self.ui.speed_button_group.button(0)
        btn1 = self.ui.speed_button_group.button(1)
        btn2 = self.ui.speed_button_group.button(2)
        btn3 = self.ui.speed_button_group.button(3)
        
        if btn0: btn0.setChecked(True)

        if self.ui.is_current_mode_HRV:
             if btn0: btn0.setText("1x")
             if btn1: btn1.setText("2x")
             if btn2: btn2.setText("5x")
             if btn3: btn3.setText("10x")
             self.playback_speed = 1.0
        else:
             if btn0: btn0.setText("10x")
             if btn1: btn1.setText("20x")
             if btn2: btn2.setText("50x")
             if btn3: btn3.setText("100x")
             self.playback_speed = 10.0 # Default for FHR

        # self.load_data_from_file("static/datasets/ECG/ECG_Person_84_rec_2_raw.csv")

    def setupConnections(self):
        """Connect buttons to their respective methods."""
        self.ui.quit_app_button.clicked.connect(self.closeApp)
        self.ui.mode_button.clicked.connect(self.toggle_mode)
        self.ui.upload_signal_button.clicked.connect(self.upload_signal)

    def closeApp(self):
        """Close the application."""
        self.app.quit()

    def toggle_mode(self):
        """Toggle mode in the design."""
        # Clear plots and reset simulation before switching
        # Stop simulation first to ensure timers stop
        if hasattr(self, 'stop_simulation'):
            self.stop_simulation()
            
        self.ui.clear_all_plots()
        self.reset_data() # Clear all signal data to start fresh in new mode
        self.enable_sim_controls(False)
        
        self.ui.toggle_mode_design()
    
        # Update Speed Options based on mode
        # HRV: 1x, 2x, 5x, 10x
        # FHR: 10x, 20x, 50x, 100x
        # Access buttons via group ID (0, 1, 2, 3 assumed order of creation)
        btn0 = self.ui.speed_button_group.button(0)
        btn1 = self.ui.speed_button_group.button(1)
        btn2 = self.ui.speed_button_group.button(2)
        btn3 = self.ui.speed_button_group.button(3)
        
        if self.ui.is_current_mode_HRV:
            if btn0: btn0.setText("1x")
            if btn1: btn1.setText("2x")
            if btn2: btn2.setText("5x")
            if btn3: btn3.setText("10x")
        else:
            if btn0: btn0.setText("10x")
            if btn1: btn1.setText("20x")
            if btn2: btn2.setText("50x")
            if btn3: btn3.setText("100x")
            
        # Reset speed to default (first button)
        if btn0:
            btn0.setChecked(True)
            # Trigger logic manually since setChecked doesn't emit clicked signal
            first_btn_text = btn0.text()
            self.playback_speed = float(first_btn_text.replace('x', ''))
            self.logger.info(f"Playback speed reset to: {self.playback_speed}x")

    def upload_signal(self):
        """Open a file dialog to select a signal file and initiate loading."""
        
        # Stop any running simulation before loading new data
        if hasattr(self, 'stop_simulation'):
            self.stop_simulation()
            self.enable_sim_controls(False) # Disable controls during load

        filepath, _ = QFileDialog.getOpenFileName(self.MainWindow, "Open Signal File", "/static/datasets/", "CSV Files (*.csv);;All Files (*)")
        if filepath:
            self.logger.info(f"Uploading file: {filepath}")
            self.ui.upload_signal_button.setEnabled(False)
            self.ui.upload_signal_button.setText("Loading...")
            
            mode = "HRV" if self.ui.is_current_mode_HRV else "FHR"
            input_fs = self.ui.fs_input.value()
            
            self.file_worker = FileLoadWorker(filepath, mode, input_fs)
            self.file_worker.finished.connect(self.on_file_loaded)
            self.file_worker.error.connect(self.on_worker_error)
            self.file_worker.start()

    def reset_data(self):
        """Clear all loaded signal data from memory."""
        attributes_to_clear = [
            'current_x_data', 'full_raw_y', 'full_filtered_data', 
            'full_peak_times', 'full_hrv_data', 'full_summary_dict', 
            'full_summary_text', 'full_fhr_data', 'full_uc_data', 
            'full_stv_data', 'full_accel_points', 'full_decel_points',
            'current_fhr_time'
        ]
        
        for attr in attributes_to_clear:
            if hasattr(self, attr):
                delattr(self, attr)
        
        self.current_index = 0
        self.current_index_float = 0.0
        
        # Also clear metric cards via update_plots_static if needed, 
        # but ui.clear_all_plots() handles plot clearing.
        # We might want to clear metric values visually too.
        for key, widget in self.ui.metric_widgets.items():
             val_label = widget.findChild(QtWidgets.QLabel, f"val_{key}")
             if val_label:
                 val_label.setText("-")

    def on_hrv_analysis_finished(self, filtered_y_data, peak_times, hrv_data, summary_dict, summary_text):
        self.ui.upload_signal_button.setEnabled(True)
        self.ui.upload_signal_button.setText("Upload Signal")
        
        # Store full data for simulation
        self.full_filtered_data = filtered_y_data
        self.full_peak_times = peak_times
        self.full_hrv_data = hrv_data
        self.full_summary_text = summary_text
        self.full_summary_dict = summary_dict # Store dict for UI population
        
        # Initial Plot (Static View)
        self.update_plots_static()
        
        # Enable controls
        self.enable_sim_controls(True)

    def update_plots_static(self):
        if not hasattr(self, 'full_filtered_data'):
            return 
        
        # Initial View: Zoom to simulation window start, NOT full signal
        window_size = Config().SIMULATION_WINDOW_SEC
        
        # 1. Raw Signal (Widget 01)
        self.ui.plot_widget_01.setXRange(0, window_size, padding=0)
        # self.ui.plot_widget_01.enableAutoRange(axis='x') # Disable full auto
        
        # 2. Filtered Signal (Widget 02)
        self.ui.plot_widget_02.setXRange(0, window_size, padding=0)
        
        # 3. HRV Metrics (Widget 03)
        self.ui.plot_widget_03.setXRange(0, window_size, padding=0)

        self.ui.plot_widget_02.clear()
        self.ui.plot_widget_02.plot(self.current_x_data, self.full_filtered_data, pen='w')
        
        # Fixed Y-Range for Filtered Signal
        y_min = np.min(self.full_filtered_data)
        y_max = np.max(self.full_filtered_data)
        margin = (y_max - y_min) * 0.1
        if margin == 0: margin = 1.0
        self.ui.plot_widget_02.setYRange(y_min - margin, y_max + margin, padding=0)
        self.ui.plot_widget_02.enableAutoRange(axis='y', enable=False)

        self.ui.plot_widget_03.clear()
        if len(self.full_hrv_data) > 1:
            hrv_data_ms = self.full_hrv_data * 1000
            self.ui.plot_widget_03.plot(self.full_peak_times[:-1], hrv_data_ms, pen='w')
            
            # Fixed Y-Range for HRV Metrics
            y_min = np.min(hrv_data_ms)
            y_max = np.max(hrv_data_ms)
            margin = (y_max - y_min) * 0.1
            if margin == 0: margin = 1.0
            self.ui.plot_widget_03.setYRange(y_min - margin, y_max + margin, padding=0)
            self.ui.plot_widget_03.enableAutoRange(axis='y', enable=False)

        # Populate Stats Cards if dict is available
        if hasattr(self, 'full_summary_dict'):
             d = self.full_summary_dict
             
             # Calculate BPM separately if not in dict (HRVAnalysis doesn't seem to have BPM explicit key)
             # BPM = 60 / (Mean RR in seconds) or similar.
             # "Mean RR Interval (ms)" is available.
             bpm = "-"
             if "Mean RR Interval (ms)" in d:
                 try:
                    mean_rr = d["Mean RR Interval (ms)"]
                    if mean_rr > 0:
                        bpm_val = 60000.0 / mean_rr
                        bpm = f"{bpm_val:.1f}"
                 except:
                    pass
             
             # self.logger.info(f"Stats Dictionary Keys: {list(d.keys())}")
             # self.logger.info(f"Calculated BPM: {bpm}")
             
             # ui_key now refers to the simple ID like 'bpm', 'mean_rr'
             def update_card(key, ui_key, value_override=None):
                 val = "-"
                 if value_override is not None:
                     val = value_override
                 elif key in d:
                     val = d[key]
                 
                 if ui_key in self.ui.metric_widgets:
                      widget = self.ui.metric_widgets[ui_key]
                      # Object name is f"val_{ui_key}"
                      val_label = widget.findChild(QtWidgets.QLabel, f"val_{ui_key}")
                      if val_label:
                          val_label.setText(str(val))
                          # self.logger.info(f"Updated widget {ui_key} with value {val}")
                      else:
                          self.logger.warning(f"Could not find label 'val_{ui_key}' in widget for {ui_key}")
                 else:
                      self.logger.warning(f"Metric widget for key '{ui_key}' not found in ui.metric_widgets")

             # Map Controller keys (HRVAnalysis dict) to UI IDs
             update_card(None, "bpm", value_override=bpm)
             update_card("Mean RR Interval (ms)", "mean_rr") 
             update_card("SDNN (ms)", "sdnn")
             update_card("RMSSD (ms)", "rmssd")
             update_card("pNN50 (%)", "pnn50")

    # --- Simulation Logic ---

    def enable_sim_controls(self, enable):
        self.ui.play_pause_button.setEnabled(enable)
        self.ui.stop_button.setEnabled(enable)

    def toggle_play_pause(self):
        if self.is_simulating:
            self.pause_simulation()
        else:
            self.play_simulation()

    def play_simulation(self):
        if not hasattr(self, 'full_filtered_data') and not hasattr(self, 'full_fhr_data'):
            return

        self.is_simulating = True
        self.ui.play_pause_button.setText("⏸") # Set to Pause icon
        self.ui.play_pause_button.setToolTip("Pause")
        self.ui.stop_button.setEnabled(True)
        
        if self.current_index >= len(self.current_x_data) - 1:
            self.current_index = 0
            self.current_index_float = 0.0
            
        # Better: Update every 20ms (50fps) for smoother "point-by-point" feel
        self.timer_interval_ms = 20
        self.simulation_timer.start(self.timer_interval_ms)

    def pause_simulation(self):
        self.is_simulating = False
        self.simulation_timer.stop()
        self.ui.play_pause_button.setText("▶") # Set to Play icon
        self.ui.play_pause_button.setToolTip("Resume")

    def stop_simulation(self):
        self.pause_simulation()
        self.current_index = 0
        self.current_index_float = 0.0 # Reset float tracker
        self.ui.stop_button.setEnabled(False)
        
        self.ui.play_pause_button.setText("▶") # Reset to Play icon
        self.ui.play_pause_button.setToolTip("Start Simulation")
        
        # Reset to static view
        if self.ui.is_current_mode_HRV:
             self.update_plots_static()
        else:
             # Reset FHR view
             if not hasattr(self, 'full_fhr_data'):
                 return
                 
             self.ui.plot_widget_01.clear()
             self.ui.plot_widget_02.clear()
             self.ui.plot_widget_04.clear()
             # Logic to reset X range
             self.ui.plot_widget_01.enableAutoRange(axis='x')
             self.ui.plot_widget_02.enableAutoRange(axis='x')
             self.ui.plot_widget_03.enableAutoRange(axis='x')
             self.ui.plot_widget_04.enableAutoRange(axis='x')
             
             self.plot_fhr_and_uc(self.current_fhr_time, self.full_fhr_data, self.full_uc_data)
             self.plot_stv(self.current_fhr_time, self.full_fhr_data)
             self.plot_accel_decel(self.current_fhr_time, self.full_fhr_data, self.fs_fhr)


    def change_speed(self, index):
        # speed_text = self.ui.speed_combo.currentText() # Old
        # Get the button that was clicked
        button = self.ui.speed_button_group.button(index)
        if button:
            speed_text = button.text()
            self.playback_speed = float(speed_text.replace('x', ''))
            self.logger.info(f"Playback speed set to: {self.playback_speed}x")

    def update_simulation(self):
        # Calculate how many samples to advance
        # Use float accumulator to be precise
        if not hasattr(self, 'current_index_float'):
            self.current_index_float = float(self.current_index)
            
        points_to_add = (self.data_fs * (self.timer_interval_ms / 1000.0)) * self.playback_speed
        self.current_index_float += points_to_add
        self.current_index = int(self.current_index_float)
        
        if self.current_index >= len(self.current_x_data):
            self.current_index = len(self.current_x_data) - 1
            self.stop_simulation()
            return

        # Update Plots
        # Performance optimization: Don't set full data array every frame if array is huge.
        # But PyQtGraph is fast. Let's try slicing.
        
        current_x = self.current_x_data[:self.current_index]
        current_time_val = self.current_x_data[self.current_index]
        
        # Moving Window Logic
        # Dynamic Window Size based on Mode
        if self.ui.is_current_mode_HRV:
            window_size = 5.0 # 5 seconds for ECG (Zoomed In)
        else:
            window_size = Config().SIMULATION_WINDOW_SEC # 30s or configured value for FHR
            
        min_x = 0
        max_x = current_time_val
        
        if current_time_val > window_size:
            min_x = current_time_val - window_size
            
        # Ensure we always show the window size if possible, or at least up to current time
        # Ideally, X-axis range should be [min_x, max_x]
        # But max_x might be small at start. 
        # Strategy: 
        # If current_time < window_size: Range [0, window_size] (so it fills up)
        # Else: Range [current_time - window_size, current_time] (scrolling)
        
        # Add a small lookahead buffer (e.g., 5% of window) so the trace doesn't hug the right edge
        lookahead = window_size * 0.05
        
        if current_time_val < window_size:
            # Initial fill. Keep standard range or add buffer.
            # Usually [0, window_size] is cleaner while filling.
            # But let's add buffer if desired. 
            # User wants "shift" to happen.
            view_min = 0
            view_max = window_size + lookahead
        else:
            # Scrolling: [current - window + buffer, current + buffer]
            # Wait, standard scrolling is [current - window, current]
            # With buffer: [current - window, current + buffer] (Size > window) -> Shrinks trace?
            # Or shift whole window: [current - window + buffer, current + buffer] (Size = window).
            # If we shift whole window, the latest point is at `current`, and `max` is `current + buffer`.
            # So there is empty space of size `buffer` on the right.
            view_max = current_time_val + lookahead
            view_min = view_max - (window_size + lookahead) # Ensure left side is correct?
            # No, we want total span = window_size? Or just show the window?
            # Config().SIMULATION_WINDOW_SEC is likely the amount of data seen.
            # If we add buffer, we can either zoom out slightly (show window + buffer) or shift.
            # Standard plotter behavior: Show [current - window, current + buffer].
            view_min = current_time_val - window_size

        # Apply X Range to all plots
        self.ui.plot_widget_01.setXRange(view_min, view_max, padding=0)
        self.ui.plot_widget_02.setXRange(view_min, view_max, padding=0)
        self.ui.plot_widget_03.setXRange(view_min, view_max, padding=0)
        self.ui.plot_widget_04.setXRange(view_min, view_max, padding=0)

        if self.ui.is_current_mode_HRV:
            if not hasattr(self, 'full_filtered_data'):
                self.stop_simulation()
                return

            current_y = self.full_filtered_data[:self.current_index]
            
            # Update Raw Signal (subset)
            if hasattr(self, 'full_raw_y'):
                 self.ui.plot_widget_01.clear()
                 self.ui.plot_widget_01.plot(current_x, self.full_raw_y[:self.current_index], pen='w')

            # Update Filtered
            self.ui.plot_widget_02.clear()
            # Optimization: could plot only view_min:current_index if array is huge
            self.ui.plot_widget_02.plot(current_x, current_y, pen='w')
            
            # Reveal metrics
            # Filter peaks that have occurred
            valid_peaks_mask = self.full_peak_times < current_time_val
            current_peaks = self.full_peak_times[valid_peaks_mask]
            
            if len(current_peaks) > 1:
                current_hrv = self.full_hrv_data[:len(current_peaks)-1]
                if len(current_hrv) > 0:
                     self.ui.plot_widget_03.clear()
                     self.ui.plot_widget_03.plot(current_peaks[:-1], current_hrv * 1000, pen='w')

        else: # FHR Mode
            current_fhr = self.full_fhr_data[:self.current_index]
            current_uc = self.full_uc_data[:self.current_index]
            
            self.ui.plot_widget_01.clear()
            self.ui.plot_widget_01.plot(current_x, current_fhr, pen={'color':'white', 'width': 2})
            
            self.ui.plot_widget_03.clear()
            self.ui.plot_widget_03.plot(current_x, current_uc, pen='w')
            
            # STV
            if hasattr(self, 'full_stv_data'):
                 idx_stv = max(0, self.current_index - 1)
                 self.ui.plot_widget_02.clear()
                 self.ui.plot_widget_02.plot(current_x[1:idx_stv+1], self.full_stv_data[:idx_stv], title="STV")
                 
            # Accel/Decel
            # Use the new current_time parameter to filter events
            self.ui.plot_widget_04.clear()
            self.plot_accel_decel(self.current_x_data, self.full_fhr_data, self.fs_fhr, current_time=current_time_val)

    def on_file_loaded(self, time, signal, fhr, uc, fs):
        self.ui.upload_signal_button.setEnabled(True)
        self.ui.upload_signal_button.setText("Upload Signal")
        
        self.data_fs = fs # Set global FS for simulation
        
        # Update FS input if calculated differently
        if fs != self.ui.fs_input.value():
            # If calculated FS is significantly different, assume input was default/guess and update it
            if abs(fs - self.ui.fs_input.value()) > 0.1:
                self.ui.fs_input.setValue(int(fs))
                self.logger.info(f"Updated UI FS input to calculated: {fs}")
                # Optional: Don't annoy user with popup every time if logic is solid,
                # or only popup if it was a big surprise.
                # Keeping popup for now as confirmation.
                # User requested removal:
                # QtWidgets.QMessageBox.information(
                #     self.MainWindow, 
                #     "Sampling Rate Detected", 
                #     f"Detected sampling rate: {fs:.1f} Hz based on time data.\nPlayback speed adjusted."
                # )

        if self.ui.is_current_mode_HRV:
             if signal is None:
                 self.show_error("Could not detect ECG signal column.")
                 return
             
             # Create X data if time is missing
             if time is None:
                 time = np.arange(len(signal)) / fs
             
             self.current_x_data = time
             self.full_raw_y = signal # Store raw for sim
             
             self.plot_data(time, signal, fs)

        else: # FHR Mode
             if fhr is None:
                  self.show_error("Could not detect FHR column.")
                  return
             
             if time is None:
                 time = np.arange(len(fhr)) # Fallback if no time
                 
             self.current_x_data = time
             self.current_fhr_time = time
             self.full_fhr_data = fhr
             self.full_uc_data = uc
             self.fs_fhr = fs

             self.ui.clear_all_plots()
             
             # Store STV for sim
             self.full_stv_data = np.abs(np.diff(fhr))
             
             self.plot_fhr_and_uc(time, fhr, uc)
             self.plot_stv(time, fhr)
             self.plot_accel_decel(time, fhr, fs)
             
             self.enable_sim_controls(True) # Enable manually since FHR doesn't use worker for analysis yet
             
             # Pre-calculate Accel/Decel for efficient plotting/simulation
             self.full_accel_points, self.full_decel_points = self.identify_accel_decel(fhr, fs)

    def on_worker_error(self, message):
        self.ui.upload_signal_button.setEnabled(True)
        self.ui.upload_signal_button.setText("Upload Signal")
        self.show_error(message)

    def show_error(self, message):
        self.logger.error(message)
        QtWidgets.QMessageBox.critical(self.MainWindow, "Error", message)

    def load_data_from_file(self, filepath):
        # Legacy method kept but redirected to new logic if needed
        # Or removed if not used anywhere else
        pass
         
    def plot_data(self, x_data, y_data, fs=500):
        """Plot the data on plot_widget_01 with error handling."""
        try:
            self.ui.plot_widget_01.clear()
            self.ui.plot_widget_01.plot(x_data, y_data, pen='w')  # Plot raw ECG data with white pen
            
            # Set Initial X-Axis Range to Window Size (Zoomed In)
            window_size = Config().SIMULATION_WINDOW_SEC
            self.ui.plot_widget_01.setXRange(0, window_size, padding=0)
            
            # Set Fixed Y-Axis Range
            y_min = np.min(y_data)
            y_max = np.max(y_data)
            margin = (y_max - y_min) * 0.1 # 10% margin
            if margin == 0: margin = 1.0
            
            self.ui.plot_widget_01.setYRange(y_min - margin, y_max + margin, padding=0)
            self.ui.plot_widget_01.enableAutoRange(axis='y', enable=False) # Disable auto-scale to keep it fixed
            
            if self.ui.is_current_mode_HRV:
                 # Trigger Analysis
                 self.start_hrv_analysis(x_data, y_data, fs)

        except Exception as e:
            self.show_error(f"Failed to plot data: {e}")

    def start_hrv_analysis(self, x_data, y_data, fs):
        self.enable_sim_controls(False) # Ensure disabled
        self.ui.upload_signal_button.setEnabled(False)
        self.ui.upload_signal_button.setText("Analyzing...")
        
        self.analysis_worker = AnalysisWorker("HRV", y_data, fs)
        # We need to pass x_data to plotting slot, or store it
        self.current_x_data = x_data 
        self.analysis_worker.finished_hrv.connect(self.on_hrv_analysis_finished)
        self.analysis_worker.error.connect(self.on_worker_error)
        self.analysis_worker.start()

    def on_hrv_analysis_finished(self, filtered_y_data, peak_times, hrv_data, summary_dict, summary_text):
        self.ui.upload_signal_button.setEnabled(True)
        self.ui.upload_signal_button.setText("Upload Signal")
        
        self.ui.plot_widget_02.clear()
        self.ui.plot_widget_02.plot(self.current_x_data, filtered_y_data, pen='w')

        self.ui.plot_widget_03.clear()
        if len(hrv_data) > 1:
            hrv_data_ms = hrv_data * 1000
            self.ui.plot_widget_03.plot(peak_times[:-1], hrv_data_ms, pen='w')

        # self.ui.stats_data_label.setText(summary_text)
        self.logger.info(f"HRV Analysis returned. Keys: {summary_dict.keys()}")
        
        # Store for simulation updates
        self.full_summary_dict = summary_dict
        self.full_summary_text = summary_text
        self.full_peak_times = peak_times
        self.full_hrv_data = hrv_data
        self.full_filtered_data = filtered_y_data
        
        # Populate Stats Cards
        self.update_plots_static() # This calls the stats update logic we added earlier
        
        self.enable_sim_controls(True)

    def plot_HRV_data(self, x_data, y_data):
        # Legacy method replaced by start_hrv_analysis
        pass

    def run(self):
        """Run the application."""
        self.MainWindow.showFullScreen()
        self.app.exec_()

    def upload_data(self, file_path):
        """
        Returns:
            time (array): Time values.
            fhr (array): Fetal Heart Rate values.
            uc (array): Uterine Contraction values.
        """
        try:
            # Read CSV file
            data = pd.read_csv(file_path)
            time = data['Time'].values
            fhr = data['FHR'].values
            uc = data['UC'].values

            return time, fhr, uc
            return time, fhr, uc
        except Exception as e:
            self.show_error(f"Error loading file: {e}")
            return None, None, None

    def plot_fhr_and_uc(self, time, fhr, uc):
        """
        Plot Baseline FHR and UC in two separate PlotWidgets.

        Parameters:
            time (array): Time values.
            fhr (array): Fetal Heart Rate values.
            uc (array): Uterine Contraction values.
        """
        # Calculate the baseline FHR using Savitzky-Golay filter
        processed_fhr = savgol_filter(fhr, window_length=15, polyorder=2)  # Adjust window_length as needed

        baseline_fhr = np.mean(processed_fhr)
        baseline_fhr_array = np.full_like(time, baseline_fhr)

        # Plot Baseline FHR (smoothed FHR)

        self.ui.plot_widget_01.plot(time, processed_fhr, pen={'color': 'white', 'width': 2}, name="Processed FHR")
        self.ui.plot_widget_01.plot(time, baseline_fhr_array, pen={'color': 'red', 'width': 2}, name="Baseline FHR")

        # Green line for FHR
        self.ui.plot_widget_03.plot(time, uc, pen='w')  # Blue line for UC

    def plot_stv(self, time, fhr):
        """
        Plot Short-Term Variability (STV).

        Parameters:
            time (array): Time values.
            fhr (array): Fetal Heart Rate values.
            graph_widget2: PyQtGraph widget for plotting.
        """

        stv = np.abs(np.diff(fhr))  # Difference between consecutive FHR values

        time_stv = time[1:]  # Shorten time array to match STV length

        # Plot STV
        self.ui.plot_widget_02.plot(time_stv, stv, title="Short-Term Variability (STV)")

    def plot_accel_decel(self, time, fhr, fs=4, current_time=None):
        # Allow plotting subset if current_time is specified
        
        # If we haven't pre-calculated (static mode or first load), do it now
        if not hasattr(self, 'full_accel_points'):
             self.full_accel_points, self.full_decel_points = self.identify_accel_decel(fhr, fs)
        
        accel_indices = self.full_accel_points
        decel_indices = self.full_decel_points

        # Filter if simulation
        if current_time is not None:
             # Assuming indices correspond to time array roughly if time is linear
             # If time is provided, we can map time to index or check time values
             # But here we have indices.
             # Convert current_time to index? 
             # Simpler: 'time' array is passed. 
             # We just need to filter indices that are within the current time scope
             # But wait, plot takes x,y.
             pass
             
        # Plot FHR as a thin line (Background for markers)
        # self.ui.plot_widget_04.plot(time, fhr, pen={'color': 'w', 'width': 1}) # Already plotted in update_sim usually? 
        # In static mode, yes. In sim mode, we plot line separately. 
        # Let's assume this function handles markers mainly.
        # But legacy call included line. Let's keep line for static.
        
        limit_idx = len(time)
        if current_time is not None:
             # Find limit for simulation using searchsorted
             limit_idx = np.searchsorted(time, current_time)

        # Plot FHR trace (Background)
        # Even if limit_idx is small, we plot what we have
        if limit_idx > 0:
             self.ui.plot_widget_04.plot(time[:limit_idx], fhr[:limit_idx], pen={'color': 'w', 'width': 1})

        # Highlight accelerations in green
        if len(accel_indices) > 0:
            valid_accel = accel_indices
            if current_time is not None:
                 valid_accel = [i for i in accel_indices if i < limit_idx]
            
            if len(valid_accel) > 0:
                 # Ensure indices are within bounds
                 valid_accel = [i for i in valid_accel if i < limit_idx and i < len(time)]
                 if len(valid_accel) > 0:
                    self.ui.plot_widget_04.plot(time[valid_accel], fhr[valid_accel],
                                            pen=None, symbol='o', symbolBrush='g', symbolSize=8, name="Accel")

        # Highlight decelerations in red
        if len(decel_indices) > 0:
            valid_decel = decel_indices
            if current_time is not None:
                 valid_decel = [i for i in decel_indices if i < limit_idx]

            if len(valid_decel) > 0:
                 valid_decel = [i for i in valid_decel if i < limit_idx and i < len(time)]
                 if len(valid_decel) > 0:
                    self.ui.plot_widget_04.plot(time[valid_decel], fhr[valid_decel],
                                            pen=None, symbol='o', symbolBrush='r', symbolSize=8, name="Decel")

    def identify_accel_decel(self, fhr, fs): # Added fs argument
        accel_indices = []
        decel_indices = []
        
        config = Config().CLINICAL_THRESHOLDS
        accel_bpm = config.get("ACCEL_BPM", 15)
        accel_dur_sec = config.get("ACCEL_SEC", 15)
        decel_bpm = config.get("DECEL_BPM", 15)
        decel_dur_sec = config.get("DECEL_SEC", 15)

        # Convert duration to samples
        accel_samples = int(accel_dur_sec * fs) # FHR fs is usually low (4Hz), make sure we handle this
        decel_samples = int(decel_dur_sec * fs)
        
        # Smooth FHR slightly to remove noise for detection
        smoothed_fhr = savgol_filter(fhr, window_length=15, polyorder=2) # Keep original smoothing for baseline estimation purposes or simple noise reduction
        
        # Simple threshold logic:
        # A rise of >15 bpm for >15 secs. 
        # This is strictly hard to detect with simple diff. 
        # We need to detect sustained change.
        
        # Better approach: Compare window mean with baseline.
        # But baseline varies. 
        # Let's use the rolling baseline logic already somewhat present or improved.
        
        baseline = np.median(fhr) # Simple baseline for now or use the savgol smoothed one as moving baseline
        # FIGO says baseline is average over 10 min. 
        # For simplicity in this logic fix, we check sustained deviation from a local baseline.
        
        # Logic: 
        # 1. Find segments where FHR > baseline + 15
        # 2. Check if duration > 15s
        
        is_accel = fhr > (baseline + accel_bpm)
        is_decel = fhr < (baseline - decel_bpm)
        
        # Find continuous regions
        def get_continuous_regions(bool_array, min_samples):
            regions = []
            start = None
            for i, val in enumerate(bool_array):
                if val and start is None:
                    start = i
                elif not val and start is not None:
                    if (i - start) >= min_samples:
                        regions.append((start, i))
                    start = None
            if start is not None and (len(bool_array) - start) >= min_samples:
                 regions.append((start, len(bool_array)))
            return regions
            
        accel_regions = get_continuous_regions(is_accel, accel_samples)
        decel_regions = get_continuous_regions(is_decel, decel_samples)

        # Return indices for plotting (e.g., center of event) or all points
        # The previous code returned a list of points. Let's return all points in events for highlighting.
        
        accel_points = []
        for start, end in accel_regions:
            accel_points.extend(range(start, end))
            
        decel_points = []
        for start, end in decel_regions:
            decel_points.extend(range(start, end))

        return accel_points, decel_points
