import zipfile
from io import BytesIO
import logging


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessor:

    """Класс для обработки файлов, таких как ZIP-архивы."""

    @staticmethod
    def extract_zip(file_bytes: bytes, temp_dir: str):
        try:
            with zipfile.ZipFile(BytesIO(file_bytes), 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            return True
        except zipfile.BadZipFile:
            logger.error("Ошибка: это не ZIP файл или файл поврежден.")
            return False