import os
import sys
from multiprocessing import cpu_count
accesslog = '-'
bind = '0.0.0.0:{}'.format(os.getenv('PORT', '8000'))
capture_output = True
errorlog = '-'
preload_app = True
worker_tmp_dir = os.getenv('XDG_RUNTIME_DIR', '/tmp')
workers = cpu_count() + 1
threads = cpu_count()