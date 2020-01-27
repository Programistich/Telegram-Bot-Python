import telebot
import random
from telebot import types
import assets
import time

# id_admin - id telegram account
# parse_mode = HTML
# con - connect db
# table_phrase = table in db with phrase
# table_user = table in db with user
# start_ru


bot = telebot.TeleBot(assets.token)
cur = assets.con.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет\nС помощью этого бота вы можете получать рандомные фразы с известной '
                                      'всем '
                                      'жвачки Love Is', reply_markup=keyboard_start_ru())


@bot.message_handler(content_types=['text'])
def user_message(message):
    if message.text == "Рандомная фраза":
        cur.execute("""SELECT id, rus_phrase FROM {table} """.format(table=assets.table_phrase))
        array = cur.fetchall()
        assets.con.commit()
        random_phrase_id = random.randint(1, 50)
        for item in array:
            if item[0] == random_phrase_id:
                text = assets.start_ru + '\n' + '\n' + '...' + item[1]
                bot.send_message(message.chat.id, text, reply_markup=keyboard_start_ru(), parse_mode=assets.parse_mode)
                cur.execute(
                    'INSERT INTO {table} (id, phrase) VALUES ({id}, \'{phrase}\');'.format(table=assets.table_user,
                                                                                           id=message.chat.id,
                                                                                           phrase=random_phrase_id))
                assets.con.commit()
    if message.text[:6] == '/write' and message.chat.id == assets.id_admin:
        cur.execute("""SELECT DISTINCT id FROM {table} """.format(table=assets.table_user))
        array = cur.fetchall()
        assets.con.commit()
        for item in array:
            print(item[0])
            bot.send_message(item[0], message.text[6:], parse_mode=assets.parse_mode)

    if message.text == '/admin' and message.chat.id == assets.id_admin:
        cur.execute("""SELECT COUNT(id) FROM {table} """.format(table=assets.table_user))
        array_1 = cur.fetchall()
        cur.execute("""SELECT COUNT(DISTINCT id) FROM {table}""".format(table=assets.table_user))
        array_2 = cur.fetchall()
        assets.con.commit()
        for item_1 in array_1:
            for item_2 in array_2:
                text = 'Количевство запросов: ' + str(item_1[0]) + '\n' + 'Количевство пользователей: ' + str(item_2[0])
                bot.send_message(assets.id_admin, text, parse_mode=assets.parse_mode)


def keyboard_start_ru():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phrase = types.KeyboardButton(text="Рандомная фраза")
    keyboard.add(button_phrase)
    return keyboard


bot.polling(none_stop=True)
