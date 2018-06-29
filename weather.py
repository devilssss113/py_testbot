import requests


def get_weather():
    s_city = "Mykolaiv"
    city_id = 700569
    appid = "c5c028337d94e8f3003fb9b42caaaa41"
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                     params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()

        weather_disc = data['weather'][0]['description']
        temp_min = int(round(data['main']['temp_min']))
        temp_max = int(round(data['main']['temp_max']))

        str_temp_min = add_plus(temp_min)
        str_temp_max = add_plus(temp_max)

        icon = (data['weather'][0]['icon'])
        icon_url = 'http://openweathermap.org/img/w/' + icon + '.png'

        temp_final = (weather_disc.title() + '\n' + str_temp_min + "..." + str_temp_max)
        return icon_url, temp_final

    except Exception as e:
        print("Exception (weather):", e)




def add_plus(temp):
    if temp >= 0:
        temp_plus = ('+' + str(temp))
        return temp_plus
    else:
        return temp


get_weather()