import tkinter as tk
from tkinter import ttk

class KeyHandler(object):

	def on_class_button(self, k):
		self.class_ind = k
		for i, b in enumerate(self.class_buttons):
			if (k - 1) != i:
				b['state'] = 'normal'
			else:
				print('disabled')
				b['state'] = 'disabled'
		print(self.class_ind)

	def set_n_frame(self, s):
		v = int(float(s))
		self.n_frame = v