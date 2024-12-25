from telegram import Update
from telegram.ext import CallbackContext
from PIL import Image
import os
import tempfile
from FileProcessor import FileProcessor

class MessageHandlerClass:
    """Класс для обработки сообщений."""

    def __init__(self, bot):
        self.bot = bot

    async def handle_zip(self, update: Update, context: CallbackContext):
        file = update.message.document
        file_info = await file.get_file()
        file_bytes = await file_info.download_as_bytearray()

        with tempfile.TemporaryDirectory() as temp_dir:
            if not FileProcessor.extract_zip(file_bytes, temp_dir):
                await update.message.reply_text("Ошибка: это не ZIP файл или файл поврежден.")
                return

            if self.bot.expected_type == 'background':
                await self.bot.process_background_zip(temp_dir, update)
            elif self.bot.expected_type == 'overlay':
                await self.bot.process_overlay_zip(temp_dir, update)

    async def handle_photo(self, update: Update, context: CallbackContext):
        file = update.message.photo[-1]
        file_info = await file.get_file()
        file_path = os.path.join(tempfile.gettempdir(), f"temp_{file.file_id}.jpg")
        await file_info.download_to_drive(file_path)

        if self.bot.expected_type == 'background':
            self.bot.image_manager.add_background(Image.open(file_path))
            reply_markup = self.bot.create_main_menu_button()
            await update.message.reply_text("Фон получен.", reply_markup=reply_markup)
        else:
            reply_markup = self.bot.create_main_menu_button()
            await update.message.reply_text("Ошибка: фото принимаются только для фонов.", reply_markup=reply_markup)

    async def handle_png_document(self, update: Update, context: CallbackContext):
        if self.bot.expected_type != 'overlay':
            reply_markup = self.bot.create_main_menu_button()
            await update.message.reply_text("Ошибка: PNG файлы принимаются только для шаблонов.",
                                            reply_markup=reply_markup)
            return

        file = update.message.document
        file_info = await file.get_file()
        file_path = os.path.join(tempfile.gettempdir(), f"overlay_{file.file_id}.png")
        await file_info.download_to_drive(file_path)

        self.bot.image_manager.add_overlay(Image.open(file_path))
        reply_markup = self.bot.create_main_menu_button()
        await update.message.reply_text("Шаблон (PNG) получен.", reply_markup=reply_markup)

    async def handle_sets_count(self, update: Update, context: CallbackContext):
        try:
            sets_count = int(update.message.text)
            if sets_count > 0:
                if sets_count > len(self.bot.image_manager.background_images):
                    reply_markup = self.bot.create_main_menu_button()
                    await update.message.reply_text(
                        f"Ошибка: недостаточно фонов для создания {sets_count} наборов. Пожалуйста, загрузите больше фонов.",
                        reply_markup=reply_markup
                    )
                else:
                    self.bot.generated_sets_count = sets_count
                    await update.message.reply_text(
                        f"Количество наборов установлено: {sets_count}. Генерация начнется.")
                    await self.bot.generate_images(update.message)
            else:
                await update.message.reply_text("Пожалуйста, введите положительное число.")
        except ValueError:
            await update.message.reply_text("Ошибка: Пожалуйста, введите число.")