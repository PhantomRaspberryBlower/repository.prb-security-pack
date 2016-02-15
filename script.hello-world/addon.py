import xbmc, xbmcgui
 
#get actioncodes from https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10 
ACTION_NAV_BACK = 92

class MyClass(xbmcgui.Window):
  def __init__(self):
    self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, 'special://home/addons/script.hello-world/fanart.jpg'))
    self.strActionInfo = xbmcgui.ControlLabel(10, 10, 800, 200, '', 'font13', '0xFF00FF00')
    self.addControl(self.strActionInfo)
    self.strActionInfo.setLabel('Push HOME to quit, SELECT to display welcome message')

  def onAction(self, action):
    if (action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK):
      self.message('Goodbye cruel world!')
      self.close()
    if action == ACTION_SELECT_ITEM:
      self.message('Hello World!')

  def message(self, message):
    dialog = xbmcgui.Dialog()
    dialog.ok("My Message Title", message)

window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
if window.getProperty('MyAddonIsRunning') != 'true':
  mydisplay = MyClass()
  # Remove waiting dialog (like hourglass)
  xbmc.executebuiltin("Dialog.Close(busydialog)")
  mydisplay .doModal()
  del mydisplay
  window.setProperty('MyAddonIsRunning', 'false')
