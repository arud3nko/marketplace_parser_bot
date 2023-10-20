import logging

from aiogram import Router, types, F
from aiogram.enums import ParseMode

from aiohttp import web

from app.db.db import DB
from app.bot.bot import bot
from app.config.config import (BASE_WEBHOOK_URL, TABLE_PRODUCTS, TABLE_SENT_TO_ADMIN, TABLE_CATEGORIES,
                               ITER_CATEGORY_ID, ITER_PRODUCT_ID, ITER_PRODUCT_TITLE, ITER_PRODUCT_PRICE,
                               ITER_PRODUCT_PRICE_DISCOUNT,
                               ITER_PRODUCT_VENDOR_CODE, ITER_PRODUCT_LINK, ITER_PRODUCT_IMAGE_LINK,
                               ITER_PRODUCT_CREATED_AT,
                               ITER_CATEGORY_ADMIN_CHAT_ID, ITER_CATEGORY_CHANNEL_CHAT_ID,
                               ITER_CATEGORY_MULTI_CHANNEL_CHAT_ID, WEBHOOK_PATH)

post_router = Router()


@post_router.callback_query(F.data.startswith("send_to_channel::"))
async def send_to_channel_query(callback: types.CallbackQuery):
    """
    Отправка товара в канал
    :param callback:
    :return:
    """
    product_id = int(callback.data.split("::")[1])

    db = DB()

    product = await db.select_where(table_name=TABLE_SENT_TO_ADMIN,
                                    where_cond="product_id",
                                    where_value=product_id)

    _, title, price, price_discount, vendor_code, link, image_link, date, category_id, pid = product[0]

    category = await db.select_where(table_name=TABLE_CATEGORIES,
                                     where_cond="id",
                                     where_value=category_id)

    title = title.replace('.', '\\.') \
        .replace('|', '\\|') \
        .replace('-', '\\-') \
        .replace('#', '\\#') \
        .replace('_', '\\_') \
        .replace('!', '\\!') \
        .replace('(', '\\(') \
        .replace(')', '\\)') \
        .replace('+', '\\+') \


    message_1 = f"""*{title}*

📌 *{int(price_discount)} ₽* \| ~{int(price)} ₽~
"""

    message_2 = f"""
{"Код товара: " + vendor_code}
""" if "ozon" in link else ""

    message_3 = f"""
Смотреть на [{"OZON" if "ozon" in link else "WILDBERRIES"}]({link})

❤️ \- Супер
👍🏻 \- Пойдёт
😐 \- Не очень
💵 \- Дороговато

\\#{str(category[0][1]).replace(' ', '_').lower()}
\\#{"ozon" if "ozon" in link else "wildberries"}
""".replace('_', '\_')

    message = message_1 + message_2 + message_3

    await bot.send_photo(chat_id=category[0][ITER_CATEGORY_CHANNEL_CHAT_ID],
                         photo=image_link,
                         caption=message,
                         reply_markup=None,
                         parse_mode=ParseMode.MARKDOWN_V2)

    if category[0][ITER_CATEGORY_MULTI_CHANNEL_CHAT_ID]:
        await bot.send_photo(chat_id=category[0][ITER_CATEGORY_MULTI_CHANNEL_CHAT_ID],
                             photo=image_link,
                             caption=message,
                             reply_markup=None,
                             parse_mode=ParseMode.MARKDOWN_V2)

    await callback.message.delete()

    logging.info(f"Sent post to channel {category[0][ITER_CATEGORY_CHANNEL_CHAT_ID]} | Product ID {product_id}")

    return web.Response(status=200)


@post_router.callback_query(F.data.startswith("drop_post::"))
async def drop_post(callback: types.CallbackQuery):
    """
    Удаление товара из админ-чата
    :param callback:
    :return:
    """
    product_id = int(callback.data.split("::")[1])

    db = DB()

    await db.delete(table_name=TABLE_SENT_TO_ADMIN,
                    where_cond="product_id",
                    where_value=product_id)

    await callback.message.delete()
