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
        f"👋 Здравствуйте, <b>{user_name}</b>!\n\n"
        "Я помогу вам легко и быстро оформить заявку на <b>фото- и видеосъёмку</b>.\n\n"
        "📝 <b>Для оформления заявки потребуется указать:</b>\n"
        "1️⃣ Ваше имя\n"
        "2️⃣ Контактный номер телефона\n"
        "3️⃣ Город проведения съёмки\n"
        "4️⃣ Желаемый формат съёмки\n\n"
        "Нажмите кнопку ниже, чтобы начать! 👇"
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
        "ℹ️ <b>Справка по боту:</b>\n\n"
        "• /start — перезапустить бота и начать сначала\n"
        "• /apply — начать оформление заявки\n"
        "• /cancel — отменить текущее заполнение заявки\n"
        "• /help — получить помощь\n\n"
        "При заполнении заявки вы сможете проверить и подтвердить каждый введенный пункт!"
    )
    await message.answer(text=text, parse_mode="HTML")


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "❌ отмена")
@router.message(F.text.casefold() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего процесса заполнения заявки"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Сейчас нет активного заполнения заявки. Чтобы начать, введите /start",
            reply_markup=remove_keyboard()
        )
        return

    await state.clear()
    await message.answer(
        "❌ Заполнение заявки отменено.\n\nЧтобы начать заново в любой момент, отправьте команду /start или /apply.",
        reply_markup=remove_keyboard()
    )
