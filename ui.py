from PyQt5.QtWidgets import QMainWindow, QTextEdit, QMenuBar, QApplication, QMenu, QAction, qApp, QSystemTrayIcon, \
    QStyle
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
import sys


class OutputLogger(QObject):
    emit_write = Signal(str, int)

    class Severity:
        DEBUG = 0
        ERROR = 1

    def __init__(self, io_stream, severity):
        super().__init__()

        self.io_stream = io_stream
        self.severity = severity

    def write(self, text):
        self.io_stream.write(text)
        self.emit_write.emit(text, self.severity)

    def flush(self):
        self.io_stream.flush()


OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout, OutputLogger.Severity.DEBUG)
OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr, OutputLogger.Severity.ERROR)

sys.stdout = OUTPUT_LOGGER_STDOUT
sys.stderr = OUTPUT_LOGGER_STDERR


class MainWindow(QMainWindow):
    tray_icon = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle('DeviceStatus - console')
        self.resize(650, 450)
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet('QTextEdit {background-color: #202136; color: #F4F5F9;}')

        OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        # OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)

        # menu_bar = QMenuBar()
        # menu = menu_bar.addMenu('File')
        # menu.addAction('hello', lambda: print('Hello!'))
        # menu.addAction('Exit', lambda: self.closeEvent(True))
        # menu.addAction('fail', lambda: print('Fail!', file=sys.stderr))
        # self.setMenuBar(menu_bar)

        self.setCentralWidget(self.text_edit)

        # Инициализируем QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def append_log(self, text, severity):
        text = repr(text)

        # if severity == OutputLogger.Severity.ERROR:
        #     self.text_edit.append('<b>{}</b>'.format(text))
        # else:
        #     self.text_edit.append(text)
        text = text.replace("'", "").replace("\\n", "")
        if text:
            try:
                self.text_edit.append(text)
            except:
                self.text_edit.clear()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )
