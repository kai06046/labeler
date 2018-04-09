import copy
import json
import os
import time
import tkinter as tk
from tkinter import ttk

import cv2
import numpy as np
from PIL import Image, ImageTk

from src.keyhandler import KeyHandler
from src.utils import Utils

N = 300

class Labeler(tk.Frame, Utils, KeyHandler):

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
        self.n_done_video = 0

        # variables for frame
        self._c_width = self._c_height = self._r_width = self._r_height = None
        self.n_frame = 1

        # variables for class indexes
        self.class_ind = 1
        self.class_buttons = []
        self.results = dict()

        # variables for drawing rectangle
        self.is_mv = False
        self.is_checked = False
        self.mv_pt = None
        self.p1 = None

        # widgets
        self.parent = None
        self.display_frame = None
        self.disply_l = None
        self.op_frame = None
        self.info_frame = None
        self.scale_n_frame = None
        self.bbox_tv = self.done_bbox_tv = None
        self.label_done_obj = self.label_n_frame = self.label_video_name = self.label_time = self.label_done_n_video = self.label_done_n_frame = self.label_xy = None

    def run(self):
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

        self.create_ui()

        # update
        self.update_display()
        self.update_info()

        # display label ratio relative to whole window
        self.parent.update_idletasks()
        self._r_height = self.__frame__.shape[0] / self.parent.winfo_reqheight()
        self._r_width = self.__frame__.shape[1] / self.parent.winfo_reqwidth()

        # maximize the window
        self.parent.state('zoomed')

        self.parent.mainloop()

    def generate_bind_key(self):
        self.parent.bind('<Escape>', self.on_close)
        self.parent.bind('<Delete>', self.on_delete)
        self.parent.bind('<x>', self.on_delete)
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
        self.parent.bind('<Control-a>', self.on_prev)
        self.parent.bind('<Control-d>', self.on_next)
        self.parent.bind('<Control-Left>', self.on_prev)
        self.parent.bind('<Control-Right>', self.on_next)
        self.parent.bind('<Next>', self.on_next_done)
        self.parent.bind('<Prior>', self.on_prev_done)
        self.parent.bind('h', self.on_settings)
        self.bbox_tv.bind('<Control-a>', self.on_select_all)
        self.done_bbox_tv.bind('<Button-1>', self.tvitem_click)

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
        self.info_frame.grid_rowconfigure(2, weight=1)
        self.create_bbox_tv()
        self.create_done_bbox_tv()
        self.create_info()

        # bind event key
        self.generate_bind_key()

    def create_menu(self):

        menu = tk.Menu(self.parent)
        self.parent.config(menu=menu)

        file = tk.Menu(menu)
        file.add_command(label='載入影像檔案路徑', command=lambda type='dir': self.on_load(type=type))
        file.add_command(label='載入影像檔案', command=lambda type='file': self.on_load(type=type))
        file.add_command(label='儲存', command=self.on_save)

        help = tk.Menu(menu)
        help.add_command(label='設定', command=self.on_settings)

        menu.add_cascade(label='File', menu=file)
        menu.add_cascade(label='Help', menu=help)

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

    def create_bbox_tv(self):
        bboxlist_label_frame = ttk.LabelFrame(self.info_frame, text='Bounding boxes')
        bboxlist_label_frame.grid(row=0, column=0, sticky='news', padx=5)

        img = ImageTk.PhotoImage(file='icons/delete.png')
        delete_button = ttk.Button(bboxlist_label_frame, image=img, command=self.on_delete, cursor='hand2')
        delete_button.image = img
        delete_button.grid(row=0, column=0, sticky='e', padx=5)

        self.bbox_tv = ttk.Treeview(bboxlist_label_frame, height=10)
        self.bbox_tv['columns'] = ('c', 'tl', 'br')
        self.bbox_tv.heading('#0', text='', anchor='center')
        self.bbox_tv.column('#0', anchor='w', width=0)
        self.bbox_tv.heading('c', text='class')
        self.bbox_tv.column('c', anchor='center', width=90)
        self.bbox_tv.heading('tl', text='左上坐標')
        self.bbox_tv.column('tl', anchor='center', width=120)
        self.bbox_tv.heading('br', text='右下坐標')
        self.bbox_tv.column('br', anchor='center', width=120)
        self.bbox_tv.grid(row=1, column=0, sticky='news', padx=5)

        # define color
        self.bbox_tv.tag_configure('1', foreground='limegreen')
        self.bbox_tv.tag_configure('2', foreground='deepskyblue')
        self.bbox_tv.tag_configure('3', foreground='red2')
        self.bbox_tv.tag_configure('4', foreground='purple')
        self.bbox_tv.tag_configure('5', foreground='orange')

        self.label_xy = ttk.Label(bboxlist_label_frame, text='x: -- y: --')
        self.label_xy.grid(row=2, column=0, sticky='w', padx=5)

    def create_done_bbox_tv(self):
        bboxlist_label_frame = ttk.LabelFrame(self.info_frame, text='檢視已標註的 BBoxes')
        bboxlist_label_frame.grid(row=1, column=0, sticky='news', padx=5)

        self.done_bbox_tv = ttk.Treeview(bboxlist_label_frame, height=10)
        self.done_bbox_tv['columns'] = ('f_ind', 'n')
        self.done_bbox_tv.heading('#0', text='', anchor='center')
        self.done_bbox_tv.column('#0', anchor='w', width=0)
        self.done_bbox_tv.heading('f_ind', text='幀數')
        self.done_bbox_tv.column('f_ind', anchor='center', width=90)
        self.done_bbox_tv.heading('n', text='BBoxes 數量')
        self.done_bbox_tv.column('n', anchor='center', width=120)
        self.done_bbox_tv.grid(row=0, column=0, sticky='news', padx=5)

        vsb = ttk.Scrollbar(bboxlist_label_frame, orient="vertical", command=self.done_bbox_tv.yview)
        vsb.grid(row=0, column=1, sticky='news')

        self.done_bbox_tv.configure(yscrollcommand=vsb.set)

        label = ttk.Label(bboxlist_label_frame, text='各類別已標註數量:', font=("", 10, "bold"))
        label.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=10)
        self.label_done_obj = ttk.Label(bboxlist_label_frame, text="1: --\n2:-- \n3: --\n4: --\n5: --")
        self.label_done_obj.grid(row=2, column=0, columnspan=2, sticky='w', padx=5)

    def create_info(self):
        text_video_name = '-----'
        text_time = '--:--:--'
        text_n_video = '--/--'
        text_done_n_video = '--/--'
        text_done_n_frame = '--/--'

        info_label_frame = ttk.LabelFrame(self.info_frame, text='影像信息')
        info_label_frame.grid(row=2, column=0, sticky='news', padx=5)

        self.label_video_name = ttk.Label(info_label_frame, text='影像檔名: %s' % text_video_name)
        self.label_video_name.grid(row=0, column=0, sticky=tk.W, padx=5)
        self.label_time = ttk.Label(info_label_frame, text='影像時間: %s' % text_time)
        self.label_time.grid(row=1, column=0, sticky=tk.W, padx=5)
        self.label_n_video = ttk.Label(info_label_frame, text='影像 index: %s' % text_n_video)
        self.label_n_video.grid(row=2, column=0, sticky=tk.W, padx=5)

        # self.label_done_n_video = ttk.Label(info_label_frame, text='已完成標註影像數: %s' % text_done_n_video)
        # self.label_done_n_video.grid(row=3, column=0, sticky=tk.W, padx=5)
        self.label_done_n_frame = ttk.Label(info_label_frame, text='已完成標註幀數: %s' % text_done_n_frame)
        self.label_done_n_frame.grid(row=4, column=0, sticky=tk.W, padx=5)

        # video operation frame
        video_op_frame = tk.Frame(info_label_frame)
        video_op_frame.grid(row=5, column=0, sticky='news', padx=5, pady= 10)

        img_next = ImageTk.PhotoImage(file='icons/next.png')
        img_prev = ImageTk.PhotoImage(file='icons/prev.png')
        img_save = ImageTk.PhotoImage(file='icons/save.png')
        b_prev = ttk.Button(video_op_frame, image=img_prev, command=self.on_prev, cursor='hand2')
        b_prev.image = img_prev
        b_prev.grid(row=0, column=0, sticky='news', padx=10, pady=0)

        b_next = ttk.Button(video_op_frame, image=img_next, command=self.on_next, cursor='hand2')
        b_next.image = img_next
        b_next.grid(row=0, column=1, sticky='news', padx=10, pady=0)

        b_save = ttk.Button(video_op_frame, image=img_save, command=self.on_save, cursor='hand2')
        b_save.image = img_save
        b_save.grid(row=0, column=2, sticky='news', padx=10, pady=0)

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

    def init_all(self):
        self.root_dir = "/".join(self.video_path.split('/')[:-1])
        self.init_video()

        # load previous label if file exists
        filename = self.video_path.split('.avi')[0] + '_label.txt'
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = f.readlines()
            self.results = {eval(l)[0]: eval(l)[1] for l in data}
        else:
            self.results = dict()

        # change class index
        self.n_frame = 1
        if self.n_frame in self.results.keys():
            self.class_reindex()
        else:
            self.on_class_button(k=1)

        # update treeview rows
        self.update_treeview()

        # change scalebar state
        self.scale_n_frame.state(['!disabled'])
        self.scale_n_frame['to_'] = self.total_frame

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
            text_n_video = '%s/%s' % (self.video_dirs.index(self.video_path) + 1 if self.video_dirs is not None else 1,\
             len(self.video_dirs) if self.video_dirs is not None else 1)
            # text_done_n_video = '%s/%s' % (self.n_done_video, len(self.video_dirs) if self.video_dirs is not None else 1)
            text_done_n_frame = '%s/%s' % (len(self.results.keys()), N)
            self.label_video_name.configure(text='影像檔名: %s' % text_video_name)

            count_list = [value[0] for k, v in self.results.items() for value in v]
            v = [count_list.count(i) for i in range(1, 6)]
            self.label_done_obj.configure(text="1: %s\n2: %s\n3: %s\n4: %s\n5: %s" % tuple(v))

            sec = round(self.n_frame / self.fps, 2)
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            text_time = "%d:%02d:%02d" % (h, m, s)

            self.label_time.configure(text='影像時間: %s' % text_time)
            self.scale_n_frame.set(self.n_frame)
            self.label_n_frame.configure(text='%s/%s' % (self.n_frame, self.total_frame))
            self.label_n_video.configure(text='影像 index: %s' % text_n_video)
            # self.label_done_n_video.configure(text='已完成標註影像數: %s' % text_done_n_video)
            self.label_done_n_frame.configure(text='已完成標註幀數: %s' % text_done_n_frame)

        self.parent.after(100, self.update_info)

    def update_treeview(self):
        for x in self.bbox_tv.get_children():
            self.bbox_tv.delete(x)
        for x in self.done_bbox_tv.get_children():
            self.done_bbox_tv.delete(x)

        # current bounding boxes treeview
        if self.n_frame in self.results.keys():
            bboxes = self.results[self.n_frame]
            for i, v in enumerate(bboxes):
                self.bbox_tv.insert('', 'end', str(i), values=v, tags = (str(v[0])))

        # done bounding boxes treeview
        for k in sorted(self.results.keys()):
            v2 = (k, len(self.results[k]))
            self.done_bbox_tv.insert('', 'end', str(k), values=v2)

    def class_reindex(self):
        existed_class = [v[0] for v in self.results[self.n_frame]]
        if self.class_ind > 1 and self.class_ind != 5:
            self.on_class_button(k=self.class_ind-1)
        elif self.class_ind == 1:
            for i in range(2, 5):
                if i not in existed_class:
                    self.on_class_button(k=i)
                    break
