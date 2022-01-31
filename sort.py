####################################################
###### A program that sorts a certain folder #######
######             Made by Ilaik5            #######
####################################################

# Imports
import ast
import json
from PyQt5 import QtWidgets, QtGui
import shutil
from tkinter import messagebox
import os
import sys
from pathlib import Path

# A Function that can sort a certain folder


def sort_folder(folder_path):



    # Checks if the program should backup the selected folder
    Backup_folder = False
    with open(os.path.join(Path(sys.argv[0]).parent,'config.json'), 'r') as f:

        try:

            b_lines= json.load(f)
            if b_lines["backup"] == "True":
                Backup_folder = True

        except json.decoder.JSONDecodeError:
            answer = messagebox.askquestion("Create backup folder?", f"Do you want us to create a backup folder of {folder_path}?, You will be only asked this once if you want to change this afterwards you can do that by opening the app directly")
            if answer == "yes":
                with open(os.path.join(Path(sys.argv[0]).parent,'config.json'), 'w') as f:
                    f.write(json.dumps({"backup": "True"}))
                    Backup_folder = True
            else:
                with open(os.path.join(Path(sys.argv[0]).parent,'config.json'), 'w') as f:
                    f.write(json.dumps({"backup": "False"}))
                    Backup_folder = False

    # Checks if the selected file/folder is a folder if not it will notify the user
    if os.path.isfile(folder_path):
        messagebox.showerror("Error", "You have chosen a file to sort. You can only choose directories")
        return

    # Tells the user that if he won't close some programs they wont be sorted
    if messagebox.askyesno("Warning", "Every program that is open will not be sorted (it will not close the proccess, it'll just skip over them), Do you want to proceed?") == False:
        return

    # Loads extensions with categories
    with open(os.path.join(Path(sys.argv[0]).parent.parent,'file_types.json'), 'r') as file:
        sorting_dict = json.load(file)
    # Gets all extension
    all_extensions = []
    for key in list(sorting_dict.keys()):
        for value in sorting_dict[key]:
            all_extensions.append(value)
    # Creates a DesktopBackup folder
    if Backup_folder == True:
        counter = 1
        for file in os.listdir(folder_path):
            if "FolderSorter-BackupFolder" in os.path.basename(file):
                counter += 1
        os.makedirs(os.path.join(folder_path, f'FolderSorter-BackupFolder - {counter}'), exist_ok=True)
        backup_folder = os.path.join(folder_path, f'FolderSorter-BackupFolder - {counter}')
        print('Created backup folder')
    # Creates a "files" dictionaries that will contain all file paths by categories
    files = {}
    files["other"] = []
    for key in list(sorting_dict.keys()):
        files[key] = []


    # Sorts file pathes by categories
    for file in os.listdir(folder_path):
        if not os.path.isdir(os.path.join(folder_path, file)) and os.path.isfile(os.path.join(folder_path, file)):
            extention = file.split('.')[-1].lower()
            if extention == 'ini':
                continue
            for c,key in enumerate(list(sorting_dict.keys())):
                if extention not in all_extensions:
                    if not os.path.exists(os.path.join(folder_path, "Other")):
                        os.makedirs(os.path.join(folder_path, "Other"), exist_ok=True)
                    files["other"].append(os.path.join(folder_path, file))
                    break
                if extention in sorting_dict[key]:
                    files[key].append(os.path.join(folder_path, file))


    # Moves all the files to the backup folder
    if Backup_folder == True:
        for file in os.listdir(folder_path):
            if not file.endswith('.ini') and "FolderSorter-BackupFolder" not in file:
                print(f"Copying {file} to Backup folder")
                try:
                    if os.path.isfile(os.path.join(folder_path,file)):
                        shutil.copy2(os.path.join(folder_path,file), os.path.join(backup_folder,file))
                    else:
                        shutil.copytree(os.path.join(folder_path, file), os.path.join(backup_folder, file))
                except:
                    pass

    # Creates the categorised folders
    for name in list(files.keys()):
        if files[name] != []:
            print(f'Creating folder {name}')
            os.makedirs(os.path.join(folder_path, name), exist_ok=True)

    # Moves all the files to the dedicated folder
    for file in files:
        if files[file] != []:
            for path in files[file]:
                print(f'Moving {os.path.basename(path)} to folder {file}')
                try:
                    shutil.move(path, os.path.join(folder_path, file))
                except:
                    pass


# A function that asks you to select a folder and then calls the sort on that folder
def select_folder(win):
    folderpath = QtWidgets.QFileDialog.getExistingDirectory(win, 'Select Folder')
    if folderpath != '':
        sort_folder(folderpath)
        print('Done!')

def update_config_file(button):
    if button.isChecked():
        with open(os.path.join(Path(sys.argv[0]).parent,'config.json'), 'w') as f:
            f.write(json.dumps({"backup":"True"}))

        button.setStyleSheet("background-color : lightblue")
    else:
        with open(os.path.join(Path(sys.argv[0]).parent,'config.json'), 'w') as f:
            f.write(json.dumps({"backup":"False"}))
        button.setStyleSheet("background-color : lightgrey")

# UI app
def main():

    # Sets up the window and buttons
    app = QtWidgets.QApplication(sys.argv)
    windows = QtWidgets.QWidget()
    windows.resize(250, 120)
    windows.move(100, 100)
    windows.setWindowTitle('Folder Sorter')
    windows.setWindowIcon(QtGui.QIcon('gnome_edit_clear.ico'))
    select_folder_btn = QtWidgets.QPushButton(windows)
    select_folder_btn.setText("Select a folder to sort")
    select_folder_btn.move(55, 10)
    select_folder_btn.resize(150, 75)
    select_folder_btn.clicked.connect(lambda: select_folder(windows))
    backup_folder_toggle = QtWidgets.QCheckBox(windows)

    # Loads the status of the backup data (true/fasle) so it will save as the user left it
    with open(os.path.join(Path(sys.argv[0]).parent,'config.json'), 'r') as f:
        f.seek(0)
        try:
            j= json.loads(f.read())
            if j["backup"] == "True":
                backup_folder_toggle.setChecked(True)
            else:
                backup_folder_toggle.setChecked(False)
        except json.decoder.JSONDecodeError:
            backup_folder_toggle.setChecked(True)

    backup_folder_toggle.move(55, 90)
    backup_folder_toggle.setText("Backup selected folder")
    backup_folder_toggle.stateChanged.connect(lambda: update_config_file(backup_folder_toggle))
    backup_folder_toggle.setStyleSheet("background-color : lightgrey")
    windows.show()
    sys.exit(app.exec_())

# Checks if program was ran from right click or directly
if len(sys.argv) != 2:
    main()
else:
    sort_folder(sys.argv[-1])