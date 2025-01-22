# BioRhythm Analyzer

A **CTG Heart Failure Monitoring System** that processes Heart Rate Variability (HRV) and Fetal Heart Rate (FHR) signals to detect potential abnormalities. This project combines advanced signal processing with an intuitive graphical interface for healthcare professionals.

---

## Demo Video

<video src="https://github.com/user-attachments/assets/81f050d4-e398-4a57-8f2a-261e20b89963" controls="controls" style="max-width: 100%;"></video>

---

## HRV Analysis

<img width="1280" alt="Screen Shot 2024-12-20 at 2 01 11 AM" src="https://github.com/user-attachments/assets/6c8a327b-7ff4-43be-8d97-aa36962327a5" />

- **Raw Signal:** Displays the original input signal for analysis.  
- **Filtered Signal:** Shows the cleaned, processed signal using advanced filtering techniques.  
- **HRV Metrics:** Visualizes key parameters such as SDNN, RMSSD, and pNN50 for heart rate variability analysis.  
- **Stats Section:** Includes detailed insights like mean RR intervals, outliers, histograms, and more.

---

## FHR Analysis

<img width="1280" alt="Screen Shot 2024-12-20 at 2 01 24 AM" src="https://github.com/user-attachments/assets/6bd46dc6-fd48-4a2b-97da-89b56c0a47e7" />

- **Baseline FHR:** Tracks the average fetal heart rate over time.  
- **Uterine Contraction:** Monitors the correlation between uterine contractions and FHR patterns.  
- **Short-Term Variability (STV):** Highlights rapid changes in FHR.  
- **Acceleration/Deceleration:** Detects anomalies with color-coded markers (green = normal, red = critical).

---

## Installation

1. Clone the repository and navigate to the folder:  
   ```bash
   git clone https://github.com/your-username/biorhythm-analyzer.git  
   cd biorhythm-analyzer
   ```
2. Install the dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:  
   ```bash
   python main.py
   ```

---

## Contributors

<div align="center">
   <table>
     <tr>
           <td align="center">
         <a href="https://github.com/YassienTawfikk" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/126521373?v=4" width="150px;" alt="Yassien Tawfik"/>
           <br />
           <sub><b>Yassien Tawfik</b></sub>
         </a>
       </td>
       <td align="center">
         <a href="https://github.com/Mazenmarwan023" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/127551364?v=4" width="150px;" alt="Madonna Mosaad"/>
           <br />
           <sub><b>Mazen Marwan</b></sub>
         </a>
       </td>     
       <td align="center">
         <a href="https://github.com/madonna-mosaad" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/127048836?v=4" width="150px;" alt="Madonna Mosaad"/>
           <br />
           <sub><b>Madonna Mosaad</b></sub>
         </a>
       </td>
           <td align="center">
         <a href="https://github.com/nancymahmoud1" target="_blank">
           <img src="https://avatars.githubusercontent.com/u/125357872?v=4" width="150px;" alt="Nancy Mahmoud"/>
           <br />
           <sub><b>Nancy Mahmoud</b></sub>
         </a>
       </td>
     </tr>
   </table>
</div>
