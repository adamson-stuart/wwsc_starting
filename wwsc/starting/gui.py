from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
from PyQt5 import uic, QtGui
import time
from wwsc.starting.race_sequence import RaceSequence
import qrcode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Race Control")

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_race)
        self.stop_button = QPushButton("Stop")

        self.setCentralWidget(self.start_button)

    def start_race(self):
        print ("And we're off!")

from PIL import Image

def pil2pixmap(im):
    if im.mode == "RGB":
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
    elif  im.mode == "RGBA":
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")
    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
    pixmap = QtGui.QPixmap.fromImage(qim)
    return pixmap

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class Gui:
    def __init__(self, main_window, relay_control):
        self.main_window = main_window
        self.relay_control = relay_control
        relay_control.set_callback(self)
        self.race_sequence = None
        self.set_status("","","")
        main_window.start_button.clicked.connect(self.start_race)
        main_window.test_relays.clicked.connect(self.start_test)
        main_window.download_qr_code.setPixmap(pil2pixmap(self.get_video_download_url()))

    def relay_callback(self, lights, horns):
        print (lights)
        print (horns)
        self.main_window.light1.setChecked(lights[0])
        self.main_window.light2.setChecked(lights[1])
        self.main_window.light3.setChecked(lights[2])
        self.main_window.horn1.setChecked(horns[0])
        self.main_window.horn2.setChecked(horns[1])

    def get_video_download_url(self):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data('http://'+get_ip()+':8081/videos/')
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        print (img)
        print (type(img))
        return img

    def set_race_sequence(self, race_sequence):
        self.race_sequence = race_sequence

    def start_race(self):
        self.race_sequence.start()

    def set_status(self, current_time, start_time, race_time):
        self.main_window.start_time.setText(start_time)
        self.main_window.race_time.setText(race_time)
        
    def start_test(self):
        self.relay_control.start_test()

if __name__ == "__main__":
    app = QApplication([])
    """
    root_window = MainWindow()
    root_window.resize(300,200)
    root_window.show()
    """

    from wwsc.starting.dummy_relay_control import DummyRelayControl
    from wwsc.starting.camera_control import CameraControl

    root_window = uic.loadUi("mainwindow.ui")
    root_window.show()
    relay_control = DummyRelayControl([1,2,3],[4,5])
    gui = Gui(root_window, relay_control)
    race_sequence = RaceSequence(relay_control, CameraControl(),gui)
    gui.set_race_sequence(race_sequence)
    app.exec()

