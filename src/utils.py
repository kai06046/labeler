import logging

import cv2
import numpy as np
from PIL import Image, ImageTk

LOGGER = logging.getLogger(__name__)
COLOR = [(50, 205, 50), (255, 191, 0), (0, 0, 238), (211, 85, 186), (0, 165, 255)]
label_text = {1: 'O', 2: 'X', 3: '=', 4: 'T', 5: '?'}

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
                    if self.is_mv and (self.class_ind == class_ind and self.class_ind != 5):
                        continue
                    cv2.rectangle(self.__frame__, p1, p2, color, 1)
                    cv2.putText(self.__frame__, label_text[class_ind], (p1[0], p1[1] - 10), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (255, 255, 255), 3)
                    cv2.putText(self.__frame__, label_text[class_ind], (p1[0], p1[1] - 10), cv2.FONT_HERSHEY_TRIPLEX, 0.7, color, 1)

            if self.is_mv and self.mv_pt is not None and self.p1 is not None:
                color = COLOR[self.class_ind - 1]
                xmin = min(self.p1[0], self.mv_pt[0])
                ymin = min(self.p1[1], self.mv_pt[1])
                xmax = max(self.p1[0], self.mv_pt[0])
                ymax = max(self.p1[1], self.mv_pt[1])
                cv2.rectangle(self.__frame__, (xmin, ymin), (xmax, ymax), color, 1)
                cv2.putText(self.__frame__, label_text[self.class_ind], (xmin, ymin-10), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (255, 255, 255), 3)
                cv2.putText(self.__frame__, label_text[self.class_ind], (xmin, ymin-10), cv2.FONT_HERSHEY_TRIPLEX, 0.7, color, 1)

        if self.parent.state() == 'zoomed':
            shape = self.__frame__.shape
            self.parent.update()
            r1 = (shape[1] / self.parent.winfo_width())
            r2 = (shape[0] / self.parent.winfo_height())
            shrink_r = max(r1, r2)
            self._c_width = self._r_width / shrink_r
            nw = int(shape[1] * self._c_width)
            nh = int(shape[0] * nw / shape[1])
            self._c_height = nw / shape[1]
            newsize = (nw, nh)
            self.__frame__ = cv2.resize(self.__frame__, newsize)

        self.__frame__ = cv2.cvtColor(self.__frame__, cv2.COLOR_BGR2RGB)
