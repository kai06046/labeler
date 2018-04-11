import logging
import sys
import tkinter as tk

from src.app import Labeler

LOGGER = logging.getLogger(__name__)

# parser = argparse.ArgumentParser(description='Some arguement for path connector')
# parser.add_argument('-m', '--max', type=int, default=300, help='maximum frame for displaying path')
# parser.add_argument('-t', '--tolerance', type=int, default=38, help='maximum tolerance of distance')
# args = vars(parser.parse_args())

def log_handler(*loggers):
	formatter = logging.Formatter(
		'%(asctime)s %(filename)12s:L%(lineno)3s [%(levelname)8s] %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)

	# stream handler
	sh = logging.StreamHandler(sys.stdout)
	sh.setLevel(logging.INFO)
	sh.setFormatter(formatter)

	for logger in loggers:
		logger.addHandler(sh)
		logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s %(filename)12s:L%(lineno)3s [%(levelname)8s] %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		stream=sys.stdout
	)
	log_handler(LOGGER)
	labeler = Labeler()
	labeler.run()
