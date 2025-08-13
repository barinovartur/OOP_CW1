from PIL import Image
import zipfile
import os
import tempfile

class ImageManager:
    """Класс для управления изображениями."""

    def __init__(self, settings):
        self.settings = settings  # Сохраняем настройки
        self.background_images = []
        self.overlay_images = []
        self.generated_images = []

    def crop_to_9_16(self, image):
        width, height = image.size
        target_ratio = 9 / 16

        if width / height > target_ratio:
            # Обрезаем по ширине
            new_width = int(height * target_ratio)
            x = (width - new_width) // 2
            return image.crop((x, 0, x + new_width, height))
        else:
            # Обрезаем по высоте
            new_height = int(width / target_ratio)
            y = (height - new_height) // 2
            return image.crop((0, y, width, y + new_height))
    def add_background(self, image):
        if self.settings.should_crop_to_9_16():  # Добавьте проверку настроек
            image = self.crop_to_9_16(image)
        self.background_images.append(image)


    def add_overlay(self, image):
        if self.settings.should_crop_to_9_16():  # Добавьте проверку настроек
            image = self.crop_to_9_16(image)
        self.overlay_images.append(image)

    def clear_images(self):
        self.background_images.clear()
        self.overlay_images.clear()
        self.result_images.clear()

    def generate_images(self, sets_count: int):
        self.result_images = []
        for i in range(sets_count):
            bg = self.background_images[i % len(self.background_images)]
            for overlay in self.overlay_images:
                bg = bg.convert("RGBA")
                overlay = overlay.convert("RGBA")
                overlay_resized = overlay.resize(bg.size, Image.Resampling.LANCZOS)
                result = Image.alpha_composite(bg, overlay_resized)
                self.result_images.append(result)

    def save_images_as_zip(self, zip_path):
        # Создание ZIP архива
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Идем по всем шаблонам
            for idx, overlay in enumerate(self.overlay_images):
                folder_name = str(idx + 1)  # Имя папки будет номером шаблона
                folder_path = f"{folder_name}/"  # Папка внутри архива

                # Создаем папку (фактически создаем пустой файл для создания папки)
                zipf.writestr(folder_path, '')

                # Генерируем изображения для текущего шаблона и сохраняем их в соответствующую папку
                for img_idx in range(idx, len(self.background_images) * len(self.overlay_images), len(self.overlay_images)):
                    if img_idx >= len(self.result_images):
                        break  # Если индекс выходит за пределы, то прекращаем обработку

                    result = self.result_images[img_idx]  # Изображение для текущего фона и шаблона
                    img_filename = f"{folder_path}image_{img_idx + 1}.png"  # Имя файла для изображения

                    # Сохраняем изображение во временный файл
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                        result.save(temp_file, "PNG")
                        temp_file.seek(0)

                        # Читаем данные изображения из временного файла
                        with open(temp_file.name, 'rb') as image_file:
                            img_data = image_file.read()

                        # Записываем изображение в папку внутри архива
                        zipf.writestr(img_filename, img_data)

                    # Удаляем временный файл
                    os.remove(temp_file.name)

    def save_images_individually(self):
        temp_files = []
        for result in self.result_images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                result.save(temp_file, "PNG")
                temp_files.append(temp_file.name)
        return temp_files