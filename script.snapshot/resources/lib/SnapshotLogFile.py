#!/usr/bin/env python

import time
from resources.lib.SnapshotFileIO import SnapshotFileIO
from cStringIO import StringIO

class SnapshotLogFile:

  # Save settings to log file
  def record_log_file(self, path, log_tup, disk_space_warning_percentage):
    file_str = StringIO()
    csv_file_str = StringIO()
    file_str.write('Local Time, Latitude, Longitude, Altitude (ft.), '
                   'Speed (mph), GPS Time (utc), Image File, Image '
                   'Description, SMS Mobile Number, Email\n')
    line_str = ("%s, %f, %f, %f, %f, %s, %s, %s, '%s', %s\n" %
               (log_tup[0], log_tup[1], log_tup[2], log_tup[3],
                log_tup[4], log_tup[5], log_tup[6], log_tup[7],
                log_tup[8].replace("+44","(+44)"), log_tup[9]))
    file_str.write(line_str)
    csv_file_str.write(line_str)

    # Check destination path exists if it does check free-space is
    # greater that disk space warning percentage (default is 14%)
    # if it doesn't then remove the oldest file in path
    sfio = SnapshotFileIO(path, disk_space_warning_percentage, ".csv")
    if sfio.folder_exist(path) != True:
      sys.exit()
    if sfio.file_exist(path + "/" + time.strftime("%Y-%m-%d") + ".csv"):
      file_obj = open(path + "/" + time.strftime("%Y-%m-%d") + ".csv", "a")
      file_obj.write(csv_file_str.getvalue())
    else:
      file_obj = open(path + "/" + time.strftime("%Y-%m-%d") + ".csv", "w")
      file_obj.write(file_str.getvalue())
    file_obj.close    