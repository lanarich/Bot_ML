from aiogram import Bot
from aiogram.types import Message
from keyboards.predict_item_kb import predict_item_keyboard



async def get_started(message: Message, bot:Bot):
    await bot.send_message(message.from_user.id, f'Доброго времени суток \n'
                                                 f'Это бот, который содержит в себе ML модель \n\n\n', reply_markup=predict_item_keyboard)

