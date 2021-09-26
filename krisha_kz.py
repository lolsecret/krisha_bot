import csv
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HOST = 'https://krisha.kz'
URL = 'https://krisha.kz/arenda/kvartiry/almaty/?das[live.rooms]=1&das[rent.period]=2'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
}
last_page = 1
img_not_found = 'https://previews.123rf.com/images/kaymosk/kaymosk1804/kaymosk180400005/99776312-error-404-page-not-found-error-with-glitch-effect-on-screen-vector-illustration-for-your-design.jpg'

def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def get_content(html):
    soup = BeautifulSoup(html, features="html.parser")
    items = soup.find_all('div', class_='a-card__inc')
    houses = []
    for item in items:
        img = item.find('picture', class_='is-moderated')
        houses.append({
            'title': item.find('a', class_='a-card__title').get_text(),
            'subtitle': item.find('div', class_='a-card__subtitle').get_text(strip=True),
            'preview': item.find('div', class_='a-card__text-preview').get_text(strip=True),
            'owner': item.find('div', class_='owners__label').get_text(strip=True),
            'created_at': ''.join([it.get_text(strip=True) for it in item.find_all('div', class_='card-stats__item')][1:2]),
            'link': HOST + item.find('a', class_='a-card__title').get('href'),
            'price': item.find('div', class_='a-card__price').get_text(strip=True).replace(u'\xa0', ' '),
            'image': img.get('data-full-src') if hasattr(img, 'class') else img_not_found,
            'href': item.find('a').get('href')
        })
    return houses


def download_image(url):
    r = requests.get(url, allow_redirects=True)

    a = urlparse(url)
    filename = os.path.basename(a.path)
    open(filename, 'wb').write(r.content)
    return filename


# def parse_href(href):
#     result = re.match(f'/show/{href}')
#     return result.group(1)


def update_lastkey(new_key, lastkey_file):
    lastkey = new_key

    with open(lastkey_file, "r+") as f:
        data = f.read()
        f.seek(0)
        f.write(str(new_key))
        f.truncate()

    return new_key


def new_appartments(lastkey_file):
    lastkey = open(lastkey_file, 'r').read()
    html = get_html(URL)
    soup = BeautifulSoup(html.content, features="html.parser")
    new = []
    items = soup.find_all('div', class_='a-card__inc')

    for i in items:
        key = i.find('a').get('href').split("/")[3]
        print(f'key:{key}, lastkey:{lastkey}')
        if lastkey != key:
            houses = parse()
            return houses[0]
        break
    return new


def parse(lastkey_file=False):

    # for page in range(1, last_page):
        # print(f'Парсинг страницы #{page} из {last_page}')
    html = get_html(URL)
    print('ya tut')
    houses = get_content(html.content)

    # Скачиваем картинку
    # download_image(img)
    return houses

