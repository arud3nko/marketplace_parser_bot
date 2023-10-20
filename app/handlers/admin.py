from app.bot.states.new_category import NewCategoryStates
from app.enums.dialogs import NewCategory

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.enums import ParseMode

from app.db.db import DB
from app.config.config import (DB_CATEGORIES_TABLE, SUPER_ADMIN_CHAT_ID, TABLE_CATEGORIES,
                               ITER_CATEGORY_ID, ITER_CATEGORY_NAME, ITER_CATEGORY_OZON_LINK, ITER_CATEGORY_WB_LINK,
                               ITER_CATEGORY_ADMIN_CHAT_ID, ITER_CATEGORY_CHANNEL_CHAT_ID,
                               ITER_CATEGORY_MULTI_CHANNEL_CHAT_ID)
from app.keyboards.keyboards import build_kb_cancel_multi_channel

admin_router = Router()


def format_special_chars(string: str) -> str:
    # return string.replace("_", '\\_')\
    #               .replace("*", '\\*')\
    #               .replace("[", '\\[')\
    #               .replace("]", '\\]')\
    #               .replace("(", '\\(')\
    #               .replace(")", '\\)')\
    #               .replace("~", '\\~')\
    #               .replace("`", '\\`')\
    #               .replace(">", '\\>')\
    #               .replace("#", '\\#')\
    #               .replace("+", '\\+')\
    #               .replace("-", '\\-')\
    #               .replace("=", '\\=')\
    #               .replace("|", '\\|')\
    #               .replace("{", '\\{')\
    #               .replace("}", '\\}')\
    #               .replace(".", '\\.')\
    #               .replace("!", '\\!')

    return string


def format_category_info_message(ID: int, name: str, ozon: str, wb: str, admin: str, channel: str, multi: str) -> str:
    return f"""<b>{format_special_chars(name)}</b>\n
<b>id</b>: {ID}
<b>ozon</b>: {format_special_chars(ozon)}
<b>wb</b>: {format_special_chars(wb)}
<b>admin</b>: {format_special_chars(admin)}
<b>channel</b>: {format_special_chars(channel)}
<b>multi_channel</b>: {format_special_chars(multi)}\n
"""


@admin_router.message(Command(commands='cancel'), ~StateFilter(default_state), F.chat.id == SUPER_ADMIN_CHAT_ID)
async def process_cancel_command_state(message: Message, state: FSMContext):
    await state.clear()


@admin_router.message(Command(commands='cancel'), StateFilter(default_state), F.chat.id == SUPER_ADMIN_CHAT_ID)
async def process_cancel_command_state_default(message: Message, state: FSMContext):
    await state.clear()


@admin_router.message(Command(commands='delete'), StateFilter(default_state), F.chat.id == SUPER_ADMIN_CHAT_ID)
async def delete_category_handler(message: Message, state: FSMContext):
    db = DB()

    categories = await db.select(table_name=TABLE_CATEGORIES)

    all_categories_formatted_message = ""

    for category in categories:
        all_categories_formatted_message += format_category_info_message(
            ID=category[ITER_CATEGORY_ID],
            name=category[ITER_CATEGORY_NAME],
            ozon=category[ITER_CATEGORY_OZON_LINK],
            wb=category[ITER_CATEGORY_WB_LINK],
            admin=category[ITER_CATEGORY_ADMIN_CHAT_ID],
            channel=category[ITER_CATEGORY_CHANNEL_CHAT_ID],
            multi=category[ITER_CATEGORY_MULTI_CHANNEL_CHAT_ID]
        )

    await message.answer(
        text=all_categories_formatted_message,
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        text=NewCategory.GET_TO_DELETE_ID
    )
    await state.set_state(NewCategoryStates.get_to_delete_id)


@admin_router.message(StateFilter(NewCategoryStates.get_to_delete_id), F.chat.id == SUPER_ADMIN_CHAT_ID)
async def get_to_delete_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(text="Ошибка: ID категории должен быть числом")

    db = DB()
    categories = await db.select(table_name=TABLE_CATEGORIES)

    ID = int(message.text)
    IDs = [category[ITER_CATEGORY_ID] for category in categories]

    if not ID in IDs:
        await message.answer(text="Ошибка: категория с таким ID не найдена")

    try:
        await db.delete(table_name=TABLE_CATEGORIES,
                        where_cond="id",
                        where_value=ID)
        await message.answer(
            text=NewCategory.OK_DELETE
        )
    except Exception as e:
        await message.answer(text=f"Ошибка при удалении категории: {e}")
    finally:
        await state.clear()


@admin_router.message(Command(commands='new_category'), StateFilter(default_state), F.chat.id == SUPER_ADMIN_CHAT_ID)
async def new_category_handler(message: Message, state: FSMContext):
    await message.answer(
        text=NewCategory.GET_TITLE
    )
    await state.set_state(NewCategoryStates.get_category_title)


@admin_router.message(StateFilter(NewCategoryStates.get_category_title), F.chat.id == SUPER_ADMIN_CHAT_ID)
async def set_title(message: Message, state: FSMContext):
    await message.answer(
        text=NewCategory.GET_WB_LINK
    )
    await state.update_data(category_title=message.text)
    await state.set_state(NewCategoryStates.get_wb_category_link)


@admin_router.message(NewCategoryStates.get_wb_category_link,
                      F.text.startswith("https://") & F.chat.id == SUPER_ADMIN_CHAT_ID)
async def set_wb_link(message: Message, state: FSMContext):
    await state.update_data(category_wb_link=message.text)
    await message.answer(
        text=NewCategory.GET_OZON_LINK
    )
    await state.set_state(NewCategoryStates.get_ozon_category_link)


@admin_router.message(NewCategoryStates.get_ozon_category_link,
                      F.text.startswith("https://") & F.chat.id == SUPER_ADMIN_CHAT_ID)
async def set_wb_link(message: Message, state: FSMContext):
    await state.update_data(category_ozon_link=message.text)
    await message.answer(
        text=NewCategory.GET_ADMIN_CHAT_ID
    )
    await state.set_state(NewCategoryStates.get_admin_chat_id)


@admin_router.message(NewCategoryStates.get_admin_chat_id, F.chat.id == SUPER_ADMIN_CHAT_ID)
async def set_admin_chat_id(message: Message, state: FSMContext):
    await state.update_data(admin_chat_id=message.text)
    await message.answer(
        text=NewCategory.GET_CHANNEL_CHAT_ID
    )
    await state.set_state(NewCategoryStates.get_channel_chat_id)


@admin_router.message(NewCategoryStates.get_channel_chat_id, F.chat.id == SUPER_ADMIN_CHAT_ID)
async def set_channel_chat_id(message: Message, state: FSMContext):
    if not message.text[0] == "@":
        await message.answer(text="Ошибка: ID (никнейм) канала должен начинаться с @\nПример: @test")
        return

    await state.update_data(channel_chat_id=message.text)
    await message.answer(
        text=NewCategory.GET_MULTI_CHANNEL_CHAT_ID,
        reply_markup=build_kb_cancel_multi_channel()
    )
    await state.set_state(NewCategoryStates.get_multi_channel_chat_id)


@admin_router.callback_query(NewCategoryStates.get_multi_channel_chat_id, F.data.startswith("cancel_multi_channel"))
async def cancel_multi_channel(callback: CallbackQuery, state: FSMContext):
    await state.update_data(multi_channel_chat_id=None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await create_category(state, callback.message)


@admin_router.message(NewCategoryStates.get_multi_channel_chat_id, F.chat.id == SUPER_ADMIN_CHAT_ID)
async def set_multi_channel_chat_id(message: Message, state: FSMContext):
    if not message.text[0] == "@":
        await message.answer(text="Ошибка: ID (никнейм) канала должен начинаться с @\nПример: @test")
        return

    await state.update_data(multi_channel_chat_id=message.text)

    await create_category(state, message)


async def create_category(state, message):
    category_data = await state.get_data()
    db = DB()

    await db.insert(table_name=DB_CATEGORIES_TABLE,
                    title=category_data["category_title"],
                    wb_link=category_data["category_wb_link"],
                    ozon_link=category_data["category_ozon_link"],
                    admin_chat_id=category_data["admin_chat_id"],
                    channel_chat_id=category_data["channel_chat_id"],
                    multi_channel_chat_id=category_data["multi_channel_chat_id"])

    await message.answer(
        text=NewCategory.OK
    )

    await state.clear()
