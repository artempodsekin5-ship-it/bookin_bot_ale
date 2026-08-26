import html
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import get_start_keyboard, remove_keyboard

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    user_name = html.escape(message.from_user.first_name) if message.from_user else "гость"

    text = (
        f"йоу, <b>{user_name}</b>\n\n"
        "сделаем стильный контент! чтобы забронить съемку, ответь всего на 4 быстрых вопроса:\n\n"
        "• как тебя зовут\n"
        "• твой контакт для связи\n"
        "• в каком ты городе\n"
        "• формат съемки\n\n"
        "жми кнопку ниже и погнали:"
    )

    await message.answer(
        text=text,
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    text = (
        "<b>Что по командам:</b>\n\n"
        "• /start — открыть главное меню\n"
        "• /apply — записаться на съемку\n"
        "• /cancel — сбросить заполнение\n"
        "• /help — эта инфа\n\n"
        "каждый шаг можно будет подтвердить или поправить, если опечатался."
    )
    await message.answer(text=text, parse_mode="HTML")


@router.message(Command("cancel"))
@router.message(F.text.casefold().contains("отмен"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего процесса заполнения заявки"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Сейчас нет активной записи. Чтобы начать, введи /start",
            reply_markup=remove_keyboard()
        )
        return

    await state.clear()
    await message.answer(
        "Запись отменена.\n\nЕсли захочешь снова — пиши /start или /apply",
        reply_markup=remove_keyboard()
    )
