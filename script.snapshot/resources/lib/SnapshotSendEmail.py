#!/usr/bin/env python

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class SnapshotSendEmail:

  # Initilize Object
  def __init__(self, verbose):
    self.verbose = verbose

  # Used to send email
  def send_email(self, send_to, sent_from, username, password, smtp_server, port, subject, output_path, filename, image_full_path, image_type, gps_tup):
    hyper_link = ''
    if str(gps_tup[0]) != "*** NO GPS FIX! ***":
      if len(str(gps_tup[1])) > 3:
        hyper_link = ('<a href="http://www.openstreetmap.org/?mlat=%s&mlon=%s&zoom=16">OpenStreetMap</a>'
                      '  -  <a href="https://www.google.com/maps/search/%s,%s">Google Maps</a>'
                      '  -  <a href="http://www.bing.com/maps/?v=2&cp=%s~%s&lvl=17&dir=0&sty=r&sp=Point.%s_%s">Bing Maps</a><br>' % 
                      (gps_tup[1], gps_tup[2], gps_tup[1], gps_tup[2], gps_tup[1], gps_tup[2], gps_tup[1], gps_tup[2]))

    if len(send_to) > 0:
      # Send email with images as attachments
      try:
        fp = open(image_full_path)
        msgImage = MIMEImage(fp.read(), image_type)
        fp.close()
        msg = MIMEMultipart('related')
        msg["From"] = sent_from
        msg["To"] = send_to
        msg["Subject"] = subject
        msg.preamble = "The Phantom Raspberry Blower has struck again!"

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)
        msgText = MIMEText('Snapshot taken from Raspberry Pi Dash Camera.', 'plain')
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        msgText = MIMEText('<b>Snapshot taken from Raspberry Pi Dash Camera.'
                           '</b><br><img src="cid:image1">%s<br>The Phantom Raspberry Blower'
                           ' has struck again!<br>' % hyper_link, 'html')
        msgAlternative.attach(msgText)

        # Define the image's ID as referenced above
        msgImage.add_header('Content-Type', 'image/jpg', filename=filename + '.jpg')
        msgImage.add_header('Content-ID', 'image1')
        msgImage.add_header('Content-Disposition', 'inline', filename=filename + '.jpg')
        msg.attach(msgImage)

        # Send email and image attachment
        smtpObj = smtplib.SMTP(smtp_server, port)
        smtpObj.login(username, password)
        smtpObj.sendmail(sent_from, send_to, msg.as_string())
        smtpObj.quit()
        if self.verbose ==True:
          print("Email sent successfully :)")
        return True
      except smtplib.SMTPException:
        print("Something wicked happened :(")
        return False
    else:
      print("No email settings!")
      return False
