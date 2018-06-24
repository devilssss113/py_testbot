# -*- coding: utf-8 -*-
import config
import time
import random
import apiai, json
import re
import logging
import ssl

from aiohttp import web
from mwt import MWT
import telebot

WEBHOOK_HOST = ("https://jailbot20.herokuapp.com/" + config.token)
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
#
# WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(config.token)


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(config.token)

app = web.Application()

# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)


# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    pass


@MWT(timeout=10*60)
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


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
