import RPi.GPIO as GPIO
import threading
import time

class ReplayControl:
    def __init__(self, light_pins, horn_pins):
        self.light_pins = light_pins
        self.horn_pins = horn_pins
        self.horn_status = []

        # Use BCM channel numbers rather than pin numbers
        GPIO.setmode(GPIO.BCM)

        # Enable all pins as output pins and ensure they are off
        for pin in light_pins:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        for pin in horn_pins:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            self.horn_status.append(0)

    def set_lights(self, lights):
        for i, status in enumerate(lights):
            GPIO.output(self.light_pins[i],GPIO.HIGH is status else GPIO.LOW)

    def sound_horn(self, horns):
        for i, status in enumerate(horns):
            if status:
                GPIO.output(self.horn_pins[i],GPIO.HIGH)
                silence_thread = threading.Thread(target=self.silence_horn, args=(i,))
                silence_thread.start()
                
    def start_test(self):
        silence_thread = threading.Thread(target=self.run_tests, args=("ignore",))
        silence_thread.start()
        
    def run_tests(self, ignore):
        """
        Turn things one 1 by 1
        
        """
        time.sleep(5)

        for horn in self.horn_pins:
            GPIO.output(horn,GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(horn,GPIO.LOW)
            time.sleep(1)

        for light in self.light_pins:
            GPIO.output(light,GPIO.HIGH)
            time.sleep(5)
            GPIO.output(light,GPIO.LOW)
            time.sleep(1)

    def silence_horn(self, horn):
        """
        Silence a horn after 1 second.  This would be invoked in a separate thread

        """
        time.sleep(1)
        GPIO.output(self.horn_pins[horn],GPIO.LOW)
