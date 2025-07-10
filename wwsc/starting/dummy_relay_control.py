import threading
import time

class DummyRelayControl:
    def __init__(self, light_pins, horn_pins):
        self.light_pins = light_pins
        self.horn_pins = horn_pins
        self.light_status = [False]*3
        self.horn_status = [False]*2
        self.callback = None

    def set_lights(self, lights):
        print (f"Light set to {lights}")
        self.light_status = lights
        if self.callback is not None:
            self.callback.relay_callback(self.light_status,self.horn_status)

    def sound_horn(self, horns):
        print (f"Horn set to {horns}")
        self.horn_status = horns
        if self.callback is not None:
            self.callback.relay_callback(self.light_status,self.horn_status)

    def set_callback(self, callback):
        self.callback = callback

    def start_test(self):
        test_thread = threading.Thread(target=self.run_tests, args=("ignore",))
        test_thread.start()
        
    def run_tests(self, ignore):
        """
        Turn things one 1 by 1
        
        """
        time.sleep(5)
        
        for i, horn in enumerate(self.horn_pins):
            print (f"Test horn {horn}")
            horns = [False]*len(self.horn_pins)
            horns[i]=True
            self.sound_horn(horns)
            horns[i]=False
            time.sleep(1)

        for i, light in enumerate(self.light_pins):
            lights = [False]*len(self.light_pins)
            lights[i]=True
            self.set_lights(lights)
            print (f"Test light {light}")
            time.sleep(1)
            lights[i]=False
            self.set_lights(lights)
                
