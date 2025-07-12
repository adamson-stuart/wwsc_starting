from time import time
import cv2
import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
class CameraControl:
    def __init__(self, preview_area):
        self.recording = False
        self.last_video_frame_time = time()*1000
        self.preview_area = preview_area
        self.overlay_string=""
        self.camera = cv2.VideoCapture(0)
        print(self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,640))
        print(self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480))
        print(self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE,3))
        print(self.camera.get(cv2.CAP_PROP_EXPOSURE))
        print(self.camera.set(cv2.CAP_PROP_EXPOSURE,200.0))
        print(self.camera.set(cv2.CAP_PROP_FPS,5))
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)

    def set_overlay_string(self, text):
        self.overlay_string = text

    def start_recording(self):
        if not self.recording:
            filename = "/var/www/html/"+str(datetime.datetime.now())+".mp4"
            fourcc = cv2.VideoWriter_fourcc(*'X264')
            self.output = cv2.VideoWriter(filename, fourcc, 30.0,(640,480))
            self.recording = True
            return filename
        
        return None

    def stop_recording(self):
        if self.recording:
            self.output.release()
            self.recording = False
        
    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            cv2.putText(frame, self.overlay_string,(5,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
            if self.recording:
                current_millis = time() * 1000
                if current_millis - self.last_video_frame_time > 250:
                    self.output.write(frame)
                    self.last_video_frame_time = current_millis
            rbg_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h,w,ch=rbg_image.shape
            bytes_per_line = ch*w
            qt_image = QImage(rbg_image.data,w,h,bytes_per_line, QImage.Format_RGB888)
            scaled_image = qt_image.scaled(120,120)
            self.preview_area.setPixmap(QPixmap.fromImage(scaled_image))


