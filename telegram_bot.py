import asyncio

import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from sql_db import SQL
from krisha_kz import new_appartments, download_image, update_lastkey, parse

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

db = SQL('db.db')

@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)

    await message.answer("Вы успешно подписались на рассылку \nЖдите, скоро выйдут новые объявления")


# Команда отписки
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны")
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписались")

    await message.answer("Вы успешно подписались на рассылку \nЖдите, скоро выйдут новые объявления")


# проверяем наличие новых игр и делаем рассылки
async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        # проверяем наличие новых игр
        new_houses = new_appartments('lastkey.txt')
        if new_houses:
            # если объявления есть, переворачиваем список и итерируем
            # получаем список подписчиков бота
            subscriptions = db.get_subscriptions()
            # отправляем всем новость
            with open(download_image(new_houses['image']), 'rb') as photo:
                for s in subscriptions:
                    await bot.send_photo(
                    s[1],
                    photo,
                    caption=new_houses['title'] + "\n\n" + "*Адрес*: " + new_houses['subtitle'] + "\n" +
                    "*Описание*: " + new_houses['preview'] + "\n\n" 
                    "*Хозяин/специалист*: " + new_houses['owner'] + "\n"
                    "*Цена*: " + new_houses['price'] + "\n\n"
                    "*Ссылка*: " + new_houses['link'] + "\n" +
                    "*Опубликован*: " + new_houses['created_at'] + "\n\n"
                    ,
                    disable_notification=True,
                    parse_mode='Markdown'
                    )
            update_lastkey(new_houses['href'].split("/")[3], 'lastkey.txt')



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(300))
    executor.start_polling(dp, skip_updates=True)