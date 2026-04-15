# wwsc_starting
WWSC Racing Start System

# Running
python wwsc/starting/gui.py <optional video>

If you provide an arguement to the program then it will attempt to load this video for simulation rather than using a camera.  This
is useful for development


# Required libraries
Other than a recent python version you will require the following installed
- QT5 and the python bindings
- Python opencv library

# Running without a Raspberry PI
This progream is designed to be run on a raspberry PI and uses the RPi GPIO library in order to control the lights and horns.
If you wish to run on a non PI device for development of other parts of the system this can be easily achieved by renaming the
RPi_DUMMY folder to RPi.  This will then provide enough of the RPi GPIO library for the program to run - of course it won't be able 
to control anything!
