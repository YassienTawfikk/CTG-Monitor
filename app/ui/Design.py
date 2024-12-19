import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore

# Define style variables
MAIN_WINDOW_STYLE = "background-color:#001e1e;"
BUTTON_STYLE = ("QPushButton {"
                "    color: rgb(255, 255, 255);"
                "    border: 3px solid rgb(255, 255, 255);"
                "}"
                "QPushButton:hover {"
                "    background-color:rgba(245, 245, 245,50);"
                "}")
QUIT_BUTTON_STYLE = ("QPushButton {"
                     "    color: rgb(255, 255, 255);"
                     "    border: 3px solid rgb(255, 255, 255);"
                     "}"
                     "QPushButton:hover {"
                     "    border-color:rgb(253, 94, 80);"
                     "    color:rgb(253, 94, 80);"
                     "}")
LABEL_STYLE = "color:white;"
GROUP_BOX_STYLE = "color:white;"


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        """Set up the UI components."""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 800)
        font = QtGui.QFont()
        font.setFamily("Gujarati Sangam MN")
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(MAIN_WINDOW_STYLE)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.setupTitleLayout(self.centralwidget)
        self.setupControllerLayout(self.centralwidget)
        self.setupMainGridLayout(self.centralwidget)

        MainWindow.setCentralWidget(self.centralwidget)

    # Title layout setup
    def setupTitleLayout(self, parent_widget):
        horizontalLayoutWidget = QtWidgets.QWidget(parent_widget)
        horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 411, 80))
        title_layout = QtWidgets.QHBoxLayout(horizontalLayoutWidget)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_icon = QtWidgets.QLabel(horizontalLayoutWidget)
        title_icon.setMaximumSize(QtCore.QSize(64, 64))
        title_icon.setPixmap(QtGui.QPixmap("static/images/heart_title_icon.png"))
        title_icon.setScaledContents(True)
        title_layout.addWidget(title_icon)

        self.title_label = QtWidgets.QLabel(horizontalLayoutWidget)
        self.title_label.setMaximumSize(QtCore.QSize(280, 64))
        font = QtGui.QFont()
        font.setFamily("Hiragino Sans GB")
        font.setPointSize(25)
        font.setBold(True)
        font.setItalic(True)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(LABEL_STYLE)
        self.title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.title_label.setText("BioRhythm Analyzer")
        title_layout.addWidget(self.title_label)

    # Controller layout setup
    def setupControllerLayout(self, parent_widget):
        horizontalLayoutWidget_2 = QtWidgets.QWidget(parent_widget)
        horizontalLayoutWidget_2.setGeometry(QtCore.QRect(690, 10, 581, 80))
        controller_layout = QtWidgets.QHBoxLayout(horizontalLayoutWidget_2)
        controller_layout.setContentsMargins(0, 0, 0, 0)

        self.mode_button = self.addButton(controller_layout, "mode_button", "Current Mode: HRV", 180, BUTTON_STYLE)
        self.is_current_mode_HRV = True

        self.upload_signal_button = self.addButton(controller_layout, "upload_signal_button", "Upload Signal", 180, BUTTON_STYLE)
        self.quit_app_button = self.addButton(controller_layout, "quit_app_button", "X", 50, QUIT_BUTTON_STYLE, True)

    def addButton(self, layout, object_name, text, max_size, style, is_bold=False):
        button = QtWidgets.QPushButton()
        button.setMaximumSize(QtCore.QSize(max_size, 50))
        font = QtGui.QFont()
        font.setFamily("Hiragino Sans GB")
        font.setPointSize(15 if not is_bold else 40)
        font.setBold(is_bold)
        button.setFont(font)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet(style)
        button.setText(text)
        button.setObjectName(object_name)
        layout.addWidget(button)
        return button

    # Grid layout setup
    def setupMainGridLayout(self, parent_widget):
        gridLayoutWidget = QtWidgets.QWidget(parent_widget)
        gridLayoutWidget.setGeometry(QtCore.QRect(10, 100, 1261, 671))
        main_grid_layout = QtWidgets.QGridLayout(gridLayoutWidget)
        main_grid_layout.setContentsMargins(0, 0, 0, 0)

        # Define group boxes with graphs
        self.graph01_groupBox, self.plot_widget_01 = self.addGroupBox(main_grid_layout, "graph01_groupBox", "Raw Signal", 0, 0, True)
        self.graph02_groupBox, self.plot_widget_02 = self.addGroupBox(main_grid_layout, "graph02_groupBox", "Filtered Signal", 0, 1, True)
        self.graph03_groupBox, self.plot_widget_03 = self.addGroupBox(main_grid_layout, "graph03_groupBox", "HRV Metrics", 1, 0, True)
        self.graph04_groupBox, self.plot_widget_04 = self.addGroupBox(main_grid_layout, "alert_messages_groupBox", "Acceleration/Deceleration",
                                                                      1, 1, True, True)
        self.alert_messages_groupBox, self.stats_data_label = self.addGroupBox(main_grid_layout, "alert_messages_groupBox", "Stats", 1, 1)

    def addGroupBox(self, layout, object_name, title, row, col, isGraph=False, isHidden=False):
        group_box = QtWidgets.QGroupBox()
        font = QtGui.QFont()
        font.setFamily("Hiragino Sans GB")
        group_box.setFont(font)
        group_box.setStyleSheet(GROUP_BOX_STYLE)
        group_box.setTitle(title)
        group_box.setObjectName(object_name)
        layout.addWidget(group_box, row, col)

        widget = None  # Holds either the plot_widget or label

        if isGraph:
            widget = self.addGraphView(group_box)  # Plot widget is created
        else:
            # Create a QLabel to display HRV data
            label = QtWidgets.QLabel(group_box)
            label.setObjectName(f"{object_name}_label")
            # label.setFont(font)
            label.setStyleSheet(
                "color: white; background-color: transparent; border: none;"
            )  # Style consistent with existing

            label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            # label.setWordWrap(True)

            # Set fixed size for the label
            label.setFixedSize(600, 250)  # Adjust width and height as needed

            # Add label to the group box layout
            group_box_layout = QtWidgets.QVBoxLayout(group_box)
            group_box_layout.setContentsMargins(10, 10, 10, 10)  # Add some spacing
            group_box_layout.addWidget(label)

            widget = label  # Assign label to the widget variable

        if isHidden:
            group_box.hide()
            widget.hide()

        return group_box, widget

    def addGraphView(self, group_box):
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('#001e1e')
        plot_widget.showGrid(x=True, y=True, alpha=0.3)

        graph_layout = QtWidgets.QVBoxLayout()
        graph_layout.addWidget(plot_widget)
        group_box.setLayout(graph_layout)
        return plot_widget

    # --------------------------------------------------------------------------------------------------------------------------------------

    def toggle_mode_design(self):
        self.is_current_mode_HRV = not self.is_current_mode_HRV
        self.clear_all_plots()
        self.toggle_groupBox04()
        self.adjust_titles()

    def clear_all_plots(self):
        self.plot_widget_01.clear()
        self.plot_widget_02.clear()
        self.plot_widget_03.clear()
        self.plot_widget_04.clear()
        self.stats_data_label.setText("")

    def adjust_titles(self):
        if self.is_current_mode_HRV:
            self.mode_button.setText("Current Mode: HRV")
            self.graph01_groupBox.setTitle("Raw Signal")
            self.graph02_groupBox.setTitle("Filtered Signal")
            self.graph03_groupBox.setTitle("HRV Metrics")
        else:
            self.mode_button.setText("Current Mode: FHR")
            self.graph01_groupBox.setTitle("Baseline FHR")
            self.graph02_groupBox.setTitle("STV")
            self.graph03_groupBox.setTitle("Uterine contraction")

    def toggle_groupBox04(self):
        if self.is_current_mode_HRV:
            self.show_widget([self.alert_messages_groupBox, self.stats_data_label])
            self.hide_widget([self.graph04_groupBox, self.plot_widget_04])
        else:
            self.hide_widget([self.alert_messages_groupBox, self.stats_data_label])
            self.show_widget([self.graph04_groupBox, self.plot_widget_04])

    def show_widget(self, List):
        for n in List:
            n.show()

    def hide_widget(self, List):
        for n in List:
            n.hide()
