from pydub import AudioSegment
import librosa
import math
import wave
import time
import os


class Song:
    def __init__(self):
        self.path = None
        self.song = None
        self.audio_set = False
        self.time = 0

        self.accompaniment = None
        self.vocals = None
        self.drums = None
        self.bass = None

    def set_song(self, song_file):
        self.audio_set = False

        self.path = song_file
        self.song = self.load_song(song_file)
        self.time = math.floor(librosa.get_duration(filename=song_file))

        if Song.not_spleetered(song_file):
            print("spleeter is working")
            self.spleeter(self.path.split("/")[-1])
            print("Spleeter completed")
        else:
            print("File has already been spleeted and stored in cache")

        self.open_sub_files(song_file)

    def open_sub_files(self, file_name):
        folder = file_name.split("/")[-1].split(".")[0]
        org_path = os.getcwd().replace("\\", "/")

        self.vocals = wave.open(f"{org_path}/cache/{folder}/vocals.wav", "rb")
        self.accompaniment = wave.open(f"{org_path}/cache/{folder}/other.wav", "rb")
        self.bass = wave.open(f"{org_path}/cache/{folder}/bass.wav", "rb")
        self.drums = wave.open(f"{org_path}/cache/{folder}/drums.wav", "rb")

        print("Sub Files loading is complete")

    def load_song(self, song_file):
        if song_file:
            song_type_name = song_file.split("/")[-1]
            if song_type_name.split(".")[-1] == "mp3":

                if not os.path.exists(song_file.split(".")[0] + ".wav"):
                    song_name = song_type_name
                    song_dst = song_type_name.split(".")[0] + ".wav"

                    Song.convert(song_name, song_dst)
                    self.path = str(os.getcwd() + "\\" + song_dst)
                    return wave.open(str(os.getcwd() + "\\" + song_dst), "rb")

                return wave.open(song_file.replace("mp3", "wav"), "rb")

            return wave.open(song_file, "rb")

        else:
            return None

    @staticmethod
    def spleeter(file):
        os.chdir("./")
        os.system(f'"spleeter separate -o ./cache/ -p spleeter:4stems {file}"')

    @staticmethod
    def not_spleetered(song_file):
        name = song_file.split("/")[-1].split(".")[0]
        return not os.path.isdir(f"./cache/{name}") and "cache" not in song_file  # only file name

    @staticmethod
    def convert(src, dst):
        # convert mp3 to wav
        print("converting file")
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")
        print("File converted")


# C:\Users\cyber\AppData\Roaming\Python\Python39\Scripts
