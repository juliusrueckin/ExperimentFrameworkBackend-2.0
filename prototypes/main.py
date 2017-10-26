#import some stuff for process management
import subprocess
import collections
import os
import signal
import time
import re
import sys
import select
import threading

from threading  import Thread
from queue import Queue, Empty

# boolean that holds true, if posix is a built-in-module
ON_POSIX = 'posix' in sys.builtin_module_names

# read output line by line
def enqueue_output(out, queue):
	for line in iter(out.readline, b''):
		queue.put(line)
	out.close()

# initialize subprocess
proc = subprocess.Popen("python bubble.py",stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1, preexec_fn=os.setsid, close_fds=ON_POSIX)

# initialize thread, that processes output of subprocess
queue = Queue()
t = Thread(target=enqueue_output, args=(proc.stdout, queue))
t.daemon = True # thread dies with the program
t.start()

# do other things here

# read line without blocking
while proc.poll() is None:
	try:
		line = queue.get_nowait() # or queue.get(timeout=.1)
	except Empty:
		#print('no output yet')
		pass
	else: # got line
		# do something with line
		print(line.decode("utf-8"))