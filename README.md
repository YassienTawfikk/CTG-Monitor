# BioRhythm Analyzer

![Overview](https://github.com/user-attachments/assets/da79273a-23d4-41ff-818c-d32d171b76af)

**A Comprehensive ECG & CTG Monitoring System**

BioRhythm Analyzer is a sophisticated biomedical application designed for the real-time analysis and visualization of cardiac signals. It supports both Adult Heart Rate Variability (HRV) analysis from ECG signals and Fetal Heart Rate (FHR) monitoring from Cardiotocography (CTG) data.

The system combines advanced signal processing algorithms with an intuitive, medically-oriented user interface to assist healthcare professionals and researchers in detecting potential cardiac abnormalities.

---

## Key Features

<https://github.com/user-attachments/assets/bc54996a-2a32-4933-bb69-18c26dfe5d60>

### 1. Dual Analysis Modes

- **HRV Mode (ECG)**: Focuses on adult cardiac health, analyzing R-R intervals to derive Time-Domain metrics.
- **FHR Mode (CTG)**: Dedicated to fetal monitoring, correlates Fetal Heart Rate with Uterine Contractions (UC) to assess fetal well-being.

![HRV Analysis Screenshot](https://github.com/user-attachments/assets/544edf40-6a7d-47d0-bb8c-b5ac885a3d08)

### 2. Advanced Signal Processing

- **Noise Reduction**: Implements configurable Butterworth bandpass filtering to isolate relevant frequency bands (default 1-50Hz).
- **QRS Detection**: Uses a robust modified **Pan-Tompkins Algorithm** for accurate R-peak detection even in noisy signals.

### 3. Intelligent Visual Aids

![FHR Analysis Screenshot](https://github.com/user-attachments/assets/5b956073-395a-48cc-8718-72fd3da12e73)

- **Event Highlighting**: Automatically detects and highlights clinical events on the charts.
  - **Green Shaded Regions**: periods of FHR Acceleration.
  - **Red Shaded Regions**: periods of FHR Deceleration.
- **Dynamic Plots**: Real-time scrolling graphs with auto-scaling axes.

### 4. Real-time Simulation

- Replays static CSV datasets as live signals.
- **Playback Controls**: Play, Pause, and Adjustable Speed (1x, 10x, 20x, 50x, 100x).

---

## Technical Architecture

### Signal Processing Pipeline

The application follows a strict pipeline to ensure data integrity and clinical accuracy:

1. **Data Ingestion**:
    - Auto-detection of CSV columns (`Time`, `ECG`, `FHR`, `UC`).
    - Automatic Sampling Frequency (FS) calculation based on time timestamps.
2. **Pre-processing**:
    - **Filter**: `scipy.signal.butter` (Bandpass).
    - **Smooting**: Savitzky-Golay filter applied to FHR for baseline estimation.
3. **Analysis**:
    - **HRV**:
        - *SDNN*: Standard Deviation of NN intervals.
        - *RMSSD*: Root Mean Square of Successive Differences.
        - *pNN50*: Percentage of successive RR intervals > 50ms.
    - **FHR**:
        - *Baseline*: Median FHR over a moving window.
        - *STV*: Short-Term Variability (epoch-to-epoch differences).
        - *Accel/Decel*: Logic-based detection of sustained deviations from baseline.

### Configuration (`app/config.py`)

The application is highly configurable via `app/config.py`. Key parameters include:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| **FS** | 500 Hz | Default sampling frequency if not detected. |
| **FILTER** | 1-50 Hz | Bandpass filter range for ECG. |
| **ACCEL_BPM** | 15 (Configurable) | BPM increase required for Acceleration. |
| **ACCEL_SEC** | 15s | Duration required for Acceleration. |
| **DECEL_BPM** | 15 | BPM decrease trigger for Deceleration. |

> **Note on Tuning**: For low-amplitude simulated datasets, thresholds can be lowered (e.g., to 5 BPM) in `app/config.py` to ensure events are visually detected.

---

## Installation & Usage

### Prerequisites

- Python 3.8+
- Virtual Environment (recommended)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/YassienTawfikk/CTG-Monitor.git
   cd CTG-Monitor
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**

   ```bash
   python main.py
   ```

---

## User Interface

### HRV Dashboard

<img width="400" alt="HRV Dashboard Screenshot" src="https://github.com/user-attachments/assets/2d87cbc5-8ddd-48b5-b1ba-9efcf80efc41" />

- **Top Row**: Raw Signal vs Filtered Signal.
- **Metrics**: Real-time calculation of Mean RR, SDNN, RMSSD.
- **Histograms**: Visual distribution of RR intervals to spot outliers.

### FHR Dashboard

- **Main Trace**: Time-synchronized FHR (top) and Uterine Contraction (bottom) plots.
- **Visual Cues**:
  - **Green Bands**: Accelerations (Sign of fetal well-being).
  - **Red Bands**: Decelerations (Potential distress).

---

## Contributors

<div align="center">
   <table>
     <tr>
       <td align="center">
         <a href="https://github.com/YassienTawfikk" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/126521373?v=4" width="100px;" alt="Yassien Tawfik"/>
           <br />
           <sub><b>Yassien Tawfik</b></sub>
         </a>
       </td>
       <td align="center">
         <a href="https://github.com/Mazenmarwan023" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/127551364?v=4" width="100px;" alt="Mazen Marwan"/>
           <br />
           <sub><b>Mazen Marwan</b></sub>
         </a>
       </td>
       <td align="center">
         <a href="https://github.com/madonna-mosaad" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/127048836?v=4" width="100px;" alt="Madonna Mosaad"/>
           <br />
           <sub><b>Madonna Mosaad</b></sub>
         </a>
       </td>
       <td align="center">
         <a href="https://github.com/nancymahmoud1" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/125357872?v=4" width="100px;" alt="Nancy Mahmoud"/>
           <br />
           <sub><b>Nancy Mahmoud</b></sub>
         </a>
       </td>
     </tr>
   </table>
</div>
