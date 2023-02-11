from lib.primitives.queue import Queue as BaseQueue, QueueEmpty

class Queue(BaseQueue):
    def __init__(self, maxsize = 0):
        super().__init__(maxsize)
        
    def put_nowait(self, val):  # Put an item into the queue without blocking.
        if self.full():
            self.make_room()
        self._put(val)
            
    def make_room(self):
        if self.empty():
            raise QueueEmpty()
        self._queue.pop(0)
