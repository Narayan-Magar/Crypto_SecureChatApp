import os
import struct

class Salsa20Cipher:
    def __init__(self, key, nonce, rounds=20):
        """
        key: 16 or 32 bytes
        nonce: 8 bytes
        rounds: typically 20
        """
        if len(key) not in (16, 32):
            raise ValueError("Key must be either 16 or 32 bytes long")
        if len(nonce) != 8:
            raise ValueError("Nonce must be 8 bytes long")
        self.key = key
        self.nonce = nonce
        self.rounds = rounds
        self.counter = 0
        # Use different constants based on key length
        if len(key) == 32:
            self.constants = b"expand 32-byte k"
        else:
            self.constants = b"expand 16-byte k"

    def _rotl(self, x, n):
        return ((x << n) & 0xffffffff) | (x >> (32 - n))

    def _quarterround(self, a, b, c, d):
        b ^= self._rotl((a + d) & 0xffffffff, 7)
        c ^= self._rotl((b + a) & 0xffffffff, 9)
        d ^= self._rotl((c + b) & 0xffffffff, 13)
        a ^= self._rotl((d + c) & 0xffffffff, 18)
        return a, b, c, d

    def _salsa20_block(self, counter):
        if len(self.key) == 32:
            k = struct.unpack('<8I', self.key)
            constants = struct.unpack('<4I', self.constants)
            n = struct.unpack('<2I', self.nonce)
            state = [
                constants[0],
                k[0], k[1], k[2], k[3],
                constants[1],
                n[0], n[1],
                counter & 0xffffffff,
                (counter >> 32) & 0xffffffff,
                constants[2],
                k[4], k[5], k[6], k[7],
                constants[3]
            ]
        else:  # 16-byte key
            k = struct.unpack('<4I', self.key)
            constants = struct.unpack('<4I', self.constants)
            n = struct.unpack('<2I', self.nonce)
            state = [
                constants[0],
                k[0], k[1], k[2],
                k[3],
                constants[1],
                n[0], n[1],
                counter & 0xffffffff,
                (counter >> 32) & 0xffffffff,
                constants[2],
                k[0], k[1], k[2], k[3],
                constants[3]
            ]
        x = state[:]  # copy the state
        for i in range(self.rounds // 2):
            # Column rounds
            x[0], x[4], x[8],  x[12] = self._quarterround(x[0], x[4], x[8],  x[12])
            x[5], x[9], x[13], x[1]  = self._quarterround(x[5], x[9], x[13], x[1])
            x[10], x[14], x[2], x[6]  = self._quarterround(x[10], x[14], x[2], x[6])
            x[15], x[3], x[7],  x[11] = self._quarterround(x[15], x[3], x[7],  x[11])
            # Row rounds
            x[0], x[1], x[2],  x[3]  = self._quarterround(x[0], x[1], x[2],  x[3])
            x[5], x[6], x[7],  x[4]  = self._quarterround(x[5], x[6], x[7],  x[4])
            x[10], x[11], x[8], x[9]  = self._quarterround(x[10], x[11], x[8], x[9])
            x[15], x[12], x[13], x[14] = self._quarterround(x[15], x[12], x[13], x[14])
        output = [(x[i] + state[i]) & 0xffffffff for i in range(16)]
        return struct.pack('<16I', *output)

    def keystream(self, length):
        out = b""
        counter = self.counter
        while len(out) < length:
            block = self._salsa20_block(counter)
            out += block
            counter += 1
        self.counter = counter
        return out[:length]

    def encrypt(self, data):
        ks = self.keystream(len(data))
        return bytes(a ^ b for a, b in zip(data, ks))

    def decrypt(self, data):
        # Decryption is the same as encryption (XOR is reversible)
        return self.encrypt(data)

class EncryptionManager:
    def __init__(self, key=None):
        """
        If no key is provided, generate a new 32-byte key for the session.
        """
        if key is None:
            key = os.urandom(32)
        self.key = key

    def encrypt_message(self, message):
        """
        Encrypts the message using Salsa20. Generates a random 8-byte nonce,
        prepends it to the ciphertext, and returns the hex-encoded string.
        """
        plaintext = message.encode('utf-8')
        nonce = os.urandom(8)  # Salsa20 uses an 8-byte nonce.
        cipher = Salsa20Cipher(self.key, nonce)
        encrypted_bytes = cipher.encrypt(plaintext)
        # Prepend nonce to ciphertext and return as hex.
        return (nonce + encrypted_bytes).hex()

    def decrypt_message(self, encrypted_message):
        """
        Expects a hex-encoded message with the first 8 bytes as the nonce.
        Returns the decrypted plaintext.
        """
        try:
            data = bytes.fromhex(encrypted_message)
            nonce = data[:8]
            ciphertext = data[8:]
            cipher = Salsa20Cipher(self.key, nonce)
            decrypted_bytes = cipher.decrypt(ciphertext)
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return encrypted_message
