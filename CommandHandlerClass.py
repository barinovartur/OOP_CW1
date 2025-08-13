from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


class CommandHandlerClass:
    """Класс для обработки команд."""

    def __init__(self, bot):
        self.bot = bot

    async def start(self, update: Update, context: CallbackContext):
        keyboard = [
            [InlineKeyboardButton("📩Отправить фоны", callback_data="send_background")],
            [InlineKeyboardButton("📥Отправить шаблоны", callback_data="send_overlay")],
            [InlineKeyboardButton("📍Генерировать изображения", callback_data="generate_images")],
            [InlineKeyboardButton("🗑Очистить все", callback_data="clear_all")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.message:
            await update.message.reply_text("Добро пожаловать в Auto Creo Bot!🙌🏻\nВыберите одно из действий ниже:",
                                            reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.edit_text("Выберите одно из действий ниже:",
                                                          reply_markup=reply_markup)