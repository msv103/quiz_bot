import asyncio
import logging
from aiogram import Bot
import quiz 
import db


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = '8291378804:AAF4-s-wPMTim4f7BE7CtDFFfv8OZ99jXgY'

# Объект бота
bot = Bot(token=API_TOKEN)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Запускаем создание таблицы базы данных
    await db.create_table()

    await quiz.dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

