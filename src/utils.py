import cv2
import numpy as np
from PIL import Image, ImageTk

COLOR = [(50, 205, 50), (255, 191, 0), (0, 0, 238), (211, 85, 186), (0, 0, 0)]

class Utils(object):

    def draw(self):
        self.__frame__ = self.__orig_frame__.copy()

        # draw bounding boxes
        if self.video_path is not None:
            if self.n_frame in self.results.keys():
                boxes = self.results[self.n_frame]
                for b in boxes:
                    class_ind, p1, p2 = b
                    color = COLOR[class_ind - 1]
                    cv2.rectangle(self.__frame__, p1, p2, color, 2)

            if self.is_mv and self.mv_pt is not None and self.p1 is not None:
                color = COLOR[self.class_ind - 1]
                cv2.rectangle(self.__frame__, self.p1, self.mv_pt, color, 2)

        if self.parent.state() == 'zoomed':
            shape = self.__frame__.shape
            self.parent.update()
            r1 = (shape[1] / self.parent.winfo_width())
            r2 = (shape[0] / self.parent.winfo_height())
            shrink_r = max(r1, r2)
            self._c_width = self._r_width / shrink_r
            self._c_height = self._r_height / shrink_r
            nw = int(shape[1] * self._c_width)
            nh = int(shape[0] * nw / shape[1])
            newsize = (nw, nh)
            self.__frame__ = cv2.resize(self.__frame__, newsize)

        self.__frame__ = cv2.cvtColor(self.__frame__, cv2.COLOR_BGR2RGB)
