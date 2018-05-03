
import sys
import os

import PyQt5
import operator

import play
from PyQt5.QtWidgets import (QWidget, QPushButton, QFileDialog, QStyle,
                             QHBoxLayout, QVBoxLayout, QApplication, QFrame, QSplitter, QMainWindow, QTableWidgetItem)
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSlot
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import pyqtgraph as pg
import numpy as np
import imageReaderTest

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

        self.motionArray = []
        self.refreshProgressBar(0)


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

    def setAudio(self,filePath):
        url = PyQt5.QtCore.QUrl.fromLocalFile(filePath)
        content = PyQt5.QtMultimedia.QMediaContent(url)
        self.audio_player = PyQt5.QtMultimedia.QMediaPlayer()
        self.audio_player.setMedia(content)
        self.audio_player.stateChanged.connect(self.mediaStateChanged)
        #self.audio_player.play();




    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState and self.audio_player.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.audio_player.pause()
        else:
            self.mediaPlayer.play()
            self.audio_player.play()

    def setResult(self):

        self.audio_analysis_result = {}
        self.color_analysis_result = {}
        self.motion_analysis_result = {}
        self.audioArray = {}

        diff = AudioAnalysis.compareSimilarity(root_path + self.cb_query_list.currentText() + "/" + self.cb_query_list.currentText() + ".wav")
        for f in diff:
            self.audioArray[f.name[:f.name.index(".")].encode('ascii','ignore').lower()] = f.diff
            self.audio_analysis_result[f.name[:f.name.index(".")].encode('ascii','ignore').lower()] = "%.2f" % (f.diff*100) +"%"


        self.motionArray = imageReaderTest.getMotionSimilarity(root_path + self.cb_query_list.currentText() + "/"+self.cb_query_list.currentText()+self.prefix)
        self.colorArray = imageReaderTest.getColorSimilarity("/Users/haowu/Documents/576/project/databse_videos",root_path + self.cb_query_list.currentText() + "/"+self.cb_query_list.currentText()+self.prefix)


        self.tw_categories.setRowCount(7)

        for item in self.motionArray.iteritems():
            sum_motion = sum(item[1])/600*100
            self.motion_analysis_result[item[0].lower()] = "%.2f" % sum_motion+"%"

        for item in self.colorArray.iteritems():
            sum_color = sum(item[1])/600*100
            self.color_analysis_result[item[0].lower()] = "%.2f" % sum_color + "%"

        sorted_array = []
        sorted_dic ={}

        for item in self.audio_analysis_result.iteritems():
            sum_motion_all = sum(self.motionArray[item[0]])/600*100
            sum_color_all = sum(self.colorArray[item[0]])/600*100
            sum_audio = self.audioArray[item[0]] * 100
            sorted_dic[item[0]] = sum_motion_all *0.3 + sum_color_all * 0.5+ sum_audio*0.2

        sorted_array = sorted(sorted_dic.items(), key=operator.itemgetter(1),reverse=True)

        #sorted(sorted_dic.items(),key=lambda item:item[1],reverse=True)
        index = 0
        for item in sorted_array:
            self.tw_categories.setItem(index, 0, QTableWidgetItem(item[0]))
            self.tw_categories.setItem(index, 1, QTableWidgetItem(self.motion_analysis_result[item[0]]))
            self.tw_categories.setItem(index, 2, QTableWidgetItem(self.color_analysis_result[item[0]]))
            self.tw_categories.setItem(index, 3, QTableWidgetItem(self.audio_analysis_result[item[0]]))
            self.tw_categories.setItem(index, 4, QTableWidgetItem("%2f"%(sorted_dic[item[0]])+"%"))
            index += 1




        self.refreshProgressBar(100)

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

        self.prefix = ""
        if self.rb_is_new_query.isChecked():
            self.prefix = "_"

        audioFileName = self.cb_query_list.currentText()+".wav"
        audioFilePath = root_path+self.cb_query_list.currentText()+"/"+audioFileName



        videoFileName = self.cb_query_list.currentText()+self.prefix + "_output.mov"
        videoFilePath = os.getcwd()+"/" + videoFileName

        self.refreshProgressBar(10)
        checkPathIsAvailable = False
        if not os.path.isfile(videoFilePath):
            try:
                video = play.VideoGenerator()
                video.generateVideo(root_path + self.cb_query_list.currentText() + "/", self.cb_query_list.currentText()+self.prefix)
                checkPathIsAvailable = True
            except:
                QtGui.QMessageBox.information(self, "Alert", "Wrong File Path")
        else:
            checkPathIsAvailable = True
        if checkPathIsAvailable:
            self.refreshProgressBar(30)
            self.setVideo()

            self.setAudio(audioFilePath)

            self.setResult()


            if videoFilePath != '':
                self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(videoFilePath)))
                self.btn_query_play.setEnabled(True)


    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState and self.audio_player.state() == QMediaPlayer.PlayingState:
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
        self.audio_player.setPosition(position)

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
        self.selectText = current.text()
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

        if len(self.motionArray)>0:
            self.setChart()


    def setChart(self):
        category_data = {}
        motionData = self.motionArray[self.selectText.encode('ascii','ignore').lower()]
        colorData = self.colorArray[self.selectText.encode('ascii','ignore').lower()]
        for i in range(len(motionData)):
            category_data[i] = str(i)
        self.chart.setData(category_data,motionData,colorData,50)

    def refreshProgressBar(self,value):
        self.pb_process.setValue(value)
        app.processEvents()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainInterface()
    window.show()

    sys.exit(app.exec_())
