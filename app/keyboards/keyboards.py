from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_kb_cancel_multi_channel() -> InlineKeyboardMarkup:
    inline_kb_accept = [
        [InlineKeyboardButton(text="Не отправлять в мульти-канал", callback_data=f"cancel_multi_channel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_accept)


def build_kb_send_to_channel(ID: int) -> InlineKeyboardMarkup:
    inline_kb_accept_post = [
        [InlineKeyboardButton(text="Опубликовать".upper(), callback_data=f"send_to_channel::{ID}")],
        [InlineKeyboardButton(text="Удалить".upper(), callback_data=f"drop_post::{ID}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_accept_post)
