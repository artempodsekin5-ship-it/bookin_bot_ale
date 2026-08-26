import html
import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import config
from keyboards import (
    get_cancel_keyboard,
    get_final_confirm_keyboard,
    get_format_choice_keyboard,
    get_phone_keyboard,
    get_step_confirm_keyboard,
    remove_keyboard,
)
from states import ApplicationForm

logger = logging.getLogger(__name__)
router = Router(name="application")


async def ask_name(target: Message | CallbackQuery, state: FSMContext, is_edit: bool = False):
    """Запрос ввода имени"""
    await state.set_state(ApplicationForm.waiting_for_name)
    prompt = (
        "✏️ Напиши имя или ник ещё раз:"
        if is_edit
        else "📋 <b>1/4: Как тебя зовут?</b> ✍️\n\nНапиши имя или ник:"
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(prompt, parse_mode="HTML", reply_markup=get_cancel_keyboard())
        await target.answer()
    else:
        await target.answer(prompt, parse_mode="HTML", reply_markup=get_cancel_keyboard())


async def ask_phone(target: Message | CallbackQuery, state: FSMContext, is_edit: bool = False):
    """Запрос ввода номера телефона"""
    await state.set_state(ApplicationForm.waiting_for_phone)
    prompt = (
        "✏️ Отправь контакт или напиши номер ещё раз:"
        if is_edit
        else "📱 <b>2/4: Номер для связи</b>\n\n"
             "Поделись контактом по кнопке ниже или напиши номер вручную (например: <code>+7 999 123-45-67</code>):"
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(prompt, parse_mode="HTML", reply_markup=get_phone_keyboard())
        await target.answer()
    else:
        await target.answer(prompt, parse_mode="HTML", reply_markup=get_phone_keyboard())


async def ask_city(target: Message | CallbackQuery, state: FSMContext, is_edit: bool = False):
    """Запрос ввода города"""
    await state.set_state(ApplicationForm.waiting_for_city)
    prompt = (
        "✏️ Напиши город съёмки ещё раз:"
        if is_edit
        else "🏙️ <b>3/4: В каком ты городе?</b>\n\nГде планируем снимать:"
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(prompt, parse_mode="HTML", reply_markup=get_cancel_keyboard())
        await target.answer()
    else:
        await target.answer(prompt, parse_mode="HTML", reply_markup=get_cancel_keyboard())


async def ask_format(target: Message | CallbackQuery, state: FSMContext, is_edit: bool = False):
    """Запрос формата съемки"""
    await state.set_state(ApplicationForm.waiting_for_format)
    prompt = (
        "✏️ Выбери или напиши формат съёмки ещё раз:"
        if is_edit
        else "📸 <b>4/4: Формат съёмки</b>\n\n"
             "Выбери подходящий вариант кнопкой или напиши свой текстом:"
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(prompt, parse_mode="HTML", reply_markup=get_format_choice_keyboard())
        await target.answer()
    else:
        await target.answer(prompt, parse_mode="HTML", reply_markup=get_format_choice_keyboard())


# ==================== СТАРТ ЗАПОЛНЕНИЯ ЗАЯВКИ ====================

@router.callback_query(F.data == "start_application")
async def start_application_callback(callback: CallbackQuery, state: FSMContext):
    """Старт заполнения по кнопке"""
    await state.clear()
    await ask_name(callback, state)


@router.message(Command("apply"))
async def start_application_command(message: Message, state: FSMContext):
    """Старт заполнения по команде /apply"""
    await state.clear()
    await ask_name(message, state)


# ==================== ШАГ 1: ИМЯ ====================

@router.message(ApplicationForm.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext):
    """Получение имени и запрос подтверждения"""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Имя слишком короткое. Пожалуйста, введите корректное имя:")
        return

    await state.update_data(temp_name=name)
    await state.set_state(ApplicationForm.confirm_name)

    await message.answer(
        f"Записали имя:\n👉 <b>{html.escape(name)}</b>\n\nОставляем?",
        reply_markup=get_step_confirm_keyboard("name"),
        parse_mode="HTML"
    )


@router.callback_query(ApplicationForm.confirm_name, F.data == "step_confirm_name")
async def confirm_name_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение имени -> переход к телефону"""
    data = await state.get_data()
    name = data.get("temp_name")
    await state.update_data(name=name)
    await callback.message.edit_text(
        f"✅ Имя: <b>{html.escape(str(name))}</b>",
        parse_mode="HTML"
    )
    await ask_phone(callback, state)


@router.callback_query(ApplicationForm.confirm_name, F.data == "step_edit_name")
async def edit_name_callback(callback: CallbackQuery, state: FSMContext):
    """Повторный ввод имени"""
    await callback.message.delete()
    await ask_name(callback, state, is_edit=True)


# ==================== ШАГ 2: ТЕЛЕФОН ====================

@router.message(ApplicationForm.waiting_for_phone, F.contact)
@router.message(ApplicationForm.waiting_for_phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    """Получение телефона и запрос подтверждения"""
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = f"+{phone}"
    else:
        phone = message.text.strip()
        # Базовая проверка
        digits_only = [c for c in phone if c.isdigit()]
        if len(digits_only) < 7:
            await message.answer(
                "⚠️ Номер телефона слишком короткий. Пожалуйста, укажите корректный номер:",
                reply_markup=get_phone_keyboard()
            )
            return

    await state.update_data(temp_phone=phone)
    await state.set_state(ApplicationForm.confirm_phone)

    await message.answer(
        f"Твой номер:\n👉 <b>{html.escape(phone)}</b>\n\nОставляем?",
        reply_markup=get_step_confirm_keyboard("phone"),
        parse_mode="HTML"
    )


@router.callback_query(ApplicationForm.confirm_phone, F.data == "step_confirm_phone")
async def confirm_phone_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение телефона -> переход к городу"""
    data = await state.get_data()
    phone = data.get("temp_phone")
    await state.update_data(phone=phone)
    await callback.message.edit_text(
        f"✅ Телефон: <b>{html.escape(str(phone))}</b>",
        parse_mode="HTML"
    )
    await ask_city(callback, state)


@router.callback_query(ApplicationForm.confirm_phone, F.data == "step_edit_phone")
async def edit_phone_callback(callback: CallbackQuery, state: FSMContext):
    """Повторный ввод телефона"""
    await callback.message.delete()
    await ask_phone(callback, state, is_edit=True)


# ==================== ШАГ 3: ГОРОД ====================

@router.message(ApplicationForm.waiting_for_city, F.text)
async def process_city(message: Message, state: FSMContext):
    """Получение города и запрос подтверждения"""
    city = message.text.strip()
    if len(city) < 2:
        await message.answer("⚠️ Название города слишком короткое. Введите город ещё раз:")
        return

    await state.update_data(temp_city=city)
    await state.set_state(ApplicationForm.confirm_city)

    await message.answer(
        f"Город съёмки:\n👉 <b>{html.escape(city)}</b>\n\nОставляем?",
        reply_markup=get_step_confirm_keyboard("city"),
        parse_mode="HTML"
    )


@router.callback_query(ApplicationForm.confirm_city, F.data == "step_confirm_city")
async def confirm_city_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение города -> переход к формату съемки"""
    data = await state.get_data()
    city = data.get("temp_city")
    await state.update_data(city=city)
    await callback.message.edit_text(
        f"✅ Город: <b>{html.escape(str(city))}</b>",
        parse_mode="HTML"
    )
    await ask_format(callback, state)


@router.callback_query(ApplicationForm.confirm_city, F.data == "step_edit_city")
async def edit_city_callback(callback: CallbackQuery, state: FSMContext):
    """Повторный ввод города"""
    await callback.message.delete()
    await ask_city(callback, state, is_edit=True)


# ==================== ШАГ 4: ФОРМАТ СЪЁМКИ ====================

@router.callback_query(ApplicationForm.waiting_for_format, F.data.startswith("format_choice:"))
async def process_format_button(callback: CallbackQuery, state: FSMContext):
    """Выбор формата через inline-кнопку"""
    format_selected = callback.data.split(":", 1)[1]
    await state.update_data(temp_format=format_selected)
    await state.set_state(ApplicationForm.confirm_format)

    await callback.message.edit_text(
        f"Формат съёмки:\n👉 <b>{html.escape(format_selected)}</b>\n\nОставляем?",
        reply_markup=get_step_confirm_keyboard("format"),
        parse_mode="HTML"
    )


@router.message(ApplicationForm.waiting_for_format, F.text)
async def process_format_text(message: Message, state: FSMContext):
    """Ввод своего формата съёмки текстом"""
    format_entered = message.text.strip()
    await state.update_data(temp_format=format_entered)
    await state.set_state(ApplicationForm.confirm_format)

    await message.answer(
        f"Формат съёмки:\n👉 <b>{html.escape(format_entered)}</b>\n\nОставляем?",
        reply_markup=get_step_confirm_keyboard("format"),
        parse_mode="HTML"
    )


@router.callback_query(ApplicationForm.confirm_format, F.data == "step_confirm_format")
async def confirm_format_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение формата -> переход к итоговой заявке"""
    data = await state.get_data()
    chosen_format = data.get("temp_format")
    await state.update_data(format=chosen_format)
    await callback.message.edit_text(
        f"✅ Формат: <b>{html.escape(str(chosen_format))}</b>",
        parse_mode="HTML"
    )
    await show_summary(callback, state)


@router.callback_query(ApplicationForm.confirm_format, F.data == "step_edit_format")
async def edit_format_callback(callback: CallbackQuery, state: FSMContext):
    """Повторный выбор/ввод формата"""
    await callback.message.delete()
    await ask_format(callback, state, is_edit=True)


# ==================== ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ И ОТПРАВКА АДМИНУ ====================

async def show_summary(target: Message | CallbackQuery, state: FSMContext):
    """Отображение итоговой карточки заявки перед отправкой админу"""
    await state.set_state(ApplicationForm.confirm_final)
    data = await state.get_data()

    name = data.get("name", "—")
    phone = data.get("phone", "—")
    city = data.get("city", "—")
    fmt = data.get("format", "—")

    summary_text = (
        "📋 <b>Чекни заявку перед отправкой:</b>\n\n"
        f"👤 <b>Имя:</b> {html.escape(str(name))}\n"
        f"📱 <b>Связь:</b> {html.escape(str(phone))}\n"
        f"🏙️ <b>Город:</b> {html.escape(str(city))}\n"
        f"📸 <b>Формат:</b> {html.escape(str(fmt))}\n\n"
        "<i>Если всё сходится — жми кнопку ниже 🔥</i>"
    )

    if isinstance(target, CallbackQuery):
        await target.message.answer(
            summary_text,
            reply_markup=get_final_confirm_keyboard(),
            parse_mode="HTML"
        )
        await target.answer()
    else:
        await target.answer(
            summary_text,
            reply_markup=get_final_confirm_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(ApplicationForm.confirm_final, F.data == "final_send")
async def final_send_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Финальная отправка заявки админу"""
    data = await state.get_data()
    user = callback.from_user
    created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    name = data.get("name", "—")
    phone = data.get("phone", "—")
    city = data.get("city", "—")
    fmt = data.get("format", "—")

    user_link = f"@{user.username}" if user.username else "Не указан"
    user_mention = f"<a href=\"tg://user?id={user.id}\">{html.escape(user.full_name)}</a>"

    admin_message = (
        "⚡ <b>НОВАЯ ЗАЯВКА НА СЪЁМКУ!</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Имя клиента:</b> {html.escape(str(name))}\n"
        f"📱 <b>Телефон:</b> <code>{html.escape(str(phone))}</code>\n"
        f"🏙️ <b>Город:</b> {html.escape(str(city))}\n"
        f"📸 <b>Формат:</b> {html.escape(str(fmt))}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>Информация о пользователе:</b>\n"
        f"• Профиль: {user_mention}\n"
        f"• Username: {user_link}\n"
        f"• Telegram ID: <code>{user.id}</code>\n"
        f"• Дата: {created_at}"
    )

    # Отправка администраторам
    admin_count_sent = 0
    if config.admin_ids:
        for admin_id in config.admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode="HTML"
                )
                admin_count_sent += 1
            except Exception as e:
                # В случае если админ не запустил бота или заблокировал его
                logger.error(f"Не удалось отправить заявку админу {admin_id}: {e}")

    await callback.message.edit_text(
        "🖤 <b>Заявка улетела!</b>\n\n"
        "Скоро свяжемся с тобой для обсуждения деталей и мудборда 📸✨\n\n"
        "Если захочешь оформить ещё раз — пиши /start или /apply",
        parse_mode="HTML"
    )

    await state.clear()
    await callback.answer("Заявка успешно отправлена!")


@router.callback_query(ApplicationForm.confirm_final, F.data == "final_restart")
async def final_restart_callback(callback: CallbackQuery, state: FSMContext):
    """Заполнение заявки заново"""
    await callback.message.delete()
    await state.clear()
    await ask_name(callback, state)


@router.callback_query(ApplicationForm.confirm_final, F.data == "final_cancel")
async def final_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена заявки"""
    await state.clear()
    await callback.message.edit_text(
        "🚫 Оформление заявки отменено.\n\nЕсли захочешь снова — тыкай /start или /apply",
        parse_mode="HTML"
    )
    await callback.answer("Заявка отменена")
