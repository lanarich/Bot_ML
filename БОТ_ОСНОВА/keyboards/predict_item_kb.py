from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

predict_item_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Предсказать цену для одного наблюдения'
        ),
        KeyboardButton(
            text='Предсказать цену для нескольких наблюдений'
        ),
        KeyboardButton(
            text='Оценить бота'
        ),
        KeyboardButton(
            text='Статистика оценок'
        )
    ]
], resize_keyboard= True, one_time_keyboard= True, input_field_placeholder= 'Нажмите на одну из кнопок ниже')
