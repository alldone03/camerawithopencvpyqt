
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtGui import QPixmap
import mediapipe as mp
wCam, hCam = 640, 480


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    changedataview = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        datatosend = 0
        cap = cv2.VideoCapture(0)

        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        mp_drawing_styles = mp.solutions.drawing_styles

        with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)as hands:
            while self._run_flag:
                ret, img = cap.read()
                img = cv2.flip(img, 2)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img.flags.writeable = False
                results = hands.process(img)
                img.flags.writeable = True
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    datatosend = 1
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            img,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())
                else:
                    datatosend = 0
            if ret:
                self.changedataview.emit(datatosend)
                self.change_pixmap_signal.emit(img)
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()
        self.disply_width = 640
        self.display_height = 480
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(863, 530)
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.camera = QtWidgets.QLabel(self.centralwidget)
        self.camera.setGeometry(QtCore.QRect(10, 0, 640, 480))
        self.camera.setText("")
        self.camera.setObjectName("camera")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(670, 20, 161, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.PlainText)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.detectionlbl = QtWidgets.QLabel(self.centralwidget)
        self.detectionlbl.setGeometry(QtCore.QRect(670, 80, 161, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.detectionlbl.setFont(font)
        self.detectionlbl.setTextFormat(QtCore.Qt.PlainText)
        self.detectionlbl.setAlignment(QtCore.Qt.AlignCenter)
        self.detectionlbl.setObjectName("detectionlbl")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 863, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.changedataview.connect(self.updatestate)
        self.thread.start()

    def updatestate(self, data):
        decision = "Ada" if bool(data) else "Tidak Ada"
        self.detectionlbl.setText(str(decision))

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

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
        self.label_2.setText(_translate("MainWindow", "Status Detection"))
        self.detectionlbl.setText(_translate("MainWindow", "-"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
