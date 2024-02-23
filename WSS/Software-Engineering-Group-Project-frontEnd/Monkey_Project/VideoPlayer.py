from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QStyle, QSlider
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import sys


# Create a window
class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('Player.ico'))
        self.setWindowTitle('Jtube')
        self.setGeometry(350, 100, 700, 500)

        p = self.palette()
        p.setColor(QPalette.Window, Qt.white)
        self.setPalette(p)

        self.create_player()


    #create the media player
    def create_player(self):

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videowidget = QVideoWidget()


        self.openbtn = QPushButton('Open Video')
        self.openbtn.clicked.connect(self.open_file)


        self.playbtn = QPushButton()
        self.playbtn.setEnabled(False)
        self.playbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playbtn.clicked.connect(self.play_video)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)


        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        #utility buttons
        hbox.addWidget(self.openbtn)
        hbox.addWidget(self.playbtn)
        hbox.addWidget(self.slider)


        vbox = QVBoxLayout()
        vbox.addWidget(videowidget)

        vbox.addLayout(hbox)

        self.mediaPlayer.setVideoOutput(videowidget)

        self.setLayout(vbox)

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        
        
    #open video file
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playbtn.setEnabled(True)
            
    #play video
    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()


    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playbtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playbtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
            

    #set the position of the slider
    def position_changed(self, position):
        self.slider.setValue(position)


    #set the duration of the slider
    def duration_changed(self, duration):
        self.slider.setRange(0, duration)


    def set_position(self, position):
        self.mediaPlayer.setPosition(position)



#for the application to run
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())