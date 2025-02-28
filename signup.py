import bcrypt
import sqlite3
import re
import hashlib
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QLinearGradient, QPalette, QColor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox

# Import our RSA module (for key generation)
# from custom_rsa import generate_rsa_keys

class SignupWindow(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window

        self.setWindowTitle("Viber Lite - Signup")
        self.setFixedSize(650, 700)

        layout = QVBoxLayout()
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#4CAF50"))
        gradient.setColorAt(1, QColor("#202020"))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap("D:\\cw2 of pa\\coursework2-ShirilMahato-1-main\\edit2\\Viberlite.png")
        logo_label.setPixmap(logo_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))

        title_label = QLabel("Viber Lite")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")

        logo_layout = QVBoxLayout()
        logo_layout.addWidget(logo_label)
        logo_layout.addSpacing(10)
        logo_layout.addWidget(title_label)
        layout.addLayout(logo_layout)

        layout.addSpacing(60)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)

        # We still ask for a secret key, although for this plain-text keys demo it’s not used to encrypt the RSA keys.
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Secret Key")
        self.secret_key_input.setEchoMode(QLineEdit.Password)
        self.secret_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)

        self.confirm_secret_key_input = QLineEdit()
        self.confirm_secret_key_input.setPlaceholderText("Confirm Secret Key")
        self.confirm_secret_key_input.setEchoMode(QLineEdit.Password)
        self.confirm_secret_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)

        self.signup_button = QPushButton("Sign up")
        self.signup_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #440099;
            }
        """)

        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.secret_key_input)
        layout.addWidget(self.confirm_secret_key_input)
        layout.addWidget(self.signup_button)

        layout.addSpacing(50)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        layout.addSpacing(20)

        signin_text = QLabel("Already have an Account?")
        signin_text.setAlignment(Qt.AlignCenter)
        signin_text.setStyleSheet("color: white;")

        signin_link = QLabel("<a href='#'>Signin Here</a>")
        signin_link.setAlignment(Qt.AlignCenter)
        signin_link.setStyleSheet("color: white; font-weight: bold;")
        signin_link.setOpenExternalLinks(False)
        signin_link.linkActivated.connect(self.open_signin)

        signin_layout = QVBoxLayout()
        signin_layout.addWidget(signin_text)
        signin_layout.addWidget(signin_link)

        layout.addLayout(signin_layout)

        layout.setContentsMargins(120, 0, 120, 0)
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        palette = QPalette()
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        self.signup_button.clicked.connect(self.signup)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#6700B3"))
        gradient.setColorAt(1, QColor("#440099"))
        painter.fillRect(self.rect(), gradient)

    def open_signin(self):
        self.close()
        self.login_window.show()

    def signup(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        secret_key = self.secret_key_input.text()
        confirm_secret_key = self.confirm_secret_key_input.text()

        if not username or not email or not password or not confirm_password or not secret_key or not confirm_secret_key:
            QMessageBox.warning(self, "Signup Error", "Please fill in all the fields.")
            return

        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Signup Error", "Please enter a valid email address.")
            return

        if self.username_exists(username):
            QMessageBox.warning(self, "Signup Error", "Username already exists. Please choose a different username.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Signup Error", "Passwords do not match. Please enter matching passwords.")
            return

        if secret_key != confirm_secret_key:
            QMessageBox.warning(self, "Signup Error", "Secret Keys do not match. Please enter matching Secret Keys.")
            return

        hashed_password = self.hash_password(password)
        self.save_user(username, email, hashed_password, secret_key)

        QMessageBox.information(self, "Signup Successful", "Your account has been created successfully!")

    def is_valid_email(self, email):
        email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        return bool(re.match(email_regex, email))

    def username_exists(self, username):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, email TEXT, password TEXT, secret_key TEXT, rsa_public TEXT, rsa_private TEXT)")
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def save_user(self, username, email, password, secret_key):
        from custom_rsa import generate_rsa_keys
        private_key, public_key = generate_rsa_keys(bit_length=512)
        rsa_public_str = f"{public_key.n},{public_key.e}"
        rsa_private_str = f"{private_key.n},{private_key.e},{private_key.d}"
        # Now store the PEM strings in the database...
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, email TEXT, password TEXT, secret_key TEXT, rsa_public TEXT, rsa_private TEXT)")
        cursor.execute(
            "INSERT INTO users (username, email, password, secret_key, rsa_public, rsa_private) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, password, secret_key, rsa_public_str, rsa_private_str)
        )
        conn.commit()
        conn.close()



if __name__ == "__main__":
    app = QApplication([])
    login_window = QWidget()  # Placeholder for the login window
    signup_window = SignupWindow(login_window)
    signup_window.show()
    app.exec_()
