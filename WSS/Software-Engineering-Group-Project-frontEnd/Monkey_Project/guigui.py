from PyQt5.QtWidgets import *
from ui_GUI import Ui_MainWindow
from PyQt5.QtCore import Qt
import os
from PyQt5 import QtWidgets, QtGui, QtCore
import csv
import json
from datetime import datetime

json_file = "folder_info.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.icon_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)
        
        self.tableWidget = self.ui.tableWidget  

        # Connections
        self.ui.add_folder_btn.clicked.connect(self.add_folder)
        self.ui.export_file_btn.clicked.connect(self.export_files)
        #self.ui.view_data_btn.clicked.connect(self.display_csv) # TODO not implemented

        #create context menu
        self.createContextMenu()

    def createContextMenu(self):
        self.context_menu = QMenu(self)
        self.context_menu.addAction("Process Video", self.printIndex)

        self.ui.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget.customContextMenuRequested.connect(self.showContextMenu)
    
    def showContextMenu(self, position):
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

    # Add files to the app
    #def add_files(self):
        #files = QFileDialog.getOpenFileNames(
            #self,
            #caption='Add trap videos to the app',  # set popup window title
            #directory=':\\',  # resume from last directory
            #filter='Supported Format (*.avi;*.mp4)'  # set file format this funtn takes in
        #)
        #if files:
            #print(files)  # placeholder
            
    def add_folder(self):
        # Create a file dialog that allows the user to browse and select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        # Set the selected folder path to the push button's text property
        if folder_path:
            self.process_folder(folder_path, json_file)   

    
       # Get the video file from the folder and add it to the json list
    def process_folder(self, folder_path, json_file):
    # Recursively process all files and subfolders in the folder
        data_all = {}
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                # If the item is a file, process it
                if item.endswith(".AVI") or item.endswith(".mp4"):
                    file_path = os.path.join(folder_path, item_path)
                    file_name = os.path.basename(file_path)
                    file_size_byte = os.path.getsize(file_path)
                    file_size_mb = file_size_byte/(1024*1024)
                    file_modified = os.path.getmtime(file_path)
                    file_modified_time = datetime.fromtimestamp(file_modified)
                    json_file_modified_time = file_modified_time.strftime("%Y-%m-%d %H:%M:%S")
                    category_name = os.path.basename(folder_path)
                    data_temp = {
                        "file_state" : 3,
                        "file_name": file_name, 
                        "file_path": file_path, 
                        "file_modified_time": json_file_modified_time,
                        "file_size_mb": file_size_mb,
                        "file_animal" : "Waiting"
                    }
                    if category_name in data_all:
                        data_all[category_name].append(data_temp)
                    else:
                        data_all[category_name] = [data_temp]
            elif os.path.isdir(item_path):
                # If the item is a folder, recursively process its contents
                self.process_folder(item_path, json_file)

        # Check if the file already exists
        if os.path.exists(json_file):
            with open(json_file, "r") as f:
                try:
                    existing_data_all = json.load(f)
                except ValueError:
                    existing_data_all = {}
                
        else:
            existing_data_all = {}

        # Merge the new data with existing data
        for category_name, category_data in data_all.items():
            if category_name in existing_data_all:
                existing_data_all[category_name].extend(category_data)
            else:
                existing_data_all[category_name] = category_data

        with open(json_file, "w") as f:
            json.dump(existing_data_all, f, indent = 4)
            
        self.refreshTableHome()

    # Refresh the table of main page
    def refreshTableHome(self):
        self.tableWidget.clear()
        # Load the JSON data from the file into a Python object
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        
        # Get the list of categories from the data
        cat_list = list(data.keys())
        # Create a dictionary to store status for each camera
        camera_status = []

        # Check file states for each camera
        for camera, files in data.items():
            # Initialize variables to keep track of file states for current camera
            completed = True
            paused = True
            ready = True
            for file in files:
                file_state = file["file_state"]
                if file_state != 3:
                    ready = False
                if file_state != 2:
                    completed = False
                if file_state != 1:
                    paused = False

            # Assign status for current camera
            if completed:
                status = "Completed"
            elif paused:
                status = "Paused"
            elif ready:
                status = "Ready to process"
            else:
                status = "Processing"
            camera_status.insert(0, status)
        # Create the table widget and set the number of rows and columns
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(len(cat_list))
        
        # Set the selection behavior to SelectRows
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)   

        # Set the table header labels
        item = QtWidgets.QTableWidgetItem("File Name")
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem("Videos Inside")
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem("Status")
        self.tableWidget.setHorizontalHeaderItem(2, item)

        # Loop through the categories and add them to the table
        for i, category in enumerate(cat_list):
            count = len(data[category])
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(category))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(count)))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(camera_status[i-1]))
            # self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem("Processing"))
        # Set the left-click event for the row

        # Make all items in the table not editable
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(i, j)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)


    def export_files(self):
        # Example data
        data = [
            ["video_date", "animal_presence?", "monkey_presence?"],
            ["Feb.2", "Yes", "No"],
            ["Jan.15", "Yes", "Yes"],
            ["April.12", "No", "No"]
        ]

        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(data)


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

    with open("Monkey_Project/style.qss", "r") as style_file:
        style_str = style_file.read()

    app.setStyleSheet(style_str)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
