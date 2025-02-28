import sqlite3
from dashboard import ChatHeaderWidget
from imports import *
from contact_functions import ContactFunctions
from database import get_contacts, update_chat_history
from PyQt5.QtCore import pyqtSignal, QRect, QPropertyAnimation
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QTextBrowser, QLineEdit, QPushButton,
    QMessageBox, QStackedWidget
)
from PyQt5.QtGui import QPixmap, QLinearGradient, QPalette, QColor
from socketio import Client

# Hybrid encryption routines are in chat_encryption.py
# The ChatFunctions class uses them to encrypt/decrypt messages
from chat_functions import ChatFunctions

# Our simplified RSAKey container (in plain text "n,e" or "n,e,d" format)
from custom_rsa import RSAKey

class MainWindow(QMainWindow, ChatFunctions, ContactFunctions):
    update_gui_signal = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.update_gui_signal.connect(self.update_gui)

        # UI Setup
        self.setWindowTitle("Viber Lite")
        self.setFixedSize(800, 600)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#6700B3"))
        gradient.setColorAt(1, QColor("#440099"))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left Panel
        self.left_panel_layout = QVBoxLayout()
        self.left_panel_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(self.left_panel_layout)

        # Logo + Title
        logo_title_layout = QHBoxLayout()
        viber_logo_label = QLabel()
        pix = QPixmap("D:\\5th sem\\cw of crypto\\crypto\\crypto\Viberlite.png")
        if not pix.isNull():
            viber_logo_label.setPixmap(pix.scaled(80, 80, Qt.KeepAspectRatio))
        else:
            viber_logo_label.setText("Logo")
        logo_title_layout.addWidget(viber_logo_label)

        viber_title_label = QLabel("Viber Lite")
        viber_title_label.setStyleSheet("font-size: 25px; color: white;")
        logo_title_layout.addWidget(viber_title_label, alignment=Qt.AlignRight)
        self.left_panel_layout.addLayout(logo_title_layout)

        # Separator
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setFrameShadow(QFrame.Sunken)
        self.left_panel_layout.addWidget(line_separator)

        # Contacts list
        self.contact_list_widget = QListWidget()
        self.contact_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: none;
                color: black;
                font-size: 20px;
            }
            QListWidget::item:selected {
                background-color: #440099;
                color: white;
            }
        """)
        self.left_panel_layout.addWidget(self.contact_list_widget)

        # Add / Delete Contact Buttons
        add_contact_button = QPushButton("Add Contact")
        add_contact_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #440099;
            }
        """)
        add_contact_button.clicked.connect(self.add_contact)
        self.left_panel_layout.addWidget(add_contact_button)

        delete_contact_button = QPushButton("Delete Contact")
        delete_contact_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #440099;
            }
        """)
        delete_contact_button.clicked.connect(self.delete_contact)
        self.left_panel_layout.addWidget(delete_contact_button)

        # Right Panel
        self.right_panel_layout = QVBoxLayout()
        self.right_panel_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(self.right_panel_layout)

        self.stacked_widget = QStackedWidget()
        self.right_panel_layout.addWidget(self.stacked_widget)

        # Conversation List Widget
        self.conversation_list_widget = QWidget()
        conv_layout = QVBoxLayout(self.conversation_list_widget)
        conv_layout.setContentsMargins(10, 10, 10, 10)
        self.stacked_widget.addWidget(self.conversation_list_widget)

        # Chat Widget
        self.chat_widget = QWidget()
        chat_layout = QVBoxLayout(self.chat_widget)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        self.stacked_widget.addWidget(self.chat_widget)

        # Chat Header
        self.chat_header_widget = ChatHeaderWidget("", "")
        chat_layout.addWidget(self.chat_header_widget)

        # Chat History
        self.chat_history_widget = QTextBrowser()
        self.chat_history_widget.setReadOnly(True)
        self.chat_history_widget.setStyleSheet("""
            QTextBrowser {
                background-color: #E0E0E0;
                border: none;
                padding: 10px;
                font-size: 14px;
                color: black;
            }
        """)
        chat_layout.addWidget(self.chat_history_widget)

        # Chat Input
        self.chat_input_widget = QLineEdit()
        self.chat_input_widget.setPlaceholderText("Type your message here...")
        self.chat_input_widget.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                color: black;
            }
        """)
        chat_layout.addWidget(self.chat_input_widget)

        # Send Button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #440099;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        chat_layout.addWidget(self.send_button)

        self.contact_list_widget.itemSelectionChanged.connect(self.show_conversation)
        self.chat_history = {}
        self.file_sent_flag = False

        # SocketIO Setup
        from socketio import Client
        self.socketio = Client()
        self.socketio.on('connect', self.on_connect, namespace='/chat')
        self.socketio.on('message', self.receive_message, namespace='/chat')
        print("DEBUG: Connecting to server for /chat namespace...")
        self.socketio.connect('http://192.168.1.71:5000', namespaces=['/chat'])

        # Load contacts
        contacts = get_contacts(self.username)
        for contact, chat_hist in contacts:
            item = QListWidgetItem(contact)
            self.contact_list_widget.addItem(item)
            self.chat_history[contact] = chat_hist.split("\n")

        # Animate the send button
        self.animation = QPropertyAnimation(self.send_button, b"geometry")
        self.animation.setDuration(1000)
        self.animation.setStartValue(QRect(0, 0, 100, 50))
        self.animation.setEndValue(QRect(0, 0, 200, 100))
        self.animation.start()

        # RSA Key Management
        self.load_my_keys()
        self.load_contact_keys()

    def load_my_keys(self):
        """Load user RSA keys from the users table (format: 'n,e,d' & 'n,e')."""
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT rsa_private, rsa_public FROM users WHERE username = ?", (self.username,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise Exception("User keys not found in database.")

        rsa_private_str = row[0].strip()  # "n,e,d"
        rsa_public_str = row[1].strip()   # "n,e"

        parts = [p.strip() for p in rsa_private_str.split(",")]
        if len(parts) != 3:
            raise Exception("Invalid RSA private key format: " + rsa_private_str)
        try:
            n, e, d = map(int, parts)
        except Exception as exc:
            raise Exception("Failed to convert RSA private key parts to int: " + str(exc))
        self.rsa_private_key = RSAKey(n, e, d)

        parts = [p.strip() for p in rsa_public_str.split(",")]
        if len(parts) != 2:
            raise Exception("Invalid RSA public key format: " + rsa_public_str)
        n, e = map(int, parts)
        self.my_rsa_public_key = RSAKey(n, e)

    def load_contact_keys(self):
        """Load contact RSA keys (in 'n,e' format) from the dashboard table."""
        self.contact_keys = {}
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        for index in range(self.contact_list_widget.count()):
            contact_item = self.contact_list_widget.item(index)
            contact_username = contact_item.text()
            cursor.execute(
                "SELECT contact_rsa_public FROM dashboard WHERE username = ? AND contact = ?",
                (self.username, contact_username)
            )
            row = cursor.fetchone()
            if row is not None:
                rsa_public_str = row[0].strip()
                if rsa_public_str:
                    parts = [p.strip() for p in rsa_public_str.split(",")]
                    if len(parts) == 2:
                        n, e = map(int, parts)
                        self.contact_keys[contact_username] = RSAKey(n, e)
        conn.close()

    def on_connect(self):
        print(f"DEBUG: Connected to /chat namespace with SID - sending register event for {self.username}")
        self.socketio.emit('register', {'username': self.username}, namespace='/chat')

    def update_gui(self, sender):
        selected_contact_name = self.contact_list_widget.currentItem()
        if selected_contact_name:
            selected_contact_name = selected_contact_name.text()
            if sender == selected_contact_name:
                self.display_chat_history(selected_contact_name)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Quit", "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username
