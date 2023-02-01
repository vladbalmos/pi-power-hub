from lib.primitives.queue import Queue as BaseQueue, QueueFull

class Queue(BaseQueue):
    def __init__(self, maxsize = 0):
        super().__init__(maxsize)
        
            
    def make_room(self):
        if self.empty():
            raise QueueFull()
        self._queue.pop(0)
