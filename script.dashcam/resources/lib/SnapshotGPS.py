#!/usr/bin/env python

import os
import time

# Used to fetch user defined settings in kodi
import xml.etree.ElementTree as et
from GPSController import *

class SnapshotGPS:

  # Initilize Object
  def __init__(self):
    self.serial_connector = 'ttyAMA0'
    user_settings_path = '/home/pi/.kodi/userdata/addon_data/script.gps/settings.xml'
    # Open the settings xml file (/home/pi/.kodi/userdata/addon_data/script.gps)
    tree = et.parse(user_settings_path)
    root = tree.getroot()
    for child in root:
      if child.get('id') == 'serial_connector':
        self.serial_connector = self.fetch_serial_name(child.get('value'))
    self.search_prior_gpsd_process(self.serial_connector)
    
  # Fetch serial connection name from id
  def fetch_serial_name(self, conn):
    if conn == '4':
      return 'ttyAMA0'
    else:
      return 'ttyUSB%s' % str(conn)

  # Fetch gps data
  def fetch_gps_data(self, gpsc):
    FEET_PER_METER = 3.2808399
    tup = ("*** NO GPS FIX! ***",);
    if len(str(gpsc.fix.latitude)) > 3:
      tup = (self.formatDateTime(str(gpsc.utc)), float(gpsc.fix.latitude),
             float(gpsc.fix.longitude), float(round(gpsc.fix.altitude * FEET_PER_METER,1)),
             float(round(gpsc.fix.speed,1)), str(gpsc.utc));
    return tup

  # Prepare gps socket
  def prepare_gps_socket(self):
    gpsc = GpsController()
    gpsc.start()
    try:
      if self.prior_gpsd_process == False:
        os.system('python /home/pi/python_scripts/gps/gps_locator/resources/lib/apply_update.py')
        os.system('python /home/pi/python_scripts/gps/gps_locator/resources/lib/apply_update.py --gps-enabled = True --communication %s' % self.serial_connector)
      timer = 10
      while len(str(gpsc.fix.latitude)) < 4 and timer > 0:
        time.sleep(0.5)
        timer -= 1
      return self.fetch_gps_data(gpsc)
    except:
      print('Something wicked happened! :( \n' + str(sys.exc_info()[0]))
      raise
    finally:
      gpsc.stopController()
      gpsc.join()

  # Check if gpsd is already running
  def search_prior_gpsd_process(self, conn):
    import commands
    output = commands.getoutput('ps -aux')
    if ('gpsd /dev/%s' % (str(conn))) in output:
      self.prior_gpsd_process = True
    else:
      self.prior_gpsd_process = False

  # Format date and time to human readable 
  def formatDateTime(self, utc):
    try:
      date_str = utc
      new_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.000Z')
      new_date_str = new_date.strftime('%d-%m-%Y %H:%M:%S')
      return new_date_str
    except:
      return time.strftime("%d-%m-%Y %H:%M:%S")

