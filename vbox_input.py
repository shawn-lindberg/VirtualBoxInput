# VirtualBox does not seem to do a very good job of handling input from certain
# sources, such as Dragonfly/Natlink. The purpose of this is simply to intercept
# key events and then pass them on to a virtual machine using VBoxManage.
# Author: Shawn Lindberg, 2013/10/22
import subprocess
import time
import wx

# Configuration.
VirtualBoxManageFilename = "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"
VirtualBoxVMName = "Ubuntu Linux 64 bit for VPN"

# Mapping of wx Keycodes to scancodes.
# Based on http://www.win.tue.nl/~aeb/linux/kbd/scancodes-1.html
ScancodesFromwxKeycode = {
	wx.WXK_ESCAPE			: [0x01], # (Esc)
	ord('1')				: [0x02], # (1!)
	ord('2')				: [0x03], # (2@)
	ord('3')				: [0x04], # (3#)
	ord('4')				: [0x05], # (4$)
	ord('5')				: [0x06], # (5%E)
	ord('6')				: [0x07], # (6^)
	ord('7')				: [0x08], # (7&)
	ord('8')				: [0x09], # (8*)
	ord('9')				: [0x0a], # (9()
	ord('0')				: [0x0b], # (0))
	ord('-')				: [0x0c], # (-_)
	ord('+')				: [0x0d], # (=+)
	wx.WXK_BACK				: [0x0e], # (Backspace)
	wx.WXK_TAB				: [0x0f], # (Tab)
	ord('Q')				: [0x10], # (Q)
	ord('W')				: [0x11], # (W)
	ord('E')				: [0x12], # (E)
	ord('R')				: [0x13], # (R)
	ord('T')				: [0x14], # (T)
	ord('Y')				: [0x15], # (Y)
	ord('U')				: [0x16], # (U)
	ord('I')				: [0x17], # (I)
	ord('O')				: [0x18], # (O)
	ord('P')				: [0x19], # (P)
	ord('[')				: [0x1a], # ([{)
	ord(']')				: [0x1b], # (]})
	wx.WXK_RETURN			: [0x1c], # (Enter)
	wx.WXK_CONTROL			: [0x1d], # (LCtrl)
	ord('A')				: [0x1e], # (A)
	ord('S')				: [0x1f], # (S)
	ord('D')				: [0x20], # (D)
	ord('F')				: [0x21], # (F)
	ord('G')				: [0x22], # (G)
	ord('H')				: [0x23], # (H)
	ord('J')				: [0x24], # (J)
	ord('K')				: [0x25], # (K)
	ord('L')				: [0x26], # (L)
	ord(';')				: [0x27], # (;:)
	ord('\'')				: [0x28], # ('")
	ord('~')				: [0x29], # (`~)
	wx.WXK_SHIFT			: [0x2a], # (LShift)
	ord('\\')				: [0x2b], # (\|)
	ord('Z')				: [0x2c], # (Z)
	ord('X')				: [0x2d], # (X)
	ord('C')				: [0x2e], # (C)
	ord('V')				: [0x2f], # (V)
	ord('B')				: [0x30], # (B)
	ord('N')				: [0x31], # (N)
	ord('M')				: [0x32], # (M)
	ord(',')				: [0x33], # (,<)
	ord('.')				: [0x34], # (.>)
	ord('/')				: [0x35], # (/?)
	# 36 (RShift)
	wx.WXK_NUMPAD_MULTIPLY	: [0x37], # (Keypad-*) or (*/PrtScn) on a 83/84-key keyboard
	wx.WXK_ALT				: [0x38], # (LAlt)
	wx.WXK_SPACE			: [0x39], # (Space bar)
	wx.WXK_CAPITAL			: [0x3a], # (CapsLock)
	wx.WXK_F1				: [0x3b], # (F1)
	wx.WXK_F2				: [0x3c], # (F2)
	wx.WXK_F3				: [0x3d], # (F3)
	wx.WXK_F4				: [0x3e], # (F4)
	wx.WXK_F5				: [0x3f], # (F5)
	wx.WXK_F6				: [0x40], # (F6)
	wx.WXK_F7				: [0x41], # (F7)
	wx.WXK_F8				: [0x42], # (F8)
	wx.WXK_F9				: [0x43], # (F9)
	wx.WXK_F10				: [0x44], # (F10)
	wx.WXK_NUMLOCK			: [0x45], # (NumLock)
	wx.WXK_SCROLL			: [0x46], # (ScrollLock)
	wx.WXK_NUMPAD7			: [0x47], # (Keypad-7/Home)
	wx.WXK_NUMPAD8			: [0x48], # (Keypad-8/Up)
	wx.WXK_NUMPAD9			: [0x49], # (Keypad-9/PgUp)
	wx.WXK_NUMPAD_SUBTRACT	: [0x4a], # (Keypad--)
	wx.WXK_NUMPAD4			: [0x4b], # (Keypad-4/Left)
	wx.WXK_NUMPAD5			: [0x4c], # (Keypad-5)
	wx.WXK_NUMPAD6			: [0x4d], # (Keypad-6/Right)
	wx.WXK_NUMPAD_ADD		: [0x4e], # (Keypad-+)
	wx.WXK_NUMPAD1			: [0x4f], # (Keypad-1/End)
	wx.WXK_NUMPAD2			: [0x50], # (Keypad-2/Down)
	wx.WXK_NUMPAD3			: [0x51], # (Keypad-3/PgDn)
	wx.WXK_NUMPAD0			: [0x52], # (Keypad-0/Ins)
	wx.WXK_NUMPAD_DECIMAL	: [0x53], # (Keypad-./Del)
	
	wx.WXK_NUMPAD_ENTER		: [0xe0, 0x1c], # (Keypad Enter)
	# e0 1d (RCtrl)
	# e0 2a (fake LShift)
	wx.WXK_NUMPAD_DIVIDE	: [0xe0, 0x35], # (Keypad-/)
	# e0 36 (fake RShift)
	# e0 37 (Ctrl-PrtScn)
	# e0 38 (RAlt)
	# e0 46 (Ctrl-Break)
	wx.WXK_HOME				: [0xe0, 0x47], # (Grey Home)
	wx.WXK_UP				: [0xe0, 0x48], # (Grey Up)
	wx.WXK_PAGEUP			: [0xe0, 0x49], # (Grey PgUp)
	wx.WXK_LEFT				: [0xe0, 0x4b], # (Grey Left)
	wx.WXK_RIGHT			: [0xe0, 0x4d], # (Grey Right)
	wx.WXK_END				: [0xe0, 0x4f], # (Grey End)
	wx.WXK_DOWN				: [0xe0, 0x50], # (Grey Down)
	wx.WXK_PAGEDOWN			: [0xe0, 0x51], # (Grey PgDn)
	wx.WXK_INSERT			: [0xe0, 0x52], # (Grey Insert)
	wx.WXK_DELETE			: [0xe0, 0x53], # (Grey Delete)
}

# Converts wx KeyEvents to scancodes.
#
# event:	The wx KeyEvent.
# down:		Whether the event is a keydown event.
#
# returns:	A list of scancodes.
#
def KeyboardScancodesFromWXKeyEvent(event, down):
	"""Converts wx KeyEvents to scancodes."""
	
	keycode = event.GetKeyCode()
	
	# Copy the list.
	scanCodes = list(ScancodesFromwxKeycode[keycode])
	
	# We have to manually handle releases.
	if down == False:
		scanCodes[-1] |= 0x80
	
	#print "keycode %02x -> scancodes %s" % (keycode, ", ".join(["%02x" % scancode for scancode in scancodes]))
	return scanCodes

# Sends keyboard scancodes to a VirtualBox VM.
#
# scanCodes:	A list of scancodes.
#
def SendKeyboardScanCodes(scanCodes):
	"""Sends keyboard scancodes to a VirtualBox VM."""
	# VirtualBox does not handle a long string of scan codes very well, so we
	# will split them into groups and send them separately.
	groupSize = 10
	scanCodeGroups = [scanCodes[index:index + groupSize]
					  for index in range(0, len(scanCodes), groupSize)]
	
	for scanCodeGroup in scanCodeGroups:
		# Send this group of scan codes.
		args = [VirtualBoxManageFilename, "controlvm", VirtualBoxVMName,
				"keyboardputscancode"]
		
		# Append the scancodes.
		scanCodeList = ["%02x" % scanCode for scanCode in scanCodeGroup]
		#print scanCodeList
		args.extend(scanCodeList)
		
		subprocess.call(args)

class InputPanel(wx.Panel):
	"""Catches the keys."""
	
	def __init__(self, parent):
		# Note: WANTS_CHARS allows us to process return and tab keys rather than
		# have them get eaten by navigation.
		wx.Panel.__init__(self, parent, -1, style = wx.WANTS_CHARS)

		self.__parent = parent

		# We want to keep track of the scan codes and send them off in batches
		# after a period of inactivity.
		self.__scanCodes = []
		self.__lastScanCodeActivityTimeSeconds = time.time()
		
		# Make a timer and start it.
		self.__timer = wx.Timer(self, wx.ID_ANY)
		self.__timer.Start(250, wx.TIMER_CONTINUOUS)

		# Event bindings.
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

		# Set focus after bindings so handler can run.
		self.SetFocus()

	def __del__(self):
		# Stop the timer.
		self.__timer.Stop()

	# Timer handler.
	def OnTimer(self, event):
		# Has it been long enough since the last activity?
		currentTimeSeconds = time.time()
		elapsedTimeSeconds = currentTimeSeconds - self.__lastScanCodeActivityTimeSeconds

		if elapsedTimeSeconds < 0.25:
			return
		
		# Send the scan codes and then prepare for the next batch.
		if self.__scanCodes:
			SendKeyboardScanCodes(self.__scanCodes)
		
		self.__scanCodes = []
		self.__lastScanCodeActivityTimeSeconds = time.time()

	def OnKeyDown(self, event):
		# Get scan codes from the event and queue them up.
		scanCodes = KeyboardScancodesFromWXKeyEvent(event, True)
		self.__scanCodes.extend(scanCodes)
		self.__lastScanCodeActivityTimeSeconds = time.time()
		
		#self.__parent.SetStatusText(">Key down: %02x." % scancode)
		
		# Don't pass the event upwards.
		#event.Skip()

	def OnKeyUp(self, event):
		# Get scan codes from the event and queue them up.
		scanCodes = KeyboardScancodesFromWXKeyEvent(event, False)
		self.__scanCodes.extend(scanCodes)
		self.__lastScanCodeActivityTimeSeconds = time.time()
		
		#self.__parent.SetStatusText(">Key up: %02x." % scancode)
		
		# Don't pass the event upwards.
		#event.Skip()

class InputWindow(wx.Frame):
	"""Basically the UI."""

	def __init__(self):
		wx.Frame.__init__(self, None, -1, "Name Here")

		# Initialize the menus.
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()

		exit = wx.MenuItem(fileMenu, 1, 'E&xit\tCtrl+Q')
		# exit.SetBitmap(wx.Bitmap('icons\exit.png'))

		fileMenu.AppendItem(exit)

		menubar.Append(fileMenu, '&File')

		helpMenu = wx.Menu()

		about = wx.MenuItem(helpMenu, 2, '&About')

		helpMenu.AppendItem(about)

		menubar.Append(helpMenu, '&Help')

		self.SetMenuBar(menubar)

		# Some other things.
		self.__statusBar = self.CreateStatusBar()

		self.Bind(wx.EVT_MENU, self.OnExit, id = 1)
		self.Bind(wx.EVT_MENU, self.OnAbout, id = 2)

		panel = InputPanel(self)

		# I'm not sure exactly what's going on, but the order of these calls seems to matter.
		self.Layout()
		self.Show()

	def OnExit(self, event):
		self.Close()

	def OnAbout(self, event):
		aboutInfo = wx.AboutDialogInfo()
		aboutInfo.SetIcon(wx.EmptyIcon())
		aboutInfo.SetName('Name Here')
		aboutInfo.SetVersion('0.1 (beta)')
		aboutInfo.SetDescription("")
		aboutInfo.AddDeveloper('Shawn Lindberg')

		wx.AboutBox(aboutInfo)

def Main():
	"""Does the main work of the program."""
	
	# Start the UI stuff and make it go.
	# Note: False here prevents stdout/stderr from being redirected to new window(s).
	app = wx.App(False)
	InputWindow()
	app.MainLoop()

if __name__ == "__main__":
	Main()
