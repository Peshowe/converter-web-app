import os
import psutil
import sys

THRESHOLD = 2 * 1024 * 1024


class MemoryUsageMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        request._mem = psutil.Process(os.getpid()).memory_info()

    def process_response(self, request, response):
        mem = psutil.Process(os.getpid()).memory_info()
        diff = mem.rss - request._mem.rss
        # if diff > THRESHOLD:
        print("MEMORY USAGE %r" % ((diff, request.path),))
        return response