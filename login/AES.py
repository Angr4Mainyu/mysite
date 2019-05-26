import base64
from Crypto.Cipher import AES
import hashlib

def encrypt(key, instr,iv='8765432187654321'):
    key=hashlib.md5(str_to_bytes(key)).hexdigest()
    mystr = _pad(instr)
    cipher = AES.new(key, AES.MODE_CBC,iv)
    ret = base64.b64encode(cipher.encrypt(mystr))
    return ret.decode()

def decrypt(key, encryptedData,iv='8765432187654321'):
    key=hashlib.md5(str_to_bytes(key)).hexdigest()
    # print(key)
    encryptedData = base64.b64decode(encryptedData)
    cipher = AES.new(key, AES.MODE_CBC,iv)
    ret = _unpad(cipher.decrypt(encryptedData))
    ret = ret.decode(encoding="utf-8")
    return ret
def str_to_bytes(data):
    u_type = type(b''.decode('utf8'))
    if isinstance(data, u_type):
        return data.encode('utf8')
    return data
def _pad(s):
    BS = AES.block_size
    s = s.encode("utf-8")
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode("utf-8")

def _unpad(s):
    return s[:-ord(s[len(s)-1:])]

def main():
    encryptedData = 'Zrq5Gvyu+GgWCDI5TI6r3g=='
    mystr = '合肥'
    key = '1234567812345678'
    iv = '8765432187654321'

    # print(encrypt(key, mystr))
    # print(decrypt(key, encryptedData))