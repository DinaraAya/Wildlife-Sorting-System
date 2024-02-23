from PyQt5.QtWidgets import *
from ui_GUI import Ui_MainWindow
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QUrl
import csv
import os
import json
from PyQt5 import QtWidgets, QtMultimedia, uic, QtCore

file_info = "file_info.json"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.icon_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)

        # Connections
        self.ui.add_folder_btn.clicked.connect(self.add_files)
        self.ui.open_vid_btn.clicked.connect(self.open_file)
        self.ui.play_btn.clicked.connect(self.play_video)
        #self.ui.export_file_btn.clicked.connect(self.export_files)
        #self.ui.view_data_btn.clicked.connect(self.display_csv) # TODO not implemented

        #Create context menu for the tableWidget
        self.createContextMenu()

        # Add QMediaPlayer and QVideoWidget
        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self.ui.widget_2)
        self.media_player.setVideoOutput(self.video_widget)
        self.video_widget.setObjectName("widget_2")
        self.video_widget.setAutoFillBackground(True) 
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile("/Users/dinarablyat/Downloads/send_Dinara/Camera Trap Video 001 _ Blue Duiker.mp4")))

        self.media_player.play()

        #Replay video when video ends
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        #Connect movement of the slider with video
        self.ui.horizontalSlider.sliderMoved.connect(self.set_position)

    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0) 
            self.media_player.play()  

    #set the position of the slider
    def position_changed(self, position):
        self.ui.horizontalSlider.setValue(position)

    #set the duration of the slider
    def duration_changed(self, duration):
        self.ui.horizontalSlider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)


    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.media_player.play()

    def createContextMenu(self):
        self.context_menu = QMenu(self)
        self.context_menu.addAction("Process Video (blank/non-blank)", self.printIndex)
        self.context_menu.addAction("Process Video (Monkey presence)")

        self.ui.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget.customContextMenuRequested.connect(self.showContextMenu)
    
    def showContextMenu(self, position):
        self.context_menu.exec_(self.ui.tableWidget.mapToGlobal(position))

    def printIndex(self):
        selected_indexes = self.ui.tableWidget.selectedIndexes()
        for index in selected_indexes:
            print(f"Row: {index.row()}, Colunm: {index.column()}")

    # Change checkable status of pushbuttons when stackedwidget changed
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_widget.findChildren(QPushButton) \
                   + self.ui.full_menu_widget.findChildren(QPushButton)

        for btn in btn_list:
            if index in [4, 5]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)

    def add_files(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Video Files (*.mp4 *.avi *.mov)")

        if file_path:
            self.append_json(file_path, file_info)

    def append_json(self, file_path, file_info):

        data_all = {}

        if os.path.isfile(file_path) and (file_path.endswith(".AVI") or file_path.enswith(".mp4")):
            file_name = os.path.basename(file_path)
            file_size_byte = os.path.getsize(file_path)
            file_size_mb = file_size_byte/ (1024 * 1024)
            category_name = os.path.dirname(file_path)
            data_temp = {
                "file_name": file_name,
                "file_path": file_path,
                "file_size_mb": file_size_mb,
            }

            if category_name in data_all:
                data_all[category_name].append(data_temp)
            else:
                data_all[category_name] = [data_temp]
       
        if os.path.exists(file_info):
            with open(file_info, "r") as f:
                try:
                    existing_data_all = json.load(f)
                except ValueError:
                    existing_data_all = {}
        else:
            existing_data_all = {}

        for category_name, category_data in data_all.items():
            if category_name in existing_data_all:
                existing_data_all[category_name].extend(category_data)
            else:
                existing_data_all[category_name] = category_data
        
        with open(file_info, "w") as f:
            json.dump(existing_data_all, f, indent=4)

        self.refreshTableHome()

    def refreshTableHome(self):
        self.ui.tableWidget.clear()

        with open(file_info, 'r') as f:
            data = json.load(f)

        cat_List = list(data.keys())

        self.ui.tableWidget.setRowCount(len(cat_List))

        self.ui.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        item = QtWidgets.QTableWidgetItem("File Name")
        self.ui.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem("Directory")
        self.ui.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem("Status")
        self.ui.tableWidget.setHorizontalHeaderItem(2, item)

        for i, category in enumerate(cat_List):
            count = len(data[category])
            self.ui.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(category))

            for j, file_data in enumerate(data[category]):
            # Set the file name in the first column
                self.ui.tableWidget.setItem(i + j, 0, QtWidgets.QTableWidgetItem(file_data["file_name"]))
            # Set the directory in the second column
                self.ui.tableWidget.setItem(i + j, 1, QtWidgets.QTableWidgetItem(category))


    # Functions for changing menu page
    def on_home_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_home_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_process_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_process_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_data_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_data_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_help_btn_1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_help_btn_2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)


#if there's an error with qss, copy your relative path to qss file and paste it in "open" brackets

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    with open("Software-Engineering-Group-Project-frontEnd/Monkey_Project/style.qss", "r") as style_file:
        style_str = style_file.read()

    app.setStyleSheet(style_str)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
