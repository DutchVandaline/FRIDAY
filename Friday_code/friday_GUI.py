import tkinter as tk
from PIL import Image, ImageTk
from itertools import count
from friday_assistant import FridayAssistant
from friday_whisper import FridayListen
import threading

class ImageLabel(tk.Label):
    """A label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

def start_listening():
    assistant = FridayAssistant()
    threading.Thread(target=assistant.run_assistant).start()

def start_gui():
    root = tk.Tk()
    root.title("Friday")
    root.configure(bg="black")

    gif_label = ImageLabel(root, borderwidth=0)
    gif_label.pack()
    gif_label.load('Gui.gif')

    button_frame = tk.Frame(root, bg="black")
    button_frame.pack()

    listen_button = tk.Button(button_frame, text="Start Talking", command=start_listening, bg="black", fg="white", padx=20, pady=10, font=("Arial", 12))
    listen_button.grid(row=0, column=0, padx=10, pady=10)

    exit_button = tk.Button(button_frame, text="Exit", command=root.destroy, bg="black", fg="white", padx=20, pady=10, font=("Arial", 12))
    exit_button.grid(row=0, column=1, padx=10, pady=10)
    root.mainloop()


