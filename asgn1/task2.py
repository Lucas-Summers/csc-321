from ssl import RAND_bytes
import sys
from Crypto.Cipher import AES

def pad(data, block_size=16):
    padding_len = block_size - len(data) % block_size
    padding = bytes([padding_len] * padding_len)
    return data + padding


def unpad(data, block_size=16):
    padding_len = data[-1]
    return data[:-padding_len]

def cbc_encrypt(im):
    key = RAND_bytes(16)
    iv = RAND_bytes(16)

    cipher = AES.new(key, AES.MODE_ECB)
    padded_file = pad(im)

    encrypted_data = bytes()
    prev_block = iv

    for i in range(0, len(padded_file), 16):
        block = padded_file[i:i+16]
        block = bytes(x ^ y for x, y in zip(block, prev_block))
        encrypted_block = cipher.encrypt(block)
        encrypted_data += encrypted_block
        prev_block = encrypted_block

    return encrypted_data, key, iv


def cbc_decrypt(encrypted_string, key, iv):

    cipher = AES.new(key, AES.MODE_ECB)

    decrypted_data = b''
    prev_block = iv

    for i in range(0, len(encrypted_string), 16):
        encrypted_block = encrypted_string[i:i+16]
        decrypted_block = cipher.decrypt(encrypted_block)
        decrypted_block = bytes(
            x ^ y for x, y in zip(decrypted_block, prev_block))
        decrypted_data += decrypted_block
        prev_block = encrypted_block

    decrypted_data = unpad(decrypted_data)

    return decrypted_data

def submit(user_string):
    encoded_string = user_string.replace(";", "%3B")
    encoded_string = encoded_string.replace("=", "%3D")

    encoded_plaintext = f"userid=456;userdata={encoded_string};session-id=31337".encode()
    encoded_plaintext = pad(encoded_plaintext)

    ciphertext, key, iv = cbc_encrypt(encoded_plaintext)
    return ciphertext, key, iv


def verify(encrypted_string, key, iv):

    decrypted_data = cbc_decrypt(encrypted_string, key, iv)
    print("decrypted data:",decrypted_data)
    admin_encoded = ";admin=true;".encode()
    return admin_encoded in decrypted_data

def flip_the_bits(ciphertext):
    ciphertext_blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
    target_block = ciphertext_blocks[0] 
    xor1 = ord('3') ^ ord(';') 
    xor2 = ord('9') ^ ord('=') 
    mod_cipher_block = target_block[:4] + bytes([target_block[4] ^ xor1]) + target_block[5:10] + bytes([target_block[10] ^ xor2]) + target_block[11:15] + bytes([target_block[15] ^ xor1])
    print("modified cipher block:", mod_cipher_block)
    ciphertext_blocks[0] = bytes(mod_cipher_block)
    modified_ciphertext = b''.join(ciphertext_blocks)
    return modified_ciphertext

def main():

    user_attack = "3admin9true3"
    cipher, key, iv = submit(user_attack)
    print("cipher:",cipher)
    mod_cipher = flip_the_bits(cipher)
    print("decrypted data without modifying:", cbc_decrypt(cipher, key, iv))
    print("modified cipher:", mod_cipher)
    val = verify(mod_cipher, key, iv)
    print(val)


if __name__ == "__main__":
    main()