import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
import numpy as np
from scipy.signal import savgol_filter

from app.ui.Design import Ui_MainWindow
from app.HRVanalysis import HRV_analysis


class MainController:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

        # Connect signals to slots
        self.setupConnections()

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
        self.ui.toggle_mode_design()

    def upload_signal(self):
        """Open a file dialog to select a signal file and initiate loading."""

        filepath, _ = QFileDialog.getOpenFileName(self.MainWindow, "Open Signal File", "/", "CSV Files (*.csv);;All Files (*)")
        if filepath:

            if self.ui.is_current_mode_HRV:  # Check if HRV mode is activated
                self.load_data_from_file(filepath)

            else:
                time, fhr, uc = self.upload_data(filepath)

                if time is not None:
                    self.ui.clear_all_plots()

                    # Plot Graph 1 & Graph 3: FHR and UC
                    self.plot_fhr_and_uc(time, fhr, uc)

                    # Plot Graph 2: STV
                    self.plot_stv(time, fhr)

                    # Plot Graph 4: Accelerations and Decelerations
                    self.plot_accel_decel(time, fhr)

    def load_data_from_file(self, filepath):
        """Load data from a given CSV file using Pandas with error handling."""
        try:
            # Load data using Pandas, which automatically handles malformed files more gracefully
            data = pd.read_csv(filepath)
            x_data = data.iloc[:, 0].tolist()  # Assuming the first column contains x-data
            y_data = data.iloc[:, 1].tolist()  # Assuming the second column contains y-data
            self.plot_data(x_data, y_data)
        except pd.errors.EmptyDataError:
            print("No data: The file is empty.")
        except pd.errors.ParserError:
            print("Error parsing data: Check the file format.")
        except FileNotFoundError:
            print(f"File not found: {filepath}")
        except Exception as e:
            print(f"Failed to read or parse the CSV file: {e}")

    def plot_data(self, x_data, y_data):
        """Plot the data on plot_widget_01 with error handling."""
        try:
            self.ui.plot_widget_01.clear()
            self.ui.plot_widget_01.plot(x_data, y_data, pen='w')  # Plot raw ECG data with white pen

            if self.ui.is_current_mode_HRV:  # Check if HRV mode is activated
                self.plot_HRV_data(x_data, y_data)
        except Exception as e:
            print(f"Failed to plot data: {e}")

    def plot_HRV_data(self, x_data, y_data):
        self.filter = HRV_analysis(y_data)  # Initialize filtering with ECG data

        filtered_y_data = self.filter.apply_filter()  # Filter the ECG data
        self.ui.plot_widget_02.clear()
        self.ui.plot_widget_02.plot(x_data, filtered_y_data, pen='w')  # Plot filtered ECG data

        hrv_data = self.filter.calculate_hrv()  # Calculate HRV data
        peak_times = self.filter.get_peak_times()  # Get the peak times corresponding to HRV data

        self.ui.plot_widget_03.clear()
        if len(hrv_data) > 1:
            hrv_data_ms = hrv_data * 1000

            self.ui.plot_widget_03.plot(peak_times[:-1], hrv_data_ms, pen='w')

        _, hrv_summary = self.filter.summarize_hrv()
        self.ui.stats_data_label.setText(hrv_summary)

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
        except Exception as e:
            print("Error loading file:", e)
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

    def plot_accel_decel(self, time, fhr):
        # Identify accelerations and decelerations
        accel_indices, decel_indices = self.identify_accel_decel(fhr)

        # Plot FHR as a thin line
        self.ui.plot_widget_04.plot(time, fhr, pen={'color': 'w', 'width': 1})

        # Highlight accelerations in green
        if accel_indices:
            self.ui.plot_widget_04.plot(time[accel_indices], fhr[accel_indices],
                                        pen=None, symbol='o', symbolBrush='g', symbolSize=6)

        # Highlight decelerations in red
        if decel_indices:
            self.ui.plot_widget_04.plot(time[decel_indices], fhr[decel_indices],
                                        pen=None, symbol='o', symbolBrush='r', symbolSize=6)

    def identify_accel_decel(self, fhr, threshold=0.1, duration=3):
        accel_indices = []
        decel_indices = []

        # Smooth FHR using a rolling average to remove small noise
        smoothed_fhr = np.convolve(fhr, np.ones(duration) / duration, mode='valid')

        for i in range(len(smoothed_fhr) - duration):
            change = smoothed_fhr[i + duration] - smoothed_fhr[i]
            if change >= threshold:  # Significant increase (acceleration)
                accel_indices.append(i + duration // 2)  # Center of the window
            elif change <= -threshold:  # Significant decrease (deceleration)
                decel_indices.append(i + duration // 2)

        return accel_indices, decel_indices
