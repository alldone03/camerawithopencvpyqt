

from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtGui import QPixmap
import sys
import os


from datetime import datetime

pathtosave = "C:/Users/Aldan Prayogi/Pictures/fotopy"


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):

        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            cv_img = cv2.flip(cv_img, 2)
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class Ui_MainWindow(object):
    dataimage = []

    def __init__(self):
        super().__init__()
        self.disply_width = 640
        self.display_height = 480
        MainWindow.setObjectName("Camera")
        MainWindow.resize(1034, 536)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.camera = QtWidgets.QLabel(self.centralwidget)
        self.camera.setGeometry(QtCore.QRect(10, 10, 640, 480))
        self.camera.setObjectName("camera")
        self.pbcapture = QtWidgets.QPushButton(self.centralwidget)
        self.pbcapture.setGeometry(QtCore.QRect(790, 150, 141, 41))
        self.pbcapture.setObjectName("pbcapture")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(690, 10, 331, 61))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1034, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.pbcapture.clicked.connect(self.savefile)

        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(
            self.update_image)
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def savefile(self):
        # print(str(os.path.exists('savedImage.jpg')))
        try:
            filename = datetime.now().strftime("%Y-%m-%d %H-%M-%S")+'.jpg'
            print(filename + " Saved")
            cv2.imwrite(os.path.join(pathtosave, filename), self.dataimage)
        except:
            print("error")

    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.camera.setPixmap(qt_img)
        self.dataimage = cv_img

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(
            self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        self.pbcapture.setText(_translate("MainWindow", "Take Picture"))
        self.label.setText(_translate("MainWindow", "Kamera buatankuu"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
