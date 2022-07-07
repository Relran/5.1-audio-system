import math
import time

from Boot import Boot

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class GUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('SSP')
        self.setWindowIcon(QIcon('./pictures/icon.jpg'))
        self.setIconSize(QSize(30, 30))
        self.setGeometry(500, 500, 500, 500)
        self.setMinimumSize(500, 500)
        self.setMaximumSize(500, 500)
        self.toolbar = None
        self.label2 = None
        self.label = None
        self.slider = None
        self.volume_slider = None
        self.repeat_option_btn = None
        self.play_pause_btn = None
        self.player = None
        self.song_list = QListWidget(self)

        self.essential = Boot()

        self.init_ui()

    def init_ui(self):

        background_image = QImage("./pictures/main_background.jpg")
        resized_image = background_image.scaled(QSize(500, 500))  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(resized_image))
        self.setPalette(palette)

        # creating top toolbar
        self.toolbar = QToolBar()
        self.label = QLabel("0:0", self)
        self.label.setGeometry(350, 400, 50, 50)
        self.label2 = QLabel("50%", self)
        self.label2.setGeometry(457, 140, 50, 50)
        self.addToolBar(self.toolbar)

        upload_act = QToolButton()
        upload_act.setIcon(QIcon("./pictures/upload.png"))
        upload_act.clicked.connect(self.open_file_name_dialog)

        self.play_pause_btn = QToolButton()
        self.play_pause_btn.setIcon(QIcon("./pictures/play_button.png"))
        self.play_pause_btn.clicked.connect(self.play_pause)

        forward_btn = QToolButton()
        forward_btn.setIcon(QIcon("./pictures/forward_button.png"))
        forward_btn.clicked.connect(self.forward)

        backward_btn = QToolButton()
        backward_btn.setIcon(QIcon("./pictures/backward_button.png"))
        backward_btn.clicked.connect(self.backward)

        self.repeat_option_btn = QToolButton()
        self.repeat_option_btn.setIcon(QIcon("./pictures/repeat_off.png"))
        self.repeat_option_btn.clicked.connect(self.repeat_change)

        self.toolbar.addWidget(upload_act)
        self.toolbar.addWidget(self.repeat_option_btn)
        self.toolbar.addWidget(backward_btn)
        self.toolbar.addWidget(self.play_pause_btn)
        self.toolbar.addWidget(forward_btn)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(150, 400, 200, 30)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.sliderMoved.connect(self.change_time)
        self.essential.gui_thread.addThread(target=self.song_slider_time)

        self.volume_slider = QSlider(Qt.Vertical, self)
        self.volume_slider.setGeometry(450, 50, 30, 100)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.sliderMoved.connect(self.change_volume)

        self.song_list.setGeometry(0, 40, 150, 100)
        self.song_list.setSortingEnabled(True)
        self.song_list.itemDoubleClicked.connect(self.manually_switch_song)

        self.essential.stream.set_slider(self.slider)
        # creating media player interactions

    def open_file_name_dialog(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        song_file, _ = QFileDialog.getOpenFileName(self, "File Explorer", "",
                                                        "wav files (*.wav);;mp3 files (*.mp3)",
                                                                      options=options)
        if song_file:
            wav = song_file.split(".")[0] + ".wav"
            mp3 = song_file.split(".")[0] + ".mp3"

            if wav not in self.essential.stream.playlist and mp3 not in self.essential.stream.playlist:
                self.song_list.addItem(song_file)
                self.essential.stream.playlist.append(song_file)
            else:
                print("Cant duplicate songs")
        else:
            print("No song selected")

    def song_slider_time(self):
        while True:
            if self.essential.stream.exactly_one_second_pass:
                self.slider.setValue(self.essential.stream.current_second)
                self.set_time()

    def set_time(self, value=None):
        if not value:
            song_sec = self.essential.stream.current_second % 60
            song_min = math.floor((self.essential.stream.current_second - song_sec) / 60)
        else:
            song_sec = value % 60
            song_min = math.floor((value - song_sec) / 60)
        self.label.setText(f"{song_min}:{song_sec}")

    def change_time(self, value):
        self.set_time(value)
        self.essential.stream.current_second = value

    def change_volume(self, value):
        self.essential.stream.volume = value
        self.essential.stream.volume_changed = True
        self.label2.setText(f'{value}%')

    def repeat_change(self):
        if self.essential.stream.repeat_off:
            self.essential.stream.repeat_playlist = True
            self.essential.stream.repeat_off = False
            self.repeat_option_btn.setIcon(QIcon("./pictures/repeat_playlist.png"))

        elif self.essential.stream.repeat_playlist:
            self.essential.stream.repeat_track = True
            self.essential.stream.repeat_playlist = False
            self.repeat_option_btn.setIcon(QIcon("./pictures/repeat_track.png"))

        else:
            self.essential.stream.repeat_off = True
            self.essential.stream.repeat_track = False
            self.repeat_option_btn.setIcon(QIcon("./pictures/repeat_off.png"))

    def manually_switch_song(self, song_file):
        if not self.essential.stream.updating:
            self.essential.stream.index = self.essential.stream.playlist.index(song_file.text())
            self.essential.stream.forward_song(manual_change=True)

        else:
            print("Stream is updating, wait until finish")

    def forward(self):
        if self.essential.stream.song.audio_set and not self.essential.stream.updating:
            self.essential.stream.forward_song()

    def backward(self):
        if self.essential.stream.song.audio_set and not self.essential.stream.updating:

            if self.essential.stream.repeat_track:
                self.essential.stream.forward_song()

            elif not self.essential.stream.index == 1:
                self.essential.stream.index -= 2
                self.essential.stream.forward_song()

            else:
                print("Can't go backward")

    def play_pause(self):
        if self.essential.stream.server.speaker_dict == [] and self.essential.stream.server.just_connected == []:
            print("No speakers connected")
            return
        elif len(self.essential.stream.playlist) == 0:
            print("Playlist is empty, choose a song")
            return
        else:
            self.essential.stream.playing = not self.essential.stream.playing

            if self.essential.stream.playing:
                self.essential.stream.start_time = math.floor(time.time())
                self.play_pause_btn.setIcon(QIcon("./pictures/pause_button.png"))

            else:
                self.play_pause_btn.setIcon(QIcon("./pictures/play_button.png"))


def main():
    app = QApplication([])
    window = GUI()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
