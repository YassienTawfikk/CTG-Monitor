import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore

# Define style variables
# Define style variables
MAIN_WINDOW_STYLE = "background-color:#1e1e1e;" # Slightly lighter dark for modern feel
BUTTON_STYLE = ("QPushButton {"
                "    color: white;"
                "    background-color: #2c3e50;"
                "    border: 2px solid #34495e;"
                "    border-radius: 8px;"
                "    padding: 8px;"
                "    font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "    background-color: #34495e;"
                "    border-color: #5d6d7e;"
                "}"
                "QPushButton:pressed {"
                "    background-color: #1a252f;"
                "}")

QUIT_BUTTON_STYLE = ("QPushButton {"
                     "    color: #e74c3c;"
                     "    background-color: transparent;"
                     "    border: 2px solid #e74c3c;"
                     "    border-radius: 25px;"
                     "    font-weight: bold;"
                     "}"
                     "QPushButton:hover {"
                     "    background-color: #e74c3c;"
                     "    color: white;"
                     "}")

LABEL_STYLE = "color:#ecf0f1; font-weight: bold;"
GROUP_BOX_STYLE = ("QGroupBox { "
                   "    color: #ecf0f1; "
                   "    border: 1px solid #7f8c8d; "
                   "    border-radius: 5px;"
                   "    margin-top: 20px; "
                   "    font-weight: bold;"
                   "} "
                   "QGroupBox::title { "
                   "    subcontrol-origin: margin; "
                   "    subcontrol-position: top left; "
                   "    padding: 0 5px; "
                   "    left: 10px;"
                   "}")

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        """Set up the UI components using dynamic layouts."""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 800)
        font = QtGui.QFont()
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(MAIN_WINDOW_STYLE)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Main vertical layout
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Top Header Layout
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(15)
        
        # --- Title Section ---
        title_icon = QtWidgets.QLabel()
        title_icon.setMaximumSize(QtCore.QSize(50, 50))
        title_icon.setPixmap(QtGui.QPixmap("static/images/heart_title_icon.png"))
        title_icon.setScaledContents(True)
        self.header_layout.addWidget(title_icon)

        self.title_label = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(LABEL_STYLE)
        self.title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.title_label.setText("BioRhythm Analyzer")
        self.header_layout.addWidget(self.title_label)
        
        # Spacer to push controls to the right
        self.header_layout.addStretch()
        
        # --- Control Section ---
        self.mode_button = self.addButton("mode_button", "Mode: HRV", BUTTON_STYLE)
        self.upload_signal_button = self.addButton("upload_signal_button", "Upload Signal", BUTTON_STYLE)
        
        # FS Input
        self.fs_input = QtWidgets.QSpinBox()
        self.fs_input.setRange(1, 10000)
        self.fs_input.setValue(500)
        self.fs_input.setSuffix(" Hz")
        self.fs_input.setPrefix("FS: ")
        
        # SpinBox Styling with Arrows
        SPINBOX_STYLE = ("QSpinBox {"
                         "    color: white;"
                         "    background-color: #2c3e50;"
                         "    border: 2px solid #34495e;"
                         "    border-radius: 5px;"
                         "    padding: 5px;"
                         "    font-weight: bold;"
                         "}"
                         "QSpinBox::up-button {"
                         "    subcontrol-origin: border;"
                         "    subcontrol-position: top right;"
                         "    width: 20px;"
                         "    border-left: 1px solid #34495e;"
                         "    border-bottom: 1px solid #34495e;"
                         "    border-top-right-radius: 5px;"
                         "    background-color: #2c3e50;"
                         "}"
                         "QSpinBox::down-button {"
                         "    subcontrol-origin: border;"
                         "    subcontrol-position: bottom right;"
                         "    width: 20px;"
                         "    border-left: 1px solid #34495e;"
                         "    border-top: 1px solid #34495e;"
                         "    border-bottom-right-radius: 5px;"
                         "    background-color: #2c3e50;"
                         "}"
                         "QSpinBox::up-button:hover, QSpinBox::down-button:hover {"
                         "    background-color: #34495e;"
                         "}"
                         "QSpinBox::up-arrow {"
                         "    image: url(static/images/arrow_up.png);"
                         "    width: 10px; height: 10px;"
                         "}"
                         "QSpinBox::down-arrow {"
                         "    image: url(static/images/arrow_down.png);"
                         "    width: 10px; height: 10px;"
                         "}")
                         
        self.fs_input.setStyleSheet(SPINBOX_STYLE)
        self.fs_input.setMinimumHeight(40)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.fs_input.setFont(font)
        
        self.header_layout.addWidget(self.mode_button)
        self.header_layout.addWidget(self.upload_signal_button)
        self.header_layout.addWidget(self.fs_input)
        
        # --- Simulation Controls ---
        self.sim_controls_layout = QtWidgets.QHBoxLayout()
        self.sim_controls_layout.setSpacing(10)
        
        # Combined Play/Pause Button
        self.play_pause_button = self.addButton("play_pause_button", "▶", BUTTON_STYLE)
        self.play_pause_button.setFixedWidth(50)
        self.play_pause_button.setEnabled(False)
        self.play_pause_button.setToolTip("Play/Pause Simulation")
        
        self.stop_button = self.addButton("stop_button", "⏹", BUTTON_STYLE)
        self.stop_button.setFixedWidth(50)
        self.stop_button.setEnabled(False) 
        self.stop_button.setToolTip("Stop Simulation")
        
        # Segmented Control for Speed
        self.speed_controls_layout = QtWidgets.QHBoxLayout()
        self.speed_controls_layout.setSpacing(0) # Connected buttons
        
        self.speed_button_group = QtWidgets.QButtonGroup(MainWindow)
        self.speed_button_group.setExclusive(True)
        
        speeds = ["10x", "20x", "50x", "100x"]
        self.speed_buttons = {}
        
        SEGMENT_BTN_STYLE = ("QPushButton {"
                             "    color: white;"
                             "    background-color: #2c3e50;"
                             "    border: 2px solid #34495e;"
                             "    padding: 5px 10px;"
                             "    font-weight: bold;"
                             "}"
                             "QPushButton:checked {"
                             "    background-color: #3498db;"
                             "    border-color: #3498db;"
                             "}"
                             "QPushButton:hover {"
                             "    background-color: #34495e;"
                             "}"
                             "QPushButton:first {"
                             "    border-top-left-radius: 8px;"
                             "    border-bottom-left-radius: 8px;"
                             "}"
                             "QPushButton:last {"
                             "    border-top-right-radius: 8px;"
                             "    border-bottom-right-radius: 8px;"
                             "}")

        for i, spd in enumerate(speeds):
            btn = QtWidgets.QPushButton(spd)
            btn.setCheckable(True)
            btn.setFixedWidth(100) # Fixed width to prevent resizing on text change
            btn.setStyleSheet(SEGMENT_BTN_STYLE)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            if i == 0:
                btn.setChecked(True)
            
            self.speed_button_group.addButton(btn, i) # Id matches index
            self.speed_controls_layout.addWidget(btn)
            self.speed_buttons[spd] = btn # keep ref just in case

        self.sim_controls_layout.addWidget(self.play_pause_button)
        self.sim_controls_layout.addWidget(self.stop_button)
        self.sim_controls_layout.addLayout(self.speed_controls_layout)
        
        self.header_layout.addLayout(self.sim_controls_layout)
        
        self.quit_app_button = self.addButton("quit_app_button", "X", QUIT_BUTTON_STYLE, True)
        self.quit_app_button.setFixedSize(50, 50)
        self.header_layout.addWidget(self.quit_app_button)

        self.main_layout.addLayout(self.header_layout)

        # Content Grid Layout
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setSpacing(10)
        
        # Define group boxes with graphs
        self.graph01_groupBox, self.plot_widget_01 = self.addGroupBox("graph01_groupBox", "Raw Signal", True)
        self.graph02_groupBox, self.plot_widget_02 = self.addGroupBox("graph02_groupBox", "Filtered Signal", True)
        self.graph03_groupBox, self.plot_widget_03 = self.addGroupBox("graph03_groupBox", "HRV Metrics", True)
        
        # Graph 4 / Alert Box share the same spot
        self.graph04_groupBox, self.plot_widget_04 = self.addGroupBox("graph04_groupBox", "Acceleration/Deceleration", True)
        
        # Stats Group Box with Grid Layout for Cards
        self.alert_messages_groupBox = QtWidgets.QGroupBox()
        self.alert_messages_groupBox.setObjectName("stats_groupBox")
        self.alert_messages_groupBox.setStyleSheet(GROUP_BOX_STYLE)
        self.alert_messages_groupBox.setTitle("Analysis Stats")
        
        self.stats_layout = QtWidgets.QGridLayout(self.alert_messages_groupBox)
        self.stats_layout.setContentsMargins(10, 20, 10, 10)
        self.stats_layout.setSpacing(10)
        
        # We will populate this grid dynamically or set up static cards
        # Let's create placeholders for common metrics
        self.metric_widgets = {} 
        # Structure: key/ID -> Display Title
        self.metrics_info = {
            "bpm": "BPM",
            "mean_rr": "RR Mean (ms)",
            "sdnn": "SDNN (ms)",
            "rmssd": "RMSSD (ms)",
            "pnn50": "pNN50 (%)"
        }
        
        # We want a specific order for the grid
        ordered_keys = ["bpm", "mean_rr", "sdnn", "rmssd", "pnn50"]
        
        for i, key in enumerate(ordered_keys):
            title = self.metrics_info[key]
            # Pass key as the ID for internal object name
            card = self.create_metric_card(title, "-", key) 
            self.metric_widgets[key] = card
            self.stats_layout.addWidget(card, i // 2, i % 2)
            
        # Add to main grid
        # Row 0
        self.grid_layout.addWidget(self.graph01_groupBox, 0, 0)
        self.grid_layout.addWidget(self.graph02_groupBox, 0, 1)
        # Row 1
        self.grid_layout.addWidget(self.graph03_groupBox, 1, 0)
        self.grid_layout.addWidget(self.graph04_groupBox, 1, 1)
        self.grid_layout.addWidget(self.alert_messages_groupBox, 1, 1) # Stacked
        
        # Set row and column stretch to ensure equal sizing/resizing
        self.grid_layout.setRowStretch(0, 1)
        self.grid_layout.setRowStretch(1, 1)
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)

        self.main_layout.addLayout(self.grid_layout)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Initial State
        self.is_current_mode_HRV = True
        self.toggle_mode_design() # Set proper visibility

    def addButton(self, object_name, text, style, is_bold=False):
        button = QtWidgets.QPushButton()
        button.setMinimumHeight(40)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(is_bold)
        button.setFont(font)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet(style)
        button.setText(text)
        button.setObjectName(object_name)
        button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        return button

    def create_metric_card(self, title, value, key_id):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("background-color: #2c3e50; border-radius: 8px; border: 1px solid #34495e;")
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setStyleSheet("color: #bdc3c7; font-size: 10pt; background: transparent; border: none;")
        lbl_title.setAlignment(QtCore.Qt.AlignCenter)
        
        lbl_value = QtWidgets.QLabel(value)
        # Use simple ID for object name
        lbl_value.setObjectName(f"val_{key_id}")
        lbl_value.setStyleSheet("color: #2ecc71; font-size: 16pt; font-weight: bold; background: transparent; border: none;")
        lbl_value.setAlignment(QtCore.Qt.AlignCenter)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        return frame

    def addGroupBox(self, object_name, title, isGraph=False):
        group_box = QtWidgets.QGroupBox()
        font = QtGui.QFont()
        group_box.setFont(font)
        group_box.setStyleSheet(GROUP_BOX_STYLE)
        group_box.setTitle(title)
        group_box.setObjectName(object_name)
        
        group_layout = QtWidgets.QVBoxLayout(group_box)
        group_layout.setContentsMargins(5, 15, 5, 5)

        widget = None

        if isGraph:
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground(None) # Transparent
            plot_widget.getPlotItem().getAxis('bottom').setPen('w')
            plot_widget.getPlotItem().getAxis('left').setPen('w')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            group_layout.addWidget(plot_widget)
            widget = plot_widget
        else:
             # Just return layout container for custom widgets
             pass

        return group_box, widget

    # --------------------------------------------------------------------------------------------------------------------------------------

    def toggle_mode_design(self):
        self.is_current_mode_HRV = not self.is_current_mode_HRV
        self.toggle_groupBox04()
        self.adjust_titles()

    def clear_all_plots(self):
        self.plot_widget_01.clear()
        self.plot_widget_02.clear()
        self.plot_widget_03.clear()
        self.plot_widget_04.clear()
        # Reset cards
        for m, widget in self.metric_widgets.items():
             val_label = widget.findChild(QtWidgets.QLabel, f"val_{m}")
             if val_label: val_label.setText("-")

    def adjust_titles(self):
        if self.is_current_mode_HRV:
            self.mode_button.setText("Mode: HRV")
            self.graph01_groupBox.setTitle("Raw Signal")
            self.graph02_groupBox.setTitle("Filtered Signal")
            self.graph03_groupBox.setTitle("HRV Metrics")
        else:
            self.mode_button.setText("Mode: FHR")
            self.graph01_groupBox.setTitle("Baseline FHR")
            self.graph02_groupBox.setTitle("STV")
            self.graph03_groupBox.setTitle("Uterine Contraction")

    def toggle_groupBox04(self):
        if self.is_current_mode_HRV:
            self.alert_messages_groupBox.show()
            self.graph04_groupBox.hide()
            self.plot_widget_04.hide()
        else:
            self.alert_messages_groupBox.hide()
            self.graph04_groupBox.show()
            self.plot_widget_04.show()
