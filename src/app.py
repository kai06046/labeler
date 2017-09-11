import tkinter as tk
from tkinter import ttk
import cv2
import time, os, json, copy
import numpy as np
from PIL import Image, ImageTk

from src.interface import Interface
from src.utils import Utils

class Labeler(tk.Frame, Interface, Utils):

    def __init__(self, *args, **kwargs):

        self.video_dirs = None
        self.video_path = None
        self.__video__ = None
        self.__frame__ = None
        self.__orig_frame__ = None
        self.__image__ = None

        self._c_width = self._c_height = self._r_width = self._r_height = None
        self.n_frame = 1
        
        # UI
        self.parent = tk.Tk()
        self.parent.title('Burying Beetle Behavior Labeler')
        self.parent.iconbitmap('icons/title.ico')
        self.parent.protocol('WM_DELETE_WINDOW', self.on_close)
        self.parent.option_add('*tearOff', False)
        tk.Grid.rowconfigure(self.parent, 0 , weight=1)
        tk.Grid.columnconfigure(self.parent, 0 , weight=1)
        tk.Grid.rowconfigure(self.parent, 1 , weight=1)
        tk.Grid.columnconfigure(self.parent, 1 , weight=1)

        # style = ttk.Style()
        # style.configure("Treeview.Heading", font=('Georgia', 14))
        # style.configure("Treeview", font=('Georgia', 12))

        self.create_ui()

        # update
        self.update_display()
        # self.update_label()

        # display label ratio relative to whole window
        self.parent.update_idletasks()
        self._r_height = self.__frame__.shape[0] / self.parent.winfo_reqheight()
        self._r_width = self.__frame__.shape[1] / self.parent.winfo_reqwidth()
        
        # maximize the window
        # self.parent.state('zoomed')

        self.parent.mainloop()

    def create_ui(self):

        self.create_menu()

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        # display panel
        self.__frame__ = np.zeros((720, 1280, 3), dtype='uint8')
        cv2.putText(self.__frame__, 'Load Video', (300, 360), 7, 5, (255, 255, 255), 2)
        self.__orig_frame__ = self.__frame__.copy()
        self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))

        self.display_frame = tk.Frame(self.parent, bg='red')
        self.display_frame.grid(row=0, column=0, padx=10, pady=10)
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(1, weight=1)
        self.disply_l = ttk.Label(self.display_frame, image=self.__image__)
        self.disply_l.grid(row=0, column=0, sticky='news')

        # frame operation frame
        self.op_frame = tk.Frame(self.display_frame, bg='blue')
        self.op_frame.grid(row=1, column=0, sticky='news', padx=10, pady=10)
        self.op_frame.grid_rowconfigure(0, weight=1)
        self.op_frame.grid_rowconfigure(1, weight=1)
        self.op_frame.grid_columnconfigure(0, weight=1)
        self.create_button()

        self.info_frame = tk.Frame(self.parent, bg='green')
        self.info_frame.grid(row=0, column=1, rowspan=2, sticky='news', pady=10)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)

        # display info
        self.create_info()

        # bind event key
        self.parent.bind('<Escape>', self.on_close)

    def create_menu(self):

        menu = tk.Menu(self.parent)
        self.parent.config(menu=menu)

        file = tk.Menu(menu)
        file.add_command(label='載入影像檔案路徑', command=lambda type='dir': self.on_load(type=type))
        file.add_command(label='載入影像檔案', command=lambda type='file': self.on_load(type=type))

        menu.add_cascade(label='File', menu=file)

    def create_button(self):
        pass

    def create_info(self):
        pass

    def init_video(self):
        if self.__video__ is not None:
            self.__video__.release()
        self.__video__ = cv2.VideoCapture(self.video_path)
        self.width = int(self.__video__.get(3))
        self.height = int(self.__video__.get(4))
        self.fps = int(self.__video__.get(5))
        self.resolution = (self.width, self.height)
        self.total_frame = int(self.__video__.get(cv2.CAP_PROP_FRAME_COUNT))

        print(self.video_path, (self.width, self.height), self.fps, self.resolution, self.total_frame)

    def update_display(self):
        if self.video_path is not None:
            self.update_frame()
        try:
            self.draw()
            self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))            
            self.disply_l.configure(image=self.__image__)
        except:
            pass

        self.disply_l.after(20, self.update_display)

    def update_frame(self):
        self.__video__.set(cv2.CAP_PROP_POS_FRAMES, self.n_frame - 1)
        ok, self.__frame__ = self.__video__.read()
        self.__orig_frame__ = self.__frame__.copy()
