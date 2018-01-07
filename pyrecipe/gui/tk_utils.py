"""
	various utils to for tkinter
"""

import os

from pyrecipe.gui import tk, ttk

class Warn(tk.Toplevel):
	
    def __init__(self, msg):
        tk.Toplevel.__init__(self)
        self.title("Pyrecipe Information")
        center(self)

        self.message = tk.Message(self, text=msg)
        self.message.pack(pady=10, padx=10)
        
        self.checkmark = tk.PhotoImage(file='/home/michael/code/git/pyrecipe/pyrecipe/images/checkmark.gif')
        self.ok = tk.Button(self, text="Ok", image=self.checkmark, compound="left", command=self.destroy)
        self.ok.pack(side=tk.BOTTOM)

    def play_sound(self):
        self.sound()
		
    def sound(self):
        os.system('play -q /usr/share/sounds/KDE-Sys-Warning.ogg')

class PrepOptionsMenu(tk.OptionMenu):

    def __init__(self, parent, var, *args):
        super().__init__(parent, var, *args)
		

class EntryPopup(tk.Entry):

    def __init__(self, parent, text, **kw):
        ''' If relwidth is set, then width is ignored '''
        super().__init__(parent, **kw)
        self.insert(0, text) 
        self['exportselection'] = False
        self.focus_force()
        self.bind("<Control-a>", self.selectAll)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<Return>", self.enter)

    def selectAll(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'

    def enter(self, event):
        self.destroy()


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
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                      background='#878787', relief='solid', borderwidth=1,
                      font=("unbuntu", "12", "normal"))
        label.pack(ipadx=1)
        self.tw.after(5000, lambda: self.tw.destroy())


    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


