import RPi.GPIO as GPIO
import threading
import time

class RelayControl:
    def __init__(self, light_pins, horn_pins, start_pin):
        self.light_pins = light_pins
        self.horn_pins = horn_pins
        self.start_pin = start_pin
        self.light_status = [False]*len(light_pins)
        self.horn_status = [False]*len(horn_pins)
        
        self.callback = None

        # Use BCM channel numbers rather than pin numbers
        GPIO.setmode(GPIO.BCM)

        # Enable all pins as output pins and ensure they are off
        for pin in light_pins:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        for pin in horn_pins:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Set the remote start pin as input and enable to internal pull down resistor
        GPIO.setup(self.start_pin, GPIO.IN, GPIO.PUD_DOWN)

        self.start_remote_start_monitor()

    def set_callback(self, callback):
        self.callback = callback

    def set_lights(self, lights):
        for i, status in enumerate(lights):
            GPIO.output(self.light_pins[i],GPIO.HIGH if status else GPIO.LOW)
            self.light_status[i]=status
        if self.callback is not None:
            self.callback.relay_callback(self.light_status,self.horn_status)


    def sound_horn(self, horns):
        for i, status in enumerate(horns):
            if status>0:
                GPIO.output(self.horn_pins[i],GPIO.HIGH)
                self.horn_status[i]=status
                if self.callback is not None:
                    self.callback.relay_callback(self.light_status,self.horn_status)

                # Start a thread to silence the horn after a short period of time
                silence_thread = threading.Thread(target=self.silence_horn, args=(i,status))
                silence_thread.start()
                
    def start_remote_start_monitor(self):
        remote_thread = threading.Thread(target=self.check_starting_order, args=("ignore",))
        remote_thread.start()

    def check_starting_order(self, ignore):
        """
        Check to see if the remote start has been activated. This is checked every 100ms.  Once activated any
        further presses are ignored for another 20 seconds to "debounce" the signal 
        """
        while True:
            if GPIO.input(self.start_pin):
                if self.callback is not None:
                    self.callback.remote_start()
                    time.sleep(20)
            time.sleep(0.1)

    def start_test(self):
        test_thread = threading.Thread(target=self.run_tests, args=("ignore",))
        test_thread.start()
        
    def run_tests(self, ignore):
        """
        Turn things one 1 by 1
        
        """

        for i,horn in enumerate(self.horn_pins):
            horns=[0]*len(self.horn_pins)
            horns[i] = 0.5
            self.sound_horn(horns)
            time.sleep(1)

        for i,light in enumerate(self.light_pins):
            lights=[0]*len(self.light_pins)
            lights[i] = 0.5
            self.set_lights(lights)
            time.sleep(1)
        lights=[0]*len(self.light_pins)
        self.set_lights(lights)

    def silence_horn(self, horn, delay):
        """
        Silence a horn after delay seconds.  This would be invoked in a separate thread

        """
        time.sleep(delay)
        GPIO.output(self.horn_pins[horn],GPIO.LOW)
        self.horn_status[horn]=False
        if self.callback is not None:
            self.callback.relay_callback(self.light_status,self.horn_status)

