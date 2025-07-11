from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from picamera2.previews.qt import QGlPicamera2


class CameraControl:
    def __init__(self, preview_area):
        self.interface = Picamera2()
        self.interface.configure(self.interface.create_video_configuration(main={"size": (640, 480)}))
        qpicamera2 = QGlPicamera2(picam2, width=800, height=480, keep_ar=False)
        preview_area.addWidget(qpicamera2, 80)

        self.interface.start()


    def set_overlay_string(self, text):
        pass

    def start_recording(self):
        encoder = H264Encoder(10000000)
        output = FileOutput("test.h264")
        self.interface.start_encoder(encoder, output)
        
    def stop_recording(self):
        self.interface.stop_encoder()


qpicamera2 = QGlPicamera2(picam2, width=800, height=480, keep_ar=False)
layout_h.addWidget(qpicamera2, 80)

picam2.start()
