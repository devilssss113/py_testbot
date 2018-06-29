# -*- coding: utf-8 -*-
import config
import Privat24
import weather
import time
import random
import apiai, json
import re
import logging
import telebot
import os
import datetime
import platform
from flask import Flask, request


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


global token
global GROUP_ID
if platform.uname().system == 'Windows':
    print("Using LOCAL settings")
    token = config.token_test
    GROUP_ID = config.group_id_test
else:
    print("Using DEPLOY settings")
    token = config.token_deploy
    GROUP_ID = config.group_id_deploy

bot = telebot.TeleBot(token)
server = Flask(__name__)


def get_admin_ids(bot, chat_id):
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def user_mute(message):
    random.seed(version=2)

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

    if message.from_user.username is None:
        pos_winner = message.from_user.first_name
    else:
        pos_winner = message.from_user.username

    if datetime.datetime.now().day > config.start_date[0].day:
        config.start_ban_value.clear()
        config.start_ban_value.append(0)
        config.winner.clear()
        config.winner.append(0)
        config.start_ban_value.append(0)
        config.start_ban_value.clear()
        config.start_ban_value.append(0)
        config.start_date.clear()
        config.start_date.append(datetime.datetime.now())
        if int(ban_value) > config.start_ban_value[0]:
            config.winner.clear()
            config.winner.append(pos_winner)
            config.start_ban_value.clear()
            config.start_ban_value.append(ban_value)
    elif datetime.datetime.now().day == config.start_date[0].day:
        if int(ban_value) > config.start_ban_value[0]:
            config.winner.clear()
            config.winner.append(pos_winner)
            config.start_ban_value.clear()
            config.start_ban_value.append(ban_value)

    bot.send_message(message.chat.id, text=('Сегодняшний рекорд равен: ' + str(config.start_ban_value[0]) + ". Наш победитель - " + str(config.winner[0])))


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


def length_duel_namer(length):
    if length < 5:
        length_name = "прыщик"
    elif 4 < length < 10:
        length_name = "болтик"
    elif 9 < length < 15:
        length_name = "писюрик"
    elif 14 < length < 20:
        length_name = "агрегат"
    elif 19 < length < 25:
        length_name = "покоритель сердец"
    elif 24 < length < 31:
        length_name = "черный властелин"
    elif length > 31:
        length_name = "разрыватель"
    return length_name


def length_duel(m):
    opp1 = m.from_user
    opp2 = m.reply_to_message.from_user
    bot_opp = bot.get_me().id

    if opp1.username is None:
        opp1_name = opp1.first_name
    else:
        opp1_name = opp1.username

    if opp2.username is None:
        opp2_name = opp2.first_name
    else:
        opp2_name = opp2.username

    opp1length = random.randrange(1, 30, 1)

    if opp2.id == bot_opp:
        opp2length = random.randrange(29, 200, 1)
    elif opp2.username == "Devilssss113":
        opp2length = random.randrange(29, 40, 1)
    elif opp2.username == "Varvara123456":
        opp2length = random.randrange(29, 40, 1)
    else:
        opp2length = random.randrange(1, 30, 1)

    bot.send_message(m.chat.id, text="Объявлена дуэль между " + str(opp1_name) + " и " + str(opp2_name))
    bot.send_message(m.chat.id, text="У " + opp1_name + " " + str(opp1length) + " сантиметровый  " + length_duel_namer(opp1length) +
                                     ". У " + opp2_name + " " + str(opp2length) + " саниметровый " + length_duel_namer(opp2length) +
                                     ". Выводы делайте сами")





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
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Я здесь')
    pass


@bot.message_handler(commands=['weather'])
def weather_command(message):
    icon_url, temp_final = weather.get_weather()
    print(icon_url)
    bot.send_message(message.chat.id, text=temp_final)
    pass


@bot.message_handler(commands=['curdata'])
def handle_exdate(message):
    if any(regex.findall(message.text) for regex in config.regex_data):
        m = re.search(r'(1|2|3|)[0-9]\.(0|1|)[0-9]\.20(0|1|2)[0-9]', message.text)
        if m:
            data = m.group(0)
            print(data)
            bot.send_message(message.chat.id, Privat24.exchange_on_date(data))
    else:
        bot.send_message(message.chat.id,'Введи дату')
    pass


@bot.message_handler(commands=['currency'])
def handle_excur(message):
    bot.send_message(message.chat.id, Privat24.exchange_current())
    pass


@bot.message_handler(commands=['shodka'])
def handle_shodka(message):
    if message.from_user.id in get_admin_ids(bot, message.chat.id):
        if message.reply_to_message.text != "0":
            config.shodka_message.clear()
            config.shodka_message.append(message.reply_to_message)
            bot.send_message(message.chat.id, message.text, reply_to_message_id=message.reply_to_message)
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, disable_notification=False)
        else:
            config.shodka_message.clear()
            bot.send_message(message.chat.id, "Информация о сходке аннулирована", reply_to_message_id=message.reply_to_message)
    else:
        if config.shodka_message[0] != 0:
            bot.send_message(message.chat.id, "Вот", reply_to_message_id=config.shodka_message[0].message_id)
        else:
            bot.send_message(message.chat.id, "Чёт я хз")
    pass


@bot.message_handler(commands=['duel'])
def handle_duel(message):
    if message.reply_to_message is not None:
        length_duel(message)
    elif message.reply_to_message is None:
        bot.send_message(message.chat.id, text="Выбери оппонента. Напиши в ответ своему обидчику слово Дуэль")
    pass

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, 'Версия ' + config.bot_version + '. Бан за мат выдается методом рулетки. Отвечаю лишь на сообщения со словом Бот или'
                                      ' ответы на мои сообщения.'
                                      ' Команды бана (Фас, Асталависта) доступны лишь администраторам. Присутвуют дуэли.'
                                      'Полный список доступных команд писать откровенно лень)')
    pass

@bot.message_handler(commands=['winner'])
def handle_winner(message):
    bot.send_message(message.chat.id, text=(
                'Сегодняшний рекорд равен: ' + str(config.start_ban_value[0]) + ". Наш победитель - " + str(
            config.winner[0])))
    pass


# Обработчик новых людей в чате.
@bot.message_handler(func=lambda message: True, content_types=['new_chat_members'])
def handle_welcome(message):
    bot.send_message(message.chat.id, text='Приветствую в нашем чате, ' + message.from_user.first_name + '!')

# Обработчик ушедших людей в чате.
@bot.message_handler(func=lambda message: True, content_types=['left_chat_member'])
def handle_bye(message):
    bot.send_message(message.chat.id, text='От нас уходят лишь вперед ногами, ' + message.from_user.first_name + '!')

@bot.message_handler(func=lambda message: message.text is not None and message.chat.id in GROUP_ID)
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
    #duel invite
    elif any(regex.findall(message.text) for regex in config.length_duel_invite):
        if message.reply_to_message is not None:
            length_duel(message)
        elif message.reply_to_message is None:
            bot.send_message(message.chat.id, text="Выбери оппонента. Напиши в ответ своему обидчику слово Дуэль")

    #bot answer on keyword in chat
    elif any(regex.findall(message.text) for regex in config.regexes_botname):
            bot_ai_answer(message, 0)

    #bot answer on reply
    elif message.reply_to_message is not None:
        if message.reply_to_message.from_user.id == bot.get_me().id:
            bot_ai_answer(message, 1)

@bot.edited_message_handler(func=lambda message: message.text is not None and message.chat.id in GROUP_ID)
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
    @server.route('/' + token, methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://jailbot20.herokuapp.com/' + token)
        return "!", 200

    server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
else:
    bot.polling(none_stop=True, interval=0)