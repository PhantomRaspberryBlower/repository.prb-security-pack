# GPS script to work with Adafruit Ultimate GPS Breakout component
# connected to Raspberry Pi using either UART (GPIO pins) or USB

# Date: 03 March 2015
# written by: Phantom Raspberry Blower

import xbmc, xbmcgui, xbmcaddon
import os
import smtplib
import commands
import time

from datetime import datetime
from resources.lib.GPSController import *

__addon__ = xbmcaddon.Addon(id='script.gps-locator')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__author__ = "Phantom Raspberry Blower"
__url__ = ""
__svn_url__ = ""
__credits__ = ""
 
#get actioncodes from https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h

ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10 
ACTION_NAV_BACK = 92

class GpsClass(xbmcgui.Window):
  # Initilize the GpsLocator class
  def __init__(self):
    self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    # Background Image
    self.window.setProperty('MyAddonIsRunning', 'true')
    self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, 'special://home/addons/script.gps-locator/background.jpg'))
    # Display Press HOME to exit
    self.lExit = xbmcgui.ControlLabel(1020, 80, 800, 200, '', 'font13', '0xFFFFFFFF')
    self.addControl(self.lExit)
    self.lExit.setLabel('Press SELECT to run')
    # GPS TIME CONTROLS
    self.lTime = xbmcgui.ControlLabel(340, 230, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lTime)
    self.lTime.setLabel('GPS Time:')
    self.vTime = xbmcgui.ControlLabel(620, 230, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.vTime)
    # Latitude CONTROLS
    self.lLatitude = xbmcgui.ControlLabel(340, 280, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lLatitude)
    self.lLatitude.setLabel('Latitude:')
    self.vLatitude = xbmcgui.ControlLabel(620, 280, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.vLatitude)
    # Longitude CONTROLS
    self.lLongitude = xbmcgui.ControlLabel(340, 330, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lLongitude)
    self.lLongitude.setLabel('Longitude:')
    self.vLongitude = xbmcgui.ControlLabel(620, 330, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.vLongitude)
    # Altitude CONTROLS
    self.lAltitude = xbmcgui.ControlLabel(340, 380, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lAltitude)
    self.lAltitude.setLabel('Altitude:')
    self.vAltitude = xbmcgui.ControlLabel(620, 380, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.vAltitude)
    # Speed CONTROLS
    self.lSpeed = xbmcgui.ControlLabel(340, 430, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lSpeed)
    self.lSpeed.setLabel('Speed:')
    self.vSpeed = xbmcgui.ControlLabel(620, 430, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.vSpeed)
    # Heading CONTROLS
    self.lHeading = xbmcgui.ControlLabel(340, 480, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lHeading)
    self.lHeading.setLabel('Heading:')
    self.vHeading = xbmcgui.ControlLabel(620, 480, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.vHeading)
    # Rate of Climb CONTROLS
    self.lClimb = xbmcgui.ControlLabel(340, 530, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.lClimb)
    self.lClimb.setLabel('Rate of Climb:')     
    self.vClimb = xbmcgui.ControlLabel(620, 530, 400, 200, '', 'font16', '0xFFFFFFFF')
    self.addControl(self.vClimb)

  def onAction(self, action):
    if action == ACTION_SELECT_ITEM:
      from cStringIO import StringIO
      file_str = StringIO()
      csv_file_str = StringIO()
      gpsc = GpsController()
      try:
        # Display waiting dialog (hourglass)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.disk_space_critical = self.critical_disk_space(output_path, disk_space_warning_percentage)
        gpsc.start()
        file_str.write('Time, Latitude, Longitude, Altitude (ft.), Speed (mph), Heading (deg.(true)), Rate of Climb (ft./min.)\n')
        for x in range(0,int(self.duration_count)):
          time.sleep(int(self.refresh_interval))
          self.lExit.setLabel('Please wait %s seconds' % str(int(self.duration_count) * int(self.refresh_interval) - (x * int(self.refresh_interval) + 1)))
          line_str = str(self.fetch_gps_data(gpsc))
          file_str.write(line_str)
          csv_file_str.write(line_str)
          file_str.write(line_str)

        # Check if user enabled recording of log
        if self.log_enabled == "true":

          # Check destination path exists
          if self.folder_exist(output_path) != True:
            self.message("Folder path '%s' does not exist!" % output_path, "Error")
            sys.exit()

          # Check destination path capacity
          if self.disk_space_critical == True:
            self.message("*** WARNING! Critical Disk Space ***\n\nDeleting oldest file...", "Warning")

            # Remove the oldest file from destination path
            self.filename_list.remove(self.oldest_file_in_tree(output_path, (".csv")))
            os.remove(self.oldest_file_in_tree(output_path, (".csv")))

          if self.file_exist(output_path + "/" + time.strftime("%Y-%m-%d") + ".csv"):
            # Append data to existing file
            file_obj = open(output_path + "/" + time.strftime("%Y-%m-%d") + ".csv", "a")
            file_obj.write(csv_file_str.getvalue())
          else:
            # Write data to a new file
            file_obj = open(output_path + "/" + time.strftime("%Y-%m-%d") + ".csv", "w")
            file_obj.write(file_str.getvalue())

          file_obj.close 

        self.lExit.setLabel('Press SELECT to run')

        self.email_msg = file_str.getvalue()
        if self.email_enabled == 'true':
           self.sendEmail()

      except:
        self.message('Something wicked happened :( \n' + str(sys.exc_info()[0]), 'Error Occurred!')
        raise

      finally:
        file_str.close()
        gpsc.stopController()
        gpsc.join()
        # Remove waiting dialog (like hourglass)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    if (action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK):
      #self.message('Goodbye', 'Exiting GPS')
      self.close()

  # Send email
  def sendEmail(self):
    from email.mime.text import MIMEText
    if len(self.email_recipient) > 0:
      try:
        msg = MIMEText(str(self.email_msg))
        msg['Subject'] = 'Raspberry Pi GPS Report (Kodi)'
        msg['From'] = str(self.email_sender)
        msg['To'] = str(self.email_recipient)

        # Send email
        smtpObj = smtplib.SMTP(str(self.smtp_server), str(self.smtp_server_port))
        smtpObj.login(str(self.username), str(self.password))
        smtpObj.sendmail(str(self.email_sender), str(self.email_recipient), msg.as_string())
        smtpObj.quit()
        self.message("Email sent successfully :)", "Email Sent")
        return True
  
      except:
        self.message('Something wicked happened :( \n' + str(sys.exc_info()[0]), 'Error Occurred!')
        raise

    else:
      return False

  # Display message to user
  def message(self, message, title):
    dialog = xbmcgui.Dialog()
    dialog.ok(title, message)

  # Used to find the oldest file in directory
  def oldest_file_in_tree(self, rootfolder, extension=".csv"):
    return min(
      (os.path.join(dirname, filename)
      for dirname, dirnames, filenames in os.walk(rootfolder)
      for filename in filenames
      if filename.endswith(extension)),
      key=lambda fn: os.stat(fn).st_mtime)

  # Used to check if folder exists
  def folder_exist(self, path):
    return os.path.isdir(path)

  # Used to check if file exists
  def file_exist(self, path):
    return os.path.exists(path)

  # Used to show free disk space
  def free_disk_space(self, path):
    st = os.statvfs(path)
    return float(st.f_bavail * st.f_frsize)

  # Used to show total disk space
  def total_disk_space(self, path):
    st = os.statvfs(path)
    return float(st.f_blocks * st.f_frsize)

  # Used to show used disk space
  def used_disk_space(self, path):
    st = os.statvfs(path)
    return float((st.f_blocks - st.f_bfree) * st.f_frsize)

  # Used to show crtitcal disk space
  def critical_disk_space(self, path, tolerance = 14):
    percent = (self.free_disk_space(path) / self.total_disk_space(path)) * 100
    if percent < tolerance:
      return True
    else:
      return False

  # Fetch serial connection name from id
  def FetchSerialName(self, conn):
    if conn == '4':
      return 'ttyAMA0'
    else:
      return 'ttyUSB%s' % str(conn)

  # Fetch gps data
  def fetch_gps_data(self, gpsc):
    self.vTime.setLabel(self.formatDateTime(str(gpsc.utc)))
    self.vLatitude.setLabel(str(gpsc.fix.latitude))
    self.vLongitude.setLabel(str(gpsc.fix.longitude))
    self.vAltitude.setLabel(str(round(gpsc.fix.altitude * FEET_PER_METER,1)) + ' ft')
    self.vSpeed.setLabel(str(gpsc.fix.speed) + ' mph')
    self.vHeading.setLabel(str(gpsc.fix.track) + ' deg (true)')
    self.vClimb.setLabel(str(gpsc.fix.climb) + ' ft/min')
    return str("%s, %s, %s, %s, %s, %s, %s\n" % (str(self.formatDateTime(str(gpsc.utc))), str(gpsc.fix.latitude), str(gpsc.fix.longitude), str(round(gpsc.fix.altitude * FEET_PER_METER,1)), str(gpsc.fix.speed), str(gpsc.fix.track), str(gpsc.fix.climb)))

  # Prepare gps socket
  def prepare_gps_socket(self):
    try:
      if self.prior_gpsd_process == False:
        os.system('python special://home/addons/script.gps-locator/resources/lib/apply_update.py')
        os.system('python special://home/addons/script.gps-locator/resources/lib/apply_update.py --gps-enabled = True --communication %s' % self.serial_connector)
      gpsc = GpsController()
      gpsc.start()
      timer = 10
      while len(str(gpsc.fix.latitude)) < 4 and timer > 0:
        time.sleep(0.5)
        timer -= 1
      self.email_msg = self.fetch_gps_data(gpsc)
    except:
      self.message('Something wicked happened :( \n' + str(sys.exc_info()[0]), 'Error Occurred!')
      raise
    finally:
      gpsc.stopController()
      gpsc.join()

  # Check if gpsd is already running
  def SearchPriorGpsdProcess(self, conn):
    output = commands.getoutput('ps -aux')
    if ('gpsd /dev/%s' % self.FetchSerialName(str(conn))) in output:
      self.prior_gpsd_process = True
    else:
      self.prior_gpsd_process = False

  # Format date and time to UK format
  def formatDateTime(self, utc):
    try:
      date_str = utc
      new_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.000Z')
      new_date_str = new_date.strftime('%d-%m-%Y  %H:%M:%S')
      return new_date_str
    except:
      return time.strftime("%d-%m-%Y  %H:%M:%S")

  # Fetch the current language settings
  def language_settings(self):
    __settings__ = xbmcaddon.Addon(id='script.gps')
    __language__ = __settings__.getLocalizedString
    self.lExit.setLabel(__language__(10001))
    self.lTime.setLabel(__language__(10002))
    self.lLatitude.setLabel(__language__(10003))
    self.lLongitude.setLabel(__language__(10004))
    self.lAltitude.setLabel(__language__(10005))
    self.lSpeed.setLabel(__language__(10006))
    self.lHeading.setLabel(__language__(10007))
    self.lClimb.setLabel(__language__(10008))
    self.no_gps_fix_txt = __language__(10009)
    self.please_wait_txt = __language__(10010)
    self.seconds_txt = __language__(10011)
    self.email_success_txt = __language__(10012)
    self.something_wicked_txt = __language__(10013)
    self.csv_heading_time = __language__(10014)
    self.csv_heading_lat = __language__(10015)
    self.csv_heading_lon = __language__(10016)
    self.csv_heading_alt = __language__(10017)
    self.csv_heading_speed = __language__(10018)
    self.csv_heading_heading = __language__(10019)
    self.csv_heading_climb = __language__(10020)

  # Fetch the configuration settings defined by the user
  def get_config_settings(self):
    __settings__ = xbmcaddon.Addon(id='script.gps')
    self.gps_enabled = __settings__.getSetting( "gps_enabled" )
    self.log_enabled = __settings__.getSetting( "log_enabled" )
    self.sms_commands_enabled = __settings__.getSetting( "sms_commands_enabled" )
    self.sms_keyword = __settings__.getSetting( "sms_keyword" )
    self.email_enabled = __settings__.getSetting( "email_enabled" )
    self.email_recipient = __settings__.getSetting( "email_recipient" )
    self.email_sender = __settings__.getSetting( "email_sender" )
    self.smtp_server = __settings__.getSetting( "smtp_server" )
    self.smtp_server_port = __settings__.getSetting( "smtp_server_port" )
    self.username = __settings__.getSetting( "username" )
    self.password = __settings__.getSetting( "password" )
    self.serial_connector = __settings__.getSetting( "serial_connector" )
    self.refresh_interval = int(__settings__.getSetting( "refresh_interval" ))
    self.duration = int(__settings__.getSetting( "duration" ))
    self.duration = self.duration * 60
    self.duration_count = int(self.duration / self.refresh_interval)

# Start main routine
if ( __name__ == "__main__" ):
  gps_enabled = False 
  log_enabled = False
  sms_commands_enabled = False
  sms_keyword = ''
  email_enabled = False
  email_recipient = ''
  email_sender = ''
  email_msg = ''
  smtp_server = ''
  smtp_server_port = ''
  username = ''
  password = ''
  serial_connector = ''
  refresh_interval = 1
  duration = 1
  duration_count = 60
  prior_gpsd_process = False
  output_path = '/media/CAMERA_DCIM/GPS'
  disk_space_warning_percentage = 14
  disk_space_critical = False

  no_gps_fix_txt = '*** No GPS Fix ***'
  email_success_txt = 'Email sent successfully :)'
  something_wicked_txt = 'Something wicked happened :('
  press_select_txt = 'Press SELECT to begin'
  please_wait_txt = 'Please wait '
  seconds_txt = ' seconds' 
  csv_heading_time = 'Time'
  csv_heading_lat = 'Latitude'
  csv_heading_lon = 'Longitude'
  csv_heading_alt = 'Altitude (ft.)'
  csv_heading_speed = 'Speed (mph)'
  csv_heading_heading = 'Heading (deg. (true))'
  csv_heading_climb = 'Rate of Climb (ft./min.)'

  window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
  if window.getProperty('MyAddonIsRunning') != 'true':
    # Display waiting dialog (like hourglass)
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    FEET_PER_METER = 3.2808399
    mydisplay = GpsClass()
    mydisplay.language_settings()
    mydisplay.get_config_settings()
    mydisplay.SearchPriorGpsdProcess(mydisplay.serial_connector)
    mydisplay.prepare_gps_socket()
    prior_gpsd_process = mydisplay.prior_gpsd_process
    # Remove waiting dialog (like hourglass)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    mydisplay .doModal()
    del mydisplay
    window.setProperty('MyAddonIsRunning', 'false')
    if prior_gpsd_process == False:
      os.system('python special://home/addons/script.gps-locator/resources/lib/apply_update.py')
