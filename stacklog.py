# Copyright (C) 2012 Vincent Povirk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import imp
import sys
import time
import threading

class StackLogger(object):
    def __init__(self, outfile, threshold):
        self.local = threading.local()
        self.outfile = outfile
        self.threshold = threshold

    def get_calls(self):
        try:
            return self.local.calls
        except AttributeError:
            self.local.calls = []
            return self.local.calls

    def __call__(self, frame, event, arg):
        if event == 'call':
            if frame.f_code.co_filename != __file__:
                calls = self.get_calls()
                calls.append((time.time(), frame))
                return self
        elif event == 'return':
            calls = self.get_calls()
            for i in range(len(calls)-1, -1, -1):
                if calls[i][1] is frame:
                    break
            else:
                return
            start_time, _frame = calls[i]
            calls[i:] = ()
            end_time = time.time()
            if end_time - start_time >= self.threshold:
                print '%s%s %s %s %s %s' % (' ' * len(calls), frame.f_code.co_filename, frame.f_code.co_name, frame.f_code.co_firstlineno, start_time, (end_time - start_time))

def main(argv):
    import __main__ # must prevent the module from being collected when we edit sys.modules, as that resets the globals

    logger = StackLogger(sys.stdout, float(argv[1]))
    filename = argv[2]
    sys.argv = argv[2:]

    module = imp.new_module('__main__')
    module.__file__ = filename
    sys.modules['__main__'] = module

    f = file(filename, 'U')
    source = f.read()
    f.close()

    sys.settrace(logger)

    exec compile(source, filename, 'exec') in module.__dict__

if __name__ == '__main__':
    sys.exit(main(sys.argv))

