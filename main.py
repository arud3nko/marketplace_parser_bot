import logging
import sys

from aiohttp import web

from aiogram import Dispatcher, Router, Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.enums.update_type import UpdateType

from app.bot.bot import bot
from app.bot.commands.admin import set_admit_commands
from app.handlers.admin_ads import admin_check_handler
from app.handlers import post, admin, any
from app.config.config import (BASE_WEBHOOK_URL, WEBHOOK_PATH, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_SECRET,
                               LOCALHOST_ADDR, ADMIN_WEBHOOK_PATH)

from aiogram.fsm.storage.redis import Redis, RedisStorage

router = Router()

redis = Redis(host=LOCALHOST_ADDR)
storage = RedisStorage(redis=redis)


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}/{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET,
                          allowed_updates=[UpdateType.MESSAGE,
                                           UpdateType.CALLBACK_QUERY])

    await set_admit_commands()


def main() -> None:
    dp = Dispatcher(storage=storage)

    dp.include_routers(router,
                       post.post_router,
                       admin.admin_router,
                       any.router)

    dp.startup.register(on_startup)

    app = web.Application()
    app.add_routes([web.post(f"/{ADMIN_WEBHOOK_PATH}", admin_check_handler)])

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=f"/{WEBHOOK_PATH}")

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
