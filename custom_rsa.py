# custom_rsa.py
import random
import math

def is_prime(n, k=5):
    """Use Miller-Rabin primality test for a better probabilistic prime test."""
    if n < 2:
        return False
    # Check small primes first
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    # Write n-1 as d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    # Witness loop
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime_candidate(length):
    """
    Generate an odd integer randomly with the given bit length.
    Ensures the most significant bit is 1 (so the number has the desired length)
    and the number is odd.
    """
    p = random.getrandbits(length)
    p |= (1 << (length - 1)) | 1
    return p

def generate_prime_number(length):
    """Generate a prime number of approximately 'length' bits using Miller-Rabin."""
    p = generate_prime_candidate(length)
    while not is_prime(p):
        p = generate_prime_candidate(length)
    return p

def egcd(a, b):
    """Extended Euclidean algorithm.
    Returns a tuple of (g, x, y) such that a*x + b*y = g = gcd(a, b).
    """
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Compute the modular inverse of a modulo m.
    Returns x such that (a * x) % m == 1.
    Raises an exception if the modular inverse does not exist.
    """
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("Modular inverse does not exist")
    return x % m

class RSAKey:
    """
    Simple RSA key container.
    For a public key, only n and e are defined.
    For a private key, n, e, and d are defined.
    """
    def __init__(self, n, e, d=None):
        self.n = n
        self.e = e
        self.d = d

def generate_rsa_keys(bit_length=512):
    """
    Generate an RSA key pair.
    :param bit_length: Total bit length for the modulus n.
    :return: (private_key, public_key) where keys are RSAKey objects.
    """
    # Generate two distinct primes of bit_length/2 each.
    p = generate_prime_number(bit_length // 2)
    q = generate_prime_number(bit_length // 2)
    while q == p:
        q = generate_prime_number(bit_length // 2)
        
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Use a common public exponent
    e = 65537  
    if math.gcd(e, phi) != 1:
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2
    d = modinv(e, phi)
    
    public_key = RSAKey(n, e)
    private_key = RSAKey(n, e, d)
    return private_key, public_key

def encrypt(message, key):
    """
    Encrypt a message (string) using the RSA public key.
    Converts the message into an integer and then applies RSA encryption.
    :param message: The plaintext string to encrypt.
    :param key: An RSAKey instance (public key).
    :return: The ciphertext as an integer.
    """
    m = int.from_bytes(message.encode('utf-8'), byteorder='big')
    if m >= key.n:
        raise ValueError("Message too long for the key size")
    c = pow(m, key.e, key.n)
    return c

def decrypt(ciphertext, key):
    """
    Decrypt an RSA-encrypted ciphertext (an integer) using the RSA private key.
    Converts the resulting integer back into a string.
    :param ciphertext: The ciphertext as an integer.
    :param key: An RSAKey instance (must include the private exponent d).
    :return: The decrypted plaintext string.
    """
    m = pow(ciphertext, key.d, key.n)
    message_length = (m.bit_length() + 7) // 8
    message_bytes = m.to_bytes(message_length, byteorder='big')
    return message_bytes.decode('utf-8')

if __name__ == "__main__":
    # For demonstration, generate a 512-bit key pair.
    private_key, public_key = generate_rsa_keys(bit_length=512)
    print("Public key (n,e):", f"{public_key.n},{public_key.e}")
    print("Private key (n,e,d):", f"{private_key.n},{private_key.e},{private_key.d}")
