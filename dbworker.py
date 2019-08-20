# -*- coding: utf-8 -*-
import shelve

# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    with shelve.open('db_file.py') as db:
        try:
            return db[user_id]
        except KeyError:  # Если такого ключа почему-то не оказалось
            return '0'  # значение по умолчанию - начало диалога

# Сохраняем текущее «состояние» пользователя в нашу базу
def set_state(user_id, value):
    with shelve.open('db_file.py') as db:
        try:
            db[user_id] = value
            return True
        except:
            # тут желательно как-то обработать ситуацию
            return False
