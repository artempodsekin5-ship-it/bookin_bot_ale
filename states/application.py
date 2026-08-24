from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    # Ввод имени и подтверждение
    waiting_for_name = State()
    confirm_name = State()

    # Ввод телефона и подтверждение
    waiting_for_phone = State()
    confirm_phone = State()

    # Ввод города и подтверждение
    waiting_for_city = State()
    confirm_city = State()

    # Ввод формата съемки и подтверждение
    waiting_for_format = State()
    confirm_format = State()

    # Финальное подтверждение заявки перед отправкой админу
    confirm_final = State()
