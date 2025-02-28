import os
from encryption import EncryptionManager  # our Salsa20-based manager
from custom_rsa import encrypt, decrypt

def encrypt_chat_message(message, recipient_public_key):
    """
    Encrypts a chat message using a hybrid RSA-Salsa20 scheme.

    Steps:
      1. Generate a random 32-byte symmetric key.
      2. Encrypt the message with Salsa20 using this key (via EncryptionManager).
      3. Convert the symmetric key to a hex string.
      4. Encrypt that hex string with the recipient's RSA public key.
      5. Return a dictionary containing both encrypted parts as hex strings.
    
    :param message: The plaintext chat message.
    :param recipient_public_key: An RSAKey object (public key) for the recipient.
    :return: A dict with keys 'encrypted_sym_key' and 'encrypted_message'.
    """
    # 1. Generate a random symmetric key.
    msg_sym_key = os.urandom(32)
    
    # 2. Encrypt the message using Salsa20 with msg_sym_key.
    enc_manager = EncryptionManager(msg_sym_key)
    encrypted_message = enc_manager.encrypt_message(message)  # hex string
    
    # 3. Convert the symmetric key to a hex string.
    sym_key_str = msg_sym_key.hex()
    
    # 4. Encrypt the symmetric key using RSA.
    # Our RSA encrypt function expects a string; it returns an integer.
    rsa_encrypted_key_int = encrypt(sym_key_str, recipient_public_key)
    # Convert the integer ciphertext to a hex string.
    encrypted_sym_key = hex(rsa_encrypted_key_int)[2:]  # strip the "0x"
    
    # 5. Return the package.
    return {
        'encrypted_sym_key': encrypted_sym_key,
        'encrypted_message': encrypted_message
    }

def decrypt_chat_message(package, recipient_private_key):
    """
    Decrypts a chat message that was encrypted using the hybrid RSA-Salsa20 scheme.

    Steps:
      1. Convert the RSA-encrypted symmetric key (hex) to an integer.
      2. Decrypt it with the recipient's RSA private key to recover the symmetric key (as a hex string).
      3. Convert the recovered symmetric key to bytes.
      4. Use the symmetric key with Salsa20 (via EncryptionManager) to decrypt the encrypted message.
    
    :param package: A dict with keys 'encrypted_sym_key' and 'encrypted_message'.
    :param recipient_private_key: An RSAKey object (private key) for the recipient.
    :return: The decrypted plaintext message.
    """
    encrypted_sym_key_hex = package['encrypted_sym_key']
    encrypted_message = package['encrypted_message']
    
    # 1. Convert the encrypted symmetric key from hex to integer.
    rsa_encrypted_key_int = int(encrypted_sym_key_hex, 16)
    
    # 2. Decrypt the symmetric key using RSA.
    sym_key_str = decrypt(rsa_encrypted_key_int, recipient_private_key)  # returns hex string
    # 3. Convert the hex string to bytes.
    msg_sym_key = bytes.fromhex(sym_key_str)
    
    # 4. Use this symmetric key to decrypt the message.
    enc_manager = EncryptionManager(msg_sym_key)
    decrypted_message = enc_manager.decrypt_message(encrypted_message)
    
    return decrypted_message
