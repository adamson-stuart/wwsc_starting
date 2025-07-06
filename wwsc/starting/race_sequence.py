from wwsc.starting.relay_control import RelayControl
from wwsc.starting.camera_control import CameraControl
import datetime
import threading

class RaceSequence:
    def __init__(self, relay_control, camera_control):
        self.starting_sequence=[{"time":-240,"lights": [1,1,1], "horn": [0,0]},
                                {"time":-238,"lights": [0,0,0], "horn": [1,0]},
                                {"time":-180,"lights": [1,1,1], "horn": [1,0]},
                                {"time":-120,"lights": [0,1,1], "horn": [1,0]},
                                {"time":-60,"lights": [0,0,1], "horn": [1,0]},
                                {"time":0,"lights": [0,0,0], "horn": [1,0]}]
        self.previous_time = None
        self.relay_control = relay_control
        self.camera_control = camera_control
        

    def reset(self):
        self.relay_control.set_lights([0,0,0])
        self.previous_time = None
        self.start_time = None

    def start(self):
        # Call reset just in case ....
        self.reset()

        # Start a thread to run the race
        self.race_thread = threading.Thread(target=self.run_race, args=("",))
        self.race_thread.start()


    def run_race(self, ignore):
        # Work out when we will start the race
        self.start_time = datetime.datetime.now() - self.starting_sequence[0]["time"]
        current_sequence = 0
        # Now loop forever running the race 
        while(True):
            now = datetime.datetime.now() - self.start_time

            while current_sequence < len(self.starting_sequence):
                # If we need to perform the next action ....
                if now > self.starting_sequence[current_sequence]["time"]:
                    self.relay_control.set_lights(self.starting_sequence[current_sequence]["lights"])
                    self.relay_control.set_horn(self.starting_sequence[current_sequence]["horn"])
                    current_sequence = current_sequence + 1
                else:
                    break

            # Generate the timing overlay string for the video
            overlay_string = f"Date: {current_date}, Current Time: {current_time}, Race Time: {race_time}"
            self.camera_control.set_overlay_string(overlay_string)

            # Sleep for 200ms - this iwll be the resolution of our timing
            time.sleep(0.2)
            

