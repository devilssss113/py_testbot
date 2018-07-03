import requests
import re

def exchange_current():
    res = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=3")
    if not bool(re.match(r"<Response.*", str(res))):
        print(res)
        data = res.json()
        print(data)

        if str(data[0]['base_ccy']) != 'BTC':
            exchange = str(data[0]['ccy']) + " | " + str(data[0]['buy']) + " | " + str(data[0]['sale']) + '\n' + \
                       str(data[1]['ccy']) + " | " + str(data[1]['buy']) + " | " + str(data[1]['sale']) + '\n' + \
                       str(data[2]['ccy']) + " | " + str(data[2]['buy']) + " | " + str(data[2]['sale'])
            print(exchange)

        else:
            exchange = 'На сегодня нет курсов валют'
        return exchange
    else:
        exchange = 'Приват не отвечает'
        return exchange

def exchange_on_date (date):
    res = requests.get("https://api.privatbank.ua/p24api/exchange_rates?json",
                     params={'date': date})
    if not bool(re.match(r"<Response.*", str(res))):
        print(res)
        data = res.json()
        print(data)

        if len(data['exchangeRate']) > 0:
            exchange = str(data['exchangeRate'][13]['currency']) + " | " + str(data['exchangeRate'][13]['saleRateNB'])\
                   + " | " + str(data['exchangeRate'][13]['purchaseRateNB']) + '\n' + \
                   str(data['exchangeRate'][15]['currency']) + " | " + str(data['exchangeRate'][15]['saleRateNB'])\
                   + " | " + str(data['exchangeRate'][15]['purchaseRateNB']) + '\n' + \
                   str(data['exchangeRate'][17]['currency']) + " | " + str(data['exchangeRate'][17]['saleRateNB'])\
                   + " | " + str(data['exchangeRate'][17]['purchaseRateNB'])

        else:
            exchange = 'На эту дату нет курсов валют'
        return exchange
    else:
        exchange = 'Приват не отвечает'
        return exchange


print(exchange_current())
print(exchange_on_date('24.12.2014'))