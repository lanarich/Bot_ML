from aiogram.types import Message, CallbackQuery
from aiogram import Bot, F
from keyboards.inline import place_kb
from aiogram import Router
from utils.database import DataBase
import os
from keyboards.predict_item_kb import predict_item_keyboard

router_mark = Router()

@router_mark.message(F.text == "Оценить бота")
async def get_inline(message: Message, bot: Bot):
    await message.answer(f'Оцени меня:', reply_markup = place_kb())

@router_mark.callback_query(F.data.startswith('set'))
async def select_mark(call: CallbackQuery, bot: Bot):
    db = DataBase(os.getenv('DATABASE_NAME'))
    mark = call.data.split(':')[1]
    db.add_mark(mark)
    answer = f'Ваше мнение важно для нас!'
    await call.message.answer(answer, reply_markup=predict_item_keyboard)
    await call.answer()
