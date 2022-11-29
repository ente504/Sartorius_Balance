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


class PublishData(QThread):
    """
    Thread class for continuously publishing the updated specimenDataframe
    to the MQTT Broker
    """

    def __init__(self):
        self.is_running = True

    def stop(self):
        self.is_running = False
        print('Stopping thread...')
        self.terminate()

    @pyqtSlot()
    def run(self):
        print("try to init Client")
        self.Client = MqttPublisher("Sartorius_Balance", broker, port, username, passkey)

        while self.is_running:
            if str(SpecimenDataFrame[1][0]) not in ["", " ", "none", "None", "False", "false"]:
                if Publish:
                    self.Client.publish(BaseTopic, build_json(SpecimenDataFrame))
                    Publish = False


class ConsoleWorkerPublish(QObject):
    """
    worker Object to  for continuously publishing the updated specimenDataframe
    see: class PublishData(QThread)
    """
    def __init__(self):
        super().__init__()
        self.Communicator = PublishData()

    def start_communication_thread(self):
        self.Communicator.start()

    def stop_communication_thread(self):
        self.Communicator.exit()


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
        self.resize(400, 300)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create and connect widgets
        self.Edit_Sample_ID = QLineEdit(self)
        self.Edit_weight = QLineEdit(self)
        self.Button_clear_Sample_ID = QPushButton("clear Sample ID", self)
        self.Button_clear_Sample_ID.clicked.connect(self.clear_SampleID_Edit)
        self.Button_clear_weight = QPushButton("clear weight", self)
        self.Button_clear_weight.clicked.connect(self.clear_weight_Edit)
        self.Button_readme = QPushButton("open readme", self)
        self.Button_readme.clicked.connect(self.open_readme)
        self.Button_Send_Data = QPushButton("send Data to Detact", self)
        self.Button_Send_Data.clicked.connect(self.send_Data)
        self.Sample_ID_Group = QGroupBox("Sample ID", self)
        self.Weight_Group = QGroupBox("weight from Balance", self)

        # Set the layout
        Edit_Sample_ID_Layout = QHBoxLayout()

        Edit_Sample_ID_Layout.addWidget(self.Edit_Sample_ID)
        Edit_Sample_ID_Layout.addWidget(self.Button_clear_Sample_ID)

        self.Sample_ID_Group.setLayout(Edit_Sample_ID_Layout)

        Edit_weight_Layout = QHBoxLayout()

        Edit_weight_Layout.addWidget(self.Edit_weight)
        Edit_weight_Layout.addWidget(self.Button_clear_weight)

        self.Weight_Group.setLayout(Edit_weight_Layout)

        Main_Layout = QVBoxLayout()

        Main_Layout.addWidget(self.Sample_ID_Group)
        Main_Layout.addWidget(self.Weight_Group)
        Main_Layout.addWidget(self.Button_Send_Data)
        Main_Layout.addWidget(self.Button_readme)

        self.centralWidget.setLayout(Main_Layout)


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

    def send_Data(self):
        print(SpecimenDataFrame)

        # Get Data into the SpecimenDataFrame
        if self.Edit_Sample_ID.text() not in ["", " ", "none", "None", "False", "false"]:
            SpecimenDataFrame[1][0] = self.Edit_Sample_ID.text()
        print(SpecimenDataFrame)

        SpecimenDataFrame[1][2] = str(timestamp())

        if self.Edit_weight.text() not in ["", " ", "none", "None", "False", "false"]:
            SpecimenDataFrame[0].append("weight")
            SpecimenDataFrame[1].append(self.Edit_weight.text())

        # init MQTT Client
        Client = MqttPublisher("Sartorius Balance", broker, port, username, passkey)

        # publish on MQTT
        if str(SpecimenDataFrame[1][0]) not in ["", " ", "none", "None", "False", "false"]:
            logging.info(build_json(SpecimenDataFrame))
            Client.publish(BaseTopic, build_json(SpecimenDataFrame))

        # inform user with message Box about the Data Transfer
        msg = QMessageBox()
        QTimer.singleShot(3000, lambda: msg.done(0))
        msg.setWindowTitle("Data Send")
        msg.setText("Data has been transmitted to Detact")
        msg.exec()D

        reset_SpecimenDataFrame()

        self.Edit_weight.clear()
        self.Edit_Sample_ID.clear()


# run application
app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
