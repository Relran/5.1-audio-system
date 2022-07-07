from Song import Song
from Server import Server

import timeit
import math
import time


class Stream:
    def __init__(self, server):
        self.song = Song()
        self.server = server
        self.updating = False
        self.playing = False
        self.repeat_off = True
        self.repeat_playlist = False
        self.repeat_track = False
        self.volume_changed = True
        self.exactly_one_second_pass = True
        self.slider = None
        self.playlist = []
        self.index = 0
        self.current_second = 0
        self.volume = 50
        self.start_time = 0

    def stream_sound_to_speakers(self):
        while True:
            while self.playing and self.playlist != []:
                self.manage_time()
                self.update_song()

                if self.exactly_one_second_pass and not self.updating and self.playing:
                    if not self.volume_changed:
                        message = f"play*{self.current_second}*"
                    else:
                        message = f"play*{self.current_second}*volume*{self.volume}*"
                        self.volume_changed = False

                    connected_speakers = self.server.speaker_dict.copy()
                    for speaker in connected_speakers:
                        conn = speaker[1]
                        try:
                            conn.send(message.encode())

                        except Exception:
                            self.disconnect_speaker_from_stream(speaker)

                elif self.current_second == self.song.time and not self.updating:
                    self.forward_song()

    def forward_song(self, manual_change=False):
        if self.repeat_track:
            if manual_change or not self.song.audio_set:
                self.update_stream(self.playlist[self.index])
                self.index += 1
                self.updating = True
            elif self.song.audio_set:
                self.current_second = 0

        elif self.index == len(self.playlist):
            if self.repeat_playlist:
                self.update_stream(self.playlist[0])
                self.updating = True
                self.index = 1
            else:
                print("End of playlist")

        else:
            self.update_stream(self.playlist[self.index])
            self.index += 1
            self.updating = True

    def update_stream(self, song_file):
        self.song.set_song(song_file)
        self.slider.setMaximum(self.song.time)

        print("Stream song updated")
        self.song.audio_set = True
        self.current_second = 0

    def update_song(self):
        """"""""" 
        update song if there is a new song selected/switched. Some just connected will join.
        """""""""
        if self.exactly_one_second_pass and self.playing and self.song.audio_set and self.updating:
            print("Updating all connected speakers...")

            self.server.speaker_dict += self.server.just_connected
            self.server.just_connected = []

            for speaker in self.server.speaker_dict:
                name = speaker[0]
                conn = speaker[1]
                try:
                    self.switch_song_to_speaker(name, conn)
                except Exception:
                    self.disconnect_speaker_from_stream(speaker)

            self.updating = False
            print("All connected speakers updated")
            print(f"Now playing song {self.song.path}")

    def switch_song_to_speaker(self, name, conn):

        if name == "center":
            frame_length = self.song.vocals.getsampwidth() * self.song.vocals.getframerate() * self.song.vocals.getnchannels()
            conn.send(f"switch*{frame_length}*".encode())
            time.sleep(0.1)
            conn.send(self.song.vocals.readframes(-1))
        elif name in ["FR", "FL"]:
            frame_length = self.song.accompaniment.getsampwidth() * self.song.accompaniment.getframerate() * self.song.accompaniment.getnchannels()
            conn.send(f"switch*{frame_length}*".encode())
            time.sleep(0.1)
            conn.send(self.song.accompaniment.readframes(-1))
        elif name in ["SR", "SL"]:
            frame_length = self.song.drums.getsampwidth() * self.song.drums.getframerate() * self.song.drums.getnchannels()
            conn.send(f"switch*{frame_length}*".encode())
            time.sleep(0.1)
            conn.send(self.song.drums.readframes(-1))
        else:  # subwoofer speaker
            frame_length = self.song.bass.getsampwidth() * self.song.bass.getframerate() * self.song.bass.getnchannels()
            conn.send(f"switch*{frame_length}*".encode())
            time.sleep(0.1)
            conn.send(self.song.bass.readframes(-1))

        time.sleep(0.5)
        conn.send("sent".encode())
        conn.recv(1024)  # wait for confirmation the data has been set
        time.sleep(0.1)

    def manage_time(self):
        if self.exactly_one_second_pass and not self.updating:
            self.start_time = math.floor(time.time())
            self.exactly_one_second_pass = False

        if math.floor(time.time()) - self.start_time == 1 and self.current_second < self.song.time:
            self.current_second += 1
            self.exactly_one_second_pass = True

    def set_slider(self, slider):
        self.slider = slider

    def disconnect_speaker_from_stream(self, speaker):
        self.server.speaker_dict.remove(speaker)
        self.server.speakers_list.append(speaker[0])
        speaker[1].close()

        print(f"Speaker {speaker[0]} disconnected")

        if len(self.server.speaker_dict) == 0:
            self.playing = False
            print("All of the speakers disconnected, pausing the stream")
