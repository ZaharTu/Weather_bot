import re

import aiohttp

import keyboard

key="5accca0b349f426144c855f9abec3dfa"
pattern_name='^\s*[A-Za-zА-Яа-яЁё\s-]+?\s*,\s*[A-Za-zА-Яа-яЁё\s-]+\s*$|^\s*[A-Za-zА-Яа-яЁё\s-]+\s*$'



async def set_city_name(name: str):
    if bool(re.fullmatch(pattern_name, name)):
        return await get_coord_by_name(name)
    return None
async def get_coord_by_zip(zip_code):
    async with aiohttp.ClientSession() as session:
        url = f'http://api.openweathermap.org/geo/1.0/zip?zip={zip_code},RU&appid={key}'
        async with session.get(url) as response:
            r = await response.json()
            print(r)
            if not r:
                return None
            return r.get("name")+"_"+r.get("zip")

async def get_coord_by_name(name):
    async with aiohttp.ClientSession() as session:
        url = f'http://api.openweathermap.org/geo/1.0/direct?q={name}&limit=7&appid={key}'
        async with session.get(url) as response:
            r = await response.json()
            if not r:
                return None
            if len(r) == 1:
                city = r[0]
                if city.get("state"):
                    return city["local_names"]["ru"] + " из " + city["state"]
                else:
                    return city["local_names"]["ru"] + " из " + city["country"]
            else:
                limit = min(len(r), 5)
                return await keyboard.set_keyboard_city(r[:limit])
