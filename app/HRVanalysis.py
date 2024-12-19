import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


class HRV_analysis:
    def __init__(self, data, fs=500):
        self.data = data
        self.fs = fs  # Sampling frequency
        self.filtered_data = None
        self.rr_intervals = None
        self.peaks = None

    def apply_filter(self, lowcut=1, highcut=50, order=5):
        """Apply a Butterworth band-pass filter to the ECG data and store it."""
        nyq = 0.5 * self.fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        self.filtered_data = filtfilt(b, a, self.data)
        return self.filtered_data

    def calculate_hrv(self):
        """Calculate HRV by detecting R-peaks and returning RR intervals in seconds."""
        if self.filtered_data is None:
            raise ValueError("Filtered data is not available. Please apply filter first.")

        self.peaks, _ = find_peaks(self.filtered_data, height=np.mean(self.filtered_data))
        self.rr_intervals = np.diff(self.peaks) / self.fs

        return self.rr_intervals

    def get_peak_times(self):
        """Return the times corresponding to detected R-peaks for plotting purposes."""
        if self.peaks is None:
            raise ValueError("Peaks data not available. Please calculate HRV first.")
        return self.peaks / self.fs  # Convert peak indices to times

    def calculate_mean_rr(self):
        """Calculate the mean RR interval."""
        return np.mean(self.rr_intervals)

    def calculate_sdnn(self):
        """Calculate the standard deviation of RR intervals (SDNN)."""
        return np.std(self.rr_intervals)

    def calculate_rmssd(self):
        """Calculate the root mean square of successive differences (RMSSD)."""
        successive_diff = np.diff(self.rr_intervals)
        return np.sqrt(np.mean(successive_diff ** 2))

    def calculate_pnn50(self):
        """Calculate the percentage of RR intervals differing by more than 50 ms."""
        diff_rr = np.abs(np.diff(self.rr_intervals)) * 1_000  # Convert to ms
        count_pnn50 = np.sum(diff_rr > 50)  # Count RR differences > 50 ms
        return (count_pnn50 / len(self.rr_intervals)) * 100

    def calculate_min_max_range(self):
        """Calculate the min, max, and range of RR intervals."""
        min_rr = np.min(self.rr_intervals)
        max_rr = np.max(self.rr_intervals)
        range_rr = max_rr - min_rr
        return min_rr, max_rr, range_rr

    def calculate_histogram(self, bins=10):
        """Calculate the histogram of RR intervals."""
        hist, bin_edges = np.histogram(self.rr_intervals, bins=bins)
        return hist, bin_edges

    def detect_outliers(self, threshold=3):
        """Detect outliers using the Z-score method."""
        z_scores = np.abs((self.rr_intervals - np.mean(self.rr_intervals)) / np.std(self.rr_intervals))
        outliers = self.rr_intervals[z_scores > threshold]
        return outliers

    def summarize_hrv(self):
        """Return a dictionary summarizing all HRV parameters."""
        if self.rr_intervals is None:
            raise ValueError("RR intervals are not available. Please calculate HRV first.")

        summary = {
            "Mean RR Interval (ms)": round(self.calculate_mean_rr() * 10_000, 2),  # Scale to ms and round
            "SDNN (ms)": round(self.calculate_sdnn() * 1_000, 2),  # Scale to ms and round
            "RMSSD (ms)": round(self.calculate_rmssd() * 1_000, 2),  # Scale to ms and round
            "pNN50 (%)": round(self.calculate_pnn50(), 2),  # Round percentage
            "Min RR Interval (ms)": round(self.calculate_min_max_range()[0] * 1_000),  # Scale and round
            "Max RR Interval (ms)": round(self.calculate_min_max_range()[1] * 1_000),  # Scale and round
            "Range RR Interval (ms)": round(self.calculate_min_max_range()[2] * 1_000),  # Scale and round
            "Outliers (ms)": [round(x * 1_000) for x in self.detect_outliers()],  # Scale outliers and round
            "Histogram": (
                self.calculate_histogram()[0].tolist(),  # Convert array to list for counts
                [round(edge * 1_000) for edge in self.calculate_histogram()[1]]  # Scale and round edges
            )
        }
        '''   '''
        # Dynamically format the summary into an aligned string
        current_stats = f"""
        {"Mean RR Interval (ms):":<30}         {summary['Mean RR Interval (ms)']}
        
        {"SDNN (ms):":<30}                {summary['SDNN (ms)']}
        {"RMSSD (ms):":<30}               {summary['RMSSD (ms)']}
        {"pNN50 (%):":<30}                {summary['pNN50 (%)']}
        
        {"Min RR Interval (ms):":<30}            {summary['Min RR Interval (ms)']}
        {"Max RR Interval (ms):":<30}           {summary['Max RR Interval (ms)']}
        {"Range RR Interval (ms):":<30}         {summary['Range RR Interval (ms)']}
        
        {"Outliers (ms):":<30}                 {summary['Outliers (ms)']}
        
        {"Histogram:":<30}                  {summary['Histogram'][0]}
        {" ":<30}                           {summary['Histogram'][1]}
        """

        return summary, current_stats
