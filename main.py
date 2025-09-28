import asyncio

from aiogram import Bot,Dispatcher
from handler import ro



async def main():
    bot = Bot(token="8417812268:AAHroxPFpPj69TPu-4fVZbQ3XmRqjpt_UdA")
    dp = Dispatcher()
    dp.include_router(ro)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("КОНЕЦ")