import unittest
from cryptography.fernet import Fernet
from flask_socketio import SocketIOTestClient
from server import app, socketio, ChatNamespace
# from encryption import EncryptionManager
from imports import*
# from chat_functions import ChatFunctions

# app = QApplication([])
class TestEncryptionManager(unittest.TestCase):

    def setUp(self):
        self.key = Fernet.generate_key()
        self.encryption_manager = EncryptionManager(self.key)

    def test_encrypt_message(self):
        message = "Test message"
        encrypted_message = self.encryption_manager.encrypt_message(message)
        self.assertNotEqual(message, encrypted_message)

    def test_decrypt_message(self):
        message = "Test message"
        encrypted_message = self.encryption_manager.encrypt_message(message)
        decrypted_message = self.encryption_manager.decrypt_message(encrypted_message)
        self.assertEqual(message, decrypted_message)
        
class TestLoginWindow(unittest.TestCase):
    app = QApplication([])
    def setUp(self):
        self.login = LoginWindow(None)

    def test_title(self):
        self.assertEqual(self.login.windowTitle(), "Viber Lite - Login")

    def test_username_input(self):
        QTest.keyClicks(self.login.username_input, 'testuser')
        self.assertEqual(self.login.username_input.text(), 'testuser')

    def test_password_input(self):
        QTest.keyClicks(self.login.password_input, 'testpassword')
        self.assertEqual(self.login.password_input.text(), 'testpassword')


class TestSignupWindow(unittest.TestCase):
    app = QApplication([])
    def setUp(self):
        self.signup = SignupWindow(None)

    def test_title(self):
        self.assertEqual(self.signup.windowTitle(), "Viber Lite - Signup")

    def test_username_input(self):
        QTest.keyClicks(self.signup.username_input, 'testuser')
        self.assertEqual(self.signup.username_input.text(), 'testuser')

    def test_email_input(self):
        QTest.keyClicks(self.signup.email_input, 'testuser@example.com')
        self.assertEqual(self.signup.email_input.text(), 'testuser@example.com')

    def test_password_input(self):
        QTest.keyClicks(self.signup.password_input, 'testpassword')
        self.assertEqual(self.signup.password_input.text(), 'testpassword')

class TestChatNamespace(unittest.TestCase):
    def setUp(self):
        self.client = socketio.test_client(app, namespace='/chat')
        self.client.get_received('/chat')

    def test_connect(self):
        self.assertTrue(self.client.is_connected('/chat'))

    def test_register(self):
        self.client.emit('register', {'username': 'testuser'}, namespace='/chat')
        # received = self.client.get_received('/chat')
        # self.assertEqual(len(received), 1)
        # self.assertEqual(received[0]['name'], 'register')
        # self.assertEqual(received[0]['args'][0]['username'], 'testuser')

    def test_message(self):
        self.client.emit('message', {'recipient': 'testuser', 'text': 'Hello, world!'}, namespace='/chat')
        received = self.client.get_received('/chat')
        # self.assertEqual(len(received), 1)
        # self.assertEqual(received[0]['name'], 'message')
        # self.assertEqual(received[0]['args'][0]['recipient'], 'testuser')
        # self.assertEqual(received[0]['args'][0]['text'], 'Hello, world!')

class TestContactFunctions(unittest.TestCase):
    app = QApplication([])
    def setUp(self):
        self.contact = ContactFunctions()

    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    @patch('PyQt5.QtWidgets.QInputDialog.getText')
    @patch('sqlite3.connect')
    def test_add_contact(self, mock_sqlite3_connect, mock_getText, mock_warning):
        # Mock the user input and database connection
        mock_getText.return_value = ('testuser', True)
        mock_conn = MagicMock()
        mock_sqlite3_connect.return_value = mock_conn

        # Mock the database cursor
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock the database query result
        mock_cursor.fetchone.return_value = None

        # Call the method
        self.contact.add_contact()

        # Check that the method called the mock functions with the correct arguments
        mock_getText.assert_called_once_with(self.contact, "Add Contact", "Enter the name of the new contact:")
        mock_sqlite3_connect.assert_called_once_with('database.db')
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username=?", ('testuser',))
        mock_warning.assert_called_once_with(self.contact, "Error", "User does not exist.")

class TestMainWindow(unittest.TestCase):
    app = QApplication([])
    def setUp(self):
        self.username = 'testuser'
        self.main_window = MainWindow(self.username)
        self.main_window.contact_list_widget = MagicMock()
        self.main_window.chat_input_widget = MagicMock()
        self.main_window.chat_history_widget = MagicMock()
        self.main_window.chat_header_widget = MagicMock()
        self.main_window.stacked_widget = MagicMock()
        self.main_window.chat_widget = MagicMock()
        self.main_window.socketio = MagicMock()
        self.main_window.update_gui_signal = MagicMock()
        self.main_window.chat_history = {'testuser': []}
        self.main_window.encryption_manager = MagicMock()
        self.main_window.animation = MagicMock()

    @patch('mainwindow.get_contacts')
    def test_init(self, mock_get_contacts):
        mock_get_contacts.return_value = [('testuser', 'Hello\\n')]
        main_window = MainWindow(self.username)
        self.assertEqual(main_window.username, self.username)
        self.assertIsInstance(main_window.cipher_suite, Fernet)
        # self.assertIsInstance(main_window.encryption_manager, MagicMock)
        # self.assertIsInstance(main_window.animation, MagicMock)

    def test_encrypt_message(self):
        message = 'Hello'
        self.main_window.encryption_manager.encrypt_message.return_value = 'encrypted_message'
        result = self.main_window.encrypt_message(message)
        self.assertEqual(result, 'encrypted_message')

    def test_decrypt_message(self):
        encrypted_message = 'encrypted_message'
        self.main_window.encryption_manager.decrypt_message.return_value = 'message'
        result = self.main_window.decrypt_message(encrypted_message)
        self.assertEqual(result, 'message')

    def test_on_connect(self):
        self.main_window.on_connect()
        self.main_window.socketio.emit.assert_called_with('register', {'username': self.username}, namespace='/chat')

    def test_update_gui(self):
        sender = 'testuser'
        self.main_window.contact_list_widget.currentItem.return_value.text.return_value = sender
        self.main_window.update_gui(sender)
        # self.main_window.display_chat_history.assert_called_with(sender)

    @patch('mainwindow.QMessageBox.question')
    def test_closeEvent(self, mock_question):
        mock_question.return_value = QMessageBox.Yes
        event = MagicMock()
        self.main_window.closeEvent(event)
        event.accept.assert_called_once()

    def test_getUsername(self):
        self.assertEqual(self.main_window.getUsername(), self.username)

    def test_setUsername(self):
        new_username = 'newuser'
        self.main_window.setUsername(new_username)
        self.assertEqual(self.main_window.getUsername(), new_username)


if __name__ == "__main__":
    unittest.main()
