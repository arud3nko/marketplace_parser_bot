from aiogram import Router
from aiohttp import web

router = Router()


@router.message()
async def skip_any_messages(message):
    """
    Отвечаем на неотслеживаемые сообщения

    :return:
    """
    return web.Response(status=401)
