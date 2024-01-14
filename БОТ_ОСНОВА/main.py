import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router
from aiogram import F

from dotenv import load_dotenv
import os
from utils.commands import set_commands
from handlers.start import get_started
from handlers.predict_item import start_predict_item, predict_item
from handlers import predict_items, user_mark, statistics
from state.prediction import PredictionState
from aiogram.filters import Command



load_dotenv()

token = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token, parse_mode='HTML')
dp = Dispatcher()


#Стартовый хендлер
dp.message.register(get_started, Command(commands='start'))

#Хендлер предсказания для одного наблюдения
dp.message.register(start_predict_item, F.text == "Предсказать цену для одного наблюдения")
dp.message.register(predict_item, PredictionState.predItem)

#Предсказание для csv файла
dp.include_routers(predict_items.router, user_mark.router_mark, statistics.router_stat)




async def start():
    await set_commands(bot)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
