#!/usr/bin/env python

import time               # Used to access current date & time
import os                 # Used to access file system
from datetime import datetime

class SnapshotCaptureImage:

#  # Initilize Object
#  def __init__(self):
    
  # Convert double decimal to degrees, minutes and seconds
  # used to save image exif gps location
  def convert_dd_to_dsm(self, dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    return "%d/1,%d/1,%d/1" % (int(degrees), int(minutes), round(seconds,2))

  # Convert latitude to reference from double decimal
  def convert_lat_ref(self, dd):
    if dd < 0:
      return "S"		# South
    else:
      return "N"		# North

  # Convert longitude to reference from double decimal
  def convert_lon_ref(self, dd):
    if dd < 0:
      return "W"		# West
    else:
      return "E"		# East

  # Convert altitude to reference from double decimal
  def convert_alt_ref(self, dd):
    if dd < 0:
      return "1"		# Below sea level
    else:
      return "0"		# Above sea level

  # Used to capture image (snapshot)
  def capture_image(self, image_width, image_height, image_quality, output_path, show_gps, gps_txt_tup):
    FEET_PER_METER = 3.2808399
    KILOMETERS_PER_MILE = 1.609344
    # Used to return the method used for image capture either raspistill or picamera
    image_method = 'raspistill'
    # Store current date and time
    timestr = time.strftime("%Y-%m-%d@%H-%M-%S")
    if (gps_txt_tup[0] != "*** NO GPS FIX! ***") and (show_gps == 'true'):
      if gps_txt_tup[5] != "None":
        new_date = datetime.strptime(gps_txt_tup[5], '%Y-%m-%dT%H:%M:%S.000Z')
        new_date_str = new_date.strftime('%Y:%m:%d')
        new_time_str = new_date.strftime('%H/1,%M/1,%S/1')
      else:
        new_date_str = ''
        new_time_str = ''
      # Capture still image
      os.system("raspistill -n -w %s -h %s -th '85:48:10' -t 500 -q %s -x GPS.GPSDateStamp='%s' -x GPS.GPSTimeStamp='%s' -x GPS.GPSLatitudeRef='%s'"
                " -x GPS.GPSLatitude='%s' -x GPS.GPSLongitudeRef='%s' -x GPS.GPSLongitude='%s'"
                " -x GPS.GPSAltitudeRef='%s' -x GPS.GPSAltitude='%s/1' -x GPS.GPSSpeedRef='M'"
                " -x GPS.GPSSpeed='%s/1' -x IFD0.Artist='Phantom Raspberry Blower'"
                " -x IFD0.Copyright='Copyright (c) 2015 Phantom Raspberry Blower'"
                " -x IFD0.Software='snapshot.py' -x IFD0.ImageDescription='Raspberry Pi Snapshot (current user)'"
                " -o %s.jpg" % (image_width, image_height, image_quality, (new_date_str), (new_time_str), self.convert_lat_ref(float(gps_txt_tup[1])), 
                str(self.convert_dd_to_dsm(float(gps_txt_tup[1]))), self.convert_lon_ref(float(gps_txt_tup[2])),
                str(self.convert_dd_to_dsm(float(gps_txt_tup[2]))), self.convert_alt_ref(int(float(gps_txt_tup[3])/FEET_PER_METER)),
                str(int(float(gps_txt_tup[3])/FEET_PER_METER)), str(int(float(gps_txt_tup[4])/KILOMETERS_PER_MILE)), (output_path + timestr)))
    else:
      os.system("raspistill -n -w %s -h %s -t 500 -q %s -x IFD0.Artist='Phantom Raspberry Blower'"
                " -x IFD0.Copyright='Copyright (c) 2015 Phantom Raspberry Blower'"
                " -x IFD0.Software='snapshot' -x IFD0.ImageDescription='Raspberry Pi Snapshot (current user)'"
                " -o %s.jpg" % (image_width, image_height, image_quality, (output_path + timestr)))

    image_full_path = output_path + timestr + ".jpg"
    image_type = 'jpg'

    # Check file exists. If not try to save the image using the 
    # picamera (PIL) module instead. This is required due to sms
    # messages commands do not create an image using the raspistill
    # command-line. Infuriatingly I don't know why!!!!
    if os.path.exists(image_full_path) != True:
      # Used to return the method used for image capture either raspistill or picamera
      image_method = 'picamera'
      import picamera
      with picamera.PiCamera() as camera:
        camera.resolution = (int(image_width), int(image_height))
        camera.exif_tags['IFD0.Artist'] = 'Phantom Raspberry Blower'
        camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2015 Phantom Raspberry Blower'
        camera.exif_tags['IFD0.Software'] = 'snapshot.py'
        camera.exif_tags['IFD0.ImageDescription'] = 'Raspberry Pi Snapshot (via sms)'
        if gps_txt_tup[0] != "*** NO GPS FIX! ***":
          if gps_txt_tup[5] != "None":
            new_date = datetime.strptime(gps_txt_tup[5], '%Y-%m-%dT%H:%M:%S.000Z')
            new_date_str = new_date.strftime('%Y:%m:%d')
            new_time_str = new_date.strftime('%H/1,%M/1,%S/1')
          else:
            new_date_str = ''
            new_time_str = ''
          camera.exif_tags['GPS.GPSLatitudeRef'] = self.convert_lat_ref(float(gps_txt_tup[1]))
          camera.exif_tags['GPS.GPSLatitude'] = str(self.convert_dd_to_dsm(float(gps_txt_tup[1])))
          camera.exif_tags['GPS.GPSLongitudeRef'] = self.convert_lon_ref(float(gps_txt_tup[2]))
          camera.exif_tags['GPS.GPSLongitude'] = str(self.convert_dd_to_dsm(float(gps_txt_tup[2])))
          camera.exif_tags['GPS.GPSAltitudeRef'] = self.convert_alt_ref(int(float(gps_txt_tup[3])/FEET_PER_METER))
          camera.exif_tags['GPS.GPSAltitude'] = "%s/1" % str(int(float(gps_txt_tup[3])/FEET_PER_METER))
          camera.exif_tags['GPS.GPSSpeedRef'] = 'M'
          camera.exif_tags['GPS.GPSSpeed'] = "%s/1" % str(int(float(gps_txt_tup[4])/KILOMETERS_PER_MILE))

          camera.exif_tags['GPS.GPSDateStamp'] = str(new_date_str)
          camera.exif_tags['GPS.GPSTimeStamp'] = str(new_time_str)
        #camera.start_preview()
        time.sleep(0.5)
        camera.capture(image_full_path, format='jpeg', quality=int(image_quality))
        #camera.stop_preview()
    return [image_full_path, timestr, image_type, image_method]
