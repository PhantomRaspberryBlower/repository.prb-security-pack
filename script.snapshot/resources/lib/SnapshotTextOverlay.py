#!/usr/bin/env python

import time       # Used to access current date & time
import os		# Used to access file system

class SnapshotTextOverlay:

  # Add text overlay
  # ----------------
  def add_text_overlay(self, image_file, show_gps, gps_txt_tup):
    now = time.strftime("%a %d-%m-%Y %X")
    if show_gps == 'true':
      if gps_txt_tup[0] != "*** NO GPS FIX! ***":
        os.system("convert '%s' \\\n -gravity north -pointsize 22 -fill white -undercolor '#00000080' -annotate +0+5 ' %s ' \\\n"
                  " -gravity southwest -pointsize 22 -fill white -annotate +0+5 ' Latitude: %s \n Longitude: %s ' \\\n"
                  " -gravity southeast -pointsize 22 -fill white -annotate +0+5 ' Altitude: %s ft. \n Speed: %s mph ' \\\n"
                  " %s" % (image_file, now, gps_txt_tup[1], gps_txt_tup[2], gps_txt_tup[3], gps_txt_tup[4], image_file))
      else:
        os.system("convert '%s' \\\n -gravity north -pointsize 22 -fill white -undercolor '#00000080' -annotate +0+5 ' %s ' \\\n"
                  " -gravity south -pointsize 22 -fill white -annotate +0+5 '*** NO GPS FIX ***' %s" % (image_file, now, image_file))  
    else:
      os.system("convert '%s' \\\n -gravity north -pointsize 22 -fill white -undercolor '#00000080' -annotate +0+5 ' %s ' \\\n"
                " %s" % (image_file, now, image_file))
