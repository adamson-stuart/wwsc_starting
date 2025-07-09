from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
import time

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

if __name__ == "__main__":
    app = QApplication([])
    root_window = MainWindow()
    root_window.resize(300,200)
    root_window.show()

    app.exec()

