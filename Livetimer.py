
from threading import Timer, Thread, Event

#   Copyright 2018-2019 AyKa Technologies
#

# This Timer Class used to send livedata using threading
class TimerClass():

    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t, self.handle_function)
        self.thread.start()
    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


