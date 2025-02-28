# custom_aes.py

def pad(plaintext):
    """
    Apply PKCS7 padding to ensure the plaintext is a multiple of 16 bytes.
    """
    padding_len = 16 - (len(plaintext) % 16)
    return plaintext + chr(padding_len) * padding_len

def unpad(padded_text):
    """
    Remove PKCS7 padding.
    """
    padding_len = ord(padded_text[-1])
    return padded_text[:-padding_len]

class AES:
    """
    A **very simplified** AES-128 dummy implementation in ECB mode.
    
    This example does not implement the full AES algorithm.
    Instead, for demonstration purposes, it simply XORs each 16-byte block
    with the key. (Note: This is NOT secure.)
    """
    block_size = 16

    def __init__(self, key):
        if len(key) != 16:
            raise ValueError("Key must be 16 bytes long for AES-128.")
        self.key = key

    def encrypt_block(self, block):
        # For demonstration, simply XOR each byte with the corresponding key byte.
        return bytes([b ^ self.key[i] for i, b in enumerate(block)])

    def decrypt_block(self, block):
        # XOR decryption is identical to encryption.
        return bytes([b ^ self.key[i] for i, b in enumerate(block)])

def aes_encrypt(plaintext, key):
    """
    Encrypts a string (plaintext) using our dummy AES in ECB mode.
    Returns a hex-encoded string.
    """
    # Pad the plaintext so its length is a multiple of 16.
    padded = pad(plaintext)
    cipher = AES(key)
    ciphertext = b""
    # Process each 16-byte block.
    for i in range(0, len(padded), AES.block_size):
        block = padded[i:i+AES.block_size].encode('utf-8')
        encrypted_block = cipher.encrypt_block(block)
        ciphertext += encrypted_block
    return ciphertext.hex()

def aes_decrypt(ciphertext_hex, key):
    """
    Decrypts a hex-encoded string that was encrypted using aes_encrypt.
    Returns the plaintext.
    """
    ciphertext = bytes.fromhex(ciphertext_hex)
    cipher = AES(key)
    decrypted = b""
    for i in range(0, len(ciphertext), AES.block_size):
        block = ciphertext[i:i+AES.block_size]
        decrypted_block = cipher.decrypt_block(block)
        decrypted += decrypted_block
    # Convert to string and remove padding.
    decrypted_text = decrypted.decode('utf-8', errors='ignore')
    return unpad(decrypted_text)
