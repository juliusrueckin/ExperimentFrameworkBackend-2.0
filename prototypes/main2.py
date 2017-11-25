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
import io

from threading  import Thread
from queue import Queue, Empty

proc = subprocess.Popen("python -u bubble.py", stdin= subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid, universal_newlines=True)

# Poll process for new output until finished
while proc.poll() is None:
	nextline = proc.stdout.readline()
	if nextline == '' and proc.poll() is not None:
		break
	sys.stdout.write("Processed stdout: " + nextline)