from time import time
#from ultralytics import YOLO
import tempfile
import cv2
import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from wwsc.starting.ftp import upload_file

VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
font_scale = 1
preview_scale = 4
class CameraControl:
    def __init__(self, preview_area, zoomed_preview_area = None, video = None, zoomed_video = None, haarcascade = None, ultralytics = None):
        self.recording = False
        self.last_video_frame_time = time()*1000
        self.preview_area = preview_area
        self.zoomed_preview_area = zoomed_preview_area
        self.overlay_string=""
        self.video_name = ""
        self.race_number = 0
        self.saved_race_number = 0
        self.zoomed_video_name = ""
        self.just_started = False
        self.race_time = -100
        if video is None:
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FOURCC,sum([ord(c)<<(i*8) for i,c in enumerate("MJPG")]))
            self.camera.set(cv2.CAP_PROP_FPS,30)
        else:
            self.camera = cv2.VideoCapture(video)
        if zoomed_video is None:
            self.zoomed_camera = cv2.VideoCapture(2)
            self.zoomed_camera.set(cv2.CAP_PROP_FOURCC,sum([ord(c)<<(i*8) for i,c in enumerate("MJPG")]))
            self.zoomed_camera.set(cv2.CAP_PROP_FPS,30)
        else:
            self.zoomed_camera = cv2.VideoCapture(zoomed_video)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,VIDEO_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,VIDEO_HEIGHT)
        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE,3)
        self.zoomed_camera.set(cv2.CAP_PROP_FRAME_WIDTH,VIDEO_WIDTH)
        self.zoomed_camera.set(cv2.CAP_PROP_FRAME_HEIGHT,VIDEO_HEIGHT)
        self.zoomed_camera.set(cv2.CAP_PROP_AUTO_EXPOSURE,3)
        self.detection = False
        if haarcascade is not None:
            #self.boat_cascade = cv2.CascadeClassifier(haarcascade)
            self.boat_cascade = None
        else:
            self.boat_cascade = None
        if ultralytics is not None:
            #self.yolo = YOLO(ultralytics)
            #self.yolo.export(format="ncnn")
            #self.yolo = YOLO("./"+ultralytics[:-3]+"_ncnn_model")
            self.yoyo = None
        else:
            self.yoyo = None
        print("Video Width: "+str(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print("Video Height: "+str(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print("Video Format: "+str(int(self.camera.get(cv2.CAP_PROP_FOURCC)).to_bytes(4)))
        print("Video Autoexposure: "+str(self.camera.get(cv2.CAP_PROP_AUTO_EXPOSURE)))
        print("Zoomed Video Width: "+str(self.zoomed_camera.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print("Zoomed Video Height: "+str(self.zoomed_camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print("Zoomed Video Format: "+str(self.zoomed_camera.get(cv2.CAP_PROP_FOURCC)))
        print("Zoomed Video Autoexposure: "+str(self.zoomed_camera.get(cv2.CAP_PROP_AUTO_EXPOSURE)))

        print("Video FPS: "+str(self.camera.get(cv2.CAP_PROP_FPS)))
        print("Zoomed Video FPS: "+str(self.zoomed_camera.get(cv2.CAP_PROP_FPS)))

        # Start a thread which fires every 50ms to attempt to read video
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)

    def set_detection(self, status):
        self.detection = status
    
    def set_overlay_string(self, text, start, race_time):
        self.overlay_string = text
        self.race_time = race_time
        if start:
            self.race_number = self.race_number+1
            self.just_started = True

    def get_available_formats(self):
        codecs_to_test = ["H264", "DIVX", "XVID", "MJPG", "WMV1", "WMV2", "FMP4", "mp4v"]
        available_codecs = ["X264"]
        for codec in codecs_to_test:
            try:
                print ("testing for codex ")
                print(codec)
                fourcc = cv2.VideoWriter_fourcc(*codec)
                print (tempfile.gettempdir()+'/codec_test.mkv')
                temp_video = cv2.VideoWriter(tempfile.gettempdir()+'/codec_test.mkv', fourcc, 30, (VIDEO_WIDTH, VIDEO_HEIGHT), isColor=True)
                #temp_video = cv2.VideoWriter(tempfile.gettempdir()+'/codec_test.mp4', fourcc, 30, (640, 480), isColor=True)
                if temp_video is not None:
                    if temp_video.isOpened():
                        available_codecs.append(codec)
            except:
                print ("Error checking codex") 
                pass
        print(available_codecs)
        return available_codecs

    def start_recording(self,video_format):
        """
        Start recording.  Note that we play a little trick here.  We say the video is running a 15 fps - but we only save down
        a frame twice a second.  This ways the video appears to run a 7.5x speed
        """
        if not self.recording:
            self.video_name = "/var/www/html/"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+video_format
            self.zoomed_video_name = "/var/www/html/zoomed_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+video_format
            filename = self.video_name+".mkv"
            if video_format == "X264":
                filename = self.video_name+".mp4"
            zoomed_filename = self.zoomed_video_name+".mkv"
            if video_format == "X264":
                zoomed_filename = self.zoomed_video_name+".mp4"
            print ("SAVING........SAVING")
            print (filename)
            fourcc = cv2.VideoWriter_fourcc(*video_format)
            self.output = cv2.VideoWriter(filename, fourcc, 15.0,(VIDEO_WIDTH,VIDEO_HEIGHT), isColor=True)
            self.output.set(cv2.VIDEOWRITER_PROP_QUALITY,100)
            print (self.output.isOpened())
            self.zoomed_output = cv2.VideoWriter(zoomed_filename, fourcc, 15.0,(VIDEO_WIDTH,VIDEO_HEIGHT))
            self.zoomed_output.set(cv2.VIDEOWRITER_PROP_QUALITY,100)
            print ("Video Quality: "+str(self.output.get(cv2.VIDEOWRITER_PROP_QUALITY)))
            self.recording = True
            return filename
        
        return None

    def stop_recording(self):
        """
        Stop recording.  This is cause the video to be saved down
        """
        if self.recording:
            self.output.release()
            self.zoomed_output.release()
            if self.race_number > self.saved_race_number:
                upload_file(self.video_name+".mkv",datetime.datetime.now().strftime("%Y%m%d")+"_"+str(self.race_number)+".MKV")
                upload_file(self.video_name+".mp4",datetime.datetime.now().strftime("%Y%m%d")+"_"+str(self.race_number)+".MP4")
                upload_file(self.video_name+".jpg",datetime.datetime.now().strftime("%Y%m%d")+"_"+str(self.race_number)+".JPG")
                upload_file(self.zoomed_video_name+".mkv",datetime.datetime.now().strftime("%Y%m%d")+"_ZOOMED_"+str(self.race_number)+".MKV")
                upload_file(self.zoomed_video_name+".mp4",datetime.datetime.now().strftime("%Y%m%d")+"_ZOOMED_"+str(self.race_number)+".MP4")
                upload_file(self.zoomed_video_name+".jpg",datetime.datetime.now().strftime("%Y%m%d")+"_ZOOMED_"+str(self.race_number)+".JPG")
                self.saved_race_number = self.saved_race_number + 1
            self.recording = False
        
    def update_frame(self):
        """
        Process 1 frame of video.  This will attempt to read a frame of video from the camera, add a text overlay onto it
        and if we are recording write out the video frame
        """
        ret, frame = self.zoomed_camera.read()
        frame_spacing= 500
        if abs(self.race_time)< 2:
            frame_spacing = 50
        if ret:
            cv2.putText(frame, self.overlay_string,(5,30),cv2.FONT_HERSHEY_SIMPLEX,font_scale,(0,0,200),2,cv2.LINE_AA)

            if self.recording:
                current_millis = time() * 1000
                # Only record 2 frames per second
                if current_millis - self.last_video_frame_time > frame_spacing:
                    self.zoomed_output.write(frame)

            # Prepare image for preview
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            rbg_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h,w,ch=rbg_image.shape
            bytes_per_line = ch*w
            qt_image = QImage(rbg_image.data,w,h,bytes_per_line, QImage.Format_RGB888)
            scale = 177.0/VIDEO_WIDTH
            scaled_image = qt_image.scaled(int(VIDEO_HEIGHT*scale), int(VIDEO_WIDTH*scale))
            image = QPixmap.fromImage(scaled_image)
            self.zoomed_preview_area.setPixmap(image)
        if self.just_started:
            try:
                filename = self.zoomed_video_name+".jpg"
                cv2.imwrite(filename,frame)
            except:
                pass

        ret, frame = self.camera.read()
        if ret:
            cv2.putText(frame, self.overlay_string,(5,30),cv2.FONT_HERSHEY_SIMPLEX,font_scale,(0,0,200),2,cv2.LINE_AA)

            if self.recording:
                current_millis = time() * 1000
                # Only record 2 frames per second
                if current_millis - self.last_video_frame_time > frame_spacing:
                    self.output.write(frame)
                    self.last_video_frame_time = current_millis

            if self.detection:
                # Haar cascade image recognition - convert to grayscale
                if self.boat_cascade is not None:
                    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    boats = self.boat_cascade.detectMultiScale(gray_image, scaleFactor=1.1,minNeighbors=5, minSize=(30,30))
                    for (x,y,width,height) in boats:
                        cv2.rectangle(frame, (x,y), (x+width,y+height), (255, 0, 0), 2)
                # YOLO image recognition
                if self.yolo is not None:
                    results = self.yolo.track(frame, verbose=False,stream=True)
                    for result in results:
                        object_types = result.names
                        if result.boxes is not None:
                            for boat in result.boxes:
                                if boat.conf[0] > 0.4:
                                    object_type = object_types[int(boat.cls[0])]
                                    confidence = float(boat.conf[0])
                                    x1, y1, x2, y2 = map(int, boat.xyxy[0])
                                    cv2.rectangle(frame, (x1,y1), (x2,y2), (255, 0, 0), 2)
                                    cv2.putText(frame, f"{object_type} {confidence:.2f}", (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
            # Prepare image for preview
            rbg_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h,w,ch=rbg_image.shape
            bytes_per_line = ch*w
            qt_image = QImage(rbg_image.data,w,h,bytes_per_line, QImage.Format_RGB888)
            scale = 201.0/VIDEO_HEIGHT
            scaled_image = qt_image.scaled(int(VIDEO_WIDTH*scale), int(VIDEO_HEIGHT*scale))
            image = QPixmap.fromImage(scaled_image)
            #image.setOffset((420-VIDEO_WIDTH*scale)/2,0)
            self.preview_area.setPixmap(image)
            if self.just_started:
                self.just_started = False
                filename = self.video_name+".jpg"
                cv2.imwrite(filename,frame)


