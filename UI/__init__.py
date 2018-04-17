
import sys
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, QFrame, QSplitter, QMainWindow)
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget




uiFile = "IRS.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(uiFile)

class MainInterface(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainInterface()
    window.show()
    sys.exit(app.exec_())