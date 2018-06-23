# -*- coding: utf-8 -*-
import config
import telebot
import time
from telebot import types
import emoji
import random
import apiai, json
import re
from mwt import MWT

bot = telebot.TeleBot(config.token)


# @bot.message_handler(func=lambda message: message.entities is not None)
# def delete_links(message):
#     for entity in message.entities:  # Пройдёмся по всем entities в поисках ссылок
#         # url - обычная ссылка, text_link - ссылка, скрытая под текстом
#         if entity.type in ["url", "text_link"]:
#             # Мы можем не проверять chat.id, он проверяется ещё в хэндлере
#             bot.send_message(message.chat.id, "Bad boy")
#             bot.delete_message(message.chat.id, message.message_id)
#         else:
#             return

# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    pass

@MWT(timeout=1*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

#  заменяемс аудио пользователя своей оберткой
# @bot.message_handler(content_types=['document', 'audio'])
# def handle_document_audio(message):
#     keyboard = types.InlineKeyboardMarkup()
#
#     text_label = ("<i>Прислал(а) </i>" + message.from_user.username)
#     like_button = types.InlineKeyboardButton(text=emoji.emojize(':heart:', use_aliases=True), callback_data='like')
#     dislike_button = types.InlineKeyboardButton(text=emoji.emojize(':broken_heart:', use_aliases=True), callback_data='dislike')
#     keyboard.add(like_button, dislike_button)
#     # keyboard = []
#     # # for i, events in enumerate(Events):
#     # #     if (events.gid == gid):
#     # keyboard = keyboard + [[types.InlineKeyboardButton(events.etkinlik + u" 👍", callback_data=i),
#     #           types.InlineKeyboardButton(events.etkinlik + u" 👎", callback_data=i + 100)]]
#     # return types.InlineKeyboardMarkup(keyboard)
#
#     bot.send_document(message.chat.id, message.audio.file_id, caption = text_label, reply_markup=keyboard, parse_mode="HTML")
#     bot.delete_message(message.chat.id, message.message_id)

# @bot.callback_query_handler(func=lambda call: True)
# def query_handler(call):
#     if call.data == 'like':
#         bot.answer_callback_query(callback_query_id=call.id, text='Ты поставил лайк!', show_alert=True)
#     # bot.editMessageReplyMarkup

# Выдаём Read-only за определённые фразы
@bot.message_handler(func=lambda message: message.text is not None and message.chat.id in config.GROUP_ID)
def set_ro(message):
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
    elif any(regex.match(message.text) for regex in config.attack_commands): #--------------------------------------------------------------------------
        if (current_user_id in current_group_admins and message.reply_to_message is not None):
            victim_id = message.reply_to_message.from_user.id
            random_ban_message_on_command = lambda: random.choice(config.ban_message_on_command)
            bot.send_message(message.chat.id, random_ban_message_on_command(), reply_to_message_id=message.reply_to_message.message_id)
            bot.restrict_chat_member(message.chat.id, victim_id, until_date=time.time() + 31)
        else:
            bot.send_message(message.chat.id, 'Нет.', reply_to_message_id=message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 31)
    elif any(regex.findall(message.text) for regex in config.regexes_botname):#---------------------------------------------------------------------------
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

@bot.edited_message_handler(func=lambda message: message.text is not None and message.chat.id in config.GROUP_ID)
def set_ro_by_command(message):
    current_user_id = message.from_user.id
    current_group_id = message.chat.id
    current_group_admins = get_admin_ids(bot, current_group_id)
    bot.send_message(message.chat.id, "got it", reply_to_message_id=message.message.id)

    if any(regex.findall(message.text) for regex in config.attack_commands):
        bot.send_message(message.chat.id, "Check it", reply_to_message_id=message.message.id)
        if (current_user_id in current_group_admins):
            random_ban_message_on_command = lambda: random.choice(config.ban_message_on_command)
            bot.send_message(message.chat.id, random_ban_message_on_command(), reply_to_message_id=message.reply_to_message)
            #bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 31)
        else:
            bot.send_message(message.chat.id, random_ban_message(), reply_to_message_id=message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 31)

bot.polling(none_stop=True, interval=0)
