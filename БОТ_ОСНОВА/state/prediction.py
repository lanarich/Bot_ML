from aiogram.fsm.state import StatesGroup, State

class PredictionState(StatesGroup):
    predItem = State()
    predItems = State()
