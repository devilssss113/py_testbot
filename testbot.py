# -*- coding: utf-8 -*-
import config
import telebot
import time
from telebot import types
import emoji
import random
import apiai, json
import re

bot = telebot.TeleBot(config.token)


@bot.message_handler(func=lambda message: message.entities is not None and message.chat.id == config.GROUP_ID)
def delete_links(message):
    for entity in message.entities:  # Пройдёмся по всем entities в поисках ссылок
        # url - обычная ссылка, text_link - ссылка, скрытая под текстом
        if entity.type in ["url", "text_link"]:
            # Мы можем не проверять chat.id, он проверяется ещё в хэндлере
            bot.send_message(message.chat.id, "Bad boy")
            bot.delete_message(message.chat.id, message.message_id)
        else:
            return

# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    pass

#  заменяемс аудио пользователя своей оберткой
@bot.message_handler(content_types=['document', 'audio'])
def handle_document_audio(message):
    keyboard = types.InlineKeyboardMarkup()

    text_label = ("<i>Прислал(а) </i>" + message.from_user.username)
    like_button = types.InlineKeyboardButton(text=emoji.emojize(':heart:', use_aliases=True), callback_data="test")
    dislike_button = types.InlineKeyboardButton(text=emoji.emojize(':broken_heart:', use_aliases=True), callback_data="test")
    keyboard.add(like_button,dislike_button)

    # keyboard = []
    # # for i, events in enumerate(Events):
    # #     if (events.gid == gid):
    # keyboard = keyboard + [[types.InlineKeyboardButton(events.etkinlik + u" 👍", callback_data=i),
    #           types.InlineKeyboardButton(events.etkinlik + u" 👎", callback_data=i + 100)]]
    # return types.InlineKeyboardMarkup(keyboard)

    bot.send_document(message.chat.id, message.audio.file_id, caption = text_label, reply_markup=keyboard, parse_mode="HTML")
    bot.delete_message(message.chat.id, message.message_id)


# Выдаём Read-only за определённые фразы
@bot.message_handler(func=lambda message: message.text is not None and message.chat.id == config.GROUP_ID)
def set_ro(message):
    if any(regex.findall(message.text) for regex in config.regexes):
        random_ban_message = lambda: random.choice(config.ban_message)
        bot.send_message(message.chat.id, random_ban_message(),reply_to_message_id=message.message_id)
    elif any(regex.findall(message.text) for regex in config.regexes_botname):
        messageWithoutBot = re.sub(config.regex_botname, repl='', string=message.text)
        request = apiai.ApiAI('9c9e550ee9194530812ae11fb0a22258').text_request()  # Токен API к Dialogflow
        request.lang = 'ru'  # На каком языке будет послан запрос
        request.session_id = 'Jailbot'  # ID Сессии диалога (нужно, чтобы потом учить бота)
        request.query = messageWithoutBot
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech']  # Разбираем JSON и вытаскиваем ответ
        # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
        if response:
            bot.send_message(message.chat.id, text=response, reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat_id, text='Я Вас не совсем понял!')

        # bot.send_message(message.chat.id, "Не упоминай мое имя, человек", reply_to_message_id=message.message_id)

        # bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time()+31)
#     @bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])
#     def handle_text_doc(message):

# отвечаем на хуйню
# @bot.message_handler(func=lambda message: message.text is not None and message.chat.id == config.GROUP_ID)
# def set_ro(message):
#     if any(regex.findall(message.text) for regex in config.regexes):
#
#         random_ban_message = lambda: random.choice(config.ban_message)

bot.polling(none_stop=True, interval=0)
# @bot.message_handler(func=lambda message: message.text and message.text.lower() in config.restricted_messages and message.chat.id == config.GROUP_ID)
# def set_ro(message):