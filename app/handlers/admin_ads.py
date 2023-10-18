from app.bot.bot import bot
from app.keyboards.keyboards import build_kb_send_to_channel

from typing import Any
from aiohttp import web

from aiogram.enums import ParseMode


def format_message(data: Any):
    title = data['title'].replace('.', '\\.')\
                     .replace('|', '\\|')\
                     .replace('-', '\\-')\
                     .replace('#', '\\#')\
                     .replace('_', '\\_')\
                     .replace('!', '\\!')\
                     .replace('(', '\\(')\
                     .replace(')', '\\)')\
                     .replace('+', '\\+')\

    message_1 = f"""*{title}*

📌 *{data['price_discount']} ₽* \| ~{data['price']} ₽~
"""

    message_2 = f"""
{"Код товара: " + data['vendor_code'] }
""" if "ozon" in data['link'] else ""

    message_3 = f"""
Смотреть на [{"OZON" if "ozon" in data['link'] else "WILDBERRIES"}]({data['link']})

❤️ \- Супер
👍🏻 \- Пойдёт
😐 \- Не очень
💵 \- Дороговато

"""

    message = message_1 + message_2 + message_3

    return message


async def format_dict(json_request: Any) -> dict:
    """
    Форматируем запрос из вебхуков в словарь
    :param json_request:
    :return:
    """

    data = {
        'product_id': json_request['product_id'],
        'admin_chat_id': json_request['admin_chat_id'],
        'channel_chat_id': json_request['channel_chat_id'],
        'multi_chat_id': json_request['multi_chat_id'],
        'title': json_request['title'],
        'price': json_request['price'],
        'price_discount': json_request['price_discount'],
        'vendor_code': json_request['vendor_code'],
        'link': json_request['link'],
        'image_link': json_request['image_link'],
        'category_id': json_request['category_id']
    }

    return data


async def admin_check_handler(request):
    """
    Отправляем запрос из вебхуков на проверку администратору канала
    :param request:
    :return: ОК
    """

    json_data = await request.json()
    data = await format_dict(json_data)

    message = format_message(data)

    await bot.send_photo(chat_id=data['admin_chat_id'],
                         photo=data['image_link'],
                         caption=message,
                         reply_markup=build_kb_send_to_channel(data['product_id']),
                         parse_mode=ParseMode.MARKDOWN_V2)

    return web.Response(status=200)
