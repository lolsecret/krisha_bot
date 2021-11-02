import asyncio
import json

import aiogram.types.input_media

import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from sql_db import SQL
from krisha_kz import new_appartments, download_image, update_lastkey, parse, remove_image

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
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны")
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписались")

    await message.answer("Вы успешно подписались на рассылку \nЖдите, скоро выйдут новые объявления")


@dp.message_handler(commands=['region'])
async def region(message: types.Message):
    btn_1 = types.InlineKeyboardButton("Алмалинский", callback_data='btn_ALM')
    btn_2 = types.InlineKeyboardButton("Медеуский", callback_data='btn_MED')
    btn_3 = types.InlineKeyboardButton("Бостандыкский", callback_data='btn_BOS')
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(btn_1).add(btn_2).add(btn_3)
    await message.reply("Выберите район: ", reply_markup=kb)


@dp.callback_query_handler(text_contains='btn_')
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    print(callback_query)
    code = callback_query.data[-1]
    print(code)
    if code == "ALM":
        await bot.answer_callback_query(callback_query.id, text='Нажата вторая кнопка')
    elif code == "MED":
        await bot.answer_callback_query(
            callback_query.id,
            text='Нажата кнопка с номером 5.\nА этот текст может быть длиной до 200 символов 😉', show_alert=True)
    else:
        await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка! code={code}')

# проверяем наличие новых игр и делаем рассылки
async def scheduled(wait_for):

    while True:
        await asyncio.sleep(wait_for)

        # проверяем наличие новых кв
        new_houses = new_appartments('lastkey.txt')
        if new_houses:
            # если объявления есть, переворачиваем список и итерируем
            # получаем список подписчиков бота
            subscriptions = db.get_subscriptions()
            # отправляем всем новость

            print('start')

            for s in subscriptions:
                media = types.MediaGroup()
                for i in new_houses["images"][:9]:
                    media.attach_photo(types.InputFile(download_image(i)))
                bot_msg = await bot.send_photo(
                    s[1],
                    types.InputFile(download_image(new_houses['image'])),
                    caption=new_houses['title'] + "\n\n"
                        "<b>Адрес:</b> " + new_houses['subtitle'] + "\n"
                        "<b>Дом:</b> " + new_houses['building'] +"\n"
                        "<b>Балкон:</b> " + new_houses['balcony'] +"\n"
                        "<b>Площадь:</b> " + new_houses['square'] + "\n"
                        "<b>Описание:</b> " + new_houses['preview'] + "\n\n"
                        "<b>Хозяин/специалист:</b> " + new_houses['owner'] + "\n"
                        "<b>Цена:</b> " + new_houses['price'] + "\n\n"
                        "<b>Ссылка:</b> " + new_houses['link'] + "\n" +
                        "<b>Опубликован:</b> " + new_houses['created_at'] + "\n\n"
                    ,
                    disable_notification=True,
                    parse_mode='html'
                )
                await bot.send_media_group(
                    s[1],
                    media=media,
                    reply_to_message_id=bot_msg.message_id
                )

            update_lastkey(new_houses['href'].split("/")[3], 'lastkey.txt')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(60))
    executor.start_polling(dp, skip_updates=True)



