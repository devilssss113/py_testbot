import datetime
from datetime import datetime
import re
import random

bot_version = "2.2.0"

token_deploy = "528720694:AAH1z9G0kGn3XhArUCbJPzDgLohw08bWCo8" #jailbot20
token_test = "568670760:AAFnMV3G0ipq7TnWhezxTLzpT49N5z6iHXM" #jaibot M
apiai_token = "9c9e550ee9194530812ae11fb0a22258"


group_id_deploy = [
    -1001194512914, #Go Guliat
    -1001261092760 #music
]

group_id_test = [
    -1001223980001, #test
]

ban_standart = 60*3
ban_super = 60*60*24
rand_min = 31
rand_max = 600
start_date = [datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')]
silent_mode = 1

shodka_message = [0]
start_ban_value = [0]
winner = [0]

random_ban_message_on_command = lambda: random.choice(ban_message_on_command)
random_ban_admin_message = lambda: random.choice(ban_message_admin)
random_ban_message = lambda: random.choice(ban_message)

regexes = [
    # your regexes here
    # re.compile(r'(хуев|хуёв)(аст|)(еньк|)(ы(й|х|е|м)|о(е|го|й|му|)|ая|ий)', re.I),
    re.compile(r'(^бля| бля)', re.I),
    # re.compile(r'(^пздц| пздц)', re.I),
    re.compile(r'(^нахой| нахой)', re.I),
    re.compile(r'Элджей', re.I),
    re.compile(r'(за|по|на|до|у|недо| |^)(бляд|блед|блид)(ищ|ун|ин|ств|у|овал|)(ю|ь|а|ы|ой|у|и|е|й|ей|ю|ем|я|о|а|у|ом|ам|ов|ы|ами|ий|ый|ого|ому|им|их|ить|ю|)', re.I),
    re.compile(r'(пидор|пидр|пидoр|пидaр)(ск|астическ|ил|ильск|)(а|у|ом|ок|ка|ки|кам|ам|ов|ы|ами|ий|ый|ого|ому|им|их|)', re.I),
    re.compile(r'(при|о|а|пре|по|на|не|ни| |^)ху(есос|еплет|ев|ёв|ел|йн|ет|й|я|ю|и|ен)(аст|)(л|)(чик|еньк|ат|)(ани|)(я| ая|ый|ой|ому|о|а|ы|ой|я|и|е|й|ей|ю|ем|ый|ого|ому|ом|)', re.I),
    re.compile(r'(при|у|пре|за| |^)(пи|пе|пы)(зд|сд)(яч|)(о|ю|ён|ен|ищ|ятин|ат|ел|ил|ец|)(к|)(а|ы|ой|у|и|е|й|ей|ю|ем|я|о|а|у|ом|ам|ов|ы|ами|ий|ый|ого|ому|им|их|ить|ю|)', re.I), #пизда
    re.compile(r'(за|по|на|до|у|недо|вы| |^)еб(а|)(ыва|уч|лив|нут|н|нн|нуть|ет|й|ть|ись)(ы(й|х|е|м)|и(я|и|е|го|й|му)|ая|ий|ся|юсь|ать|ал|ала|у|ем|ут|ет|ешь|)', re.I), #ебать
    re.compile(r'(за|по|на|до|у|недо| |^)(еб|ёб|иб)(ал|альц|лышк|лан|ен|анат|л|у|ут|ок|к)(я|ей|ям|ях|е|а|и|ут|у|ет|о|а|у|ом|)(и|)', re.I),
    #    re.compile(...),
]
regexes_botname = [re.compile((r'(^бот| бот)(ом|у|ов|а|ы|ик|)'), re.I)]
regex_data = [re.compile(r'(1|2|3|)[0-9]\.(0|1|)[0-9]\.20(0|1|2)[0-9]', re.I)]
regex_botname = re.compile((r'(^бот| бот)(ом|у|ов|а|ы|ик|)'), re.I)

attack_commands = [re.compile(r'(^Фас| Фас)', re.I)]

attack_commands_super = [re.compile(r'(^Асталависта| Асталависта)', re.I)]

length_duel_invite = [re.compile(r'(^Дуэль| Дуэль|^Дуель| Дуель)', re.I)]

ban_message_on_command = ['Рррррр', 'Не зли хозяина','Exterminate!!!','Тебя заказали.','Ничего личного, просто бизнес']

ban_message = ['Не сегодня.', 'Зря ты это сказал.', 'Лучше б я мечтал об электроовце, а не читал это.',
               'чики-брики и в бан.', 'Я в твоем возрасте такие слова не знал.', 'Лучше тебе отдохнуть.',
               'Работа не волк, а слово не воробей.', 'Подумай еще раз.', 'Ты мне не нравишься.',
               'Зачем ты это выдавил из себя?', 'Тебе так говорить не нужно на самом деле.', 'Помолчать всегда лучше.',
               'А потом рот с мылом мыть.', 'Молчание = золото, золотой ты мой.',
               'Всё равно все тлен.','Не в мою смену.','Здесь я шериф.']

ban_message_admin = ['Плохой администатор!', 'Фу-фу-фу', 'Ты должен быть примером!', 'Вот не был бы ты админом...',
                     'Прощаю', 'Я этого не видел']
