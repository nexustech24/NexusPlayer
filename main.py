import sys
import os
import vlc
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QSlider, QFileDialog,
                             QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtMultimediaWidgets import QVideoWidget
import platform


class NexusPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NexusPlayer")
        self.setGeometry(200, 200, 800, 450)

        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        self.create_ui()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_slider)

    def create_ui(self):
        widget = QWidget()
        self.layout = QVBoxLayout()

        self.video_frame = QVideoWidget()
        palette = self.video_frame.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.video_frame.setPalette(palette)
        self.video_frame.setAutoFillBackground(True)

        self.video_frame.setVisible(False)
        self.layout.addWidget(self.video_frame)

        control_layout = QHBoxLayout()

        self.play_button = QPushButton("|>| (Play)")
        self.play_button.clicked.connect(self.play_media)
        control_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("|| (Pause)")
        self.pause_button.clicked.connect(self.pause_media)
        control_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("[] (Stop)")
        self.stop_button.clicked.connect(self.stop_media)
        control_layout.addWidget(self.stop_button)

        self.layout.addLayout(control_layout)

        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)
        self.layout.addWidget(self.open_button)

        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # Default volume at 50%
        self.volume_slider.valueChanged.connect(self.set_volume)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        self.layout.addLayout(volume_layout)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.layout.addWidget(self.position_slider)

        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Media File", "",
                                                   "Media Files (*.mp4 *.avi *.webm *.mkv *.flv *.mp3 *.wav *.ogg *.flac);;All Files (*)",
                                                   options=options)
        if file_path:
            self.load_media(file_path)

    def load_media(self, file_path):
        if os.path.isfile(file_path):
            media = self.instance.media_new(file_path)
            self.media_player.set_media(media)
            media.parse()
            self.play_button.setEnabled(True)
            self.setWindowTitle(f"NexusPlayer - {os.path.basename(file_path)}")

            if file_path.lower().endswith(('.mp4', '.avi', '.webm', '.mkv', '.flv')):
                self.video_frame.setVisible(True)
                if platform.system() == "Windows":
                    self.media_player.set_hwnd(self.video_frame.winId())  # Windows-specific handle
                else:
                    self.media_player.set_xwindow(self.video_frame.winId())  # Linux/MacOS-specific handle
            else:
                self.video_frame.setVisible(False)  # Hide the video widget if it's an audio file

            self.timer.start()

    def play_media(self):
        if self.media_player.get_media() is not None:
            self.media_player.play()

    def pause_media(self):
        if self.media_player.is_playing():
            self.media_player.pause()

    def stop_media(self):
        self.media_player.stop()
        self.timer.stop()

    def set_volume(self, value):
        self.media_player.audio_set_volume(value)

    def set_position(self, position):
        self.media_player.set_position(position / 1000.0)

    def update_slider(self):
        if self.media_player.is_playing():
            position = self.media_player.get_position()
            self.position_slider.setValue(int(position * 1000))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = NexusPlayer()
    player.show()
    sys.exit(app.exec_())
