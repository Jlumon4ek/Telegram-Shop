from aiogram.fsm.state import StatesGroup, State


class TopUpState(StatesGroup):
    waiting_for_amount = State()


class MailingState(StatesGroup):
    waiting_for_message = State()


class BanUserState(StatesGroup):
    waiting_for_user_id = State()


class UnbanUserState(StatesGroup):
    waiting_for_user_id = State()


class CategoryNameState(StatesGroup):
    waiting_for_category_name = State()


class CountOfProductsState(StatesGroup):
    waiting_for_count = State()


class ProductState(StatesGroup):
    waiting_for_product = State()


class SubcategoryForm(StatesGroup):
    waiting_for_subcategory_name = State()
    waiting_for_subcategory_price = State()
    waiting_for_subcategory_group_by = State()
    waiting_for_subcategory_fileds = State()
