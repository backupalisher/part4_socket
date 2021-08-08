import socket_utils
from socket_utils import *
from ui import *
import sys


def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    init_socket()
    app.exec_()
    sio.disconnect()


if __name__ == '__main__':
    main()
