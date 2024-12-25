from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import os
import tempfile
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
class ImageSender:
    """Класс для отправки изображений (как ZIP-архив или по отдельности)."""

    def __init__(self, image_manager):
        self.image_manager = image_manager

    async def send_images_as_zip(self, message):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
            self.image_manager.save_images_as_zip(temp_zip.name)
            await message.reply_document(document=open(temp_zip.name, 'rb'), filename="result_images.zip")
        # Отправляем сообщение о завершении и добавляем кнопку возврата в главное меню
        keyboard = [[InlineKeyboardButton("Вернуться в главное меню", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("Файлы успешно отправлены! 🎉", reply_markup=reply_markup)

    class ImageSender:
        def __init__(self, image_manager):
            self.image_manager = image_manager

        async def send_images_individually(self, message):
            if message is None:
                logger.error("Ошибка: объект message равен None.")
                return

            temp_files = self.image_manager.save_images_individually()
            for file_path in temp_files:
                try:
                    await message.reply_document(document=open(file_path, 'rb'), filename=os.path.basename(file_path))
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Ошибка при отправке документа: {e}")

            keyboard = [[InlineKeyboardButton("Вернуться в главное меню", callback_data="back_to_main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text("Фото успешно отправлены! 🎉", reply_markup=reply_markup)