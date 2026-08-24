from aiogram import Router

from .common import router as common_router
from .application import router as application_router


def setup_routers() -> Router:
    main_router = Router()
    main_router.include_router(common_router)
    main_router.include_router(application_router)
    return main_router


__all__ = ["setup_routers", "common_router", "application_router"]
