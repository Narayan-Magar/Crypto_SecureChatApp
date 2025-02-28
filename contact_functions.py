from database import add_contact, get_contacts, update_chat_history
import sqlite3
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QListWidgetItem
from imports import *

from custom_rsa import RSAKey

class ContactFunctions:
    def add_contact(self):
        # Ask for the new contact's username.
        new_contact_name, ok = QInputDialog.getText(self, "Add Contact", "Enter the name of the new contact:")
        if ok and new_contact_name != "":
            # Check if the contact exists in the users table.
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT rsa_public FROM users WHERE username = ?", (new_contact_name,))
            result = cursor.fetchone()
            conn.close()
            if result is None:
                QMessageBox.warning(self, "Error", "User does not exist.")
                return
            elif new_contact_name in self.chat_history:
                QMessageBox.warning(self, "Error", "User already exists in your conversation.")
                return
            else:
                # Add the contact to the UI list.
                item = QListWidgetItem(new_contact_name)
                self.contact_list_widget.addItem(item)
                self.chat_history[new_contact_name] = []
                
                # Store the contact in the dashboard table (which saves the RSA public key).
                add_contact(self.username, new_contact_name)
                
                # Update in-memory contact_keys.
                rsa_public_str = result[0]  # expected to be in "n,e" format
                parts = rsa_public_str.split(",")
                if len(parts) == 2:
                    n, e = map(int, parts)
                    self.contact_keys[new_contact_name] = RSAKey(n, e)


    def delete_contact(self):
        # Get the selected contact's name
        selected_contact_name = self.contact_list_widget.currentItem().text()

        # Show a confirmation dialog box before deleting the contact
        reply = QMessageBox.question(
            self, "Delete Contact", f"Are you sure you want to delete {selected_contact_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove the contact from the contact list widget
            selected_item = self.contact_list_widget.currentItem()
            self.contact_list_widget.takeItem(self.contact_list_widget.row(selected_item))

            # Remove the chat history of the selected contact
            del self.chat_history[selected_contact_name]

            # Clear the chat history widget
            self.chat_history_widget.clear()

            # Update the chat header with empty values
            chat_contact_name_label = self.chat_header_widget.findChild(QLabel)
            chat_contact_name_label.setText("")

            # Switch to the conversation list if there are no contacts left
            if self.contact_list_widget.count() == 0:
                self.stacked_widget.setCurrentWidget(self.conversation_list_widget)
            else:
                # Select the first contact in the list
                self.contact_list_widget.setCurrentRow(0)
                self.show_conversation()

            # Delete the contact from the database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dashboard WHERE username=? AND contact=?", (self.username, selected_contact_name))
            conn.commit()
            conn.close()
        else:
            return
