# -*- coding: utf-8 -*-
import config
import time
import random
import apiai, json
import re
import logging
from mwt import MWT
import telebot
import os
import datetime
from flask import Flask, request

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(config.token)
server = Flask(__name__)


# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, 'Я здесь')
    pass


@MWT(timeout=10*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def user_mute(message, victim_id):
    rand_min = 31;
    rand_max = 600;
    random.seed(version=2)
    winner_value = 0
    start_date = datetime.datetime.now()

    ban_value = random.randrange(int(rand_min), int(rand_max), 1)
    if ban_value > rand_max / 2:
        #('ban is more randMax/2')
        if random.randrange(1, 100, 1) < 60:
            #('ban is set to half')
            ban_value = random.randrange(int(rand_min), int(rand_max / 2), 1)

    if ban_value > rand_max / 3:
        #('ban is more randMax/3')
        if random.randrange(1, 100, 1) < 60:
            #('ban is set to 1/3')
            ban_value = random.randrange(int(rand_min), int(rand_max / 3), 1)

    message_to_victim = ('Ты выиграл(а) ' + str(ban_value) + "секунд мута!!!")
    bot.send_message(message.chat.id, message_to_victim, reply_to_message_id=message.message_id)
    bot.restrict_chat_member(message.chat.id, victim_id, until_date=datetime.datetime.now() + ban_value)

    if datetime.datetime.now().day > start_date.day:
        winner_value = 0
        if int(ban_value) > winner_value:
            winner_value = ban_value;
            bot.send_message(message.chat.id,text=('Сегодняшний рекорд равен: ' + str(winner_value)))
            start_date = datetime.datetime.now()
    elif datetime.datetime.now().day == start_date.day:
        if int(ban_value) > winner_value:
            winner_value = ban_value;
            bot.send_message(message.chat.id, text=('Сегодняшний рекорд равен: ' + str(winner_value)))

# Выдаём Read-only за определённые фразы
@bot.message_handler(func=lambda message: message.text is not None and message.chat.id in config.GROUP_ID)
def set_ro(message):
    jailbot = bot.get_me()
    jailbot_id = jailbot.id

    current_user_id = message.from_user.id
    current_group_id = message.chat.id
    current_group_admins = get_admin_ids(bot, current_group_id)

    if any(regex.findall(message.text) for regex in config.regexes):
        random_ban_message = lambda: random.choice(config.ban_message)
        random_ban_admin_message = lambda: random.choice(config.ban_message_admin)
        if (current_user_id in current_group_admins):
            bot.send_message(message.chat.id, random_ban_admin_message(), reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, random_ban_message(),reply_to_message_id=message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 31)
    elif any(regex.match(message.text) for regex in config.attack_commands):
        if (current_user_id in current_group_admins and message.reply_to_message is not None):
            victim_id = message.reply_to_message.from_user.id
            random_ban_message_on_command = lambda: random.choice(config.ban_message_on_command)
            # bot.send_message(message.chat.id, random_ban_message_on_command(), reply_to_message_id=message.reply_to_message.message_id)
            user_mute(message, victim_id) #bot.restrict_chat_member(message.chat.id, victim_id, until_date=time.time() + 31)

        else:
            bot.send_message(message.chat.id, 'Нет.', reply_to_message_id=message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 31)
    elif any(regex.findall(message.text) for regex in config.regexes_botname):
        messageWithoutBot = re.sub(config.regex_botname, repl='', string=message.text)
        request = apiai.ApiAI(config.apiai_token).text_request()  # Токен API к Dialogflow
        request.lang = 'ru'  # На каком языке будет послан запрос
        request.session_id = 'Jailbot'  # ID Сессии диалога (нужно, чтобы потом учить бота)
        request.query = messageWithoutBot
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech']  # Разбираем JSON и вытаскиваем ответ
        # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
        if response:
            bot.send_message(message.chat.id, text=response, reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, text='Выше моего понимания!', reply_to_message_id=message.message_id)
    elif message.reply_to_message is not None:
        if str(message.reply_to_message.from_user.id) == str(jailbot_id):
            request = apiai.ApiAI(config.apiai_token).text_request()  # Токен API к Dialogflow
            request.lang = 'ru'  # На каком языке будет послан запрос
            request.session_id = 'Jailbot'  # ID Сессии диалога (нужно, чтобы потом учить бота)
            request.query = message.text
            responseJson = json.loads(request.getresponse().read().decode('utf-8'))
            response = responseJson['result']['fulfillment']['speech']  # Разбираем JSON и вытаскиваем ответ
            # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
            if response:
                bot.send_message(message.chat.id, text=response, reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, text='Выше моего понимания!', reply_to_message_id=message.message_id)


@bot.edited_message_handler(func=lambda message: message.text is not None and message.chat.id in config.GROUP_ID)
def set_ro_by_command(message):
    current_user_id = message.from_user.id
    current_group_id = message.chat.id
    current_group_admins = get_admin_ids(bot, current_group_id)
    random_ban_message = lambda: random.choice(config.ban_message)
    bot.send_message(message.chat.id, "got it", reply_to_message_id=message.message.id)
    if any(regex.findall(message.text) for regex in config.attack_commands):
        bot.send_message(message.chat.id, "Check it", reply_to_message_id=message.message.id)
        if current_user_id in current_group_admins:
            random_ban_message_on_command = lambda: random.choice(config.ban_message_on_command)
            bot.send_message(message.chat.id, random_ban_message_on_command(), reply_to_message_id=message.reply_to_message)
        else:
            user_mute(message, message.from_user.id)
            # bot.send_message(message.chat.id, random_ban_message(), reply_to_message_id=message.message_id)
            # bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 31)


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