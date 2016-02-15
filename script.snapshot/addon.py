# Snapshot script to work with PiCamera component
# connected to Raspberry Pi using CSI

# Date: 03 April 2015
# written by: Phantom Raspberry Blower

import xbmc, xbmcgui, xbmcaddon
import os
import commands
import time

from datetime import datetime

from resources.lib.SnapshotFileIO import SnapshotFileIO
from resources.lib.SnapshotGPS import SnapshotGPS
from resources.lib.SnapshotCaptureImage import SnapshotCaptureImage
from resources.lib.SnapshotTextOverlay import SnapshotTextOverlay
from resources.lib.SnapshotSendEmail import SnapshotSendEmail
from resources.lib.SnapshotLogFile import SnapshotLogFile

import xml.etree.ElementTree as et

#__addon__ = xbmcaddon.Addon(id='script.snapshot')
#__addonname__ = __addon__.getAddonInfo('name')
#__icon__ = __addon__.getAddonInfo('icon')
#__author__ = "phantom_raspberry_blower"
#__url__ = ""
#__svn_url__ = ""
#__credits__ = ""

#get actioncodes from https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10 
ACTION_NAV_BACK = 92

class SnapshotClass(xbmcgui.Window):
  # Initilize the Snapshot class
  def __init__(self):
    self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    # Background Image
    self.window.setProperty('MyAddonIsRunning', 'true')
    self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, special://home/addons/script.module.snapshot/background.jpg'))
    # Display Press HOME to exit
    self.lExit = xbmcgui.ControlLabel(470, 25, 800, 200, '', 'font16', '0xFF868784', )
    self.addControl(self.lExit)
    self.lExit.setLabel('Press SELECT to take snapshot')
    self.imgSnapshot = xbmcgui.ControlImage(320, 180, 640, 360, special://home/addons/script.module.snapshot/snapshot.jpg')
    self.addControl(self.imgSnapshot)
    self.lProgressUpdate = xbmcgui.ControlLabel(320, 560, 1280, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lProgressUpdate)
    self.lProgressUpdate.setLabel('')

  # Button press
  def onAction(self, action):
    if action == ACTION_SELECT_ITEM:
      try:
        # Display waiting dialog (like hourglass)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        width = self.Dimensions(self.FetchResolution(self.image_resolution))[0]
        height = self.Dimensions(self.FetchResolution(self.image_resolution))[1]

        # Check destination path exists if it does check free-space is
        # greater that disk space warning percentage (default is 14%)
        # if it doesn't then remove the oldest file in path
        sfio = SnapshotFileIO(output_path, DISK_SPACE_WARNING_PERCENTAGE, ".jpg")
        if sfio.folder_exist(output_path) != True:
          self.message("Folder path '%s' does not exist!" % output_path, "Error Occurred!")
          sys.exit()

        # Fetch gps location
        if (self.gps_text_overlay_enabled == 'true') and (self.text_overlay_enabled == 'true'):
          self.lProgressUpdate.setLabel('Polling gps device ...')
          sgps = SnapshotGPS()
          gps_txt_tup = sgps.prepare_gps_socket()
        else:
          gps_txt_tup = ("*** NO GPS FIX! ***",);

        # Capture image
        self.lProgressUpdate.setLabel('Capturing image ...')
        sci = SnapshotCaptureImage()
        image_return_values = sci.capture_image(width, height, image_quality, output_path, self.gps_text_overlay_enabled, gps_txt_tup)
        image_full_path = image_return_values[0]
        filename =  image_return_values[1]
        image_type = image_return_values[2]
        image_capture_method = image_return_values[3]
        if image_capture_method == 'raspistill':
          subject_new = email_subject.replace(")", " - Current User)")
        else:
          subject_new = email_subject.replace(")", " - SMS Request)")
        self.email_subject = subject_new

        # Add text overlay
        if self.text_overlay_enabled == 'true':
          self.lProgressUpdate.setLabel('Adding text overlay ...')
          self.add_text_overlay(str(image_full_path), self.gps_text_overlay_enabled, gps_txt_tup)

        self.imgSnapshot.setImage(image_full_path)

        # Send email with images as attachments
        if self.email_enabled == 'true':
          self.lProgressUpdate.setLabel('Sending email ...')
          sse = SnapshotSendEmail(False)
          if sse.send_email(self.email_to, 
                     self.email_from, 
                     self.username,
                     self.password,
                     self.smtp_server,
                     self.smtp_server_port,
                     self.email_subject,
                     output_path,
                     filename,
                     image_full_path,
                     image_type,
                     gps_txt_tup) == True:
            self.message('Email sent succesully :)', 'Email Sent.')

        # Save to log file
        if self.log_enabled == 'true':
          import time
          self.lProgressUpdate.setLabel('Saving log file ...')
          if gps_txt_tup[0] == "*** NO GPS FIX! ***":
            log_tup = (gps_txt_tup[0], 0.0, 0.0, 0.0, 0.0, '',
                       str(filename + "." + image_type), str(self.email_subject), '',
                       str(self.email_to));
          else:
            log_tup = (gps_txt_tup[0], float(gps_txt_tup[1]), float(gps_txt_tup[2]),
                       float(gps_txt_tup[3]), float(gps_txt_tup[4]), str(gps_txt_tup[5]),
                       str(filename + "." + image_type), str(self.email_subject), '',
                       str(self.email_to));
          slf = SnapshotLogFile()
          slf.record_log_file(output_path, log_tup, DISK_SPACE_WARNING_PERCENTAGE)
          time.sleep(1)
      except:
        self.message('Something wicked happened :( \n' + str(sys.exc_info()[0]), 'Error Occurred!')
        raise

      finally:
        self.lProgressUpdate.setLabel('')
        # Remove waiting dialog (like hourglass)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    if (action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK):
      #self.message('Goodbye', 'Exiting GPS')
      self.close()

  # Fetch gps location
  # ------------------
  def get_gps_location(self):
    sgps = SnapshotGPS()
    return sgps.prepare_gps_socket()

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

  # Display message to user
  def message(self, message, title):
    dialog = xbmcgui.Dialog()
    dialog.ok(title, message)

  # Used to extrapulate width & height from resolution string
  def Dimensions(self, img_res):
    t = img_res.split('x')
    w = t[0]
    h = t[1]
    return w, h

  # Used to capture image (snapshot)
  def capture_image(self, image_width, image_height, image_quality, image_output_path):
    # Store current date and time
    timestr = time.strftime("%Y-%m-%d@%H-%M-%S")
    # Capture still image
    os.system("raspistill -n -w " + str(image_width) + " -h " + str(image_height) + " -t 500 -q " + str(image_quality) + " -o " + output_path + timestr + ".jpg")
    image_full_path = image_output_path + timestr + ".jpg"
    image_type = 'jpg'
    return [image_full_path, timestr, image_type]

  # Fetch image resolution from id
  def FetchResolution(self, int):
    if int == '4':
      return '1920x1080'
    elif int == '3':
      return '1280x800'
    elif int == '2':
      return '1280x720'
    elif int == '1':
      return '800x600'
    elif int == '0':
      return '640x480'
    else:
      return ''

  # Fetch the current language settings
  def language_settings(self):
    __settings__ = xbmcaddon.Addon(id='script.snapshot')
    __language__ = __settings__.getLocalizedString
    self.lExit.setLabel(__language__(10001))
    self.please_wait_txt = __language__(10010)
    self.email_success_txt = __language__(10012)
    self.something_wicked_txt = __language__(10013)

  # Fetch the configuration settings defined by the user
  def get_config_settings(self):
    __settings__ = xbmcaddon.Addon(id='script.snapshot')
    self.snapshot_enabled = __settings__.getSetting( "snapshot_enabled" )
    self.image_quality = __settings__.getSetting( "image_quality" )
    self.image_resolution = __settings__.getSetting( "image_resolution" )
    self.output_path = __settings__.getSetting( "output_path" )
    self.log_enabled = __settings__.getSetting( "log_enabled" )
    self.text_overlay_enabled = __settings__.getSetting( "text_overlay_enabled" )
    self.gps_text_overlay_enabled = __settings__.getSetting( "gps_text_overlay_enabled" )
    self.sms_commands_enabled = __settings__.getSetting( "sms_commands_enabled" )
    self.sms_keyword = __settings__.getSetting( "sms_keyword" )
    self.email_enabled = __settings__.getSetting( "email_enabled" )
    self.email_to = __settings__.getSetting( "email_to" )
    self.email_from = __settings__.getSetting( "email_from" )
    self.smtp_server = __settings__.getSetting( "smtp_server" )
    self.smtp_server_port = __settings__.getSetting( "smtp_server_port" )
    self.username = __settings__.getSetting( "username" )
    self.password = __settings__.getSetting( "password" )

######################
# Start main routine #
######################
if ( __name__ == "__main__" ):
  DISK_SPACE_WARNING_PERCENTAGE = 14
  email_enabled = 'false'
  email_from = ''
  email_msg = ''
  email_to = ''
  gps_text_overlay_enabled = False
  image_quality = '10'
  image_resolution = ''
  log_enabled = False
  output_path = '/media/CAMERA_DCIM/Snapshot/'
  sms_commands_enabled = False
  sms_from = ''
  sms_keyword = ''
  smtp_server = ''
  smtp_server_port = ''
  snapshot_enabled = False
  text_overlay_enabled = False
  username = ''
  password = ''
  email_success_txt = 'Email sent successfully :)'
  something_wicked_txt = 'Something wicked happened :('
  press_select_txt = 'Press SELECT to begin'
  email_subject = 'Raspberry Pi Snapshot Image (kodi)'

  window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
  if window.getProperty('MyAddonIsRunning') != 'true':
    # Display waiting dialog (like hourglass)
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    mydisplay = SnapshotClass()
    mydisplay.language_settings()
    mydisplay.get_config_settings()
    # Remove waiting dialog (like hourglass)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    mydisplay .doModal()
    del mydisplay
    window.setProperty('MyAddonIsRunning', 'false')