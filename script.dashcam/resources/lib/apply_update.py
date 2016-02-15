import os, sys, getopt

# Declare variables
gps_enabled = False 
serial_connector = 'ttyAMA0'

# Populate list of command-line argument values
argv = sys.argv[1:]
try:
  # Populate list of command-line arguments
  opts, args = getopt.getopt(argv, "g:c", ["gps-enabled=", "communication="])
except:
  # Invalid command-line arguments - display valid options
  print('apply_update.py\n\t -g <gps-enabled>\n\t -c <communication>\n')
  sys.exit()

# Parse command-line arguments
for opt, arg in opts:
  if opt in ('-g', '--gps-enabled'):
    gps_enabled = True if arg else False
  elif opt in ('-c', '--communication'):
    serial_connector = arg

if gps_enabled == True:
  file_obj = open('startGPSService.sh', 'wb')
  file_obj.write('sudo gpsd /dev/%s -F /var/run/gpsd.sock' % serial_connector)  
  file_obj.close()
  os.system('/home/pi/.kodi/addons/script.module.gps/resources/lib/stopGPSService.sh')
  os.system('/home/pi/.kodi/addons/script.module.gps/resources/lib/startGPSService.sh') 
else:
  os.system('/home/pi/.kodi/addons/script.module.gps/resources/lib/stopGPSService.sh')
