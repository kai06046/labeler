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
            self.on_save()
            self.parent.quit()
            self.parent.destroy()

    # load file
    def on_load(self, type):
        self.on_save()
        if type == 'dir':
            ok = self.get_dirs()
            if ok:
                self.video_path = self.video_dirs[0]
        elif type == 'file':
            ok = self.get_file()

        if ok:
            self.init_all()
            
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

    def popup_help(self, master):

        settings_root = tk.Toplevel(master)
        settings_root.resizable(False, False)
        tk.Grid.rowconfigure(settings_root, 0, weight=1)
        tk.Grid.rowconfigure(settings_root, 1, weight=1)
        tk.Grid.columnconfigure(settings_root, 0, weight=1)
        tk.Grid.columnconfigure(settings_root, 1, weight=1)

        def exit(event):
            settings_root.destroy()

        settings_root.focus_force()
        settings_root.title('設定')

        ACTION = ['選擇需要標註的類別', '刪除選擇的標註', '刪除最後一個標註', '前一幀', '後一幀', '前100幀', '後100幀', '前 1 個已標註的幀', '後 1 個已標註的幀', '前一個影片', '下一個影片', '儲存', '設定', '離開']
        HOTKEY = ['1/2/3/4/5', 'x/DELETE', '滑鼠右鍵', 'a/Left', 'd/Right', 'w/Up', 's/Down', 'Page Up', 'Page Down', 'Ctrl+a/Left', 'Ctrl+d/Right', 'Ctrl+s', 'h', 'Escape']

        description_frame = ttk.LabelFrame(settings_root, text='關於')
        description_frame.grid(row=0, column=0, sticky='news', padx=5, pady=5)
        description_frame.grid_columnconfigure(0, weight=1)
        description_frame.grid_rowconfigure(0, weight=1)
        text = "這是一個標註埋葬蟲位置的軟體，請以滑鼠左鍵拖曳一個和埋葬蟲位置對應的長方形。"
        tk.Message(description_frame, text=text, width=400).grid(row=0, column=0, sticky='w')

        key_frame = tk.Frame(settings_root)
        key_frame.grid(row=1, column=0, sticky='news')
        key_frame.grid_rowconfigure(0, weight=1)
        key_frame.grid_columnconfigure(0, weight=1)
        key_frame.grid_columnconfigure(1, weight=1)

        hotkey = ttk.LabelFrame(key_frame, text="快捷鍵")
        action = ttk.LabelFrame(key_frame, text="操作")
        hotkey.grid_columnconfigure(0, weight=1)
        action.grid_columnconfigure(0, weight=1)
        hotkey.grid(row=0, column=0, padx=5, pady=5, sticky='news')
        action.grid(row=0, column=1, padx=5, pady=5, sticky='news')

        # action description section
        for i, a in enumerate(ACTION):
            ttk.Label(action, text=a).grid(column=0, row=i, sticky=tk.W, padx=5, pady=5)
            ttk.Label(hotkey, text=HOTKEY[i]).grid(column=0, row=i, padx=5, pady=5)

            hotkey.grid_rowconfigure(i, weight=1)
            action.grid_rowconfigure(i, weight=1)

        settings_root.update_idletasks()
        w = settings_root.winfo_screenwidth()
        h = settings_root.winfo_screenheight()

        size = (settings_root.winfo_width(), settings_root.winfo_height())
        x = w/2 - size[0]/2
        y = h/2.25 - size[1]/2
        # print("%dx%d+%d+%d" % (size + (x, y)))
        r = 0 if master.state() == 'zoomed' else r
        settings_root.geometry("%dx%d+%d+%d" % (size[0], size[1]+r, x, y))

        settings_root.bind('<Escape>', exit)
        settings_root.bind('<h>', exit)
    