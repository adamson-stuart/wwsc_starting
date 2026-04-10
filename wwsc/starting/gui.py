from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
from wwsc.starting.relay_control import RelayControl
from PyQt5 import uic, QtGui
from PIL import Image
import time
import socket
from wwsc.starting.race_sequence import RaceSequence
from wwsc.starting.camera_control import CameraControl

import qrcode


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
        self.light_status=[main_window.light_1,main_window.light_2,main_window.light_3]
        self.horn_status=[main_window.horn_1,main_window.horn_2]
        main_window.race_type.addItem("3-2-1","3-2-1")
        main_window.race_type.addItem("5-4-1","5-4-1")
        main_window.race_type.addItem("Fisherman Friend","Fisherman Friend")
        main_window.race_type.addItem("Persuit","Persuit")
        main_window.race_type.setCurrentIndex(main_window.race_type.findData("3-2-1"))
        main_window.start_button.clicked.connect(self.start_race)
        main_window.reset_button.clicked.connect(self.reset_race)
        main_window.test_relays.clicked.connect(self.start_test)
        main_window.download_qr_code.setPixmap(pil2pixmap(self.get_video_download_url()))

    def relay_callback(self, lights, horns):
        for (status, widget) in zip(lights,self.light_status):
            widget.setText("X" if status else "O")
        for (status, widget) in zip(horns,self.horn_status):
            widget.setText("X" if status else "O")

    def remote_start(self):
        self.reset_race()
        self.start_race()
        
    def set_video_filename(self, filename):
        self.main_window.video_file.setText(filename)

    def get_video_download_url(self):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data('http://'+get_ip()+'/')
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def set_race_sequence(self, race_sequence):
        self.race_sequence = race_sequence

    def start_race(self):
        self.race_sequence.start(self.main_window.race_type.currentText())

    def reset_race(self):
        self.race_sequence.reset()

    def set_status(self, current_time, start_time, race_time):
        self.main_window.start_time.setText(start_time)
        self.main_window.race_time.setText(race_time)
        
    def start_test(self):
        self.relay_control.start_test()

if __name__ == "__main__":
    app = QApplication([])

    root_window = uic.loadUi("mainwindow.ui")
    root_window.show()
    relay_control = RelayControl([5,13,6],[26,19],17)
    gui = Gui(root_window, relay_control)
    camera_control = CameraControl(gui.main_window.preview_area)
    race_sequence = RaceSequence(relay_control, camera_control,gui)
    gui.set_race_sequence(race_sequence)
    gui.reset_race()
    app.exec()

