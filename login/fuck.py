import base64
from Crypto.Cipher import AES

def Encrypt(key, iv, instr):
    mystr = _pad(instr)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ret = base64.b64encode(cipher.encrypt(mystr))
    return ret

def Decrypt(key, iv, encryptedData):
    encryptedData = base64.b64decode(encryptedData)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ret = _unpad(cipher.decrypt(encryptedData))
    ret = ret.decode(encoding="utf-8")
    return ret

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

    print(Encrypt(key, iv, mystr))
    print(Decrypt(key, iv, encryptedData))

if __name__ == '__main__':
    main()