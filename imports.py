import sys
import os
import re
import shutil
from PyQt5.QtCore import Qt, QEvent, QDir, QFileInfo, QUrl, QPropertyAnimation, QRect, QMetaObject
from PyQt5.QtGui import QColor, QPalette, QPixmap, QLinearGradient, QPainter, QFont, QIcon, QDesktopServices,QValidator

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QTextEdit, QVBoxLayout, QWidget, QFormLayout, QSizePolicy,
    QFileDialog, QMessageBox, QHBoxLayout, QTabWidget, QFrame,
    QPushButton, QListWidget, QListWidgetItem, QStackedWidget,
    QInputDialog, QFileDialog, QTextBrowser, QDialogButtonBox, QDialogButtonBox
)
from PyQt5.QtTest import QTest
import time
import base64
from unittest.mock import patch, MagicMock


from dashboard import ChatHeaderWidget
from login import LoginWindow
from signup import SignupWindow
from mainwindow import MainWindow
from encryption import EncryptionManager
from contact_functions import ContactFunctions
from chat_functions import ChatFunctions