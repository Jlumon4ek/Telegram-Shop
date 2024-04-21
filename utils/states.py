from aiogram.fsm.state import StatesGroup, State


class TopUpState(StatesGroup):
    waiting_for_amount = State()
