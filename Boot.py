from Threads import ThreadController
from Stream import Stream
from Server import Server
from Song import Song


class Boot(ThreadController, Server, Song):
    def __init__(self):
        super().__init__()
        self.gui_thread = ThreadController()
        self.server = Server()
        self.stream = Stream(self.server)

        self.start_main_threads()

    def start_main_threads(self):
        self.gui_thread.addThread(target=self.stream.stream_sound_to_speakers)
        self.gui_thread.addThread(target=self.server.connect_speakers)


# C:\Users\cyber\AppData\Roaming\Python\Python39\Scripts
