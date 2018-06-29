# -*- coding: utf-8 -*-
import config
import time
import random
import apiai, json
import re
import logging
import telebot
import os
import datetime
from flask import Flask, request

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(config.token)
server = Flask(__name__)
config.start_date = datetime.datetime.now()



def get_admin_ids(bot, chat_id):
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]



def user_mute(message):

    random.seed(version=2)
    winner_value = 0


    ban_value = random.randrange(int(config.rand_min), int(config.rand_max), 1)
    if ban_value > config.rand_max / 2:
        if random.randrange(1, 100, 1) < 60:
            ban_value = random.randrange(int(config.rand_min), int(config.rand_max / 2), 1)

    if ban_value > config.rand_max / 3:
        if random.randrange(1, 100, 1) < 60:
            ban_value = random.randrange(int(config.rand_min), int(config.rand_max / 3), 1)

    message_to_victim = (config.random_ban_message() + 'Ты выиграл(а) ' + str(ban_value) + " секунд мута!")
    bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date= time.time() + ban_value)
    bot.send_message(message.chat.id, message_to_victim, reply_to_message_id=message.message_id)

    if datetime.datetime.now().day > config.start_date.day:
        winner_value = 0
        if int(ban_value) > winner_value:
            winner_value = ban_value
            bot.send_message(message.chat.id, text=('Сегодняшний рекорд равен: ' + str(winner_value)))
            config.start_date = datetime.datetime.now()
    elif datetime.datetime.now().day == config.start_date.day:
        if int(ban_value) > winner_value:
            winner_value = ban_value;
            bot.send_message(message.chat.id, text=('Сегодняшний рекорд равен: ' + str(winner_value)))


def bot_ai_answer(message, reply):
        if reply==1:
            message_to_ai = message.text
        elif reply==0:
            message_to_ai = re.sub(config.regex_botname, repl='', string=message.text)

        request = apiai.ApiAI(config.apiai_token).text_request()  # Токен API к Dialogflow
        request.lang = 'ru'  # На каком языке будет послан запрос
        request.session_id = 'Jailbot'  # ID Сессии диалога (нужно, чтобы потом учить бота)
        request.query = message_to_ai
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech']  # Разбираем JSON и вытаскиваем ответ
        # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
        if response:
            bot.send_message(message.chat.id, text=response, reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, text='Не хочу говорить об этом', reply_to_message_id=message.message_id)


#   .----------------.  .----------------.  .-----------------. .----------------.  .----------------.  .----------------.  .----------------.  .----------------.
#  | .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
#  | |  ____  ____  | || |      __      | || | ____  _____  | || |  ________    | || |   _____      | || |  _________   | || |  _______     | || |    _______   | |
#  | | |_   ||   _| | || |     /  \     | || ||_   \|_   _| | || | |_   ___ `.  | || |  |_   _|     | || | |_   ___  |  | || | |_   __ \    | || |   /  ___  |  | |
#  | |   | |__| |   | || |    / /\ \    | || |  |   \ | |   | || |   | |   `. \ | || |    | |       | || |   | |_  \_|  | || |   | |__) |   | || |  |  (__ \_|  | |
#  | |   |  __  |   | || |   / ____ \   | || |  | |\ \| |   | || |   | |    | | | || |    | |   _   | || |   |  _|  _   | || |   |  __ /    | || |   '.___`-.   | |
#  | |  _| |  | |_  | || | _/ /    \ \_ | || | _| |_\   |_  | || |  _| |___.' / | || |   _| |__/ |  | || |  _| |___/ |  | || |  _| |  \ \_  | || |  |`\____) |  | |
#  | | |____||____| | || ||____|  |____|| || ||_____|\____| | || | |________.'  | || |  |________|  | || | |_________|  | || | |____| |___| | || |  |_______.'  | |
#  | |              | || |              | || |              | || |              | || |              | || |              | || |              | || |              | |
#  | '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
#   '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'


# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, 'Я здесь')
    bot.send_message(message.chat.id, config.bot_version)
    pass


# Обработчик новых людей в чате.
@bot.message_handler(func=lambda message: True, content_types=['new_chat_member'])
def handle_welcome(message):
    bot.send_message(message.chat.id, text='Приветствую в нашем чате, ' + message.message.from_user.username + '!', reply_to_message_id=message.message_id)


# Обработчик ушедших людей в чате.
@bot.message_handler(func=lambda message: True, content_types=['left_chat_member'])
def handle_bye(message):
    bot.send_message(message.chat.id, text='Нам будет тебя не хватать, ' + message.message.from_user.username + '!')


@bot.message_handler(func=lambda message: message.text is not None and message.chat.id in config.GROUP_ID)
def set_ro(message):

    if any(regex.findall(message.text) for regex in config.regexes):
        if (message.from_user.id in get_admin_ids(bot, message.chat.id)):
            #if admin says bad word
            bot.send_message(message.chat.id, config.random_ban_admin_message(), reply_to_message_id=message.message_id)
        else:
            #if mortal user says bad word
            user_mute(message)

    elif any(regex.match(message.text) for regex in config.attack_commands):
        if (message.from_user.id in get_admin_ids(bot, message.chat.id) and message.reply_to_message is not None):
            bot.send_message(message.chat.id, config.random_ban_message_on_command(), reply_to_message_id=message.reply_to_message.message_id)
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=time.time() + config.ban_standart)
        else:
            bot.send_message(message.chat.id, 'Нет.', reply_to_message_id=message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + config.ban_standart)

    elif any(regex.match(message.text) for regex in config.attack_commands_super):
        if (message.from_user.id in get_admin_ids(bot, message.chat.id) and message.reply_to_message is not None):
            bot.send_message(message.chat.id, "Бейби", reply_to_message_id=message.reply_to_message.message_id)
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=time.time() + config.ban_super)
            terminator = open('terminator.jpg', 'rb')
            bot.send_photo(message.chat.id, terminator)
        else:
            bot.send_message(message.chat.id, 'Нет.', reply_to_message_id=message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + config.ban_standart)
    #bot answer on keyword in chat
    elif any(regex.findall(message.text) for regex in config.regexes_botname):
            bot_ai_answer(message, 0)

    #bot answer on reply
    elif message.reply_to_message is not None:
        if message.reply_to_message.from_user.id == bot.get_me().id:
            bot_ai_answer(message, 1)

@bot.edited_message_handler(func=lambda message: message.text is not None and message.chat.id in config.GROUP_ID)
def set_ro_edited(message):
    if any(regex.findall(message.text) for regex in config.regexes):
        if message.from_user.id in get_admin_ids(bot, message.chat.id):
            bot.send_message(message.chat.id, config.random_ban_message_on_command(), reply_to_message_id=message.reply_to_message)
        else:
            user_mute(message)


#   .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.
#  | .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
#  | |    _______   | || |  _________   | || |      __      | || |  _______     | || |  _________   | || |  _________   | || |  _______     | |
#  | |   /  ___  |  | || | |  _   _  |  | || |     /  \     | || | |_   __ \    | || | |  _   _  |  | || | |_   ___  |  | || | |_   __ \    | |
#  | |  |  (__ \_|  | || | |_/ | | \_|  | || |    / /\ \    | || |   | |__) |   | || | |_/ | | \_|  | || |   | |_  \_|  | || |   | |__) |   | |
#  | |   '.___`-.   | || |     | |      | || |   / ____ \   | || |   |  __ /    | || |     | |      | || |   |  _|  _   | || |   |  __ /    | |
#  | |  |`\____) |  | || |    _| |_     | || | _/ /    \ \_ | || |  _| |  \ \_  | || |    _| |_     | || |  _| |___/ |  | || |  _| |  \ \_  | |
#  | |  |_______.'  | || |   |_____|    | || ||____|  |____|| || | |____| |___| | || |   |_____|    | || | |_________|  | || | |____| |___| | |
#  | |              | || |              | || |              | || |              | || |              | || |              | || |              | |
#  | '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
#   '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'


if config.deploy == 1 :
    @server.route('/' + config.token, methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://jailbot20.herokuapp.com/' + config.token)
        return "!", 200

    server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
else:
    bot.polling(none_stop=True, interval=0)