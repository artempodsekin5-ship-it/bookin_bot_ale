from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура в приветственном сообщении"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Записаться на съемку", callback_data="start_application")
    return builder.as_markup()


def get_step_confirm_keyboard(step: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения одного шага"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Оставляем", callback_data=f"step_confirm_{step}")
    builder.button(text="Поправить", callback_data=f"step_edit_{step}")
    builder.adjust(2)
    return builder.as_markup()


def get_format_choice_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с популярными форматами съемок"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Индивидуальная", callback_data="format_choice:Индивидуальная")
    builder.button(text="Love Story", callback_data="format_choice:Love Story")
    builder.button(text="Свадебная / Роспись", callback_data="format_choice:Свадебная / Роспись")
    builder.button(text="Контент / Бренд", callback_data="format_choice:Контент / Бренд")
    builder.button(text="Фотодень", callback_data="format_choice:Фотодень")
    builder.button(text="Мероприятие / Репортаж", callback_data="format_choice:Мероприятие / Репортаж")
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_final_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура финального подтверждения перед отправкой админу"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить заявку", callback_data="final_send")
    builder.button(text="Заполнить заново", callback_data="final_restart")
    builder.button(text="Отменить", callback_data="final_cancel")
    builder.adjust(1, 2)
    return builder.as_markup()
