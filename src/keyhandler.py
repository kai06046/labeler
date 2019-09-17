import logging
import os
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askokcancel
from datetime import datetime
from src.interface import Interface

now = datetime.now
N = 300
LOGGER = logging.getLogger(__name__)

class KeyHandler(Interface):

    # change class index
    def on_class_button(self, k):
        if k in range(1, 6) and self.video_path is not None:
            self.class_ind = k
            emo = "UNKNOWN"
            if k == 1:
                emo = "HAPPY"
            elif k == 2:
                emo = "SURPRISE"
            elif k == 3:
                emo = "NEUTRAL"
            elif k == 4:
                emo = "DISGUST"
            elif k == 5:
                emo = "FEAR"
            values = (str(len(self.bbox_tv.get_children())+1), self.n_frame, now().strftime("%Y%m%d%H%M%S%f")[:-3], emo)
            self.bbox_tv.insert('', 'end', str(len(self.bbox_tv.get_children())), values=values)
        else:
            print("emotion class button gg...")

    def on_start(self, event=None):
        current_time = now().strftime("%Y%m%d_%H%M%S")
        self.dir_path = os.path.join("results", current_time)
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)
        self.video_path = os.path.join(self.dir_path, current_time + ".avi")
        self.init_all()
        self.save_button.state(['!disabled'])
        self.start_button.state(['disabled'])


    # set value for frame index scalebar
    def set_n_frame(self, s):
        v = int(float(s))
        self.n_frame = v

    # callback for left mouse click
    def on_l_mouse(self, event=None):
        if not self.is_mv and self.video_path is not None:
            x, y = event.x, event.y
            if self.parent.state() == 'zoomed':
                x = int(x / self._c_width)
                y = int(y / self._c_height)
            self.p1 = (x, y)
            self.is_mv = True

    # callback for right mouse click
    def on_r_mouse(self, event=None):
        if self.n_frame in self.results.keys():
            n = len(self.results[self.n_frame])
            if n > 0:
                self.results[self.n_frame].pop()
                if str(n-1) in self.bbox_tv.get_children():
                    self.bbox_tv.delete(str(n-1))
                if len(self.results[self.n_frame]) == 0:
                    del self.results[self.n_frame]

            # auto change to previous class index if the current class index is not unknown
            if self.n_frame in self.results.keys():
                self.class_reindex()
            else:
                self.on_class_button(k=1)

    # callback for mouse move
    def on_mouse_mv(self, event=None):
        if self.video_path is not None:
            x, y = event.x, event.y
            if self.parent.state() == 'zoomed':
                x = min(int(x / self._c_width), int(self.width-1))
                y = min(int(y / self._c_height), int(self.height-1))

            # if self.is_mv:
            #     self.mv_pt = (x, y)
            #     self.label_xy.configure(text='x: %s y: %s x1: %s, y1: %s' % (x, y, self.p1[0], self.p1[1]))
            # else:
            #     self.label_xy.configure(text='x: %s y: %s' % (x, y))

    # callback for left mouse release
    def off_mouse(self, event=None):
        x, y = event.x, event.y
        if self.parent.state() == 'zoomed':
            x = int(x / self._c_width)
            y = int(y / self._c_height)

        if self.is_mv and self.mv_pt is not None:
            self.is_mv = False
            xmin = min(self.p1[0], x)
            ymin = min(self.p1[1], y)
            xmax = max(self.p1[0], x)
            ymax = max(self.p1[1], y)
            self.p1 = (xmin, ymin)
            self.mv_pt = (xmax, ymax)
            values = (self.class_ind, self.p1, self.mv_pt)
            if self.n_frame not in self.results.keys():
                self.results[self.n_frame] = [values]
            else:
                existed_class = [v[0] for v in self.results[self.n_frame]]
                if self.class_ind in existed_class and self.class_ind != 5:
                    ind = existed_class.index(self.class_ind)
                    self.results[self.n_frame][ind] = values
                else:
                    self.results[self.n_frame].append(values)

            # edit box for existed class
            if self.class_ind in [self.bbox_tv.item(item)['values'][0] for item in self.bbox_tv.get_children()] and self.class_ind != 5:
                for item in self.bbox_tv.get_children():
                    if self.bbox_tv.item(item)['values'][0] == self.class_ind:
                        self.bbox_tv.item(item, values=values)
                        break
            # else add new row in treeview
            else:
                self.bbox_tv.insert('', 'end', str(len(self.bbox_tv.get_children())), values=values, tags = (str(self.class_ind)))

            self.p1 = self.mv_pt = None

            # auto change to next class index if the current class index is not unknown
            if self.class_ind <= 4:
                self.on_class_button(k=self.class_ind+1)

    # callback for delete button of treeview
    def on_delete(self, event=None):
        for v in self.bbox_tv.selection():
            # index, timestamp, emo = tuple(self.bbox_tv.item(v)['values'])
            # p1, p2 = eval(','.join(p1.split(' '))), eval(','.join(p2.split(' ')))
            # values = (c, p1, p2)
            # self.results[self.n_frame].pop(self.results[self.n_frame].index(values))
            # if len(self.results[self.n_frame]) == 0:
            #     del self.results[self.n_frame]

            self.bbox_tv.delete(v)

    # callback for select rows in treeview
    def on_select_all(self, event=None):
        if self.video_path is not None:
            for x in self.bbox_tv.get_children():
                self.bbox_tv.selection_add(x)

    # callback for save results
    def on_save(self, event=None):

        if self.video_path is not None:
            data = []
            for line in self.bbox_tv.get_children():
                # for value in self.bbox_tv.item(line)['values']:
                v1, v2, v3, v4 = tuple(self.bbox_tv.item(line)['values'])
                data.append("%s,%s,%s,%s\n" % (v1, v2, v3, v4))

            record_file = os.path.join(self.dir_path, os.path.basename(self.video_path).split(".")[0] + ".csv")
            with open(record_file, "w") as f:
                f.writelines(data)

            self.video_path = None
            self.__is_live_stream = False

            self.start_button.state(['!disabled'])
            self.save_button.state(['disabled'])

            for x in self.bbox_tv.get_children():
                self.bbox_tv.delete(x)

            # video_name = self.video_path.split('/')[-1]
            # file_name = video_name.split('.avi')[0] + '_label.txt'

            # data = []
            # for k in sorted(self.results.keys()):
            #     boxes = self.results[k]
            #     boxes = sorted(boxes, key=lambda x: x[0])
            #     data.append('%s, %s\n' % (k, boxes))
            # if len(data) != 0:
            #     with open('%s/%s' % (self.root_dir, file_name), 'w+') as f:
            #         f.writelines(data)
            #     LOGGER.info('%s 已存檔於 %s' % (file_name, self.root_dir))

    # move to previous frame
    def on_left(self, event=None, step=1):
        self.check_done()

        if self.video_path is not None:
            if self.n_frame > 1 and (self.n_frame - step) >= 1:
                self.n_frame -= step
                if self.n_frame in self.results.keys():
                    self.class_reindex()
                else:
                    self.on_class_button(k=1)
                self.update_treeview()
            elif (self.n_frame - step) < 0:
                self.n_frame = 1
                if self.n_frame in self.results.keys():
                    self.class_reindex()
                else:
                    self.on_class_button(k=1)
                self.update_treeview()
                self.msg('Already the first frame!')
            else:
                self.msg('Already the first frame!')

    # move to next frame
    def on_right(self, event=None, step=1):
        self.check_done()

        if self.video_path is not None:
            if self.n_frame == self.total_frame:
                self.msg('Already the last frame!')
            elif (self.n_frame + step) > self.total_frame:
                self.n_frame = self.total_frame
                if self.n_frame in self.results.keys():
                    self.class_reindex()
                else:
                    self.on_class_button(k=1)
                self.update_treeview()
            else:
                self.n_frame += step
                if self.n_frame in self.results.keys():
                    self.class_reindex()
                else:
                    self.on_class_button(k=1)
                self.update_treeview()

    # move to previous video
    def on_prev(self, event=None):
        if self.video_dirs is not None:
            current = self.video_dirs.index(self.video_path)
            if current > 0:
                self.on_save()
                self.video_path = self.video_dirs[current-1]
                self.init_all()
            else:
                self.msg('已經是第一支影像了哦!')
        else:
            self.msg('只有一支影像哦!')

    # move to next video
    def on_next(self, event=None):
        if self.video_dirs is not None:
            current = self.video_dirs.index(self.video_path)
            if current+1 < len(self.video_dirs):
                self.on_save()
                self.video_path = self.video_dirs[current+1]
                self.init_all()
            else:
                self.msg('已經是最後一支影像了哦!')
        else:
            self.msg('只有一支影像哦!')

    # move to previous done frame
    def on_prev_done(self, event=None):
        if self.video_path is not None:
            try:
                min_n = max([f for f in self.results.keys() if f < self.n_frame])
                if min_n != self.n_frame:
                    self.n_frame = min_n
            except Exception as e:
                pass

    # move to next done frame
    def on_next_done(self, event=None):
        if self.video_path is not None:
            try:
                min_n = min([f for f in self.results.keys() if f > self.n_frame])
                if min_n != self.n_frame:
                    self.n_frame = min_n
            except Exception as e:
                pass

    # popup a help description widget
    def on_settings(self, event=None):
        self.popup_help(self.parent)

    # check if the label is done
    def check_done(self):
        n = len(self.results.keys())
        if n == N and not self.is_checked:
            self.is_checked = True
            if askokcancel('往下一個影像', '該影像已經標註 %s 了!\n要直接去下一個影像嗎?' % N):
                self.on_next()

    def tvitem_click(self, event, item=None):

        sel_items = self.done_bbox_tv.selection() if item is None else item

        if sel_items:
            self.n_frame = self.done_bbox_tv.item(sel_items)['values'][0]
            if self.n_frame in self.results.keys():
                self.class_reindex()
            else:
                self.on_class_button(k=1)
            self.update_treeview()
