from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QMessageBox, QDialog, QDialogButtonBox
)
import sqlite3
import bcrypt
from imports import *
import re
from PyQt5.QtGui import QPixmap, QLinearGradient, QPalette, QColor, QPainter

class ResetPasswordDialog(QDialog):
    def __init__(self, email, secret_key):
        super().__init__()

        self.setWindowTitle("Reset Password")
        self.setFixedSize(400, 200)

        self.email = email
        self.secret_key = secret_key

        layout = QVBoxLayout()

        label = QLabel(f"Reset password for: {email}")
        self.new_password_input = QLineEdit()
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        reset_button = QPushButton("Reset Password")
        reset_button.clicked.connect(self.reset_password)

        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)

        layout.addWidget(label)
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(reset_button)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def reset_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not new_password:
            QMessageBox.warning(self, "Invalid Password", "Please enter a new password.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        if not self.validate_secret_key():
            QMessageBox.warning(self, "Invalid Secret Key", "The provided secret key is incorrect.")
            return

        if self.update_password_in_database(new_password):
            QMessageBox.information(self, "Password Reset", "Password reset successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Password Reset Failed", "Failed to reset the password. Please try again.")

    def validate_secret_key(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT secret_key FROM users WHERE email = ?", (self.email,))
        result = cursor.fetchone()
        conn.close()

        if result is not None:
            stored_secret = result[0]
            return stored_secret == self.secret_key
        return False

    def update_password_in_database(self, new_password):
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password.decode("utf-8"), self.email))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating password in the database: {e}")
            return False

class ForgotPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Forgot Password")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()

        label = QLabel("Enter your email and secret key to reset password:")
        self.email_input = QLineEdit()
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Secret Key")
        reset_button = QPushButton("Reset Password")
        reset_button.clicked.connect(self.reset_password)

        layout.addWidget(label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.secret_key_input)
        layout.addWidget(reset_button)

        self.setLayout(layout)

    def reset_password(self):
        email = self.email_input.text()
        secret_key = self.secret_key_input.text()

        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return

        if not self.email_exists(email):
            QMessageBox.warning(self, "Email Not Found", "The provided email address is not registered.")
            return

        reset_password_dialog = ResetPasswordDialog(email, secret_key)
        result = reset_password_dialog.exec_()

        if result == QDialog.Accepted:
            print("Password reset completed.")
        else:
            print("Password reset canceled.")

    def is_valid_email(self, email):
        email_regex = r'^\S+@\S+\.\S+$'
        return re.match(email_regex, email)

    def email_exists(self, email):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

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

class LoginWindow(QWidget):
    def __init__(self, signup_window):
        super().__init__()
        self.signup_window = signup_window

        self.setWindowTitle("Viber Lite - Login")
        self.setFixedSize(650, 700)

        layout = QVBoxLayout()
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#6700B3"))
        gradient.setColorAt(1, QColor("#440099"))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        # Logo and Title
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap("D:\\5th sem\\cw of crypto\\crypto\crypto\Viberlite.png")
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

        # Login Form Widgets
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

        # Secret Key input field for login (not used for key decryption now)
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

        self.login_button = QPushButton("Sign in")
        self.login_button.setStyleSheet("""
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
        layout.addWidget(self.password_input)
        layout.addWidget(self.secret_key_input)
        layout.addWidget(self.login_button)
        
        # "Forgot Password?" link
        forgot_password_layout = QHBoxLayout()
        forgot_password_text = QLabel("<a href='#'>Forgot Password?</a>")
        forgot_password_text.setAlignment(Qt.AlignRight)
        forgot_password_text.setStyleSheet("color: white; font-weight: bold;")
        forgot_password_text.setOpenExternalLinks(False)
        forgot_password_text.linkActivated.connect(self.open_forgot_password)
        forgot_password_layout.addWidget(forgot_password_text, alignment=Qt.AlignRight)
        layout.addLayout(forgot_password_layout)

        layout.addSpacing(30)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        layout.addSpacing(20)

        signup_text = QLabel("Not have an Account? ")
        signup_text.setAlignment(Qt.AlignCenter)
        signup_text.setStyleSheet("color: white;")
        signup_link = QLabel("<a href='#'>Signup Here</a>")
        signup_link.setAlignment(Qt.AlignCenter)
        signup_link.setStyleSheet("color: white; font-weight: bold;")
        signup_link.setOpenExternalLinks(False)
        signup_link.linkActivated.connect(self.open_signup)
        layout.addWidget(signup_text)
        layout.addWidget(signup_link)
        layout.setContentsMargins(120, 0, 120, 0)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        palette = QPalette()
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.login_button.clicked.connect(self.login)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#6700B3"))
        gradient.setColorAt(1, QColor("#440099"))
        painter.fillRect(self.rect(), gradient)

    def open_signup(self):
        self.close()
        self.signup_window.show()

    def open_forgot_password(self):
        forgot_password_dialog = ForgotPasswordDialog()
        forgot_password_dialog.exec_()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter username and password.")
            return

        if self.authenticate_user(username, password):
            self.open_dashboard(username)
        else:
            QMessageBox.warning(self, "Login Error", "Invalid username or password.")

    def authenticate_user(self, username, password):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result is not None:
            hashed_password = result[0].encode("utf-8")
            if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
                return True
        return False

    def open_dashboard(self, username):
        from mainwindow import MainWindow  # Lazy import to avoid circular dependency issues
        # For plain-text key storage, we don't need to pass the secret key for decryption.
        self.main_window = MainWindow(username)
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    signup_window = SignupWindow(None)  # Replace with your actual signup window class
    login_window = LoginWindow(signup_window)
    login_window.show()
    app.exec_()
