import sqlite3


class Db_users():
    pass

    def loadDB(self):
        conn = sqlite3.connect("database.db") #id INTEGER NOT NULL PRIMARY KEY UNIQUE
        cursor = conn.cursor()
        conn.text_factory = str #id INT AUTO_INCREMENT
        cursor.execute("""CREATE TABLE IF NOT EXISTS clients
                      (user_id TEXT UNIQUE, 
                       name TEXT,
                       phone_number TEXT NULL,
                       type_service TEXT NULL,
                       master TEXT NULL,
                       time_day TEXT NULL,
                       time_hours TEXT NULL,
                       status TEXT NULL);""")
        conn.commit()
        conn.close()

    def create_table(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""CREATE TABLE IF NOT EXISTS clients2
                      (id INT AUTO_INCREMENT,
                       user_id TEXT, 
                       name TEXT,
                       phone_number TEXT NULL,
                       type_service TEXT NULL,
                       master TEXT NULL,
                       time_day TEXT NULL,
                       time_hours TEXT NULL,
                       status TEXT NULL);""")
        conn.commit()
        conn.close()

#ТАБЛИЦА 2

    def write_pos(self, chat_id):
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            conn.text_factory = str
            cursor.execute("""SELECT * FROM clients WHERE user_id = ?;""", [(chat_id)])
            results = cursor.fetchall()
            print(results[0])
            execute = """INSERT INTO clients2 (user_id, name, phone_number, 
                                                type_service, master, time_day, time_hours, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
            cursor.execute(execute, results[0])
            conn.commit()
            conn.close()

    def check_day(self, time_day, master):
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            conn.text_factory = str
            cursor.execute("""SELECT time_hours FROM clients2
                                            WHERE master = ? AND
                                                  time_day = ? AND
                                                  status = 'active';""", [(master), (time_day)])
            results = cursor.fetchall()
            return results
        except Exception:
            return []



#Таблица 1

    def insert_into(self, chat_id, name):
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            conn.text_factory = str
            cursor.execute("""INSERT INTO clients (user_id, name) VALUES
                                (?, ?);""", [(str(chat_id)), (name)])
            conn.commit()
            conn.close()
        except Exception as e:
            pass

    def update_lot(self, chat_id, param, value_param):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        conn.text_factory = str
        execute = """UPDATE clients SET {} = ?
                            WHERE user_id = ?;""".format(param)
        cursor.execute(execute, [(value_param), (chat_id)])
        conn.commit()
        conn.close()


    def confirm(self, chat_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""SELECT type_service, master, time_day, time_hours FROM clients
                                                 WHERE user_id = ?;""", [(chat_id)])
        results = cursor.fetchall()
        return results[0]


    def clear_db(self, chat_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""DELETE FROM clients WHERE user_id = ?;""", [(chat_id)])
        conn.commit()
        conn.close()





    price_list = {"Мужская стрижка": '500', 'Стрижка машинкой': '450', 'Стрижка бороды': '300', 'Детская стрижка': '350'}

    moths = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
             7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}



