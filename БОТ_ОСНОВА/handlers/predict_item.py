from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from state.prediction import PredictionState
from pydantic import BaseModel
import pickle
import pandas as pd
import sklearn
import io
import json
from keyboards.predict_item_kb import predict_item_keyboard

class Item(BaseModel):
    name: str
    year: int
    selling_price: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float

def load_model():
    with open('ridge_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

#Предобработка данных. Так как самая лучшая модель - с категориальными переменными, значит поступающие данные также
#необходимо обработать, более подробно об обработке признаков в ноутбуке

def preprocess_data(item: Item):
    #для того, чтобы проверить структуру данных, обработанных и тех, что потребляет модель, чтобы было гладко
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
    data = pd.DataFrame(dict(item), index=[0])


    columns = ['mileage', 'engine', 'max_power']
    for col in columns:
        data[col] = pd.to_numeric(data[col].str.extract('(\d+(\.\d+)?)', expand=False)[0], errors='coerce')


    data['max_torque_rpm'] = pd.to_numeric(
        data['torque'].str.extract(r'([\d,.]+)(?=\D*$|$)')[0].str.replace(',', ''), errors='coerce')
    c = data['torque'].str.extract(r'(^[\d.]+)').astype('float')
    b = data['torque'].str.contains('Nm', case=False)
    data['torque'] = c[0] * b.map({True: 1, False: 9.80665})

    data['bph/CC'] = data['max_power'] / data['engine']
    data['year2'] = data['year'] ** 2

    bins = [2, 6, 8, 20]
    data['seats'] = pd.cut(data['seats'], bins=bins, labels=['2-5', '6-7', '8+'], right=False)
    data['owner'] = data['owner'].replace(
        {'First Owner': '1-2', 'Second Owner': '1-2', 'Third Owner': '3+(test)', 'Fourth & Above Owner': '3+(test)',
         'Test Drive Car': '3+(test)'})
    data = data.drop(['selling_price', 'name'], axis=1)
    data = pd.get_dummies(data, columns=['fuel', 'seller_type', 'transmission', 'owner', 'seats'], drop_first=True)

    #вот тут как раз и дополняем колонки того чего не было при создании дамми переменных.
    data = data.reindex(columns=df.columns, fill_value=0)
    return data




async def start_predict_item(message: Message, state: FSMContext):
    await message.answer('Давайте предскажем цену для вашего наблюдения. \n'
                         'Введите данные в формате <b>json</b> как в примере ниже пример:\n'
                         '\n'
                         '{\n'
                         '    "name": "SomeCar",\n'
                         '    "year": 2019,\n'
                         '    "selling_price": 300000,\n'
                         '    "fuel": "Petrol",\n'
                         '    "seller_type": "Individual",\n'
                         '    "transmission": "Manual",\n'
                         '    "owner": "First Owner",\n'
                         '    "mileage": "23.01 kmpl",\n'
                         '    "engine": "999 CC",\n'
                         '    "max_power": "67 bhp",\n'
                         '    "torque": "91Mn@ 4250rpm",\n'
                         '    "seats": 5.0\n'
                         '}\n'
                         )
    await state.set_state(PredictionState.predItem)


async def predict_item(message: Message, state: FSMContext):
    await state.update_data(predItem = message.text)
    data = await state.get_data()
    data_input = data.get('predItem')
    trained_model = load_model()
    processed_data = preprocess_data(json.loads(data_input))
    prediction = trained_model.predict(processed_data)
    await message.answer(f'Предсказанная цена для ваших данных: \n'
                         f'\n'
                         f'🌟 👇 🌟\n'
                         f'<b>{round(prediction[0],2)}\n</b>'
                         f'🌟 👆 🌟\n', reply_markup=predict_item_keyboard)
    await state.clear()

