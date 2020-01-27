import time
import requests
import telebot
import praw
from prawcore import NotFound
from telebot import types
from telebot.types import ForceReply
from datetime import datetime
import psycopg2
import threading

# подключаем БД
con = psycopg2.connect(
    database="",
    user="",
    password="",
    host="",
    port=""
)
cur = con.cursor()
# имя таблицы в бд
table = 'alfa'
table_id = 'alfa_id'
# токен бота
bot = telebot.TeleBot('')
# подлючение реддита
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='')


@bot.message_handler(commands=['start'])
def start(message):
    print(message)
    cur.execute(
        'INSERT INTO {table} (id, username, datalast, subscription, datareg) VALUES ({id}, \'{username}\', '
        '\'{datalast}\', \'{subscription}\', \'{datareg}\');'.format(
            table=table,
            id=message.chat.id,
            datalast=str(datetime.utcfromtimestamp(int(message.date)).strftime('%Y-%m-%d %H:%M:%S')),
            datareg=str(datetime.utcfromtimestamp(int(message.date)).strftime('%Y-%m-%d %H:%M:%S')),
            username=message.from_user.username,
            subscription=''))
    con.commit()
    print('Chat Id ' + str(message.chat.id))
    bot.send_message(message.chat.id, 'Привет\n'
                                      'Этот бот предназчен для получения постов с площадки Reddit',
                     reply_markup=keyboard_start())
    bot.register_next_step_handler(message, post(message))


def post(message):
    while True:
        cur.execute("""SELECT id, username, subscription from {table} WHERE subscription NOT IN ('')""".format(
            table=table
        ))
        subred = cur.fetchall()
        cur.execute("""SELECT id_set from {table}""".format(
            table=table_id
        ))
        con.commit()
        id_set = cur.fetchall()
        print(id_set)
        for item in subred:
            if item[0] == message.chat.id:
                for submission in reddit.subreddit(item[2]).hot(limit=5):
                    if submission.id not in id_set:
                        print("Такого поста еще не было")
                        print("ID: " + submission.id)
                        print('NAME: ' + item[2])
                        print('TITLE: ' + submission.title)
                        print('--------------------------------------')
                        # submission.title_finaly = '<b>' + submission.title + '</b>'
                        # if not submission.url:
                        #     if not submission.selftext:
                        #         print('1_1')
                        #         bot.send_message(message.chat.id,
                        #                          submission.title_finaly + '\n' + '#' + str(
                        #                              submission.subreddit), parse_mode='HTML')
                        #     else:
                        #         print('1_2')
                        #         bot.send_message(message.chat.id,
                        #                          submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                        #                              submission.subreddit), parse_mode='HTML')
                        # elif is_url_image(submission.url) and submission.url[:17] == 'https://i.redd.it':
                        #     if not submission.selftext:
                        #         print('3_1')
                        #         bot.send_photo(message.chat.id,
                        #                        caption=submission.title_finaly + '\n' + '#' + str(
                        #                            submission.subreddit), photo=submission.url, parse_mode='HTML')
                        #     else:
                        #         print('3_2')
                        #         bot.send_photo(message.chat.id,
                        #                        caption=submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                        #                            submission.subreddit), photo=submission.url, parse_mode='HTML')
                        # elif submission.url[:5] == 'https':
                        #     if not submission.selftext:
                        #         print('2_1')
                        #         bot.send_message(message.chat.id,
                        #                          submission.title_finaly + '\n\n' + submission.url + '\n' + '#' + str(
                        #                              submission.subreddit), parse_mode='HTML')
                        #     else:
                        #         print('2_2')
                        #         bot.send_message(message.chat.id,
                        #                          submission.title_finaly + '\n\n' + submission.selftext + '\n\n' + submission.url + '\n' + '#' + str(
                        #                              submission.subreddit), parse_mode='HTML')
                        # else:
                        #     if not submission.selftext:
                        #         print('4_1')
                        #         bot.send_message(message.chat.id, submission.title_finaly + '\n' '#' + str(
                        #             submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
                        #     else:
                        #         print('4_2')
                        #         print('sfsfsf')
                        #         bot.send_message(message.chat.id,
                        #                          submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                        #                              submission.subreddit), parse_mode='HTML')
                        cur.execute(
                            'INSERT INTO {table} (id_set) VALUES (\'{id}\');'.format(table=table_id, id=submission.id))
                        con.commit()
                time.sleep(30)


def post_reddit(message, submission):
    if not submission.url:
        if not submission.selftext:
            print('1_1')
            bot.send_message(message.chat.id,
                             submission.title_finaly + '\n' + '#' + str(
                                 submission.subreddit), parse_mode='HTML')
        else:
            print('1_2')
            bot.send_message(message.chat.id,
                             submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                                 submission.subreddit), parse_mode='HTML')
    elif is_url_image(submission.url) and submission.url[:17] == 'https://i.redd.it':
        if not submission.selftext:
            print('3_1')
            bot.send_photo(message.chat.id,
                           caption=submission.title_finaly + '\n' + '#' + str(
                               submission.subreddit), photo=submission.url, parse_mode='HTML')
        else:
            print('3_2')
            bot.send_photo(message.chat.id,
                           caption=submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                               submission.subreddit), photo=submission.url, parse_mode='HTML')
    elif submission.url[:5] == 'https':
        if not submission.selftext:
            print('2_1')
            bot.send_message(message.chat.id,
                             submission.title_finaly + '\n\n' + submission.url + '\n' + '#' + str(
                                 submission.subreddit), parse_mode='HTML')
        else:
            print('2_2')
            bot.send_message(message.chat.id,
                             submission.title_finaly + '\n\n' + submission.selftext + '\n\n' + submission.url + '\n' + '#' + str(
                                 submission.subreddit), parse_mode='HTML')
    else:
        if not submission.selftext:
            print('4_1')
            bot.send_message(message.chat.id, submission.title_finaly + '\n' '#' + str(
                submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
        else:
            print('4_2')
            print('sfsfsf')
            bot.send_message(message.chat.id,
                             submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                                 submission.subreddit), parse_mode='HTML')


def keyboard_start():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_subs = types.KeyboardButton(text="Управление подписками")
    button_get = types.KeyboardButton(text="Получить пост с ссылки")
    button_help = types.KeyboardButton(text="Другие функции")
    keyboard.add(button_subs, button_get, button_help)
    return keyboard


@bot.message_handler(content_types=['text'])
def send(message):
    if message.text == 'Управление подписками':
        keyboard_subscription(message)
    elif message.text == 'Получить пост с ссылки':
        bot.send_message(message.chat.id, 'Введите ссылку на пост', reply_markup=ForceReply())
        bot.register_next_step_handler(message, get_post)
    elif message.text == 'Другие функции':
        bot.send_message(message.chat.id, 'Доступны команды:\n'
                                          '/list - список ваших подписок\n')
    elif message.text == '/list':
        subscription_list_text_post(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'subscription_list':
        bot.answer_callback_query(call.id)
        subscription_list_text_post(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == 'subscription_add':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 'Добавьте новую подписку', reply_markup=ForceReply())
        bot.register_next_step_handler(call.message, add_subscription)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == 'subscription_remove':
        subscription_list_text_post(call.message)
        bot.answer_callback_query(call.id)
        cur = con.cursor()
        cur.execute(
            """SELECT id, username, subscription from {table} WHERE subscription NOT IN ('')""".format(table=table))
        subscription_list_array = cur.fetchall()
        index = False
        for item in subscription_list_array:
            if item[0] == call.message.chat.id and item:
                index = True
            else:
                index = True
            if index:
                bot.send_message(call.message.chat.id,
                                 'Какую подписку удаляем?\nНажмите на название подписки в списке выше и оно '
                                 'скопируется в '
                                 'буфер обмена',
                                 reply_markup=ForceReply())
                break
            else:
                bot.send_message(call.message.chat.id, 'Ваш список подписок пуст')
                subscription_list_text_post(call.message)
        bot.register_next_step_handler(call.message, remove_subscription)
        bot.delete_message(call.message.chat.id, call.message.message_id)


def add_subscription(message):
    # проверка на присутсвие данной подписки в списке
    if sub_exists_remove(message.text):
        bot.send_message(message.chat.id, 'Данная подписка уже оформлена')
        subscription_list_text_post(message)
    else:
        # проверка на сущестовованние страницы на Reddit
        bot.send_message(message.chat.id, 'Проверка на сущестовованние страницы...')
        time.sleep(2)
        if sub_exists_add(message.text):
            # добавление данных в БД
            cur.execute(
                'INSERT INTO {table} (id, username, datalast, subscription) VALUES ({id}, \'{username}\', '
                '\'{datalast}\', '
                '\'{subscription}\');'.format(
                    table=table,
                    id=message.chat.id,
                    datalast=str(datetime.utcfromtimestamp(int(message.date)).strftime('%Y-%m-%d %H:%M:%S')),
                    username=message.from_user.username,
                    subscription=message.text))
            con.commit()
            bot.send_message(message.chat.id, 'Подписка успешно оформленна')
            time.sleep(1)
            subscription_list_text_post(message)
        else:
            bot.send_message(message.chat.id, 'Данной странницы не существует на Reddit\n'
                                              'Пожалуйста проверьте правильность названия\n'
                                              'Возможной ошибкой может быть присуствие атрибута r/')


# отписка + проверка
def remove_subscription(message):
    # проверка на присутсвие данной подписки в списке
    bot.send_message(message.chat.id, 'Проверка на наличие данной страницы в подписках...')
    time.sleep(2)
    bot.delete_message(message.chat.id, message.message_id)
    if sub_exists_remove(message.text):
        time.sleep(1)
        # удаление подписки с БД
        cur = con.cursor()
        cur.execute("""DELETE from {table} WHERE subscription = \'{subscription}\' and id = {id}""".format(
            table=table,
            subscription=message.text,
            id=message.chat.id))
        con.commit()
        bot.send_message(message.chat.id, 'Вы успешно отписались')
        time.sleep(1)
        subscription_list_text_post(message)
    else:
        bot.send_message(message.chat.id, 'Данной подписки у вас не обнаруженно')


# сообщение о подписках пользователя
def subscription_list_text_post(message):
    subscription_list_text = ''
    cur = con.cursor()
    index = False
    cur.execute("""SELECT id, username, subscription from {table} WHERE subscription NOT IN ('')""".format(
        table=table
    ))
    subscription_list_array = cur.fetchall()
    for item in subscription_list_array:
        if item[0] == message.chat.id and item:
            subscription_list_text += '• ' + '<pre>' + item[2] + '</pre>' + '\n'
            index = True
    con.commit()
    if index:
        bot.send_message(message.chat.id, 'Текущие подписки:\n{text}'.format(text=subscription_list_text),
                         parse_mode='HTML', reply_markup=keyboard_start())
    else:
        bot.send_message(message.chat.id, 'Подписки отсуствуют', reply_markup=keyboard_start())


def keyboard_subscription(message):
    keyboard = types.InlineKeyboardMarkup()
    key_subscription_list = types.InlineKeyboardButton(text='Ваши подписки', callback_data='subscription_list')
    keyboard.add(key_subscription_list)
    key_subscription_add = types.InlineKeyboardButton(text='Добавить новую подписку',
                                                      callback_data='subscription_add')
    keyboard.add(key_subscription_add)
    key_subscription_remove = types.InlineKeyboardButton(text='Отменить подписку',
                                                         callback_data='subscription_remove')
    keyboard.add(key_subscription_remove)
    key_subreddit = types.InlineKeyboardButton(text='Reddit страницы', url='https://www.reddit.com/subreddits/')
    keyboard.add(key_subreddit)
    bot.send_message(message.chat.id, text='Управление подписками', reply_markup=keyboard)


def get_post(message):
    try:
        link = message.text
        # получения поста с Reddit через ссылку
        collection = reddit.subreddit('SUBREDDIT').collections(permalink=link)
        submission = reddit.submission(collection)
        submission.title_finaly = '<b>' + submission.title + '</b>'
        if not submission.url:
            if not submission.selftext:
                print('1_1')
                bot.send_message(message.chat.id,
                                 submission.title_finaly + '\n' + '#' + str(
                                     submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
            else:
                print('1_2')
                bot.send_message(message.chat.id,
                                 submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                                     submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
        elif is_url_image(submission.url) and submission.url[:17] == 'https://i.redd.it':
            if not submission.selftext:
                print('3_1')
                bot.send_photo(message.chat.id,
                               caption=submission.title_finaly + '\n' + '#' + str(
                                   submission.subreddit), photo=submission.url, parse_mode='HTML',
                               reply_markup=keyboard_start())
            else:
                print('3_2')
                bot.send_photo(message.chat.id,
                               caption=submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                                   submission.subreddit), photo=submission.url, parse_mode='HTML',
                               reply_markup=keyboard_start())
        elif submission.url[:5] == 'https':
            if not submission.selftext:
                print('2_1')
                bot.send_message(message.chat.id,
                                 submission.title_finaly + '\n\n' + submission.url + '\n' + '#' + str(
                                     submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
            else:
                print('2_2')
                bot.send_message(message.chat.id,
                                 submission.title_finaly + '\n\n' + submission.selftext + '\n\n' + submission.url + '\n' + '#' + str(
                                     submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
        else:
            if not submission.selftext:
                print('4_1')
                bot.send_message(message.chat.id, submission.title_finaly + '\n' '#' + str(
                    submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
            else:
                print('4_2')
                print('sfsfsf')
                bot.send_message(message.chat.id,
                                 submission.title_finaly + '\n\n' + submission.selftext + '\n' + '#' + str(
                                     submission.subreddit), parse_mode='HTML', reply_markup=keyboard_start())
    except IndexError:
        bot.send_message(message.chat.id, 'Такого поста не существует')


def sub_exists_add(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists


# проверка на наличие в списке
def sub_exists_remove(sub):
    cur = con.cursor()
    cur.execute("""SELECT id, username, subscription from {table}""".format(
        table=table))
    subscription_list_array = cur.fetchall()
    for item in subscription_list_array:
        if sub == item[2]:
            return True


# проверка, являеться ли ссылка картинкой
def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    time.sleep(.25)
    if r.headers["content-type"] in image_formats:
        return True
    return False


def log(message):
    print("\n ------")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. (id = {2}) \nТекст = {3}".format(message.from_user.first_name,
                                                                  message.from_user.last_name,
                                                                  str(message.from_user.id), message.text))


bot.polling(none_stop=True, interval=0)
