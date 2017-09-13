import tkinter as tk
from tkinter import ttk
import cv2
import time, os, json, copy
import numpy as np
from PIL import Image, ImageTk

from src.interface import Interface
from src.utils import Utils
from src.keyhandler import KeyHandler

class Labeler(tk.Frame, Interface, Utils, KeyHandler):

    def __init__(self, *args, **kwargs):

        # variables for videos
        self.video_dirs = None
        self.video_path = None
        self.__video__ = None
        self.__frame__ = None
        self.__orig_frame__ = None
        self.__image__ = None
        self.width = 1280
        self.height = 720
        self.fps = None
        self.resolution = None
        self.total_frame = None
        self.root_dir = None

        # variables for frame
        self._c_width = self._c_height = self._r_width = self._r_height = None
        self.n_frame = 1

        # variables for class
        self.class_ind = 1
        self.class_buttons = []
        self.results = dict()

        # variables for drawing rectangle
        self.is_mv = False
        self.mv_pt = None
        self.p1 = None

        # widgets
        self.display_frame = None
        self.disply_l = None
        self.op_frame = None
        self.info_frame = None
        self.scale_n_frame = None
        self.treeview = None
        self.label_n_frame = self.label_video_name = self.label_time = self.label_done_n_video = self.label_done_n_frame = self.label_xy = None
        
        # UI
        self.parent = tk.Tk()
        self.parent.title('Object Labeler for video')
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
        self.update_info()

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

        self.__frame__ = np.zeros((720, 1280, 3), dtype='uint8')
        cv2.putText(self.__frame__, 'Load Video', (300, 360), 7, 5, (255, 255, 255), 2)
        self.__orig_frame__ = self.__frame__.copy()
        self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))

        # display panel frame
        self.display_frame = tk.Frame(self.parent)
        self.display_frame.grid(row=0, column=0, padx=10, pady=10)
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(1, weight=1)
        self.disply_l = ttk.Label(self.display_frame, image=self.__image__)
        self.disply_l.grid(row=0, column=0, sticky='news')
        self.disply_l.bind('<Button-1>', self.on_l_mouse)
        self.disply_l.bind('<Button-3>', self.on_r_mouse)
        self.disply_l.bind('<Motion>', self.on_mouse_mv)
        self.disply_l.bind('<ButtonRelease-1>', self.off_mouse)

        # frame operation frame
        self.op_frame = tk.Frame(self.display_frame)
        self.op_frame.grid(row=1, column=0, sticky='news', padx=10, pady=10)
        self.op_frame.grid_rowconfigure(0, weight=1)
        self.op_frame.grid_rowconfigure(1, weight=1)
        self.op_frame.grid_columnconfigure(0, weight=1)
        self.create_button()
        self.create_scale()

        # information frame
        self.info_frame = tk.Frame(self.parent)
        self.info_frame.grid(row=0, column=1, rowspan=2, sticky='news', pady=10)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        self.create_treeview()
        self.create_info()

        # bind event key
        self.parent.bind('<Escape>', self.on_close)
        self.parent.bind('<Delete>', self.on_delete)
        self.parent.bind('<r>', self.on_delete)
        self.parent.bind('<Control-s>', self.on_save)
        self.parent.bind('<Left>', self.on_left)
        self.parent.bind('<a>', self.on_left)
        self.parent.bind('<Up>', lambda event: self.on_left(event, step=100))
        self.parent.bind('<w>', lambda event: self.on_left(event, step=100))
        self.parent.bind('<Right>', self.on_right)
        self.parent.bind('<d>', self.on_right)
        self.parent.bind('<Down>', lambda event: self.on_right(event, step=100))
        self.parent.bind('<s>', lambda event: self.on_right(event, step=100))
        self.treeview.bind('<Control-a>', self.on_select_all)

    def create_menu(self):

        menu = tk.Menu(self.parent)
        self.parent.config(menu=menu)

        file = tk.Menu(menu)
        file.add_command(label='載入影像檔案路徑', command=lambda type='dir': self.on_load(type=type))
        file.add_command(label='載入影像檔案', command=lambda type='file': self.on_load(type=type))
        file.add_command(label='儲存', command=self.on_save)

        menu.add_cascade(label='File', menu=file)

    def create_button(self):

        button_label_frame = ttk.LabelFrame(self.op_frame, text='選擇類別')
        button_label_frame.grid(row=0, column=0, sticky='news')
        button_label_frame.grid_rowconfigure(0, weight=1)
        button_label_frame.grid_columnconfigure(0, weight=1)

        button_frame = tk.Frame(button_label_frame)
        button_frame.grid(row=0, column=0)

        for i in range(1, 6):
            img = ImageTk.PhotoImage(file='icons/%s.png' % i)
            func = lambda k=i: self.on_class_button(k=k)
            b = ttk.Button(button_frame, image=img, command=func, cursor='hand2')
            b.image = img
            b.grid(row=0, column=i, sticky='news', padx=10, pady=0)
            if i == self.class_ind:
                b['state'] = 'disabled'
            self.parent.bind('%s' % i, lambda event, k=i: self.on_class_button(k=k))
            self.class_buttons.append(b)

    def create_scale(self):
        scale_frame = tk.Frame(self.op_frame)
        scale_frame.grid(row=1, column=0, sticky='news', pady=10)

        scale_frame.grid_rowconfigure(0, weight=1)
        scale_frame.grid_columnconfigure(0, weight=1)

        self.label_n_frame = ttk.Label(scale_frame, text='--/--')
        self.label_n_frame.grid(row=0, column=0, padx=5)
        self.scale_n_frame = ttk.Scale(scale_frame, from_=1, to=self.total_frame, length=1250, command=self.set_n_frame)
        self.scale_n_frame.set(self.n_frame)
        self.scale_n_frame.state(['disabled'])
        self.scale_n_frame.grid(row=1, column=0, padx=10)

    def create_treeview(self):
        bboxlist_label_frame = ttk.LabelFrame(self.info_frame, text='Bounding boxes')
        bboxlist_label_frame.grid(row=0, column=0, sticky='news', padx=5)
        
        img = ImageTk.PhotoImage(file='icons/delete.png')
        delete_button = ttk.Button(bboxlist_label_frame, image=img, command=self.on_delete, cursor='hand2')
        delete_button.image = img
        delete_button.grid(row=0, column=0, sticky='e', padx=5)

        self.treeview = ttk.Treeview(bboxlist_label_frame, height=10)
        self.treeview['columns'] = ('c', 'tl', 'br')
        self.treeview.heading('#0', text='', anchor='center')
        self.treeview.column('#0', anchor='w', width=0)
        self.treeview.heading('c', text='class')
        self.treeview.column('c', anchor='center', width=90)
        self.treeview.heading('tl', text='左上坐標')
        self.treeview.column('tl', anchor='center', width=120)
        self.treeview.heading('br', text='右下坐標')
        self.treeview.column('br', anchor='center', width=120)
        self.treeview.grid(row=1, column=0, sticky='news', padx=5)

        # define color
        self.treeview.tag_configure('1', foreground='limegreen')
        self.treeview.tag_configure('2', foreground='deepskyblue')
        self.treeview.tag_configure('3', foreground='red2')
        self.treeview.tag_configure('4', foreground='purple')
        self.treeview.tag_configure('5', foreground='orange')

        self.label_xy = ttk.Label(bboxlist_label_frame, text='x: -- y: --')
        self.label_xy.grid(row=2, column=0, sticky='w', padx=5)

    def create_info(self):
        text_video_name = '-----'
        text_time = '--:--:--'
        text_done_n_video = '--/--'
        text_done_n_frame = '--/--'

        info_label_frame = ttk.LabelFrame(self.info_frame, text='影像信息')
        info_label_frame.grid(row=1, column=0, sticky='news', padx=5)

        self.label_video_name = ttk.Label(info_label_frame, text='影像檔名: %s' % text_video_name)
        self.label_video_name.grid(row=0, column=0, sticky=tk.W, padx=5)
        self.label_time = ttk.Label(info_label_frame, text='影像時間: %s' % text_time)
        self.label_time.grid(row=1, column=0, sticky=tk.W, padx=5)

        self.label_done_n_video = ttk.Label(info_label_frame, text='已完成標註影像數: %s' % text_done_n_video)
        self.label_done_n_video.grid(row=2, column=0, sticky=tk.W, padx=5)
        self.label_done_n_frame = ttk.Label(info_label_frame, text='已完成標註幀數: %s' % text_done_n_frame)
        self.label_done_n_frame.grid(row=3, column=0, sticky=tk.W, padx=5)

    def init_video(self):
        if self.__video__ is not None:
            self.__video__.release()
        ok = os.path.isfile(self.video_path)
        if ok:
            self.__video__ = cv2.VideoCapture(self.video_path)
            self.width = int(self.__video__.get(3))
            self.height = int(self.__video__.get(4))
            self.fps = int(self.__video__.get(5))
            self.resolution = (self.width, self.height)
            self.total_frame = int(self.__video__.get(cv2.CAP_PROP_FRAME_COUNT))
        else:
            string = 'Exist of %s: %s' % (self.video_path, os.path.isfile(self.video_path))
            self.msg(string, type='warning')
            self.video_path = None

        # print(self.video_path, (self.width, self.height), self.fps, self.resolution, self.total_frame)

    def update_display(self):
        if self.video_path is not None:
            self.update_frame()
        try:
            self.draw()
            self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))            
            self.disply_l.configure(image=self.__image__)
        except:
            pass

        self.disply_l.after(40, self.update_display)

    def update_frame(self):
        self.__video__.set(cv2.CAP_PROP_POS_FRAMES, self.n_frame - 1)
        ok, self.__frame__ = self.__video__.read()
        self.__orig_frame__ = self.__frame__.copy()
    
    def update_info(self):
        if self.video_path is not None:
            text_video_name = self.video_path.split('/')[-1]
            text_done_n_video = '%s/%s' % (0, len(self.video_dirs) if self.video_dirs is not None else 1)
            text_done_n_frame = '%s/%s' % (len(self.results.keys()), 300)
            self.label_video_name.configure(text='影像檔名: %s' % text_video_name)

            sec = round(self.n_frame / self.fps, 2)
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            text_time = "%d:%02d:%02d" % (h, m, s)
            
            self.label_time.configure(text='影像時間: %s' % text_time)
            self.scale_n_frame.set(self.n_frame)
            self.label_n_frame.configure(text='%s/%s' % (self.n_frame, self.total_frame))
            self.label_done_n_video.configure(text='已完成標註影像數: %s' % text_done_n_video)
            self.label_done_n_frame.configure(text='已完成標註幀數: %s' % text_done_n_frame)

        self.parent.after(200, self.update_info)
