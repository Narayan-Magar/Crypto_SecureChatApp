from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ChatHeaderWidget(QWidget):
    def __init__(self, contact_name, status):
        super().__init__()

        # Create the chat header layout
        self.chat_header_layout = QVBoxLayout(self)
        self.chat_header_layout.setContentsMargins(10, 10, 10, 10)

        # Add the contact's name and status to the chat header
        contact_name_label = QLabel(contact_name)
        contact_name_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.chat_header_layout.addWidget(contact_name_label)

        contact_status_label = QLabel(status)
        contact_status_label.setStyleSheet("font-size: 16px; color: #b2b2b2;")
        self.chat_header_layout.addWidget(contact_status_label)

        self.chat_header_layout.setSpacing(5)
