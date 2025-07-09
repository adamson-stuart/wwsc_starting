from wwsc.starting.race_sequence import RaceSequence
from wwsc.starting.dummy_relay_control import DummyRelayControl
from wwsc.starting.camera_control import CameraControl

race = RaceSequence(DummyRelayControl([1,2,3],[4,5]), CameraControl())

race.start()