import sqlite3

def create_connection():
    conn = sqlite3.connect('database.db')
    return conn

def create_table_if_not_exists():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dashboard (
            username TEXT NOT NULL,
            contact TEXT NOT NULL,
            chat_history TEXT NOT NULL,
            contact_rsa_public TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table_if_not_exists()

def add_contact(username, contact):
    conn = create_connection()
    cursor = conn.cursor()
    # Retrieve the contact's RSA public key from the users table.
    cursor.execute("SELECT rsa_public FROM users WHERE username = ?", (contact,))
    result = cursor.fetchone()
    rsa_public = result[0] if result is not None else ""
    cursor.execute("""
        INSERT INTO dashboard (username, contact, chat_history, contact_rsa_public)
        VALUES (?, ?, ?, ?)
    """, (username, contact, "", rsa_public))
    conn.commit()
    conn.close()



def get_contacts(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT contact, chat_history
        FROM dashboard
        WHERE username = ?
    """, (username,))
    contacts = cursor.fetchall()
    conn.close()
    return contacts

def update_chat_history(username, contact, chat_history):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE dashboard
        SET chat_history = ?
        WHERE username = ? AND contact = ?
    """, (chat_history, username, contact))
    conn.commit()
    conn.close()

create_table_if_not_exists()

def create_offline_messages_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offline_messages (
            recipient TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_offline_messages_table()

def add_offline_message(recipient, sender, message):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO offline_messages (recipient, sender, message)
        VALUES (?, ?, ?)
    """, (recipient, sender, message))
    conn.commit()
    conn.close()


def get_offline_messages(recipient):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message
        FROM offline_messages
        WHERE recipient = ?
    """, (recipient,))
    messages = cursor.fetchall()
    conn.close()
    return messages

def delete_offline_messages(recipient):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM offline_messages
        WHERE recipient = ?
    """, (recipient,))
    conn.commit()
    conn.close()
