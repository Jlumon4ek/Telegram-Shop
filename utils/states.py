from aiogram.fsm.state import StatesGroup, State


class TopUpState(StatesGroup):
    waiting_for_amount = State()


class MailingState(StatesGroup):
    waiting_for_message = State()


class BanUserState(StatesGroup):
    waiting_for_user_id = State()


class UnbanUserState(StatesGroup):
    waiting_for_user_id = State()
