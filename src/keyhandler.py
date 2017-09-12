import tkinter as tk
from tkinter import ttk

class KeyHandler(object):

    def on_class_button(self, k):
        self.class_ind = k
        for i, b in enumerate(self.class_buttons):
            if (k - 1) != i:
                b['state'] = 'normal'
            else:
                b['state'] = 'disabled'

    def set_n_frame(self, s):
        v = int(float(s))
        self.n_frame = v

    def on_l_mouse(self, event=None):
        if not self.is_mv:
            self.p1 = (event.x, event.y)
            self.is_mv = True

    def on_r_mouse(self, event=None):
        n = len(self.results[self.n_frame])
        if n > 0:
            self.results[self.n_frame].pop()
            if str(n-1) in self.treeview.get_children():
                self.treeview.delete(str(n-1))

    def on_mouse_mv(self, event=None):
        self.label_xy.configure(text='x: %s y: %s' % (event.x, event.y))
        if self.is_mv:
            self.mv_pt = (event.x, event.y)

    def off_mouse(self, event=None):
        if self.is_mv and self.mv_pt is not None:
            self.is_mv = False
            values = (self.class_ind, self.p1, self.mv_pt)
            if self.n_frame not in self.results.keys():
                self.results[self.n_frame] = [values]
            else:
                self.results[self.n_frame].append(values)

            self.treeview.insert('', 'end', str(len(self.treeview.get_children())), values=values, tags = (str(self.class_ind)))
            self.p1 = self.mv_pt = None
