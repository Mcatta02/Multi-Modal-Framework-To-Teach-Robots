import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from PIL import Image, ImageTk
from tracker import Tracklet
import os
from importlib import reload
from task_producer import Task
import GPT_classifier as GPT
import json

print('Loading results...')
import detector as dt
import inference as inf

IMAGE_SIZE = (640, 360)
BOT_NAME = 'Bot'

class UI:

    def __init__(self, chat):
        # initialize UI window
        self.root = tk.Tk()
        self.root.title('Project 3-1 | Robot Learning from Demonstration')
        self.root.geometry('1350x750')
        self.root.resizable(False, False)

        # images
        self.img_1 = ImageTk.PhotoImage(Image.open(dt.NO_SIGNAL).resize(IMAGE_SIZE))
        self.display_1 = tk.Label(self.root, image=self.img_1)
        self.display_1.place(x=20, y=10)
        self.img_2 = ImageTk.PhotoImage(Image.open(dt.NO_SIGNAL).resize(IMAGE_SIZE))
        self.display_2 = tk.Label(self.root, image=self.img_2)
        self.display_2.place(x=(1350 - IMAGE_SIZE[0] - 20), y=10)

        # labels
        self.label_1 = tk.Label(self.root, text='First Position', font=('Arial', 12))
        self.label_1.place(x=(20 + IMAGE_SIZE[0]//2), y=(10 + IMAGE_SIZE[1] + 15), anchor='center')
        self.label_2 = tk.Label(self.root, text='Last Position', font=('Arial', 12))
        self.label_2.place(x=(1350 - IMAGE_SIZE[0] - 20 + IMAGE_SIZE[0]//2), y=(10 + IMAGE_SIZE[1] + 15), anchor='center')

        # seperator
        self.seperator = ttk.Separator(self.root, orient='horizontal')
        self.seperator.place(x=20, y=(10 + IMAGE_SIZE[1] + 30), width=(1350 - 40), height=5)

        # labels
        self.label_3 = tk.Label(self.root, text='Objects:', font=('Arial', 12), width=15)
        self.label_3.place(x=(1350 - IMAGE_SIZE[0] - 20), y=(10 + IMAGE_SIZE[1] + 50))

        # object buttons
        print('----- reload -----')
        reload(inf)
        self.buttons = []
        i = 0
        for object in inf.tracklets:
            self.buttons.append(tk.Button(self.root, text=object.id, command=lambda id=object.id: self.button_pressed(id)))
            self.buttons[-1].place(x=(1350 - IMAGE_SIZE[0] - 20 + 100 + i * 40), y=(10 + IMAGE_SIZE[1] + 50))
            i += 1

        # get object order
        self.object_order = []
        for obj in inf.tracklets:
            self.object_order.append(obj.id)

        # buttons
        self.button_1 = tk.Button(self.root, text='Confirm Task', command=self.confirm)
        self.button_1.place(x=(1350 - IMAGE_SIZE[0] + 20), y=(750 - 65), width=150)
        self.button_2 = tk.Button(self.root, text='Retry Recording', command=self.retry)
        self.button_2.place(x=(1350 - IMAGE_SIZE[0]//2 - 20 - 75), y=(750 - 65), width=150)
        self.button_3 = tk.Button(self.root, text='Quit', command=self.quit)
        self.button_3.place(x=(1350 - 60 - 150), y=(750 - 65), width=150)

        if chat:
            # chat frame
            self.chat_frame = tk.Frame(self.root, width=IMAGE_SIZE[0], height=300)
            self.chat_frame.place(x=20, y=(10 + IMAGE_SIZE[1] + 40))

            # chat log
            self.chat_log = tk.Text(self.chat_frame, wrap=tk.WORD, state=tk.NORMAL, width=IMAGE_SIZE[0]//8, height=15)
            self.chat_log.grid(row=0, column=0, columnspan=2, pady=10)

            # first message
            s = f"{BOT_NAME}: The planned order of operations is: " + str(self.object_order)
            s = s + ". If this is right, press the \"Confirm Task\" button to activate the robot. "
            s = s + "Otherwise, send your corrections using the text box below.\n"
            self.chat_log.insert(tk.END, s)
            self.chat_log.config(state=tk.DISABLED)

            # chat entry
            self.chat_entry = tk.Entry(self.chat_frame, width=IMAGE_SIZE[0]//8)
            self.chat_entry.bind('<Return>', lambda _: self.send_message())
            self.chat_entry.grid(row=1, column=0, pady=10)

            # chat button
            self.chat_button = tk.Button(self.chat_frame, text='Send', command=self.send_message)
            self.chat_button.grid(row=1, column=1, pady=10)

            # chat logic
            self.messages = []
            self.messages.append({"role": "system", "content": GPT.openai_system_message_1})
            self.messages.append({"role": "system", "content": GPT.openai_system_message_2})
            self.messages.append({"role": "system", "content": GPT.create_system_message_3(self.object_order)})

        # logic
        self.closing = False
        self.retrying = False

    def button_pressed(self, id):
        # get tracklet corresponding to id
        tracklet = [t for t in inf.tracklets if t.id == id][0]
        tracklet: Tracklet

        # get first and last timestamp
        first_timestamp = tracklet.get_first_timestamp()
        last_timestamp = tracklet.get_last_timestamp()

        # get corresponding images
        first_image = os.path.join(dt.RESOURCES_PATH, 'video_frames', '{}.jpg'.format(first_timestamp))
        last_image = os.path.join(dt.RESOURCES_PATH, 'video_frames', '{}.jpg'.format(last_timestamp))

        # update UI
        self.img_1 = ImageTk.PhotoImage(Image.open(first_image).resize(IMAGE_SIZE))
        self.display_1.configure(image=self.img_1)
        self.img_2 = ImageTk.PhotoImage(Image.open(last_image).resize(IMAGE_SIZE))
        self.display_2.configure(image=self.img_2)

    def confirm(self):
        # apply object_order to trackets
        old_tracklets = inf.tracklets.copy()
        inf.tracklets.clear()
        for id in self.object_order:
            inf.tracklets.append([t for t in old_tracklets if t.id == id][0])

        # warn user that objects must be in place
        # mb.showwarning('Warning!', 'Before closing this pop-up, \
        #    Please make sure all objects are in their correct starting positions.')

        # warn user that objects must be in place
        # mb.showwarning('Warning!', 'Before closing this pop-up, \
        #    Please make sure all humans are at a sufficient distance from the robotic arm.')

        # execute task
        task = Task(tracklets=inf.tracklets)
        task.execute()

    def retry(self):
        self.retrying = True
        self.root.destroy()

    def quit(self):
        self.closing = True
        self.root.destroy()

    def send_message(self):
        # get message from entry box
        message = self.chat_entry.get().strip()
        self.messages.append({"role": "user", "content": message})

        # check if message is not empty
        if message:
            # update chat log
            self.chat_log.config(state=tk.NORMAL)
            self.chat_log.insert(tk.END, f"You: {message}\n")
            self.chat_log.insert(tk.END, f"{BOT_NAME}: ...\n")
            self.chat_log.config(state=tk.DISABLED)
            self.chat_entry.delete(0, tk.END)

            # disable chat while waiting for response
            self.chat_entry.config(state=tk.DISABLED)
            self.root.after(500, self.get_response)
    
    def get_response(self):
        # send message to GPT
        completion = GPT.client.chat.completions.create(
            model=GPT.model,
            messages=self.messages,
            response_format={"type": "json_object"}
        )

        # get response
        json_response = json.loads(completion.choices[0].message.content)
        self.messages.append({"role": "assistant", "content": completion.choices[0].message.content})
        print('received response:\n', completion.choices[0].message.content)

        # get information mentioned
        response = json_response['response']
        self.object_order = json_response['object_order']

        # update chat
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.delete('end-5c', 'end-2c')
        self.chat_log.insert('end-2c', response)
        self.chat_log.config(state=tk.DISABLED)

        # enable chat
        self.chat_entry.config(state=tk.NORMAL)

# ----------------------
# |        TEST        |
# ----------------------

if __name__ == '__main__':
    ui = UI()
    ui.root.mainloop()
