from aiogram.types import (ReplyKeyboardMarkup,KeyboardButton,
                           InlineKeyboardButton,InlineKeyboardMarkup)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="каталог")],
                                     [KeyboardButton(text="аборт"),KeyboardButton(text="МУХАМАД")],
                                     [KeyboardButton(text="пенис")]],
                           resize_keyboard=True,
                           input_field_placeholder="Выберите в меню")

confirmation = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Да",callback_data="yes")],
                                             [InlineKeyboardButton(text="Нет",callback_data="no")]])
request_geo = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📍 Отправить локацию", request_location=True)],
              [KeyboardButton(text="⬅️ Назад")]],
    resize_keyboard=True,
    one_time_keyboard=True
)
back_key=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад",callback_data="back")]])

city_catalog = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Укажу почтовый индекс(РФ)',callback_data="zip_code")],
                                                [InlineKeyboardButton(text='Введу название нас. пункта',callback_data="name")],
                                                [InlineKeyboardButton(text='Отправлю геолокацию⚠️Только телефон',callback_data="geo")]])

in_start = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Заново",callback_data="start")]])
async def set_keyboard_city(cities: list) -> InlineKeyboardMarkup:
    buttons=[]
    for city in cities:
        name = city.get("local_names", {}).get("ru", city["name"])
        if city.get("state"):
            text = f"{name}, {city['state']}"
        else:
            text = f"{name}, {city['country']}"
        callback_data = f"{name}_{city['lat']}_{city['lon']}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
