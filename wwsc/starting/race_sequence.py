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
    """
    Implements the main starting sequence.  Two sequences are available
     * 3 - 2 - 1 - Go
       In this sequence all lights go on at 3 minutes and then one turns off on each minutes until no lights are on at the start
     * 5 - 4 - 1 - Go
       In this sequence light 1 (class flag) goes on at 5 minutes, light 2 (preparatory) goes on at 4 minutes, light 2 goes off at 1 minute
       and class goes off on the start
    """
    def __init__(self, relay_control, camera_control, gui):
        self.starting_sequence=[{"time":-240,"lights": [1,1,1], "horn": [1,0]}]
        self.race_running = False
        self.previous_time = None
        self.relay_control = relay_control
        self.camera_control = camera_control
        self.gui = gui
        

    def reset(self):
        """
        Reset the race sequence.  We turn all the lights on so we can see the reset is happening, then reset everything
        then turn the lights off again.  The main race loop is run with a resolutrino of 200ms - so this needs to wait
        for twice this to be on the safe side to ensure the existing race exits
        """
        self.relay_control.set_lights([1,1,1])
        self.previous_time = None
        self.start_time = None
        self.race_running = False
        time.sleep(0.2)
        self.relay_control.set_lights([0,0,0])
        time.sleep(0.2)

    def start(self, sequence_type = None):
        # Call reset just in case ....
        self.reset()

        if sequence_type is None or sequence_type=="3-2-1":
            self.starting_sequence=[{"time":-240,"lights": [1,1,1], "horn": [0.5,0]},
                                    {"time":-238,"lights": [0,0,0], "horn": [0,0.5]},
                                    {"time":-180,"lights": [1,1,1], "horn": [1,0]},
                                    {"time":-120,"lights": [0,1,1], "horn": [1,0]},
                                    {"time":-60,"lights": [0,0,1], "horn": [1,0]},
                                    {"time":0,"lights": [0,0,0], "horn": [1,0]}]
        elif sequence_type == "Fisherman Friend":
            self.starting_sequence=[{"time":-60,"lights": [1,1,1], "horn": [0.5,0]},
                                    {"time":-58,"lights": [0,0,0], "horn": [0,0.5]},
                                    {"time":-30,"lights": [1,1,1], "horn": [1,0]},
                                    {"time":-20,"lights": [0,1,1], "horn": [1,0]},
                                    {"time":-10,"lights": [0,0,1], "horn": [1,0]},
                                    {"time":-9,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-8,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-7,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-6,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-5,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-4,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-3,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-2,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":-1,"lights": [0,0,1], "horn": [0,0.5]},
                                    {"time":0,"lights": [0,0,0], "horn": [1,0]}]
        else:
            self.starting_sequence=[{"time":-360,"lights": [1,1,1], "horn": [0.5,0]},
                                    {"time":-358,"lights": [0,0,0], "horn": [0,0.5]},
                                    {"time":-300,"lights": [1,0,0], "horn": [1,0]},
                                    {"time":-240,"lights": [1,1,0], "horn": [1,0]},
                                    {"time":-60,"lights": [1,0,0], "horn": [1,0]},
                                    {"time":0,"lights": [0,0,0], "horn": [1,0]}]
        self.race_running = False
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

            # Sleep for 200ms - this will be the resolution of our timing
            time.sleep(0.2)

        self.camera_control.stop_recording()
            

