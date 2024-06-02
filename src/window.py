from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setGeometry(1400, 75, 400, 300)
        self.setWindowTitle('NoteTaker')
        self.setWindowIcon(QIcon("icons/leevai_logo_circle.png"))

    def attach_default_components(self):
        self.bottom_label = QtWidgets.QLabel(self)
        self.bottom_label.setText('Processing...')
        self.bottom_label.move(175, 225)

    def set_label_text(self, text: str) -> None:
        self.bottom_label.setText(text)
