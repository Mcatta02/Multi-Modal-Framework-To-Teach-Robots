from importlib import reload
from time import sleep
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread

DISPLAY_SIZE = (720, 405)
LIVE = True

STATUS_0 = 'Loading camera preview...'
STATUS_1 = 'Camera ready. Press "Start Recording" to begin.'
STATUS_2 = 'Starting recording...'
STATUS_3 = 'Recording started. Press "Stop Recording" to end.'
STATUS_4 = 'Saving recording...'

import previewer as pv
import detector as dt

class UI:

    def __init__(self):
        # initialize UI window
        self.root = tk.Tk()
        self.root.title('Project 3-1 | Robot Learning from Demonstration')
        self.root.geometry('800x500')
        self.root.resizable(False, False)

        # closing protocol
        def on_close():
            self.closing = True
            if self.p.is_alive() or self.t.is_alive():
                self.recording = True
                dt.exit_signal = True
                self.root.after(500, on_close)
            else:
                self.root.destroy()
        self.root.protocol('WM_DELETE_WINDOW', on_close)

        # display
        img_ = Image.open(dt.NO_SIGNAL)
        self.display = tk.Label(self.root, image=ImageTk.PhotoImage(image=img_))
        self.display.pack()

        # buttons
        self.recording_button = tk.Button(self.root, text='Start Recording', command=self.record)
        self.recording_button.pack()

        # timer label
        self.timer_label = tk.Label(self.root, text='00:00')
        self.timer_label.pack()

        # status label
        self.status_label = tk.Label(self.root, text=STATUS_0)
        self.status_label.pack()

        # logic
        self.recording = False
        self.closing = False

        self.t = Thread(target=self.run_detect)
        self.p = Thread(target=self.run_preview)

        print('loading...')
        reload(pv)
        
        self.p.start()

    def run_preview(self):
        pv.run_preview(ui=self, svo=None if LIVE else dt.TEST_VIDEOS[1])
        print('preview finished')

    def run_detect(self):
        import torch
        with torch.no_grad():
            dt.run_detect(ui=self, svo=None if LIVE else dt.TEST_VIDEOS[1])
        print('detection finished')

    def record(self):
        if not self.recording: # start recording
            # stop preview
            self.recording = True
            sleep(0.5)

            self.status_label.configure(text=STATUS_2)
            self.recording_button.configure(text='Stop Recording')

            print('loading...')
            reload(dt)

            self.t.start()

        else: # stop recording
            self.recording = False
            sleep(0.5)

            self.status_label.configure(text=STATUS_4)
            self.recording_button.configure(text='Start Recording')

    def update_ui(self, image):
        img_ = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.display.configure(image=img_)
        self.display.image = img_

    def update_timer(self, time):
        self.timer_label.configure(text=time)

# ----------------------
# |        TEST        |
# ----------------------

if __name__ == '__main__':
    ui = UI()
    ui.root.mainloop()
