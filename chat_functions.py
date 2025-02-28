import json
from database import update_chat_history
from imports import *
# Import our hybrid encryption routines from chat_encryption.py
from chat_encryption import encrypt_chat_message, decrypt_chat_message

class ChatFunctions:
    def send_message(self):
        # Get the selected contact's name.
        selected_contact_name = self.contact_list_widget.currentItem().text()
        message_text = self.chat_input_widget.text().strip()
        
        if message_text != "":
            # Retrieve the recipient's RSA public key.
            if selected_contact_name not in self.contact_keys:
                QMessageBox.warning(self, "Encryption Error", "Recipient's public key not available.")
                print("DEBUG: No public key for contact:", selected_contact_name)
                return
            recipient_public_key = self.contact_keys[selected_contact_name]
            
            # Encrypt the message using the hybrid RSA–Salsa20 scheme.
            # This returns a package (a dict) containing the RSA-encrypted symmetric key
            # and the Salsa20-encrypted message.
            try:
                package = encrypt_chat_message(message_text, recipient_public_key)
            except Exception as ex:
                QMessageBox.warning(self, "Encryption Error", f"Failed to encrypt message: {ex}")
                print("DEBUG: Encryption failed:", ex)
                return           
            # Convert the package to a JSON string for transmission.
            encrypted_message_str = json.dumps(package)
            print("DEBUG: Outgoing package:", encrypted_message_str)
            
            # Append the encrypted message (as a JSON string) to the chat history.
            self.chat_history[selected_contact_name].append(f"{self.username}: {encrypted_message_str}")
            self.display_chat_history(selected_contact_name)
            self.chat_input_widget.clear()
            
            # Update the chat history in the database.
            update_chat_history(
                self.username,
                selected_contact_name,
                "\n".join(self.chat_history[selected_contact_name])
            )
            self.socketio.emit(
                'message',
                {
                    'text': f"{self.username}: {encrypted_message_str}",
                    'recipient': selected_contact_name,
                    'sender': self.username
                },
                namespace='/chat'
            )
            print("DEBUG: Message emitted to server.")

    def receive_message(self, data):
        """
        Expected data format: "sender: encrypted_message_str"
        where encrypted_message_str is a JSON string representing the encryption package.
        """
        print("DEBUG: Raw received data:", data)
        try:
            sender, encrypted_message_str = data.split(": ", 1)
        except Exception as ex:
            QMessageBox.warning(None, "Decryption Error", f"Message format error: {ex}")
            self.chat_history.setdefault("Unknown", []).append(data)
            self.update_gui_signal.emit("Unknown")
            return

        # Attempt to parse the encrypted message package.
        try:
            package = json.loads(encrypted_message_str)
            print("DEBUG: Parsed package:", package)
        except Exception as e:
            QMessageBox.warning(None, "Decryption Error", f"Failed to parse encrypted message: {e}")
            return

        # Decrypt the message using our hybrid decryption routine and our RSA private key.
        try:
            decrypted_message = decrypt_chat_message(package, self.rsa_private_key)
            print("DEBUG: Decrypted message:", decrypted_message)
        except Exception as e:
            QMessageBox.warning(None, "Decryption Error", f"Failed to decrypt message: {e}")
            return
        
        # Update the chat history for the sender.
        if sender not in self.chat_history:
            self.chat_history[sender] = []
        self.chat_history[sender].append(f"{sender}: {decrypted_message}")
        self.update_gui_signal.emit(sender)

    def show_conversation(self):
        selected_item = self.contact_list_widget.currentItem()
        if selected_item is None:
            return

        selected_contact_name = selected_item.text()
        if selected_contact_name in self.chat_history:
            chat_contact_name_label = self.chat_header_widget.findChild(QLabel)
            chat_contact_name_label.setText(selected_contact_name)
            self.display_chat_history(selected_contact_name)
            self.stacked_widget.setCurrentWidget(self.chat_widget)

    def display_chat_history(self, contact_name):
        self.chat_history_widget.clear()
        chat_history = self.chat_history[contact_name]
        for message in chat_history:
            if message.startswith("File Sent: "):
                file_path = message.replace("File Sent: ", "")
                self.chat_history_widget.append(f'<a href="file:{file_path}">{file_path}</a>')
            else:
                parts = message.split(": ", 1)
                if len(parts) == 2:
                    sender, text = parts
                    try:
                        # Try to parse the text as a JSON package and decrypt it.
                        package = json.loads(text)
                        decrypted_message = decrypt_chat_message(package, self.rsa_private_key)
                        formatted_message = f"<b>{sender}</b>: {decrypted_message}"
                    except Exception:
                        formatted_message = message
                else:
                    formatted_message = message
                self.chat_history_widget.append(formatted_message)
            self.chat_history_widget.append("")
