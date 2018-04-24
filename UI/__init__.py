import sys
import os
import play
from PyQt5.QtWidgets import (QWidget, QPushButton, QFileDialog, QStyle,
                             QHBoxLayout, QVBoxLayout, QApplication, QFrame, QSplitter, QMainWindow)
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget


root_path = "/Users/haowu/Documents/576/project/query/";
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
        self.hs_query_progress.setRange(0, 0)
        self.hs_query_progress.sliderMoved.connect(self.setPosition)
        self.btn_query_process.clicked.connect(self.openFile)

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

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainInterface()
    window.show()
    sys.exit(app.exec_())
