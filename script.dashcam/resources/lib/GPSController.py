# Script obtained from Martin O'Hanlon  GitHub account
# https://github.com/martinohanlon/vidGPSOverlay/blob/master/GPSController.py

from gps import *
import threading

class GpsController(threading.Thread):
    def __init__(self):
      threading.Thread.__init__(self)
      self.gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
      self.running = False

    def run(self):
      self.running = True
      while self.running:
        # grab EACH set of gpsd info to clear the buffer
        self.gpsd.next()

    def stopController(self):
      self.running = False

    @property
    def fix(self):
      return self.gpsd.fix

    @property
    def utc(self):
      return self.gpsd.utc

    @property
    def satellites(self):
      return self.gpsd.satellites