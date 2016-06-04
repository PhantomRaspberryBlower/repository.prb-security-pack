# Dashcam script to work with PiCamera component
# connected to Raspberry Pi using CSI

# Date: 03 April 2015
# written by: Phantom Raspberry Blower

import xbmc, xbmcgui, xbmcaddon
import os
import commands
import time

from datetime import datetime

#from resources.lib.SnapshotFileIO import SnapshotFileIO
from resources.lib.SnapshotGPS import SnapshotGPS
#from resources.lib.SnapshotCaptureImage import SnapshotCaptureImage
#from resources.lib.SnapshotTextOverlay import SnapshotTextOverlay
#from resources.lib.SnapshotSendEmail import SnapshotSendEmail
#from resources.lib.SnapshotLogFile import SnapshotLogFile

import xml.etree.ElementTree as et

#__addon__ = xbmcaddon.Addon(id='script.dashcam')
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

class DashcamClass(xbmcgui.Window):
  # Initilize the Dashcam class
  def __init__(self):
    self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    # Background Image
    self.window.setProperty('MyAddonIsRunning', 'true')
    self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, 'special://home/addons/script.module.dashcam/background.jpg'))
    # Display Press HOME to exit
    self.lExit = xbmcgui.ControlLabel(470, 25, 800, 200, '', 'font16', '0xFF868784', )
    self.addControl(self.lExit)
    self.lExit.setLabel('Press SELECT to start/stop Dashcam')
    self.lProgressUpdate = xbmcgui.ControlLabel(320, 560, 1280, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lProgressUpdate)
    self.lProgressUpdate.setLabel('')

  # Button press
  def onAction(self, action):
    if action == ACTION_SELECT_ITEM:
      try:
#        # Display waiting dialog (like hourglass)
#        xbmc.executebuiltin("ActivateWindow(busydialog)")
        width = self.Dimensions(self.FetchResolution(self.image_resolution))[0]
        height = self.Dimensions(self.FetchResolution(self.image_resolution))[1]

        ###########################
        # BULIS PLACE ACTION HERE #
        ###########################

        self.lProgressUpdate.setLabel('')
#        # Remove waiting dialog (like hourglass)
#        xbmc.executebuiltin("Dialog.Close(busydialog)")
      except:
        self.message("Something wicked happened :(", "Error!")
        sys.exit()

    if (action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK):
      self.close()

  # Fetch gps location
  # ------------------
  def get_gps_location(self):
    sgps = SnapshotGPS()
    return sgps.prepare_gps_socket()

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

#  # Used to capture image (dashcam)
#  def capture_image(self, image_width, image_height, image_quality, image_output_path):
#    # Store current date and time
#    timestr = time.strftime("%Y-%m-%d@%H-%M-%S")
#    # Capture still image
#    os.system("raspivid -n -w " + str(image_width) + " -h " + str(image_height) + " -t 500 -q " + str(image_quality) + " -o " + output_path + timestr + ".jpg")
#    image_full_path = image_output_path + timestr + ".h264"
#    image_type = 'jpg'
#    return [image_full_path, timestr, image_type]

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
    __settings__ = xbmcaddon.Addon(id='script.dashcam')
    __language__ = __settings__.getLocalizedString
    self.lExit.setLabel(__language__(10001))
    self.please_wait_txt = __language__(10010)
    self.email_success_txt = __language__(10012)
    self.something_wicked_txt = __language__(10013)

  # Fetch the configuration settings defined by the user
  def get_config_settings(self):
    __settings__ = xbmcaddon.Addon(id='script.dashcam')
    self.dashcam_enabled = __settings__.getSetting( "dashcam_enabled" )
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
  dashcam_enabled = False
  email_enabled = 'false'
  email_from = ''
  email_msg = ''
  email_to = ''
  gps_text_overlay_enabled = False
  image_quality = '10'
  image_resolution = ''
  log_enabled = False
  output_path = '/media/CAMERA_DCIM/Dashcam/'
  sms_commands_enabled = False
  sms_from = ''
  sms_keyword = ''
  smtp_server = ''
  smtp_server_port = ''
  text_overlay_enabled = False
  username = ''
  password = ''
  email_success_txt = 'Email sent successfully :)'
  something_wicked_txt = 'Something wicked happened :('
  press_select_txt = 'Press SELECT to begin'
  email_subject = 'Raspberry Pi Dashcam Image (kodi)'

  window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
  if window.getProperty('MyAddonIsRunning') != 'true':
    # Display waiting dialog (like hourglass)
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    mydisplay = DashcamClass()
    mydisplay.language_settings()
    mydisplay.get_config_settings()
    # Remove waiting dialog (like hourglass)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    mydisplay.doModal()
    del mydisplay
    window.setProperty('MyAddonIsRunning', 'false')
