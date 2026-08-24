import asyncio
import logging
import sys

# Настройка UTF-8 вывода для консоли Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import config
from handlers import setup_routers


async def set_bot_commands(bot: Bot):
    """Регистрация команд в меню Telegram"""
    commands = [
        BotCommand(command="start", description="🚀 Главное меню"),
        BotCommand(command="apply", description="📝 Оформить заявку"),
        BotCommand(command="cancel", description="❌ Отменить текущее действие"),
        BotCommand(command="help", description="ℹ️ Помощь и информация"),
    ]
    try:
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    except Exception as e:
        logging.warning(f"Не удалось установить команды меню бота (продолжаем запуск): {e}")


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)

    if not config.bot_token or config.bot_token == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "ОШИБКА: Токен бота не указан! Укажите BOT_TOKEN в файле .env перед запуском."
        )
        sys.exit(1)

    if not config.admin_ids:
        logger.warning(
            "ВНИМАНИЕ: ADMIN_IDS не указаны в файле .env! Заявки не будут отправляться в личные сообщения админу."
        )

    # Настройка сессии с поддержкой прокси и настраиваемым таймаутом
    session = AiohttpSession(
        proxy=config.proxy_url,
        timeout=float(config.request_timeout)
    )

    bot = Bot(
        token=config.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем роутеры
    main_router = setup_routers()
    dp.include_router(main_router)

    try:
        # Проверяем подключение к Telegram
        bot_info = await bot.get_me()

        # Устанавливаем команды бота
        await set_bot_commands(bot)

        print("=" * 55)
        print(f"🚀 Бот @{bot_info.username} успешно запущен и работает!")
        print(f"👑 Администраторы: {config.admin_ids if config.admin_ids else 'Не указаны'}")
        if config.proxy_url:
            print(f"🌐 Используется прокси: {config.proxy_url}")
        print("💡 Перейдите в Telegram и отправьте боту /start")
        print("🛑 Для остановки бота нажмите Ctrl + C")
        print("=" * 55)

        # Пропускаем накопившиеся апдейты и запускаем polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except TelegramNetworkError as e:
        print("\n" + "!" * 55)
        logger.error(f"Сетевая ошибка при подключении к Telegram: {e}")
        print("⚠️ Не удалось установить соединение с серверами Telegram (api.telegram.org).")
        print("💡 Возможные решения:")
        print("  1. Включите VPN (если ваш провайдер или мобильный интернет блокирует Telegram API).")
        print("  2. Или укажите PROXY_URL в файле .env (например: PROXY_URL=socks5://127.0.0.1:10808).")
        print("  3. Проверьте подключение к сети Интернет.")
        print("!" * 55 + "\n")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при работе бота: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Сессия бота закрыта.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
