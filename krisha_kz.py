import csv
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HOST = 'https://krisha.kz'
URL = "https://krisha.kz/prodazha/kvartiry/almaty/?areas=p43.263887%2C76.928178%2C43.259496%2C76.908093%2C43.257112%2C76.894532%2C43.257614%2C76.884061%2C43.252219%2C76.865006%2C43.239168%2C76.857711%2C43.237976%2C76.857453%2C43.235529%2C76.859170%2C43.227747%2C76.862603%2C43.223353%2C76.865865%2C43.220089%2C76.866466%2C43.214188%2C76.883546%2C43.214314%2C76.902600%2C43.215193%2C76.932469%2C43.224734%2C76.942082%2C43.226366%2C76.964398%2C43.238415%2C76.956674%2C43.245443%2C76.971608%2C43.274299%2C76.970235%2C43.264013%2C76.927835%2C43.263887%2C76.928178&das[_sys.hasphoto]=1&das[flat.building]=1&das[floor_not_first]=1&das[floor_not_last]=1&das[house.year][from]=1980&das[live.rooms][]=2&das[live.rooms][]=3&das[live.rooms][]=4&das[live.rooms][]=5.100&das[price][to]=40000000&lat=43.24358&lon=76.90966&zoom=13"
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
        main_data = {
            'title': item.find('a', class_='a-card__title').get_text(),
            'subtitle': item.find('div', class_='a-card__subtitle').get_text(strip=True),
            'owner': item.find('div', class_='owners__label').get_text(strip=True),
            'created_at': ''.join([it.get_text(strip=True) for it in item.find_all('div', class_='card-stats__item')][1:2]),
            'link': HOST + item.find('a', class_='a-card__title').get('href'),
            'price': item.find('div', class_='a-card__price').get_text(strip=True).replace(u'\xa0', ' '),
            'image': img.get('data-full-src') if hasattr(img, 'class') else img_not_found,
            'href': item.find('a').get('href')
        }

        url = HOST + item.find('a', class_='a-card__title').get('href')
        additional_data = get_images(url)
        main_data.update(additional_data)
        houses.append(main_data)
    return houses


def get_images(url):
    html = get_html(url)
    print(url)
    images = []
    soup = BeautifulSoup(html.content, features="html.parser")
    try:
        imgs = soup.find('div', class_="gallery__container").find('ul', class_="gallery__small-list").find_all('li')
        for i in imgs:
            img = i.img['src']
            if img:
                r = img.rfind("-")
                lst = list(img)
                lst[r:] = "-full.webp"
                lst = "".join(lst)
                images.append(lst)

    except AttributeError:
        ...
    if len(images) < 1:
        main_picture =  soup.find('div', class_="gallery__main").picture.img['src']
        images.append(main_picture)
        images.append(main_picture)
    building = soup.find('div', {'data-name': 'flat.building'}).find('div', class_='offer__advert-short-info').get_text()
    balcony = soup.find('div', {'data-name': 'flat.balcony'}).find('div', class_='offer__advert-short-info').get_text() if soup.find('div', {'data-name': 'flat.balcony'}) else ''
    square =  soup.find('div', {'data-name': 'live.square'}).find('div', class_='offer__advert-short-info').get_text()
    try:
        preview = soup.find('div', class_="offer__description").find('div', class_="text").div.get_text(strip=True).replace('\n', '')
    except AttributeError:
        preview = ''
    additional_data = {
        "square": square,
        "balcony":  balcony,
        "images": images,
        "preview": preview,
        "building": building,
    }
    return additional_data

def get_phone(url):
    from selenium import webdriver
    driver = webdriver.Chrome("/home/blank/tamerlan_projects/selenium_projects/chromedriver")
    driver.get(url)
    driver.find_element_by_class_name('show-phones').click()
    val = driver.find_element_by_class_name("offer__contacts-phones").text()
    driver.quit()
    return val


def download_image(url):
    r = requests.get(url, allow_redirects=True)

    a = urlparse(url)
    filename = os.path.basename(a.path)
    open(filename, 'wb').write(r.content)
    return filename


def remove_image(url):
    a = urlparse(url)
    filename = os.path.basename(a.path)
    os.remove(filename)
    return


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
    houses = get_content(html.content)



    # Скачиваем картинку
    # download_image(img)
    return houses

