# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Sartorius Balance Import Software
# intended for use at IPF Dresden
# Revision: @ente504
# 0.1: alpha version


import logging
from PyQt5.QtCore import QObject, QThread, pyqtSlot, QTimer
import sys
import os
import time
import json
import configparser
import datetime
from t_publishData import MqttPublisher
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QLabel,
    QGroupBox,
    QMessageBox)

# read from configuration file
CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

DeviceName = str(config["GENERAL"]["DeviceName"])
broker = str(config["MQTT"]["Broker"])
port = int(config["MQTT"]["Port"])
username = str(config["MQTT"]["UserName"])
passkey = str(config["MQTT"]["PassKey"])
BaseTopic = str(config["MQTT"]["BaseTopic"])
Readme_Path = str(config["GENERAL"]["ReadmePath"])

# variable declarations
Sample_ID = ""
Weight = ""
File_Location = ""
Publish = False
path = ""

"""
construct SpecimenDataFrame:
The Specimen Dataframe contains the relevant Data
The contained Data in this Dataframe is of Type String
The order of the Elements is to be respected 0 to 6]
The Names are taken from the SpecimenNameFrame
"""

SpecimenNameList = ["sample_id", "station_id", "timestamp"]
SpecimenDataList = [None, DeviceName, None]
SpecimenDataFrame = [SpecimenNameList, SpecimenDataList]


def reset_SpecimenDataFrame():
    """
    restores the virgin version of the SpecimenDataFrame
    """

    global SpecimenDataFrame

    SpecimenNameList = ["sample_id", "station_id", "timestamp"]
    SpecimenDataList = [None, DeviceName, None]

    SpecimenDataFrame = []
    SpecimenDataFrame = [SpecimenNameList, SpecimenDataList]


def publish_stuff():
    # publish on MQTT
    if str(SpecimenDataFrame[1][0]) not in ["", " ", "none", "None", "False", "false"]:
        logging.info(build_json(SpecimenDataFrame))
        Client.publish(BaseTopic, build_json(SpecimenDataFrame))
        print(SpecimenDataFrame[1])
        time.sleep(0.1)


def timestamp():
    """
    function produces an actual timestamp
    :return: timestamp as String
    """
    current_time = datetime.datetime.now()
    time_stamp = current_time.strftime("%d-%m-%y_%H-%M-%S")
    return_time = "%s" % time_stamp
    return time_stamp


def build_json(dataframe):
    """
    :param dataframe: takes the 2D Array SpecimenDataframe
    :return: json string build output of the provided Dataframe
    """
    data_set = {}
    json_dump = ""
    dataframe_length = int(len(dataframe[1]))

    # deconstruct specimenDataFrame and pack value pairs into .json
    if len(dataframe[0]) == len(dataframe[1]):
        for x in range(0, dataframe_length):
            if dataframe[1][x] not in ["", " ", None] and "Prüfzeit" not in dataframe[0][x]:
                key = str(dataframe[0][x])
                value = (dataframe[1][x])
                data_set[key] = value

            json_dump = json.dumps(data_set)
    else:
        logging.error("Error while transforming list into json String")

    return json_dump


class Window(QMainWindow):
    """
    GUI definition (pyqt)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        """
        methode builds the pyqt GUI then the Window class is initialised
        """

        self.setWindowTitle("Sartorius Balance Import Tool")
        self.resize(400, 250)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create and connect widgets
        self.Edit_Sample_ID = QLineEdit(self)
        self.Edit_Sample_ID.textChanged.connect(self.update_sample_id)
        self.Edit_weight = QLineEdit(self)
        self.Edit_weight.textChanged.connect(self.update_weight)

        self.Sample_ID_Label = QLabel(self)
        self.Sample_ID_Label.setText("Sample ID: -")
        self.Weight_Label = QLabel(self)
        self.Weight_Label.setText("Weight: -")

        self.Button_clear_Sample_ID = QPushButton("clear Sample ID", self)
        self.Button_clear_Sample_ID.clicked.connect(self.clear_SampleID_Edit)
        self.Button_clear_weight = QPushButton("clear weight", self)
        self.Button_clear_weight.clicked.connect(self.clear_weight_Edit)
        self.Button_readme = QPushButton("open readme", self)
        self.Button_readme.clicked.connect(self.open_readme)
        self.Button_Send_Data = QPushButton("send Data to Detact", self)
        self.Button_Send_Data.clicked.connect(self.send_Data)
        self.Button_Send_Data.setStyleSheet("background-color: lightgreen")
        # TODO: figure out how to connect the Button with the Enter Key
        self.Button_Send_Data.setAutoDefault(True)
        self.Button_Send_Data.setDefault(True)
        self.Button_Send_Data.setFixedHeight(40)
        self.Sample_ID_Group = QGroupBox("Sample ID", self)
        self.Weight_Group = QGroupBox("weight from Balance", self)
        self.send_Data_Goup = QGroupBox("Data to transmit", self)

        # Set the layout
        Edit_Sample_ID_Layout = QHBoxLayout()

        Edit_Sample_ID_Layout.addWidget(self.Edit_Sample_ID)
        Edit_Sample_ID_Layout.addWidget(self.Button_clear_Sample_ID)

        self.Sample_ID_Group.setLayout(Edit_Sample_ID_Layout)

        Edit_weight_Layout = QHBoxLayout()

        Edit_weight_Layout.addWidget(self.Edit_weight)
        Edit_weight_Layout.addWidget(self.Button_clear_weight)
        Edit_weight_Layout.addWidget(self.Weight_Label)

        self.Weight_Group.setLayout(Edit_weight_Layout)

        send_Data_Layout = QVBoxLayout()
        Data_Layout = QHBoxLayout()
        Data_Layout.addWidget(self.Sample_ID_Label)
        Data_Layout.addWidget(self.Weight_Label)
        send_Data_Layout.addLayout(Data_Layout)
        send_Data_Layout.addWidget(self.Button_Send_Data)

        self.send_Data_Goup.setLayout(send_Data_Layout)

        Main_Layout = QVBoxLayout()

        Main_Layout.addWidget(self.Sample_ID_Group)
        Main_Layout.addWidget(self.Weight_Group)
        Main_Layout.addWidget(self.send_Data_Goup)
        Main_Layout.addWidget(self.Button_readme)

        self.centralWidget.setLayout(Main_Layout)

    def update_sample_id(self):
        Sample_ID = self.Edit_Sample_ID.text()
        self.Sample_ID_Label.setText("Sample ID: " + Sample_ID)
        self.Sample_ID_Label.repaint()

    def update_weight(self):
        Weight = self.Edit_weight.text()
        output = str(self.prozess_weight_input(Weight))

        if output != "":
            self.Weight_Label.setText("Weight: " + str(output) + " mg")
            self.Weight_Label.repaint()

        else:
            self.Weight_Label.setText("Weight: no input")
            self.Weight_Label.repaint()

    def open_readme(self):

        global Readme_Path
        try:
            os.startfile(Readme_Path)
        except Exception:
            logging.error("readme file was not found")

    def clear_SampleID_Edit(self):
        self.Edit_Sample_ID.clear()
        self.Edit_Sample_ID.setFocus()

    def clear_weight_Edit(self):
        self.Edit_weight.clear()
        self.Edit_weight.setFocus()

    def prozess_weight_input(self, input_string):
        return_string = " "

        try:
            if input_string != "":
                if input_string[0] == "`":
                    try:
                        first_letters_cut = input_string[1:]
                        #last_letters_cut = first_letters_cut[:-1]
                    except:
                        logging.error("error while prozessing information from the Weight input")

                    return_string = float(first_letters_cut)

                if input_string[0] == "ß":
                    try:
                        first_letters_cut = input_string[3:]
                        #last_letters_cut = first_letters_cut[:-1]
                    except:
                        logging.error("error while prozessing information from the Weight input")

                    return_string = float("-" + first_letters_cut)

                if input_string[0] not in ["ß", "`"]:
                    return_string = input_string
            else:
                return_string = " "
        except:
            logging.error("error while processing string: String probably not long enough")
        return return_string

    def send_Data(self):

        if self.Edit_Sample_ID.text() not in ["", " "] and self.Edit_weight.text() not in ["", " "]:

            # Get Data into the SpecimenDataFrame
            SpecimenDataFrame[1][0] = self.Edit_Sample_ID.text()
            SpecimenDataFrame[1][2] = str(timestamp())

            SpecimenDataFrame[0].append("weight")
            SpecimenDataFrame[1].append(self.prozess_weight_input(self.Edit_weight.text()))

            # init MQTT Client
            self.Client = MqttPublisher("Sartorius Balance", broker, port, username, passkey)

            # publish on MQTT
            logging.info(build_json(SpecimenDataFrame))
            self.Client.publish(BaseTopic, build_json(SpecimenDataFrame))

            # disconnect and delete Client
            self.Client.__del__()

            # inform user with message Box about the Data Transfer
            msg = QMessageBox()
            QTimer.singleShot(3000, lambda: msg.done(0))
            msg.setWindowTitle("Data Send")
            msg.setText("Data has been transmitted to Detact")
            msg.exec()
            # TODO: make online Detection

            reset_SpecimenDataFrame()

            self.Edit_weight.clear()
            self.Edit_Sample_ID.clear()
            self.Weight_Label.setText("Weight: -")
            self.Sample_ID_Label.setText("Sample ID: -")

        else:
            msg = QMessageBox()
            msg.setWindowTitle("invalid data")
            msg.setText("please enter data into both text fields ")
            msg.exec()


# run application
app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
