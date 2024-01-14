import io

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
from aiogram.types import BufferedInputFile
from state.prediction import PredictionState
from aiogram import Bot
from pydantic import BaseModel
import pickle
import pandas as pd
import sklearn
import io
import json
from keyboards.predict_item_kb import predict_item_keyboard



def load_model():
    with open('ridge_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model


def preprocess_сsv(dataframe):
    #Тоже самое, но уже для датафрейма, тут нет перевода словаря в датафрей, сразу работа с файлом
    df = {'year': 2014.0,
    'km_driven': 145500.0,
    'mileage': 23.4,
    'engine': 1248.0,
    'max_power': 74.0,
    'torque': 190.0,
    'max_torque_rpm': 2000.0,
    'bph/CC': 0.05929487179487179,
    'year2': 4056196.0,
    'fuel_Diesel': 1.0,
    'fuel_LPG': 0.0,
    'fuel_Petrol': 0.0,
    'seller_type_Individual': 1.0,
    'seller_type_Trustmark Dealer': 0.0,
    'transmission_Manual': 1.0,
    'owner_3+(test)': 0.0,
    'seats_6-7': 0.0,
    'seats_8+': 0.0}

    df = pd.DataFrame(dict(df), index=[0])

    dataframe = dataframe.dropna()
    columns = ['mileage', 'engine', 'max_power']
    for col in columns:
        dataframe[col] = pd.to_numeric(dataframe[col].str.extract('(\d+(\.\d+)?)', expand=False)[0], errors='coerce')


    dataframe['max_torque_rpm'] = pd.to_numeric(
        dataframe['torque'].str.extract(r'([\d,.]+)(?=\D*$|$)')[0].str.replace(',', ''), errors='coerce')
    c = dataframe['torque'].str.extract(r'(^[\d.]+)').astype('float')
    b = dataframe['torque'].str.contains('Nm', case=False)
    dataframe['torque'] = c[0] * b.map({True: 1, False: 9.80665})

    dataframe['bph/CC'] = dataframe['max_power'] / dataframe['engine']
    dataframe['year2'] = dataframe['year'] ** 2

    bins = [2, 6, 8, 20]
    dataframe['seats'] = pd.cut(dataframe['seats'], bins=bins, labels=['2-5', '6-7', '8+'], right=False)
    dataframe['owner'] = dataframe['owner'].replace(
        {'First Owner': '1-2', 'Second Owner': '1-2', 'Third Owner': '3+(test)', 'Fourth & Above Owner': '3+(test)',
         'Test Drive Car': '3+(test)'})
    dataframe = dataframe.drop(['selling_price', 'name'], axis=1)
    dataframe = pd.get_dummies(dataframe, columns=['fuel', 'seller_type', 'transmission', 'owner', 'seats'], drop_first=True)
    dataframe = dataframe.reindex(columns=df.columns, fill_value=0)
    return dataframe

router = Router()

@router.message(F.text == "Предсказать цену для нескольких наблюдений")
async def start_predict_items(message: Message, state: FSMContext):
    await message.answer('Давайте предскажем цену нескольких наблюдений. \n'
                         'Для этого загрузите файл формата <b>csv</b> весом не более <b>20 МБ</b> \n'
                         )
    await state.set_state(PredictionState.predItems)

@router.message(PredictionState.predItems)
async def predict_items(message: Message, bot: Bot):
    document = await bot.download(message.document)
    data = pd.read_csv(document)
    data_old = data.copy()
    trained_model = load_model()
    processed_data = preprocess_сsv(data)
    prediction = trained_model.predict(processed_data)
    df_final = pd.concat([data_old, pd.DataFrame(prediction, columns=['selling_price_pred'])], axis = 1)
    csv_data = df_final.to_csv()
    pred_file = BufferedInputFile(io.BytesIO(csv_data.encode()).getvalue(), filename="Predictions.txt")
    await message.answer(f'Данные предсказаны!\n'
                         f'Скачайте новый файл, в нем появился столбец selling_price_pred', reply_markup= predict_item_keyboard)
    await bot.send_document(message.chat.id, pred_file)
