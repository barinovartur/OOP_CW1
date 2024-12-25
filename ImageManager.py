from PIL import Image
import zipfile

import tempfile

class ImageManager:
    """Класс для управления изображениями."""

    def __init__(self):
        self.background_images = []
        self.overlay_images = []
        self.result_images = []

    def add_background(self, image):
        self.background_images.append(image)

    def add_overlay(self, image):
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

    def save_images_as_zip(self, temp_zip):
        with zipfile.ZipFile(temp_zip, 'w') as zipf:
            for idx, result in enumerate(self.result_images):
                img_filename = f"image_{idx + 1}.png"
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    result.save(temp_file, "PNG")
                    temp_file.seek(0)
                    zipf.write(temp_file.name, img_filename)

    def save_images_individually(self):
        temp_files = []
        for result in self.result_images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                result.save(temp_file, "PNG")
                temp_files.append(temp_file.name)
        return temp_files
