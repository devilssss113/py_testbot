# -*- coding: utf-8 -*-
import config
import telebot
import time
import random
import apiai, json
import re
from mwt import MWT

bot = telebot.TeleBot(config.token)


# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    pass


@MWT(timeout=1*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


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
            bot.send_message(message.chat.id, random_ban_message_on_command(), reply_to_message_id=message.reply_to_message.message_id)
            bot.restrict_chat_member(message.chat.id, victim_id, until_date=time.time() + 31)
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
            bot.send_message(message.chat.id, random_ban_message(), reply_to_message_id=message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 31)


bot.polling(none_stop=True, interval=0)
