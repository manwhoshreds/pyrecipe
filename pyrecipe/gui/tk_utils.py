"""
	various utils to for tkinter
"""

import os

from tkinter import *
from tkinter.ttk import *

class Warn(Toplevel):
	
	def __init__(self, msg):
		Toplevel.__init__(self)
		self.title("Pyrecipe Information")
		self.geometry('200x100+800+450')

		message = Message(self, text=msg, width=200)
		message.pack()
		
		button = Button(self, text="Ok", command=self.destroy)
		button.pack(side=BOTTOM)
		self.play_sound()

	def play_sound(self):
		self.sound()
		
	def sound(self):
		os.system('play -q /usr/share/sounds/KDE-Sys-Warning.ogg')
		

class ToolTip(object):
	'''
		create a tooltip for a given widget
	'''
	def __init__(self, widget, text='widget info'):
		self.widget = widget
		self.text = " {} ".format(text)
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.close)

	def enter(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		# creates a toplevel window
		self.tw = Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = Label(self.tw, text=self.text, justify='left',
				background='#878787', relief='solid', borderwidth=1,
				font=("unbuntu", "12", "normal"))
		label.pack(ipadx=1)
		self.tw.after(5000, lambda: self.tw.destroy())


	def close(self, event=None):
		if self.tw:
			self.tw.destroy()