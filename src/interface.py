import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askokcancel, showinfo, showerror, showwarning
from tkinter.filedialog import askopenfilename, askdirectory
import os
from glob import glob

class Interface(object):

    # show message
    def msg(self, string, type='info'):
        root = tk.Tk()
        root.withdraw()
        if type == 'info':
            showinfo('Info', string)
        elif type == 'error':
            showerror('Error', string)
        elif type == 'warning':
            showwarning('Warning', string)
        else:
            print('Unknown type %s' % type)

    # confirm quiting
    def on_close(self, event=None):
        if askokcancel('離開', '你確定要關閉程式嗎？'):
            self.parent.quit()
            self.parent.destroy()

    # load file
    def on_load(self, type):
        if type == 'dir':
            ok = self.get_dirs()
            if ok:
                self.video_path = self.video_dirs[0]
        elif type == 'file':
            ok = self.get_file()

        if ok:
            self.root_dir = "/".join(self.video_path.split('/')[:-1])
            self.init_video()
            self.results = dict()
            self.scale_n_frame.state(['!disabled'])
            self.scale_n_frame['to_'] = self.total_frame

    def get_dirs(self):
        dirs = askdirectory(title='請選擇影像檔案的路徑', initialdir='../')

        if dirs in [None, ""]:
            return False
        else:
            video_dirs = ["%s/%s" % (dirs, f) for f in os.listdir(dirs) if f[-3:] == 'avi']
            # glob(os.path.join(dirs, '*.avi'))
            res = len(video_dirs) > 0
            if not res:
                self.msg('該路徑底下沒有影像檔案。')
                print(video_dirs)
            else:
                self.video_dirs = video_dirs
                return True

        return False

    def get_file(self):
        path = askopenfilename(title='請選擇影像檔案', filetypes=[('video file (*.avi;)', '*.avi;')])

        if path in [None, ""]:
            return False
        else:
            res = os.path.isfile(path)
            if not res:
                self.msg('請選擇正確的影像檔案。')
            else:
                self.video_path = path
                return True

        return False
