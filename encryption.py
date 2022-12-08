from cryptography.fernet import Fernet

key = Fernet.generate_key()

crypter = Fernet(key)


class encryption():

    def encrypt(psw):
        pw = crypter.encrypt(psw.encode())
        return str(pw, 'utf8')

    def decrypt(psw):
        decryptString = crypter.decrypt(psw)
        return str(decryptString, 'utf8')
