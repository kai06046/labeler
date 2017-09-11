import cv2
import numpy as np
from PIL import Image, ImageTk

COLOR = [(50, 205, 50), (255, 191, 0), (0, 215, 255), (0, 165, 255), (211, 85, 186), (255, 102, 255), (255, 255, 0), (0, 0, 0), (100, 10, 255), (255, 255, 255)]

class Utils(object):

    def draw(self):
        self.__frame__ = self.__orig_frame__.copy()

        if self.parent.state() == 'zoomed':
            shape = self.__frame__.shape
            self.parent.update()
            r1 = (shape[1] / self.parent.winfo_width())
            r2 = (shape[0] / self.parent.winfo_height())
            shrink_r = r1
            self._c_width = self._r_width / shrink_r
            self._c_height = self._r_height / shrink_r
            nw = int(shape[1] * self._c_width)
            nh = int(shape[0] * nw / shape[1])
            newsize = (nw, nh)
            self.__frame__ = cv2.resize(self.__frame__, newsize)

        self.__frame__ = cv2.cvtColor(self.__frame__, cv2.COLOR_BGR2RGB)
