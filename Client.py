from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pyaudio
import socket
import time
import math


class Connection:
    def __init__(self):
        self.my_socket = None

    def connect(self):
        self.my_socket = socket.socket()
        self.my_socket.connect(("127.0.0.1", 5555))

        print("Connected to server")
        print(f"Your speaker is {self.my_socket.recv(1024).decode()}")


class Speaker(Connection):
    def __init__(self):
        super().__init__()
        self.song_data = b''
        self.mute = False
        self.frame_length = None
        self.volume = self.volume_obj()
        self.stream = Speaker.initialize_stream()

        self.connect()
        self.start_speaker()

    @staticmethod
    def volume_obj():
        # Get default audio device using PyCAW
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    @staticmethod
    def initialize_stream():
        p = pyaudio.PyAudio()
        return p.open(format=8,
                      channels=2,
                      rate=44100,
                      output=True)
        # This format is static

    def get_song_data(self, frame_length):
        self.frame_length = frame_length

        song_data = self.my_socket.recv(self.frame_length)
        while b'sent' not in song_data:
            self.song_data += song_data
            song_data = self.my_socket.recv(self.frame_length)

        if song_data != b'sent':
            self.song_data += song_data

        print("song fully loaded to speaker")
        self.my_socket.send("data received".encode())  # confirmation

    def start_speaker(self):
        while True:
            task = list(self.my_socket.recv(1024).decode().split("*"))
            print(task)

            task_copy = task.copy()
            for command in task_copy:

                if command == "play":
                    command_index = task.index(command)

                    if task[task.index(command) + 2] == "volume":
                        volume_percentage = int(task[task.index(command) + 3])
                        self.mute = volume_percentage == 0
                        if not self.mute:
                            self.volume.SetMasterVolumeLevel(10 * math.log(volume_percentage / 100, 10), None)

                        task.remove(task[command_index + 2])  # volume
                        task.remove(task[command_index + 2])  # volume percentage

                    if not self.mute:
                        current_second = int(task[int(task.index(command) + 1)])
                        self.stream.write(self.song_data[current_second * self.frame_length: self.frame_length * (current_second + 1)])

                    task.remove(task[command_index])  # play
                    task.remove(task[command_index])  # current second

                if command == "switch":
                    self.song_data = bytes(task[task.index(command) + 2], encoding='utf8')
                    self.get_song_data(frame_length=int(task[task.index(command) + 1]))


def main():
    Speaker()


if __name__ == "__main__":
    main()
