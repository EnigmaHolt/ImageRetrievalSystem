
import sys
import os
import play
from PyQt5.QtWidgets import (QWidget, QPushButton, QFileDialog, QStyle,
                             QHBoxLayout, QVBoxLayout, QApplication, QFrame, QSplitter, QMainWindow)
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import pyqtgraph as pg
import numpy as np

import AudioAnalysis
root_path = "/Users/haowu/Documents/576/project/query/"
dataset_path = "/Users/haowu/Documents/576/project/databse_videos/"
uiFile = "IRS.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(uiFile)


class MainInterface(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.query_list = self.findQueryFiles()
        self.dataset_list = self.initializeDatasetFiles()




        for name in self.query_list:
            self.cb_query_list.addItem(name[1])

        for name in self.dataset_list:
            self.lv_dataset.addItem(name[1])

        self.btn_query_play.clicked.connect(self.play)
        self.btn_query_play.setEnabled(False)
        self.hs_query_progress.setRange(0, 0)
        self.hs_query_progress.sliderMoved.connect(self.setPosition)
        self.btn_query_process.clicked.connect(self.openFile)


        self.btn_dataset_play.clicked.connect(self.dateset_play)
        self.btn_dataset_play.setEnabled(False)
        self.lv_dataset.currentItemChanged.connect(self.dataset_list_item_clicked)
        self.hs_dataset_progress.setRange(0,0)
        self.hs_dataset_progress.sliderMoved.connect(self.dataset_setPosition)


    def findQueryFiles(self):
        query_name_list = []
        for file in os.listdir(root_path):
            if '.' not in file:
                query_name_list.append((root_path, file))
        return query_name_list

    def initializeDatasetFiles(self):
        dataset_name_list = []
        for file in os.listdir(dataset_path):
            if '.' not in file:
                dataset_name_list.append((dataset_path,file))
        return dataset_name_list

    def setVideo(self):

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def dateset_play(self):
        if self.dataset_mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.dataset_mediaPlayer.pause()
        else:
            self.dataset_mediaPlayer.play()

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def dataset_setPosition(self, position):
        self.dataset_mediaPlayer.setPosition(position)

    def openFile(self):

        videoFileName = self.cb_query_list.currentText() + "_output.mov"
        videoFilePath = os.getcwd()+"/" + videoFileName
        if not os.path.isfile(videoFilePath):
            video = play.VideoGenerator();
            video.generateVideo(root_path + self.cb_query_list.currentText() + "/", self.cb_query_list.currentText())
        self.setVideo()
        if videoFilePath != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(videoFilePath)))
            self.btn_query_play.setEnabled(True)
            self.setChart(root_path+self.cb_query_list.currentText() + "/",self.cb_query_list.currentText())

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.btn_query_play.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.btn_query_play.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.hs_query_progress.setValue(position)

    def durationChanged(self, duration):
        self.hs_query_progress.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.btn_query_play.setEnabled(False)
        # self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def dataset_mediaStateChanged(self, state):
        if self.dataset_mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.btn_dataset_play.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.btn_dataset_play.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def dataset_positionChanged(self, position):
        self.hs_dataset_progress.setValue(position)

    def dataset_durationChanged(self, duration):
        self.hs_dataset_progress.setRange(0, duration)

    def dataset_setPosition(self, position):
        self.dataset_mediaPlayer.setPosition(position)

    def dataset_handleError(self):
        self.btn_dataset_play.setEnabled(False)
        # self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())



    def dataset_list_item_clicked(self,current):
        videoFileName = current.text() + "_output.mov"
        videoFilePath = os.getcwd()+"/" + videoFileName
        if not os.path.isfile(videoFilePath):
            video = play.VideoGenerator()
            video.generateVideo(dataset_path+current.text()+"/",current.text())
        self.dataset_mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.dataset_mediaPlayer.setVideoOutput(self.videoWidget_2)
        self.dataset_mediaPlayer.stateChanged.connect(self.dataset_mediaStateChanged)
        self.dataset_mediaPlayer.positionChanged.connect(self.dataset_positionChanged)
        self.dataset_mediaPlayer.durationChanged.connect(self.dataset_durationChanged)
        self.dataset_mediaPlayer.error.connect(self.dataset_handleError)

        self.dataset_mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(videoFilePath)))
        self.btn_dataset_play.setEnabled(True)

    def setChart(self,path,name):
        diff = AudioAnalysis.compareSimilarity(path+"/"+name+".wav")

        sound_data = []
        category_data = {}
        for f in diff:
            sound_data.append(int(f.diff))
        for i in range(len(self.dataset_list)):
            category_data[i] = self.dataset_list[i][1]
        self.chart.setData(category_data,sound_data)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainInterface()
    window.show()
        # used to test
    # diff = AudioAnalysis.compareSimilarity("/Users/haowu/Documents/576/project/query/first/first.wav")
    #
    # f = open('test.txt', 'w')
    #
    # for d in diff:
    #     f.write(d.name + " : " + str(d.diff))
    # f.close()

    sys.exit(app.exec_())
