from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


class ButtonHandler:
    """Класс для обработки нажатий на кнопки."""

    def __init__(self, bot):
        self.bot = bot

    async def button_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        message = query.message

        if query.data == "send_background":
            self.bot.expected_type = 'background'
            reply_markup = self.bot.create_main_menu_button()
            await message.edit_text("Пожалуйста, отправьте ZIP архив с фонами или изображения (форматы: PNG, JPG).",
                                    reply_markup=reply_markup)

        elif query.data == "send_overlay":
            self.bot.expected_type = 'overlay'
            reply_markup = self.bot.create_main_menu_button()
            await message.edit_text("Пожалуйста, отправьте ZIP архив с шаблонами или изображения (форматы: PNG, JPG).",
                                    reply_markup=reply_markup)

        elif query.data == "generate_images":
            if self.bot.image_manager.background_images and self.bot.image_manager.overlay_images:
                keyboard = [
                    [InlineKeyboardButton("Генерировать для всех фонов", callback_data="generate_all_sets")],
                    [InlineKeyboardButton("Введите количество наборов", callback_data="input_sets_count")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text("Как вы хотите генерировать изображения?", reply_markup=reply_markup)
            else:
                await message.edit_text(
                    "Не все изображения получены. Пожалуйста, отправьте архивы с фонами и шаблонами.")
                reply_markup = self.bot.create_main_menu_button()
                await message.reply_text("Вы можете вернуться в главное меню.", reply_markup=reply_markup)

        elif query.data == "clear_all":
            self.bot.image_manager.clear_images()
            await message.edit_text("Все изображения и настройки очищены. Пожалуйста, отправьте новые архивы.")
            reply_markup = self.bot.create_main_menu_button()
            await message.reply_text("Вы можете вернуться в главное меню.", reply_markup=reply_markup)

        elif query.data == "back_to_main_menu":
            await self.bot.start_command(update, context)

        elif query.data == "send_as_zip":
            await self.bot.send_images_as_zip(message)

        elif query.data == "send_individually":
            await self.bot.send_images_individually(message)

        elif query.data == "generate_all_sets":
            self.bot.generated_sets_count = len(self.bot.image_manager.background_images)
            await self.bot.generate_images(message)

        elif query.data == "input_sets_count":
            await message.edit_text("Введите количество наборов для генерации:")