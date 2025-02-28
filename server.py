from flask import Flask, request
from flask_socketio import SocketIO, Namespace, emit
from database import add_offline_message, get_offline_messages, delete_offline_messages

app = Flask(__name__)
socketio = SocketIO(app)

class ChatNamespace(Namespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.sessions = {}  # maps usernames to session IDs
        self.message_queue = {}  # store undelivered messages if needed

    def on_connect(self):
        print("DEBUG: Client connected to /chat namespace (sid:", request.sid, ")")

    def on_disconnect(self):
        print("DEBUG: Client disconnected from /chat namespace (sid:", request.sid, ")")
        # Optionally find which user had this SID and remove them.

    def on_register(self, data):
        """
        Expects data = {'username': <the_user>}
        """
        print("DEBUG: on_register event triggered with data:", data)
        username = data.get('username')
        if username:
            self.sessions[username] = request.sid
            print("DEBUG: Registered user:", username, "with session:", request.sid)
            # Send any offline messages
            undelivered = get_offline_messages(username)
            for msg in undelivered:
                # msg = (sender, message_text)
                self.emit('message', {'text': msg[1], 'recipient': username}, room=request.sid)
            delete_offline_messages(username)
        else:
            print("DEBUG: Register event missing username")

    def on_message(self, data):
        """
        Expects data = {
          'text': 'alice: {...encrypted JSON...}',
          'recipient': 'bob',
          'sender': 'alice'
        }
        """
        print("DEBUG: on_message called with data:", data)
        print("DEBUG: Current sessions:", self.sessions)
        recipient = data.get('recipient')
        recipient_sid = self.sessions.get(recipient)
        print("DEBUG: Message received for recipient:", recipient, "SID:", recipient_sid)

        if recipient_sid:
            # The recipient is connected
            emit('message', data['text'], room=recipient_sid)
            print("DEBUG: Message emitted to recipient in real-time.")
        else:
            # The recipient is offline => store offline
            sender = data.get('sender', '')
            add_offline_message(recipient, sender, data['text'])
            print("DEBUG: Recipient offline, message stored offline.")


socketio.on_namespace(ChatNamespace('/chat'))

if __name__ == '__main__':
    print("DEBUG: Starting server on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
