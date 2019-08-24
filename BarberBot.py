# -*- coding: utf-8 -*-
# coding: utf-8
import telebot
from telebot import types
from telebot import TeleBot
from datetime import datetime
import calendar
from telebot import apihelper
import dbworker
import json
import os
from db_barber import Db_users
from flask import Flask, request


TOKEN = os.environ['token2']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
basket = 'basket.py'



def create_callback_data(action, year, month,day):
    """ Create the callback data associated to each button"""
    return "-".join([action, str(year), str(month), str(day)])

def separate_callback_data(data):
    """ Separate the callback data"""
    return tuple(int(item) for item in data.split("-"))


def create_calendar(year=None, month=None):
    now = datetime.now()
    if year == None:
        year = now.year
    if month == None:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = types.InlineKeyboardMarkup()
    #First row - Month and Year
    row = []
    row.append(types.InlineKeyboardButton(calendar.month_name[month]+ " " + str(year), callback_data=data_ignore))
    keyboard.row(*row)
    #Second row - Week Days
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(types.InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if(day == 0):
                row.append(types.InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.row(*row)
    #Last row - Buttons
    row = []
    row.append(types.InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day)))
    row.append(types.InlineKeyboardButton(" ", callback_data=data_ignore))
    row.append(types.InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day)))
    keyboard.row(*row)
    return keyboard


def process_calendar_selection(bot, update):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    """
    ret_data = (False, None)
    query = update.callback_query
    (action, year, month,day) = separate_callback_data(query.data)
    curr = datetime(int(year), int(month), 1)
    if action == "IGNORE":
        bot.answer_callback_query(callback_query_id= query.id)
    elif action == "DAY":
        bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
            )
        ret_data = True, datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")
        # UNKNOWN
    return ret_data


def create_day(chat_id, sold_hours):
    try:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        row = []
        hours = [(str(item) + ':00') for item in range(11, 21, 1)]
        f_hours = []
        for y in sold_hours:
            f_hours.append(y[0])
        for hour in f_hours:
            hours.remove(hour)
        if hours == []:
            bot.answer_callback_query(chat_id, 'Этот день полностью занят')
            pass
        for hour in hours:
            row.append(types.InlineKeyboardButton(text=hour, callback_data=f'HOUR:{hour}'))
        row.append(types.InlineKeyboardButton(text='⬅ Назад', callback_data="Назад"))
        keyboard.add(*row)
        return keyboard
    except ValueError:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        row = []
        hours = [(str(item) + ':00') for item in range(11, 21, 1)]
        for hour in hours:
            row.append(types.InlineKeyboardButton(text=hour, callback_data=f'HOUR:{hour}'))
        row.append(types.InlineKeyboardButton(text='⬅ Назад', callback_data="Назад"))
        keyboard.add(*row)
        return keyboard



def start_markup(agrs, n=None):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=n, resize_keyboard=True)
    keyboard.add(*agrs)
    return keyboard

def type_service():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for y in ["Мужская стрижка", 'Стрижка машинкой', 'Стрижка бороды', 'Детская стрижка']:
        keyboard.add(y)
    return keyboard

def master():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for y in ["Иван", 'Ивана брат', 'Марат', 'Коловрат']:
        keyboard.add(y)
    return keyboard

def get_number():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add((types.KeyboardButton(text="Отправить номер телефона", request_contact=True)), 'Отменить')
    return keyboard

def default_keyboard(row):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    rows = []
    for item in row:
        rows.append(types.InlineKeyboardButton(text=f'{item}', callback_data=f'{item}'))
    keyboard.add(*rows)
    return keyboard

def send_send(chat_id, message_id=None):
    res = db_users.confirm(chat_id)
    date = separate_callback_data(res[2])
    moth = db_users.moths[date[1]]
    if message_id is None:
        bot.send_message(text=f'Услуга: {res[0]}\n'
                          f'Мастер: {res[1]}\n'
                          f'Дата: {date[2]} {moth}\n'
                          f'Время: {res[3]} \n\n', chat_id=chat_id)
    else:
        bot.edit_message_text(text=f'Услуга: {res[0]}\n'
                                f'Мастер: {res[1]}\n'
                                f'Дата: {date[2]} {moth}\n'
                                f'Время: {res[3]} \n\n', message_id=message_id, chat_id=chat_id)
    a = ['Всё верно', 'Не та услуга', 'Не тот мастер', 'Не тот день', 'Отменить']
    bot.send_message(chat_id, 'Всё верно?', reply_markup=start_markup(a, 1))

db_users = Db_users()

@bot.message_handler(commands=['clear'])
def callback_inline(message):
    chat_id = message.from_user.id
    db_users.clear_db(chat_id)
    bot.send_message(chat_id, 'ok')

@bot.message_handler(commands=['start', 'reset'])
def callback_inline(message):
    chat_id = message.chat.id
    name = f'{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}'
    db_users.loadDB()
    db_users.create_table()
    db_users.insert_into(chat_id, name)
    dbworker.set_state(str(chat_id), '1')
    a = ["Записаться", 'Контакты', 'Адрес', "Мастера", "Услуги", "Пригласить друга", "Режим работы"]
    markup = start_markup(a, 2)
    bot.send_message(message.chat.id, f'Привет!\nЯ бот барбершопа, и я могу помочь записаться на стрижку,'
                                      f' подсказать как до нас добраться или передать, что ты опаздываешь прямо из Telegram!'
                                        f'И, кстати, если ты пригласишь друга записаться через меня,'
                                                     'то получишь 15% скидку на свою следующую запись.',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == '1')
def get_msg(message):
    print(message)
    chat_id = message.from_user.id
    if message.text == "Записаться":
        bot.send_message(chat_id, 'Понял. Пожалуйста, выбери услугу', reply_markup=type_service())
    elif message.text in ["Мужская стрижка", 'Стрижка машинкой', 'Стрижка бороды', 'Детская стрижка']:
        db_users.update_lot(chat_id, 'type_service', message.text)
        bot.send_message(chat_id, 'К какому мастеру ты хочешь записаться?', reply_markup=master())
    elif message.text in ["Иван", 'Ивана брат', 'Марат', 'Коловрат']:
        db_users.update_lot(chat_id, 'master', message.text)
        bot.send_message(chat_id, "Выбери день:", reply_markup=create_calendar()) #???
    else:
        bot.send_message(chat_id, 'ЫЫЫЫ', reply_markup=get_number())


@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == '2')
def get_msg(message):
    chat_id = message.from_user.id
    dbworker.set_state(str(chat_id), '3')
    if message.text == "Всё верно":
        bot.send_message(chat_id, 'Хорошо, мне нужен твой номер телефона.', reply_markup=get_number())
        dbworker.set_state(str(chat_id), '2')
    elif message.text in 'Не та услуга':
        bot.send_message(chat_id, 'Понял. Пожалуйста, выбери услугу', reply_markup=type_service())
    elif message.text in 'Не тот день':
        bot.send_message(chat_id, 'Понял. Пожалуйста, выбери день', reply_markup=create_calendar())
    elif message.text in 'Не тот мастер':
        bot.send_message(chat_id, 'Понял. Пожалуйста, выбери мастера', reply_markup=master())
    elif message.text == "Отменить":
        a = ["Записаться", 'Контакты', 'Адрес', "Мастера", "Услуги", "Пригласить друга", "Режим работы"]
        markup = start_markup(a)
        bot.send_message(chat_id, 'Главное меню ..', reply_markup=markup)
        dbworker.set_state(str(chat_id), '1')

@bot.message_handler(func=lambda message: dbworker.get_current_state(str(message.chat.id)) == '3')
def get_msg(message):
    chat_id = message.from_user.id
    if message.text in ["Мужская стрижка", 'Стрижка машинкой', 'Стрижка бороды', 'Детская стрижка']:
        db_users.update_lot(chat_id, 'type_service', message.text)
    elif message.text in ["Иван", 'Ивана брат', 'Марат', 'Коловрат']:
        db_users.update_lot(chat_id, 'master', message.text)
    send_send(chat_id)
    dbworker.set_state(str(chat_id), '2')


@bot.message_handler(content_types=["contact"])
def mmm(message):
    chat_id = message.from_user.id
    db_users.update_lot(chat_id, 'phone_number', message.contact.phone_number)
    db_users.update_lot(chat_id, 'status', 'active')
    res = db_users.confirm(chat_id)
    row = ['Отменить', 'Перенести', 'Опаздываю']
    price = db_users.price_list[res[0]]
    date = separate_callback_data(res[2])
    moth = db_users.moths[date[1]]
    bot.send_message(text=f'Услуга: {res[0]}\n'
                          f'Мастер: {res[1]}\n'
                          f'Дата: {date[2]} {moth}\n'
                          f'Время: {res[3]} \n'
                          f'Стоимость: {price} ₽\n\n'
                          f'Если что-то пойдет не по плану, используй кнопки под этим сообщением.', chat_id=chat_id, reply_markup=default_keyboard(row))
    a = ["Записаться", 'Мои заказы', 'Контакты', 'Адрес', "Мастера", "Услуги", "Пригласить друга", "Режим работы"]
    bot.send_message(chat_id, 'Отлично, спасибо. Я тебя записал!', reply_markup=start_markup(a, 2))
    db_users.write_pos(chat_id)
    dbworker.set_state(str(chat_id), '1')

@bot.callback_query_handler(func=lambda call: call.data == 'Назад')
def get_day(call):
    try:
        chat_id = call.message.chat.id
        bot.edit_message_text("Выбери день:", chat_id, call.message.message_id, reply_markup=create_calendar())
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data[0:3] == 'DAY')
def get_day(call):
    try:
        select_date = separate_callback_data(call.data[4:])
        chat_id = call.message.chat.id
        now = datetime.today()
        saved_date = (now.year, now.month, now.day)
        if select_date >= saved_date:
            res = db_users.confirm(chat_id)
            hours = db_users.check_day(res[2], res[1])
            markup = create_day(chat_id, hours)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=str(chat_id), reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
            db_users.update_lot(chat_id, 'time_day', call.data[4:])
        else:
            bot.answer_callback_query(chat_id, text="Эта дата уже прошла")
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data[0:4] == 'HOUR')
def get_day(call):
    try:
        chat_id = call.message.chat.id
        time_hours = call.data[5:]
        db_users.update_lot(chat_id, 'time_hours', time_hours)
        dbworker.set_state(str(chat_id), '2')
        send_send(chat_id, message_id=call.message.message_id)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data[:10] == 'NEXT-MONTH')
def next_month(call):
    try:
        chat_id = call.message.chat.id
        now = datetime.today()
        saved_date = (now.year, now.month)
        if(saved_date is not None):
            year, month = saved_date
            month += 1
            if month > 12:
                month = 1
                year += 1
            markup = create_calendar(year, month)
            bot.edit_message_text("Выбери день:", call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
    except Exception as e:
        bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data[:10] == 'PREV-MONTH')
def previous_month(call):
    try:
        chat_id = call.message.chat.id
        now = datetime.today()
        saved_date = (now.year, now.month)
        year, month = saved_date
        markup = create_calendar(year, month)
        bot.edit_message_text("Выбери день:", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    except Exception as e:
        bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data[:6] == 'IGNORE')
def ignore(call):
    bot.answer_callback_query(call.id, text="")

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=' https://barber-testbot-1996.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
