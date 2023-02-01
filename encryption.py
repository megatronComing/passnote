# -*- encoding: utf-8 -*-
'''
class for symmentric encryption
Author: Jared Yu
Contect: hfyu.hzcn@gmail.com
Version: 1.0
Update: 2023-2-21
Requires: PyQt5
'''

from Crypto import Random
from binascii import b2a_hex, a2b_hex
from Crypto.Cipher import AES
class AESCipher:
    """
    pip install pycryptodome
    there are 5 mode for AES: ECB, CBC, CTR, CFB, OFB
    CBC mode: needs a 16-bytes key and a 16-bytes iv
    ECB mode: iv is not needed
    cryptor cannot be used for encryption and decryption simoutanouly, create instances repectively for encryption and decryption
    IMPORTANT:
        For modes except ECB, decryption and encryption needs the same iv to work, which means, if
        the cipher text will be save to somewhere like a database for later decryption, iv needs to 
        be saved too. If not, use ECB mode.
    """
    def __init__(self, key:str, mode=AES.MODE_ECB, iv=Random.new().read(AES.block_size)):
        """
        key: must be 16,24 or 32 bytes, if not , extend it.
        iv: vector whose length equals to AES block
        two modes implemented in this class, which are ECB and CBC
        """
        keylen = len(key)
        if keylen != 16:
            len2extend = 16 - keylen%16
            key = key + '*'*len2extend
        self.key, self.mode, self.iv = key.encode(), mode, iv

    def __extendTo16Bytes(self, text:str):
        """ The length of the string should be a multiple of 16, if not, extend it with \0 """
        if len(text.encode()) % 16:
            extension = 16 - (len(text.encode()) % 16)
        else:
            extension = 0
        text += ("\0" * extension)
        return text.encode()
        
    def encrypt(self, text:str) -> str:
        """ encrypt the string with AES """
        # it is necessary to create a new AES instance
        if self.mode == AES.MODE_ECB:
            cryptos = AES.new(key=self.key, mode=self.mode)
        elif self.mode == AES.MODE_CBC:
            cryptos = AES.new(key=self.key, mode=self.mode, iv=self.iv)
        cipher_text = cryptos.encrypt(self.__extendTo16Bytes(text))
        # the characters of the cipher text is not necessarily ascii characters,
        # convert it to a hex string
        
        return b2a_hex(cipher_text).decode('ascii') #return a string
        #return a hex string whose type is class bytes (like b'hex string here')
        #return b2a_hex(cipher_text)

    def decrypt(self, text:str) -> str:
        """ decryption and delete the extended \0 """
        # it is necessary to create a new AES instance
        if self.mode == AES.MODE_ECB:
            cryptos = AES.new(key=self.key, mode=self.mode)
        elif self.mode == AES.MODE_CBC:
            cryptos = AES.new(key=self.key, mode=self.mode, iv=self.iv)
        plain_text = cryptos.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip("\0")


if __name__ == '__main__':
    passwd = 'HiJared@2022'
    aes = AESCipher(passwd)
    text = 'PasswordNotebookByJared@202212'
    print(f'plain text: {text}')
    result = aes.encrypt(text)
    print(f'encrypted: {result}')
    aesNew = AESCipher(passwd)
    print(f'decrypted: {aesNew.decrypt(result)}')
    
