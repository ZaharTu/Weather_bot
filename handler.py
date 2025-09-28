import asyncio, re

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import geocoder
from keyboard import *


class Reg(StatesGroup):
    city_selection_main = State()
    city_selection_zip = State()
    city_selection_zip_proof = State()
    city_selection_name = State()
    city_selection_name_list = State()
    city_selection_geo = State()
    time_selection = State()
    time_proof = State()
    end = State()
    geo_select = State()
    geo_confirm = State()

ro = Router()


async def ask_time(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, f"В какое время хочешь получать прогноз? В формате ЧЧ:ММ", state, reply_markup=back_key)
    await state.set_state(Reg.time_selection)


async def back_city(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Каким способом сообщите мне нужное расположение?", state, reply_markup=city_catalog)
    await state.set_state(Reg.city_selection_main)
async def back_city_mes(message: Message, state: FSMContext):
    await send_and_delete(message, "Каким способом сообщите мне нужное расположение?", state, reply_markup=city_catalog)
    await state.set_state(Reg.city_selection_main)

async def send_and_delete(mess_call, text: str, state: FSMContext, reply_markup=None, keep = False):
    is_cb=isinstance(mess_call, CallbackQuery)
    data = await state.get_data() if state else {}
    last_mess_id = data.get("last_mess_id")
    if not keep:
        if is_cb and last_mess_id:
            try:
                sent = await mess_call.bot.edit_message_text(
                    text=text,
                    chat_id=mess_call.message.chat.id,
                    message_id=last_mess_id,
                    reply_markup=reply_markup
                )
                await mess_call.answer()
                return sent
            except Exception:
                pass
        if not is_cb and last_mess_id:
            try:
                await mess_call.bot.delete_message(
                    chat_id=mess_call.chat.id,
                    message_id=last_mess_id
                )
            except Exception:
                pass
    if is_cb:
        sent = await mess_call.message.answer(text, reply_markup=reply_markup)
        await mess_call.answer()
    else:
        sent = await mess_call.answer(text, reply_markup=reply_markup)
    if state and sent:
        await state.update_data(last_mess_id=sent.message_id)
    return sent


@ro.callback_query(F.data == "start")
async def key_start(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Начнём с начала", state)
    await back_city(callback, state)

@ro.callback_query(F.data == "back")
async def key_back(callback: CallbackQuery, state: FSMContext):
    curr = await state.get_state()
    if (curr == Reg.city_selection_zip or curr == Reg.city_selection_name or
            curr == Reg.time_selection or curr == Reg.city_selection_name_list):
        await back_city(callback, state)
    if curr == Reg.end:
        await ask_time(callback, state)


@ro.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await send_and_delete(message, "Привет! Этот бот каждый день будет присылать"
                                " тебе прогноз погоды. Каким способом сообщите мне нужное расположение?", state, reply_markup=city_catalog)
    await state.set_state(Reg.city_selection_main)






@ro.callback_query(F.data == "zip_code")
async def zip_code_select(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Отправьте свой почтовый индекс(только РФ)", state,
                          reply_markup=back_key)
    await state.set_state(Reg.city_selection_zip)


@ro.message(Reg.city_selection_zip)
async def zip_code_answer(message: Message, state: FSMContext):
    await send_and_delete(message, "Сейчас найду!", state, keep=True)
    if 99999 < int(message.text) < 1_000_000:
        s=await geocoder.get_coord_by_zip(message.text)
        if s is not None:
            data=s.split("_")
            await send_and_delete(message, f"Я нашел {data[0].split()[0]} с индексом {data[1]},Верно?", state,
                              reply_markup=confirmation)
            await state.set_state(Reg.city_selection_zip_proof)
        else:
            await send_and_delete(message, "С таким индексом нет совпадений(\nПопробуйте еще раз", state)
            await state.set_state(Reg.city_selection_zip)
    else:
        await send_and_delete(message, "Введите корректный почтовый индекс(шестизначное число)", state)
        await state.set_state(Reg.city_selection_zip)



@ro.callback_query(Reg.city_selection_zip_proof, F.data == "yes")
async def zip_code_proof_yes(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Сохранил!", state, keep=True)
    await ask_time(callback, state)


@ro.callback_query(Reg.city_selection_zip_proof, F.data == "no")
async def zip_code_proof_no(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Давайте попробуем еще раз", state, keep=True)
    await zip_code_select(callback, state)






@ro.callback_query(F.data == "name")
async def name_select(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Важно! Если ваш населенный пункт небольшой, то лучше отправить "
                                  "геолокацию или почтовый индекс.\n"
                                    "\nВведите название вашего населенного пункта(в формате Город, Страна)", state,reply_markup=back_key)
    await state.set_state(Reg.city_selection_name)


@ro.message(Reg.city_selection_name)
async def name_answer(message: Message, state: FSMContext):
    await send_and_delete(message,"Сейчас найду!",state, keep=True)
    name = message.text
    answer = await asyncio.to_thread(geocoder.set_city_name(name))
    if answer is not None :
        await send_and_delete(message, f"Выберите ваш город из списка", state,
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=answer.inline_keyboard+back_key.inline_keyboard))
        await state.set_state(Reg.city_selection_name_list)
    else:
        await send_and_delete(message, "Введите корректное название. В формате *Город* или *Город, Страна*", state)
        await state.set_state(Reg.city_selection_name)

@ro.callback_query(Reg.city_selection_name_list)
async def name_answer_list(callback: CallbackQuery, state: FSMContext):
    data=callback.data.split("_")
    lat, lon = float(data[1]), float(data[2])
    await state.update_data(city_cord=(lat,lon))
    await send_and_delete(callback, f"Вы выбрали город {data[0]}", state)
    await ask_time(callback,state)
"""
@ro.callback_query(Reg.city_selection_name_proof, F.data == "yes")
async def name_select_proof_yes(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Отлично! Город сохранен", state)
    await ask_time(callback.message, state)


@ro.callback_query(Reg.city_selection_name_proof, F.data == "no")
async def name_select_proof_yes(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, "Жаль( давайте попробуем еще раз", state)
    await back_city(callback, state)
"""

@ro.callback_query(F.data=="geo")
async def geo_quest(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, f"Отправьте вашу геолокацию(можете выбрать место рядом с вами)", state, reply_markup=request_geo)
@ro.message(F.text == "⬅️ Назад")
async def geo_back(message: Message, state: FSMContext):
    await back_city_mes(message,state)
@ro.message(F.location)
async def geo_grab(message: Message, state: FSMContext):
    await send_and_delete(message, "Сейчас найду!", state, keep=True)
    lat=message.location.latitude
    lon=message.location.longitude
    await send_and_delete(message, f"Геолокацию получил!", state,
                          reply_markup=ReplyKeyboardRemove(),keep=True)
    await ask_time(message,state)
pattern_time="[0-2][0-9]:[0-5][0-9]"

@ro.message(Reg.time_selection)
async def time_text(message: Message, state: FSMContext):
    time_data=message.text
    if re.fullmatch(pattern_time,time_data):
        await send_and_delete(message, f"Вы указали время {time_data}, верно?", state, reply_markup=confirmation)
        await state.set_state(Reg.time_proof)
        await state.update_data(time=time_data)
    else:
        await send_and_delete(message, "Некорректно ввели время! Формат ЧЧ:ММ (пример 22:53).\nПопробуйте еще раз!",state)

@ro.callback_query(Reg.time_proof, F.data == "yes")
async def time_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data() if state else {}
    time_data= data.get("time")
    await send_and_delete(callback, f"Замечательно! Тогда пришлю прогноз в {time_data}", state, reply_markup=in_start)
    await state.set_state(Reg.end)


@ro.callback_query(Reg.time_proof, F.data == "no")
async def time_no(callback: CallbackQuery, state: FSMContext):
    await send_and_delete(callback, f"Жаль( придется пройти этот этап заново", state)
    await ask_time(callback.message, state)

