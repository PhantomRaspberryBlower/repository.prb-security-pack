#!/usr/bin/env python

# Used to fetch user defined settings in kodi
import xml.etree.ElementTree as et

class SnapshotKodiUserSettings:

  # Initilize Object
  def __init__(self, path):
    self.output_path = path

  # Used to extrapulate width & height from resolution string
  def image_dimensions(self, img_res):
    tup = img_res.split('x')
    w = tup[0]
    h = tup[1]
    return w, h

  # Fetch image resolution from id
  def fetch_resolution(self, int):
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

  # Fetch user settings (set via the kodi addon: script.snapshot)
  def get_kodi_user_settings(self, path):
    email_enabled = 'false'
    email_from = ''
    email_to = ''
    gps_text_overlay_enabled = 'false'
    image_height = 720
    image_quality = 10
    image_resolution = '1280x720'
    image_width = 1280
    log_enabled = 'false'
    output_path = ''
    password = ''
    sms_commands_enabled = 'false'
    sms_keyword = 'ping-pong'
    smtp_server = ''
    smtp_server_port = 25
    snapshot_enabled = 'true'
    text_overlay_enabled = 'false'
    username = ''

    # Open the settings xml file (.kodi/userdata/addon_data/script.snapshot)
    tree = et.parse(path)
    root = tree.getroot()
    for child in root:
      if child.get('id') == 'email_enabled':
        email_enabled = child.get('value')
      elif child.get('id') == 'email_from':
        email_from = child.get('value')
      elif child.get('id') == 'email_to':
        email_to = child.get('value')
      elif child.get('id') == 'gps_text_overlay_enabled':
        gps_text_overlay_enabled = child.get('value')
      elif child.get('id') == 'image_quality':
        image_quality = child.get('value')
      elif child.get('id') == 'image_resolution':
        image_resolution = child.get('value')
        img_dim = self.image_dimensions(self.fetch_resolution(str(image_resolution)))
        image_width = img_dim[0]
        image_height = img_dim[1]
      elif child.get('id') == 'log_enabled':
        log_enabled = child.get('value')
      elif child.get('id') == 'output_path':
        output_path = child.get('value')
      elif child.get('id') == 'password':
        password = child.get('value')
      elif child.get('id') == 'sms_commands_enabled':
        sms_commands_enabled = child.get('value')
      elif child.get('id') == 'sms_keyword':
        sms_keyword = child.get('value')
      elif child.get('id') == 'smtp_server':
        smtp_server = child.get('value')
      elif child.get('id') == 'smtp_server_port':
        smtp_server_port = child.get('value')
      elif child.get('id') == 'snapshot_enabled':
        snapshot_enabled = child.get('value')
      elif child.get('id') == 'text_overlay_enabled':
        text_overlay_enabled = child.get('value')
      elif child.get('id') == 'username':
        username = child.get('value')

    tup = (email_enabled, email_from, email_to, gps_text_overlay_enabled,
           image_height, image_quality, image_resolution, image_width,
           log_enabled, output_path, password, sms_commands_enabled,
           sms_keyword, smtp_server, smtp_server_port, snapshot_enabled,
           text_overlay_enabled, username)
    return tup