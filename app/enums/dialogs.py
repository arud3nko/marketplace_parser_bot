from enum import StrEnum


class NewCategory(StrEnum):
    GET_TITLE = "Отправьте название категории"
    GET_WB_LINK = "Отправьте ссылку на WB"
    GET_OZON_LINK = "Отправьте ссылку на OZON"
    GET_ADMIN_CHAT_ID = "Отправьте ID админ-чата"
    GET_CHANNEL_CHAT_ID = "Отправьте ID (никнейм) канала"
    GET_MULTI_CHANNEL_CHAT_ID = "Отправьте ID (никнейм) общего канала"
    OK = "Категория успешно добавлена"
