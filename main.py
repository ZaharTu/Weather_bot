import asyncio

from aiogram import Bot,Dispatcher

import tokens
from handler import ro



async def main():
    bot = Bot(token=tokens.Token_TG)
    dp = Dispatcher()
    dp.include_router(ro)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("КОНЕЦ")