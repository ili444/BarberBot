# -*- coding: utf-8 -*-
# coding: utf-8
import telebot
import dbworker
import shelve
import datetime
from datetime import datetime
import random
from cofe_lots import dict2, dict_dobavki
import os
from telebot.types import LabeledPrice
from telebot import types
from telebot import apihelper
from db_users import Db_users
import json
from flask import Flask, request

TOKEN = os.environ['token']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
basket = 'basket.py'


class Markup():
    def __init__(self, start_func):
        self.start_func = start_func
        
    def update_key(self, chat_id, key, value):
        with shelve.open('user_db.py') as db:
            dictik = (db.get(str(chat_id)))
            dictik.update({str(key): value})
            db[str(chat_id)] = dictik

    def call_value(self, chat_id, key):
        with shelve.open('user_db.py') as db:
            dictik = db.get(str(chat_id))
            value = dictik.get(key)
            return value

    def start_dif(self, chat_id):
        with shelve.open('user_db.py') as db:
            db[str(chat_id)] = {'name_lot': 'None', 'num': 'None', 'price': 'None', 'total_price': 'None',
                                'pic': 'None', 'number_ship': 'None',
                                'time': 'Ближайщее время', 'dobavka': ' ', 'koment': 'None', 'info_user': 'None',
                                'message_id': 'None', 'price_dobavka': 'None', 'size': ' ', 'num_lot': '', 'id_lot': 'None'}

    def dobavki(self, chat_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        row = []
        row.append(types.InlineKeyboardButton("⬅ Назад", callback_data='назад_инлайн'))
        for name_dobavka in dict_dobavki.keys():
            if name_dobavka == mark_up.call_value(chat_id, 'dobavka'):
                row.append(types.InlineKeyboardButton(text=f'✔ {name_dobavka}', callback_data=name_dobavka))
            else:
                row.append(types.InlineKeyboardButton(text=name_dobavka, callback_data=name_dobavka))
        row.append(types.InlineKeyboardButton("❎ Сбросить", callback_data='сбросить'))
        row.append(types.InlineKeyboardButton("🛒 В Корзину", callback_data='корзина'))
        markup.add(*row)
        return markup

    def dobavki2(self, callback):
        markup = types.InlineKeyboardMarkup(row_width=1)
        row = []
        row.append(types.InlineKeyboardButton("⬅ Назад", callback_data='назад_инлайн'))
        for name_dobavka in dict_dobavki.keys():
            if name_dobavka == callback.data:
                row.append(types.InlineKeyboardButton(text=f'✔ {name_dobavka}', callback_data=name_dobavka))
            else:
                row.append(types.InlineKeyboardButton(text=name_dobavka, callback_data=name_dobavka))
        row.append(types.InlineKeyboardButton("❎ Сбросить", callback_data='сбросить'))
        row.append(types.InlineKeyboardButton("🛒 В Корзину", callback_data='корзина'))
        markup.add(*row)
        return markup

    def basket(self, chat_id, callback):
        m = db_users.select_user(chat_id)
        if m == True:
            bot.send_message(chat_id, 'Ваша корзина пуста!', reply_markup=mark_up.add_lot())
        else:
            lots = []
            total_price = db_users.lot_price(chat_id)
            for lot in m:
                jlot = json.loads(lot[0])
                tot_price = (jlot['num'] * (jlot['price']))
                basket_lot = jlot['name_lot'] + '  ' + str(jlot['num']) + ' шт.  ' + str(tot_price) + ' ₽\n    ' + jlot['dobavka']
                lots.append(basket_lot)
            string = '\n\n☕ '.join(lots)
            mark_up.update_key(chat_id, 'total_price', total_price)
            if callback.inline_message_id == None:
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Ваша корзина :\n\n'
                                                                                                        f'☕ {string} \n\n'
                                                                                                        f'Итого: {str(total_price)}  ₽.',
                                          reply_markup=mark_up.finish_markup())
            else:
                bot.edit_message_text(inline_message_id=callback.inline_message_id, text='Вы перешли в корзину')
                bot.send_message(chat_id,
                                     text='Ваша корзина :\n\n'
                                          f'☕ {string}\n\n'
                                          f'Итого: {str(total_price)}  ₽.',
                                     reply_markup=mark_up.finish_markup())






    def catalog(self):
        keyboard = types.InlineKeyboardMarkup()
        switch_button1 = types.InlineKeyboardButton(text="Кофе", switch_inline_query_current_chat="Кофе")
        switch_button2 = types.InlineKeyboardButton(text="Десерт", switch_inline_query_current_chat="Десерт")
        keyboard.add(switch_button1, switch_button2)
        return keyboard

    def num_markup1(self):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton('1', callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton(text='⬅ Назад', switch_inline_query_current_chat="Кофе")
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data='корзина')
        a6 = types.InlineKeyboardButton("☕ Добавки", callback_data=u'добавки')
        a7 = types.InlineKeyboardButton("📝 Комментарий", callback_data=u'комент')
        a8 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        markup.add(a8)
        return markup

    def num_markup2(self, callback, num):
        markup = mark_up.top_markup(num)
        return markup

    def check_basket(self, chat_id):
            m = db_users.select_user(chat_id)
            if m == []:
                bot.send_message(chat_id, 'Ваша корзина пуста!', reply_markup=mark_up.add_lot())
            else:
                lots = []
                total_price = db_users.lot_price(chat_id)
                for lot in m:
                    jlot = json.loads(lot[0])
                    tot_price = (jlot['num'] * (jlot['price']))
                    basket_lot = jlot['name_lot'] + '  ' + str(jlot['num']) + ' шт.  ' + str(tot_price) + ' ₽\n    ' + jlot['dobavka']
                    lots.append(basket_lot)
                string = '\n\n☕ '.join(lots)
                mark_up.update_key(chat_id, 'total_price', total_price)
                mark_up.update_key(chat_id, 'id_lot', 'None')
                bot.send_message(chat_id,
                                     text='Ваша корзина :\n\n'
                                          f'☕ {string}\n\n'
                                          f'Итого: {str(total_price)}  ₽.',
                                     reply_markup=mark_up.finish_markup())


    def gg_basket(self, callback, id_lot):
        chat_id = callback.from_user.id
        name_lot = mark_up.call_value(chat_id, 'name_lot')
        num = mark_up.call_value(chat_id, 'num')
        size = mark_up.call_value(chat_id, 'size')
        price = mark_up.call_value(chat_id, 'price')
        price_dobavka = mark_up.call_value(chat_id, 'price_dobavka')
        if price_dobavka == 'None': price_dobavka = 0
        pic = mark_up.call_value(chat_id, 'pic')
        dobavka = mark_up.call_value(chat_id, 'dobavka')
        koment = mark_up.call_value(chat_id, 'koment')
        lot_price = (int(price) + price_dobavka) * num
        id_lot = mark_up.call_value(chat_id, 'id_lot')

        info_lot = json.dumps({'name_lot': name_lot, 'num': num, 'price': price, 'lot_price': lot_price,
                                'pic': pic, 'number_ship': 'None',
                                'time': 'None', 'dobavka': dobavka, 'koment': koment, 'info_user': 'None',
                                'message_id': 'None', 'price_dobavka': price_dobavka, 'size': size}, ensure_ascii=False)
        if id_lot == 'None':
            db_users.insert_into(info_lot, chat_id, lot_price)
        else:
            db_users.update_lot(info_lot, id_lot, lot_price)
        mark_up.update_key(chat_id, 'price_dobavka', 0.0)
        mark_up.update_key(chat_id, 'id_lot', 'None')

    def backbasket(self):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton(text='⬅ Назад в Корзину', callback_data=u'корзина')
        markup.add(a1)
        return markup

    def back(self):
        markup = types.InlineKeyboardMarkup(True)
        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data='назад_инлайн')
                   )
        return markup

    def finish_markup(self):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("✔Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", switch_inline_query_current_chat='изменить')
        a55 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5, a55)
        markup.add(a6, a7)
        return markup

    def add_lot(self):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
        markup.add(a1)
        return markup



    def time2(self, callback):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Ближайщее время", callback_data=u'Ближайщее время')
        a2 = types.InlineKeyboardButton("10 мин.", callback_data='10 мин.')
        a3 = types.InlineKeyboardButton("30 мин.", callback_data=u'30 мин.')
        a4 = types.InlineKeyboardButton("60 мин.", callback_data=u'60 мин.')
        a5 = types.InlineKeyboardButton("📝 Изменить", switch_inline_query_current_chat='изменить')
        a55 = types.InlineKeyboardButton("➕ Добавить", callback_data='добавить')
        a6 = types.InlineKeyboardButton("❎ Очистить", callback_data='очистить')
        a7 = types.InlineKeyboardButton("🏁 Оформить", callback_data='оформить')
        if callback.data == '10 мин.':
            a2 = types.InlineKeyboardButton("✔10 мин.", callback_data='10 мин.')
        if callback.data == 'Ближайщее время':
            a1 = types.InlineKeyboardButton("✔Ближайщее время", callback_data=u'Ближайщее время')
        if callback.data == '30 мин.':
            a3 = types.InlineKeyboardButton("✔30 мин.", callback_data=u'30 мин.')
        if callback.data == '60 мин.':
            a4 = types.InlineKeyboardButton("✔60 мин.", callback_data=u'60 мин.')
        markup.add(a1)
        markup.add(a2, a3, a4)
        markup.add(a5, a55)
        markup.add(a6, a7)
        return markup

    def common(self):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("Начать выполнение ", callback_data=u'выполнение')
        markup.add(a1)
        return markup

    def random_pool(self):
        a = random.randint(999, 9999)
        return a

    def go_basket(self):
        markup = types.InlineKeyboardMarkup(True)
        markup.add(types.InlineKeyboardButton("🛒 В корзину", callback_data='корзина'),
                   types.InlineKeyboardButton("🔃 Изменить примечание ", callback_data='комент'),
                   types.InlineKeyboardButton("⬅ Назад", callback_data='назад_инлайн')
                   )
        return markup

    def top_markup(self, num):
        markup = types.InlineKeyboardMarkup()
        a1 = types.InlineKeyboardButton("-", callback_data=u'-1')
        a2 = types.InlineKeyboardButton(str(num), callback_data='jr')
        a3 = types.InlineKeyboardButton("+", callback_data=u'+1')
        a4 = types.InlineKeyboardButton("⬅ Назад", switch_inline_query_current_chat="Кофе")
        a5 = types.InlineKeyboardButton("🛒 Корзина", callback_data=u'корзина')
        a6 = types.InlineKeyboardButton("☕ Добавки", callback_data=u'добавки')
        a7 = types.InlineKeyboardButton("📝 Комментарий", callback_data=u'комент')
        a8 = types.InlineKeyboardButton("❌ Удалить позицию", callback_data=u'удалить позицию')
        markup.add(a1, a2, a3)
        markup.add(a4, a5)
        markup.add(a6)
        markup.add(a7)
        markup.add(a8)
        return markup

    def markup_num(self, num, callback, chat_id):
        markup = mark_up.top_markup(num)
        if callback.inline_message_id == None:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback.message.message_id, reply_markup=markup)
        else:
            mark_up.show_lot(chat_id, callback.inline_message_id)
            bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup)




    def add_knopka(self, id, thumb_url, title, price, size):
        r1 = types.InlineQueryResultArticle(
            id=id,
            thumb_url=thumb_url,
            title=title,
            description=f'{size}\nЦена {price} ₽',
            input_message_content=types.InputTextMessageContent(message_text=f"{title}"
                                                                             f"\n{size}\n{price} ₽\n\n"
                                                                             f'Добавки:\nНичего не выбрано'
                                                                             f'\n\nЦена {price} ₽'
                                                                             f"[\xa0]({thumb_url})"
                                                                , parse_mode='Markdown'),
            reply_markup=mark_up.num_markup1()
        )
        return r1

    def cofe_finish(self, atr):
        r = []
        n_keys = dict2[atr].keys()
        for key1 in n_keys:
            a = dict2[atr].get(key1)
            d = mark_up.add_knopka(
                a['id'], a['thumb_url'], a['title'], a['price'], a['size']
            )
            r.append(d)
        return r

    def show_lot(self, chat_id, inline_message_id):
        id_lot = mark_up.call_value(chat_id, 'id_lot')
        if id_lot == 'None': id_lot = 1
        name_lot = mark_up.call_value(chat_id, 'name_lot')
        size = mark_up.call_value(chat_id, 'size')
        price = mark_up.call_value(chat_id, 'price')
        dobavka = mark_up.call_value(chat_id, 'dobavka')
        if dobavka == ' ' or dobavka == '':
            dobavka = 'Ничего не выбрано'
        price_dobavka = mark_up.call_value(chat_id, 'price_dobavka')
        if price_dobavka == 'None': price_dobavka = 0.0
        pic = mark_up.call_value(chat_id, 'pic')
        num = mark_up.call_value(chat_id, 'num')
        message_text = (f"№{str(id_lot)}. {name_lot}"
                        f"\n{size}\n{str(price)} ₽\n\n"
                        f'Добавки:\n{dobavka}'
                        f'\n\nЦена {str((price + price_dobavka ) * num)} ₽'
                        f"[\xa0]({pic})")

        bot.edit_message_text(text=message_text, inline_message_id=inline_message_id, parse_mode='Markdown')


mark_up = Markup('ok')

db_users = Db_users()


@bot.message_handler(commands=['start', 'reset'])
def callback_inline(message):
    chat_id = message.from_user.id
    mark_up.start_dif(chat_id)
    user_markup1 = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup1.row('☕ Каталог', '🛒 Корзина')
    user_markup1.row('📌 Акции', '📲 Обратная связь')
    db_users.loadDB()
    name = message.from_user.first_name
    dbworker.set_state(str(chat_id), '1')
    bot.send_message(message.chat.id, f'Приветствую, {name}! Я Кофе-бот!\n\nУ нас ты можешь заказать кофе!',
                     reply_markup=user_markup1)
    bot.send_message(message.from_user.id, 'Выбери категорию:',
                         reply_markup=mark_up.catalog())


@bot.inline_handler(func=lambda query: True)
def inline_query(query):
    try:
        chat_id = query.from_user.id
        num = 1
        mark_up.update_key(chat_id, 'num', num)
        if query.query == 'Кофе':
            dbworker.set_state(str(chat_id), '2')
            r = mark_up.cofe_finish(atr='cofe')
            bot.answer_inline_query(query.id, r, cache_time=0, is_personal=True)
        if query.query == 'изменить':
                lots = db_users.change_lot(chat_id)
                r = []
                for lot in lots:
                    id_id = lot[0]
                    a = json.loads(lot[1])
                    num = a['num']
                    price = a['price']
                    dobavka = 'Ничего не выбрано' if a['dobavka'] == ' ' else a['dobavka']
                    price_dobavka = a['price_dobavka']
                    size = a['size']
                    markup = mark_up.top_markup(num)
                    input_content = types.InputTextMessageContent(message_text=f"№{str(id_id)}. {a['name_lot']}"
                                                                             f"\n{size}\n{price} ₽\n\n"
                                                                             f'Добавки:\n{dobavka}'
                                                                             f'\n\nЦена {str((price + price_dobavka ) * num)} ₽'
                                                                             f"[\xa0]({a['pic']})"
                                                                , parse_mode='Markdown')
                    r2 = types.InlineQueryResultArticle(id=str(id_id),
                                                        thumb_url=a['pic'], title=a['name_lot'],
                                                        description=f'{size}\n{num} шт.\n{str((price + price_dobavka ) * num)} ₽',
                                                        input_message_content=input_content, reply_markup=markup)
                    r.append(r2)
                dbworker.set_state(str(chat_id), 'change')
                bot.answer_inline_query(query.id, r, cache_time=0, is_personal=True)
    except Exception as e:
        print(e)


@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == 'koment')
def mdd_apps(message):
    try:
        chat_id = message.chat.id
        mark_up.update_key(chat_id, 'koment', message.text)
        bot.reply_to(message, 'Добавлю это сообщение комментарием к позиции', reply_markup=mark_up.go_basket())
        dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)

@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == 'change')
def msg_apps(message):
    try:
        chat_id = message.chat.id
        lots = db_users.change_lot(chat_id)
        for lot in lots:
                a = json.loads(lot[1])
                if a['name_lot'] and ('№'+str(lot[0])+".") in message.text:
                    mark_up.update_key(chat_id, 'id_lot', lot[0])
                    mark_up.update_key(chat_id, 'name_lot', a['name_lot'])
                    mark_up.update_key(chat_id, 'price', (float(a['price'])))
                    mark_up.update_key(chat_id, 'num', a['num'])
                    mark_up.update_key(chat_id, 'pic', a['pic'])
                    mark_up.update_key(chat_id, 'dobavka', a['dobavka'])
                    mark_up.update_key(chat_id, 'price_dobavka', a['price_dobavka'])
                    break
                else:
                    pass
        dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)



@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == '2')
def msg_apps(message):
    try:
        chat_id = message.chat.id
        n_keys = dict2['cofe'].keys()
        for key1 in n_keys:
            a = dict2['cofe'].get(key1)
            if a['title'] in message.text:
                mark_up.update_key(chat_id, 'pic', a['thumb_url'])
                mark_up.update_key(chat_id, 'size', a['size'])
                mark_up.update_key(chat_id, 'name_lot', a['title'])
                mark_up.update_key(chat_id, 'price', a['price'])
            dbworker.set_state(str(chat_id), '1')
    except Exception as e:
        print(e)



@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        chat_id = message.from_user.id
        if message.text == "☕ Каталог":
            bot.send_message(chat_id, 'Выберите категорию', reply_markup=mark_up.catalog())
        if message.text == "🛒 Корзина":
            mark_up.check_basket(chat_id)
    except Exception as e:
        print(e)




@bot.callback_query_handler(func=lambda callback: dbworker.get_current_state(str(callback.from_user.id)) == 'dobavki')
def callback_inline(callback):
    try:
        if callback:
            chat_id = callback.from_user.id
            if callback.data == 'назад_инлайн':
                dbworker.set_state(str(chat_id), '1')
                num = mark_up.call_value(chat_id, 'num')
                markup = mark_up.num_markup2(callback, num)
                name_lot = mark_up.call_value(chat_id, 'name_lot')
                dobavka = mark_up.call_value(chat_id, 'dobavka')
                a = 'Ничего не выбрано' if dobavka == ' ' else dobavka
                price = mark_up.call_value(chat_id, 'price')
                pic = mark_up.call_value(chat_id, 'pic')
                size = mark_up.call_value(chat_id, 'size')
                price_dobavka = mark_up.call_value(chat_id, 'price_dobavka')
                price_dobavka = 0.0 if a == 'Ничего не выбрано' else price_dobavka
                bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                      text=f"{name_lot}"
                                                f"\n{size}\n{price} ₽\n\n"
                                                f'Добавки:\n{a}'
                                                f'\n\nЦена {(str((float(price) * num) + (price_dobavka * num)))} ₽'
                                                f"[\xa0]({pic})", parse_mode='Markdown', reply_markup=markup)
            elif callback.data == 'сбросить':
                mark_up.update_key(chat_id, 'price_dobavka', 0.0)
                mark_up.update_key(chat_id, 'dobavka', '')
                markup = mark_up.dobavki2(callback)
                bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup)
            elif callback.data == 'корзина':
                dbworker.set_state(str(chat_id), '1')
                id_lot = mark_up.call_value(chat_id, 'id_lot')
                mark_up.gg_basket(callback, id_lot)
                mark_up.basket(chat_id, callback)
            else:
                for key in dict_dobavki.keys():
                    if key in callback.data:
                        mark_up.update_key(chat_id, 'dobavka', key)
                        mark_up.update_key(chat_id, 'price_dobavka', dict_dobavki.get(key))
                        markup2 = mark_up.dobavki2(callback)
                        bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup2)
                        break
                    else:
                        mark_up.update_key(chat_id, 'price_dobavka', 0.0)
                        mark_up.update_key(chat_id, 'dobavka', callback.data)
                        markup3 = mark_up.dobavki2(callback)
                        bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=markup3)
    except Exception as e:
        print(e)





@bot.callback_query_handler(func=lambda callback: True)
def callback_inline(callback):
    try:
        if callback:
            chat_id = callback.from_user.id
            num = mark_up.call_value(chat_id, 'num')
            name_lot = mark_up.call_value(chat_id, 'name_lot')
            if callback.data == '+1':
                num += 1
                mark_up.update_key(chat_id, 'num', num)
                mark_up.markup_num(num, callback, chat_id)
            if callback.data == '-1':
                num -= 1
                if num < 1:
                    num = 1
                mark_up.update_key(chat_id, 'num', num)
                mark_up.markup_num(num, callback, chat_id)
            if callback.data == "корзина":
                dbworker.set_state(str(chat_id), '1')
                id_lot = mark_up.call_value(chat_id, 'id_lot')
                mark_up.gg_basket(callback, id_lot)
                mark_up.basket(chat_id, callback)
            if callback.data == 'удалить позицию':
                id_lot = mark_up.call_value(chat_id, 'id_lot')
                db_users.delete_lot(id_lot)
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text='Позиция удалена')
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id, text='Позиция удалена')
                mark_up.check_basket(chat_id)
            if callback.data == 'очистить':
                mark_up.update_key(chat_id, 'dobavka', '')
                mark_up.update_key(chat_id, 'price_dobavka', 0.0)
                db_users.clear_basket(chat_id)
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Ваша корзина очищена!', reply_markup=mark_up.add_lot())
            if callback.data == 'выполнение':
                number_ship = mark_up.call_value(chat_id, 'number_ship')
                bot.send_message(-1001302729558, f'Заказ номер: #{number_ship}\n\n')
                bot.answer_callback_query(callback.id, "Ваш заказ в процессе приготовления!")
            if callback.data == 'сбросить':
                mark_up.update_key(chat_id, 'price_dobavka', 0.0)
                markup = mark_up.dobavki(chat_id)
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                          text='Добавки для напитков..\n(Можно выбрать один вариант)', reply_markup=markup)
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text='Добавки для напитков..\n(Можно выбрать один вариант)',
                                          reply_markup=markup)
            if callback.data == 'добавки':
                markup = mark_up.dobavki(chat_id)
                dbworker.set_state(str(chat_id), 'dobavki')
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                          text='Добавки для напитков..\n(Можно выбрать один вариант)', reply_markup=markup)
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text='Добавки для напитков..\n(Можно выбрать один вариант)',
                                          reply_markup=markup)
            if callback.data == 'комент':
                dbworker.set_state(str(chat_id), 'koment')
                if callback.inline_message_id == None:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                          text='Напишите комментарий к данной позиции:\n\n'
                                               f'{name_lot}')
                else:
                    bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                          text='Напишите комментарий к данной позиции:\n\n'
                                               f'{name_lot}',
                                          reply_markup=mark_up.back())
            if callback.data == 'назад_инлайн':
                dbworker.set_state(str(chat_id), '1')
                num = mark_up.call_value(chat_id, 'num')
                markup = mark_up.num_markup2(callback, num)
                name_lot = mark_up.call_value(chat_id, 'name_lot')
                dobavka = mark_up.call_value(chat_id, 'dobavka')
                a = 'Ничего не выбрано' if dobavka == ' ' else dobavka
                price = mark_up.call_value(chat_id, 'price')
                pic = mark_up.call_value(chat_id, 'pic')
                size = mark_up.call_value(chat_id, 'size')
                price_dobavka = mark_up.call_value(chat_id, 'price_dobavka')
                price_dobavka = 0.0 if a == 'Ничего не выбрано' else price_dobavka
                bot.edit_message_text(inline_message_id=callback.inline_message_id,
                                      text=f"{name_lot}"
                                           f"\n{size}\n{price} ₽\n\n"
                                           f'Добавки:\n{a}'
                                           f'\n\nЦена {(str((float(price) * num) + (price_dobavka * num)))} ₽'
                                           f"[\xa0]({pic})", parse_mode='Markdown', reply_markup=markup)
            if callback.data == 'оформить':
                m = db_users.select_user(chat_id)
                lots = []
                for lot in m:
                    jlot = json.loads(lot[0])
                    tot_price = (jlot['num'] * (jlot['price']))
                    basket_lot = jlot['name_lot'] + '  ' + str(jlot['num']) + ' шт.  ' + str(
                    tot_price) + ' ₽\n    ' + jlot['dobavka']
                    lots.append(basket_lot)
                string = '\n✅ '.join(lots)
                price = mark_up.call_value(chat_id, 'total_price')
                price1 = price * 100
                prices = [LabeledPrice(label=f'Стоимость услуги: ', amount=int(price1))]
                number_ship = f'{str(chat_id)} - {str(mark_up.random_pool())}'
                mark_up.update_key(chat_id, 'number_ship', number_ship)
                title = f'Заказ: {number_ship}'
                if price1 > 6569.0:
                    bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text=f"Вы перешли к оплате заказа")
                    bot.send_invoice(callback.from_user.id, provider_token='381764678:TEST:8408',
                                     start_parameter='true',
                                     title=title,
                                     description=f'✅ {string}',
                                     invoice_payload='test',
                                     currency='RUB',
                                     prices=prices,
                                     need_phone_number=True,
                                     photo_url='http://www.tobystevens.co.uk/wp-content/uploads/2012/04/7.-SAMSUNG_COFFEE_CAFE_LOGO_GRAPHIC.jpg',
                                     photo_height=512,
                                     photo_width=512,
                                     photo_size=512,
                                     )
                else:
                    bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                          text='К сожалению, Telegram обслуживает платежи не менее 1$\n'
                                               f'Сумма вашего заказа: {price} ₽\n'
                                               f'Добавьте в корзину позиции..',
                                          reply_markup=mark_up.add_lot())
            if "Ближайщее время" == callback.data:
                markup = mark_up.time2(callback)
                mark_up.update_key(chat_id, 'time', callback.data)
                bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
            if 'мин.' in callback.data:
                markup = mark_up.time2(callback)
                mark_up.update_key(chat_id, 'time', callback.data)
                bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=markup)
            if callback.data == 'добавить':
                mark_up.update_key(chat_id, 'dobavka', ' ')
                bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id,
                                      text='Выберите категорию', reply_markup=mark_up.catalog())
    except Exception as e:
        print(e)






@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=False,
                              error_message='Oh, што-то пошло не так. Попробуйте повторить позже!')

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Проблемы с картой"
                                                " повторите платеж позже.")




@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    m = db_users.select_user(chat_id)
    #total_price = db_users.lot_price(chat_id)
    lots = []
    for lot in m:
        jlot = json.loads(lot[0])
        tot_price = (jlot['num'] * (jlot['price']))
        if jlot['koment'] == 'None':
            koment = ' '
        else:
            koment = ('\nКомментарий:    ' + jlot['koment'])
        basket_lot = jlot['name_lot'] + '  ' + str(jlot['num']) + ' шт.  ' + str(
            tot_price) + ' ₽\nДобавка:\n    ' + jlot['dobavka'] + koment
        lots.append(basket_lot)
    string = '\n\n✅ '.join(lots)
    from_chat_id = -1001302729558
    now = datetime.now()
    today = datetime.today().strftime('%H:%M')
    time_order = f"{now.year}-{now.month}-{now.day}  {today}"
    type_pay = 'Банк. карта'
    name = f'{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}'
    number_ship = mark_up.call_value(chat_id, 'number_ship')
    total_price = mark_up.call_value(chat_id, 'total_price')
    time = mark_up.call_value(chat_id, 'time')
    bot.send_message(message.from_user.id, f'Супер! Теперь ваш заказ на сумму {str(total_price)} ₽ отправлен..\n\nПозиции заказа:\n\n'
                                           f'✅ {string}\n\nНомер вашего заказа - {number_ship}\n'
                                           f'Время выполнения: {time}',
                     reply_markup=mark_up.common())
    bot.send_message(from_chat_id, f'✅ {string} ₽\n'
                                   f'___________________________\n\n'
                                   f'Номер заказа - {number_ship}\n'
                                   f'Время заказа: {time_order}\n'
                                   f'Время выполнения: {time}\n'
                                   f'Заказчик: {name}\n'
                                   f'Тип оплаты: {type_pay}\n\n'
                                   f'Итого: {str(total_price)} ₽.'
                     )
    db_users.clear_basket(chat_id)



@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

"""
@server.route('/' + 'PAYMENTS', methods=['POST'])
def Check_Payments():
    try:
        chat_id = int(request.form['label'])
        total_price1 = float(request.form['amount'])
        total_price2 = (float(mark_up.call_value(chat_id, 'total_price')) * 0.98)
        if total_price1 == total_price2:
            mark_up.finish_payments(chat_id)
        return "HTTP 200 OK", 200
    except Exception as e:
        print(e)
"""   
    
     

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://flask-est-1996.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
