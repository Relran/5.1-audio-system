from threading import Thread


class ThreadController(Thread):
    def __init__(self):
        super(ThreadController, self).__init__()
        self.activeThreads = []

    def addThread(self, target, args=None):
        if args:
            args_s = args
        else:
            args_s = None

        if args_s:
            thread = Thread(target=target, args=args_s)
        else:
            thread = Thread(target=target)

        thread.start()
        self.activeThreads.append(thread)

    def ShowActiveThreads(self):
        print(self.activeThreads)
