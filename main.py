from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from PIL import Image
import os
import tempfile
import logging
from ImageManager import ImageManager
from MessageHandler import MessageHandlerClass
from ButtonHandler import ButtonHandler
from CommandHandlerClass import CommandHandlerClass


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class SettingsManager:
    def __init__(self):
        self.crop_to_9_16 = False  # По умолчанию обрезка отключена

    def set_crop_to_9_16(self, value):
        self.crop_to_9_16 = value

    def should_crop_to_9_16(self):
        return self.crop_to_9_16


class AutoCreoBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self.settings = SettingsManager()
        self.image_manager = ImageManager(self.settings)

        self.expected_type = None
        self.generated_sets_count = 0
        self.message_handler = MessageHandlerClass(self)
        self.button_handler = ButtonHandler(self)
        self.command_handler = CommandHandlerClass(self)
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.command_handler.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler.button_handler))
        self.application.add_handler(MessageHandler(filters.Document.MimeType("application/zip"), self.message_handler.handle_zip))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.message_handler.handle_photo))
        self.application.add_handler(MessageHandler(filters.Document.MimeType("image/png"), self.message_handler.handle_png_document))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler.handle_sets_count))

    def create_main_menu_button(self):
        keyboard = [
            [InlineKeyboardButton("Вернуться в главное меню", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("Обрезать до 9:16", callback_data="toggle_crop_setting")]  # Добавьте это
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start_command(self, update: Update, context: CallbackContext):
        await self.command_handler.start(update, context)

    async def process_background_zip(self, temp_dir: str, update: Update):
        found_backgrounds = False
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if filename.lower().endswith(('png', 'jpg', 'jpeg')):
                try:
                    self.image_manager.add_background(Image.open(file_path))
                    found_backgrounds = True
                except Exception as e:
                    logger.error(f"Ошибка при открытии файла {filename}: {e}")

        if found_backgrounds:
            reply_markup = self.create_main_menu_button()
            await update.message.reply_text(f"Фоны получены, всего фонов: {len(self.image_manager.background_images)}.",
                                            reply_markup=reply_markup)
        else:
            reply_markup = self.create_main_menu_button()
            await update.message.reply_text("Не было найдено фонов в архиве.", reply_markup=reply_markup)

    async def process_overlay_zip(self, temp_dir: str, update: Update):
        found_overlay = False
        for filename in os.listdir(temp_dir):
            if filename.lower().endswith('.png'):
                try:
                    file_path = os.path.join(temp_dir, filename)
                    self.image_manager.add_overlay(Image.open(file_path))
                    found_overlay = True
                except Exception as e:
                    logger.error(f"Ошибка при обработке файла {filename}: {e}")
        if found_overlay:
            reply_markup = self.create_main_menu_button()
            await update.message.reply_text(f"Шаблоны (PNG) получены: {len(self.image_manager.overlay_images)}.",
                                            reply_markup=reply_markup)
        else:
            reply_markup = self.create_main_menu_button()
            await update.message.reply_text("В архиве не найдено PNG изображений.", reply_markup=reply_markup)

    async def generate_images(self, message):
        sets_to_generate = self.generated_sets_count if self.generated_sets_count > 0 else len(
            self.image_manager.background_images)
        self.image_manager.generate_images(sets_to_generate)

        keyboard = [
            [InlineKeyboardButton("Отправить как ZIP файл", callback_data="send_as_zip")],
            [InlineKeyboardButton("Отправить по очереди", callback_data="send_individually")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("Изображения успешно сгенерированы. Выберите способ отправки:",
                                 reply_markup=reply_markup)

    async def send_images_as_zip(self, message):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
            self.image_manager.save_images_as_zip(temp_zip.name)
            await message.reply_document(document=open(temp_zip.name, 'rb'), filename="result_images.zip")
        # Отправляем сообщение о завершении и добавляем кнопку возврата в главное меню
        keyboard = [[InlineKeyboardButton("Вернуться в главное меню", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("Файлы успешно отправлены! 🎉", reply_markup=reply_markup)

    async def send_images_individually(self, message):
        temp_files = self.image_manager.save_images_individually()
        for file_path in temp_files:
            await message.reply_document(document=open(file_path, 'rb'), filename=os.path.basename(file_path))
            os.remove(file_path)

        # Отправляем сообщение о завершении и добавляем кнопку возврата в главное меню
        keyboard = [[InlineKeyboardButton("Вернуться в главное меню", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("Фото успешно отправлены! 🎉", reply_markup=reply_markup)

    def run(self):
        self.application.run_polling()





if __name__ == "__main__":
    with open('api_token.txt', 'r') as file:
        api_token = file.read().strip()
    bot = AutoCreoBot(api_token)
    bot.run()