import datetime
import threading
import time

def format_seconds(seconds):
    negative = ""
    if seconds < 0:
        seconds =- seconds 
        negative = "-"

    hours = int(seconds / (60*60))
    minutes = int(seconds/60)%60
    second = int(seconds%60)

    return f"{negative}{minutes:02d}:{second:02d}"

class RaceSequence:
    def __init__(self, relay_control, camera_control, gui):
        self.starting_sequence=[{"time":-240,"lights": [1,1,1], "horn": [0,0]},
                                {"time":-238,"lights": [0,0,0], "horn": [1,0]},
                                {"time":-180,"lights": [1,1,1], "horn": [1,0]},
                                {"time":-120,"lights": [0,1,1], "horn": [1,0]},
                                {"time":-60,"lights": [0,0,1], "horn": [1,0]},
                                {"time":0,"lights": [0,0,0], "horn": [1,0]}]
        self.race_running = False
        self.previous_time = None
        self.relay_control = relay_control
        self.camera_control = camera_control
        self.gui = gui
        

    def reset(self):
        self.relay_control.set_lights([0,0,0])
        self.previous_time = None
        self.start_time = None
        self.race_running = False

    def start(self):
        # Call reset just in case ....
        self.reset()

        # Start a thread to run the race
        self.race_thread = threading.Thread(target=self.run_race, args=("",))
        self.race_running = True
        self.race_thread.start()


    def run_race(self, ignore):
        filename = self.camera_control.start_recording()
        self.gui.set_video_filename(filename)
        # Work out when we will start the race
        self.start_time = datetime.datetime.now() - datetime.timedelta(seconds=self.starting_sequence[0]["time"])
        current_sequence = 0
        # Now loop forever running the race 
        while(self.race_running):
            now = datetime.datetime.now()
            race_time = now - self.start_time

            while current_sequence < len(self.starting_sequence):
                # If we need to perform the next action ....
                if race_time.total_seconds() > self.starting_sequence[current_sequence]["time"]:
                    self.relay_control.set_lights(self.starting_sequence[current_sequence]["lights"])
                    self.relay_control.sound_horn(self.starting_sequence[current_sequence]["horn"])
                    current_sequence = current_sequence + 1
                else:
                    break

            # Generate the timing overlay string for the video
            start_time = self.start_time.strftime("%H:%M:%S")
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            race_time_formatted = format_seconds(race_time.total_seconds())

            overlay_string = f"Date: {current_date}, Current Time: {current_time}, Race Time: {race_time_formatted}"
            self.camera_control.set_overlay_string(overlay_string)

            if self.gui is not None:
                self.gui.set_status(current_date, start_time, str(race_time_formatted))

            # Sleep for 200ms - this iwll be the resolution of our timing
            time.sleep(0.2)

        self.camera_control.stop_recording()
            

