from PySide6.QtWidgets import QApplication
import sys
from utils import gui

def main():
    print('Welcome to thumbGen!')
    app = QApplication([])
    window = gui.MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
