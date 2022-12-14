import time
import math
import sqlite3


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Помилка зчитування з БД")
        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Користувач з таким email вже існує!")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка при додаванні користувача у БД " + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайдений")
                return False

            return res
        except sqlite3.Error as e:
            print("Помилка зчитування з БД " + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайдений")
                return False

            return res
        except sqlite3.Error as e:
            print("Помилка зчитування з БД " + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка обновлення аватарки в БД: " + str(e))
            return False
        return True

    def addPsw(self, userid, title, psw):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO passwords VALUES(NULL, ?, ?, ?, ?)", (userid, title, psw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка додавання статті у БД " + str(e))
            return False

        return True

    def getPsw(self, pswId):
        try:
            self.__cur.execute(f"SELECT title, psw FROM passwords WHERE id = {pswId} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Помилка додавання статті у БД " + str(e))

        return (False, False)

    def getPswAnonce(self, userid):
        try:
            self.__cur.execute(f"SELECT * FROM passwords WHERE userid = {userid} ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Помилка додавання статті у БД " + str(e))

        return []
    def addMessage(self, name, email, message):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO contact VALUES(NULL, ?, ?, ?, ?)", (name, email, message, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка додавання статті у БД " + str(e))
            return False

        return True