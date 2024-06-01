from aiogram import executor
from handlers import dp
from data.sqlite import Database
db = Database()


async def on_startup(dp):
    await db.check_database()
    print("Бот был запущен")


if __name__ == "__main__":
    print("Бот запускается...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
