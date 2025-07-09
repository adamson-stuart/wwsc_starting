import threading
import time

class DummyRelayControl:
    def __init__(self, light_pins, horn_pins):
        self.light_pins = light_pins
        self.horn_pins = horn_pins
        self.horn_status = []

    def set_lights(self, lights):
        print (f"Light set to {lights}")

    def sound_horn(self, horns):
        print (f"Horn set to {horns}")
                
