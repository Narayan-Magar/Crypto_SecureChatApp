import sys
import unittest
from PyQt5.QtWidgets import QApplication
# from your_module import ChatHeaderWidget  # Import your widget implementation
from imports import*

app = QApplication(sys.argv)

class TestChatHeaderWidgetIntegration(unittest.TestCase):
    def setUp(self):
        self.contact_name = "John Doe"
        self.status = "Online"
        self.widget = ChatHeaderWidget(self.contact_name, self.status)

    def test_layout_spacing(self):
        layout = self.widget.layout()
        self.assertIsNotNone(layout)
        self.assertEqual(layout.spacing(), 5)
        
key = Fernet.generate_key()
class TestEncryptionManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.encryption_manager = EncryptionManager(key)

    def test_encrypt_decrypt(self):
        original_message = "This is a secret message."
        encrypted_message = self.encryption_manager.encrypt_message(original_message)
        decrypted_message = self.encryption_manager.decrypt_message(encrypted_message)

        self.assertEqual(decrypted_message, original_message)

    def test_invalid_token_handling(self):
        invalid_encrypted_message = "InvalidEncryptedMessage"
        decrypted_message = self.encryption_manager.decrypt_message(invalid_encrypted_message)

        self.assertEqual(decrypted_message, invalid_encrypted_message)
        
class TestSignupWindowIntegration(unittest.TestCase):
    def setUp(self):
        self.login_window = None  # You can mock the LoginWindow if needed
        self.signup_window = SignupWindow(self.login_window)
        self.signup_window.show()

    def tearDown(self):
        self.signup_window.close()
        app.quit()

    def test_signup_successful(self):
        username = "testuser"
        email = "test@example.com"
        password = "testpassword"

        self.signup_window.username_input.setText(username)
        self.signup_window.email_input.setText(email)
        self.signup_window.password_input.setText(password)

        with patch.object(self.signup_window, 'hash_password', return_value='hashed_password'), \
             patch.object(self.signup_window, 'save_user') as mock_save_user:

            self.signup_window.signup_button.click()

            mock_save_user.assert_called_once_with(username, email, 'hashed_password')

            # You can add assertions to verify success message box display
            # For example: assert success message box is shown

    def test_signup_username_exists(self):
        username = "existinguser"
        email = "test@example.com"
        password = "testpassword"

        self.signup_window.username_input.setText(username)
        self.signup_window.email_input.setText(email)
        self.signup_window.password_input.setText(password)

        # Mock the username_exists method to return True
        with patch.object(self.signup_window, 'username_exists', return_value=True):
            with patch.object(self.signup_window, 'hash_password', return_value='hashed_password'), \
                 patch.object(self.signup_window, 'save_user') as mock_save_user:

                self.signup_window.signup_button.click()

                # Assert that save_user is not called when username already exists
                mock_save_user.assert_not_called()


