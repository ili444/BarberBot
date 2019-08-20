import sqlite3


class Db_users():
    pass

    def loadDB(self):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str #id INT AUTO_INCREMENT
        cursor.execute("""CREATE TABLE IF NOT EXISTS users
                      (id INTEGER NOT NULL PRIMARY KEY UNIQUE, 
                       info_lot TEXT,
                       lot_price INTEGER,
                       user_id INTEGER);
                   """)
        conn.commit()
        conn.close()

    def insert_into(self, info_lot, chat_id, lot_price):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""INSERT INTO users (info_lot, lot_price, user_id) VALUES
                            (?, ?, ?);""", [(info_lot), (lot_price), (str(chat_id))])
        conn.commit()
        conn.close()

    def lot_price(self, chat_id):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""SELECT lot_price FROM users
                                        WHERE user_id = ?;""", [(str(chat_id))])
        results = cursor.fetchall()
        lot_price = [y[0] for y in results]
        conn.commit()
        conn.close()
        return sum(lot_price)

    def check_lot(self, chat_id, info_lot):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""SELECT id FROM users
                            WHERE user_id = ?;""", [(str(chat_id))])
        if cursor.fetchall() == []:
            self.insert_into(chat_id)
        else:
            self.update_lot(chat_id, info_lot)


    def update_lot(self, info_lot, id_lot, lot_price):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""UPDATE users SET info_lot = ?, lot_price = ?
                            WHERE id = ?""", [(info_lot), (lot_price), (str(id_lot))])
        conn.commit()
        conn.close()

    def change_lot(self, chat_id):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""SELECT id, info_lot FROM users
                                WHERE user_id = ?;""", [(str(chat_id))])
        results = cursor.fetchall()
        return results


    def clear_basket(self, chat_id):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""DELETE FROM users WHERE user_id = ?;""", [(str(chat_id))])
        conn.commit()
        conn.close()

    def delete_lot(self, id_lot):
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        conn.text_factory = str
        cursor.execute("""DELETE FROM users WHERE id = ?;""", [(str(id_lot))])
        conn.commit()
        conn.close()

    def select_user(self, chat_id):
        try:
            conn = sqlite3.connect("mydatabase.db")
            cursor = conn.cursor()
            conn.text_factory = str
            cursor.execute("""SELECT info_lot FROM users
                                WHERE user_id = ?;""", [(str(chat_id))])
            results = cursor.fetchall()
            return results
        except Exception as e:
            return True



