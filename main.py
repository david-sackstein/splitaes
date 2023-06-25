from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def encrypt(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text


def decrypt(cipher_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(cipher_text)
    return unpad(decrypted, AES.block_size)


def check(a, b):
    if a == b:
        print("Decryption successful. Plaintext and decrypted text match.")
    else:
        print("Decryption failed. Plaintext and decrypted text do not match.")


class Blob:
    def __init__(self, data, initialization_vec):
        self.data = data
        self.initialization_vec = initialization_vec


block_size = 16
blob_size = block_size * 4

original_iv = bytearray([0x0 for x in range(16)])
zero_padding = bytearray([0x10 for x in range(16)])


def create_blobs(cipher_text, key):
    # TODO calculate the number of blobs correctly (there is a one-off error here)
    num_blobs = int((len(cipher_text) - block_size) / blob_size) - 1

    start = 0
    end = blob_size
    blobs = []
    iv = original_iv

    for i in range(0, num_blobs):
        part = cipher_text[start:end]

        last_block = part[-block_size:]
        encrypted_padding = encrypt(zero_padding, key, last_block)
        encrypted_padding_without_its_padding = encrypted_padding[:block_size]
        encrypted_part = part + encrypted_padding_without_its_padding

        blobs.append(Blob(encrypted_part, iv))

        iv = last_block
        start += blob_size
        end += blob_size

    blobs.append(Blob(cipher_text[start:], iv))
    return blobs


def decrypt_blobs(blobs, key):
    result = bytearray()
    for blob in blobs:
        decrypted_blob = decrypt(blob.data, key, blob.initialization_vec)
        result += decrypted_blob
    return result


# Test
def test():
    key = get_random_bytes(32)

    plain_text = bytearray([x & 0xFF for x in range(1235)])

    cipher_text = encrypt(plain_text, key, original_iv)

    blobs = create_blobs(cipher_text, key)

    decrypted = decrypt_blobs(blobs, key)

    check(decrypted, plain_text)


test()