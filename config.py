import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_ids: list[int]
    proxy_url: str | None
    request_timeout: int


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
    proxy_url_raw = os.getenv("PROXY_URL", "").strip()
    timeout_raw = os.getenv("REQUEST_TIMEOUT", "60").strip()

    admin_ids: list[int] = []
    if admin_ids_raw:
        for item in admin_ids_raw.split(","):
            cleaned = item.strip()
            if cleaned.isdigit():
                admin_ids.append(int(cleaned))

    proxy_url = proxy_url_raw if proxy_url_raw else None
    request_timeout = int(timeout_raw) if timeout_raw.isdigit() else 60

    return Config(
        bot_token=bot_token,
        admin_ids=admin_ids,
        proxy_url=proxy_url,
        request_timeout=request_timeout,
    )


config = load_config()
