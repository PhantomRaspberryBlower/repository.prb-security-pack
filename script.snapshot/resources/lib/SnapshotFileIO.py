#!/usr/bin/env python

import os		# Used to access file system

class SnapshotFileIO:

  # Initilize Object
  def __init__(self, output_path, disk_space_warning_percentage, file_extension):
    disk_space_critical = self.critical_disk_space(output_path, disk_space_warning_percentage)
    if disk_space_critical == True:
      print("*** WARNING! Critical Disk Space ***")
      print("Deleting oldest file ...")
      os.remove(self.oldest_file_in_tree(output_path, file_extension))

  # Used to find the oldest file in directory
  def oldest_file_in_tree(self, rootfolder, extension=".jpg"):
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

