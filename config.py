import re

token = "528720694:AAH1z9G0kGn3XhArUCbJPzDgLohw08bWCo8"
GROUP_ID = -1001223980001
regexes = [
        # your regexes here
        re.compile(r'\w+Хренов(аст|)(еньк|)(ы(й|х|е|м)|о(е|го|й|му)|ая|ий)', re.I),
        #    re.compile(...),
        #    re.compile(...),
        #    re.compile(...),
    ]

#Хренов(аст|)(еньк|)(ы(й|х|е|м)|о(е|го|й|му)|ая|ий)