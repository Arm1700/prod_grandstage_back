from django.core.management.base import BaseCommand
import os
from shutil import move
from django.conf import settings
from main.models import Event, EventGallery, Course, Gallery, Certificate
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def resize(image: Image.Image, quality: int = 85, max_width: int = 1200,
           original_filename: str = 'image') -> InMemoryUploadedFile:
    """
    Сжимает изображение до заданной ширины (max_width), сохраняя пропорции,
    если изначальная ширина изображения больше max_width.

    :param image: Исходное изображение (PIL.Image).
    :param quality: Качество для сжатия (по умолчанию 85).
    :param max_width: Максимальная ширина изображения после сжатия (по умолчанию 1200px).
    :param original_filename: Имя исходного файла (по умолчанию 'image').
    :return: Объект InMemoryUploadedFile с сжатыми и измененными изображениями.
    """
    # Проверяем, нужно ли изменять размер
    if image.width <= max_width:
        return None  # Если ширина меньше max_width, возвращаем None

    # Рассчитываем новое соотношение ширины и высоты
    width_percent = max_width / float(image.width)
    new_height = int(image.height * width_percent)

    # Меняем размер изображения с сохранением пропорций
    image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Создаем буфер для хранения сжатого изображения
    img_io = BytesIO()
    image.save(img_io, format='WebP', quality=quality)
    img_io.seek(0)

    # Создаем имя файла
    file_name = os.path.splitext(original_filename)[0] + '.webp'

    return InMemoryUploadedFile(img_io, None, file_name, 'image/webp', img_io.tell(), None)


class Command(BaseCommand):
    help = 'Resize images to a maximum width, compress them to WebP, and archive old files'

    def handle(self, *args, **kwargs):
        archive_base_dir = os.path.join(settings.MEDIA_ROOT, '_media')  # Директория для архивирования
        os.makedirs(archive_base_dir, exist_ok=True)  # Создаем папку, если её нет

        def archive_old_file(file_path):
            """
            Перемещает старый файл в папку _media, сохраняя структуру директорий.
            """
            if not os.path.exists(file_path):
                return  # Пропускаем, если файл уже отсутствует

            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)  # Относительный путь файла
            archive_path = os.path.join(archive_base_dir, relative_path)  # Архивный путь

            # Создаем директорию для архива, если её нет
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)

            # Если файл с таким именем уже есть, добавляем суффикс
            if os.path.exists(archive_path):
                base, ext = os.path.splitext(archive_path)
                counter = 1
                while os.path.exists(f"{base}_{counter}{ext}"):
                    counter += 1
                archive_path = f"{base}_{counter}{ext}"

            # Перемещаем файл в архив
            move(file_path, archive_path)

        def resize_and_save_image(obj, field_name):
            """
            Обрабатывает изображение в указанном поле объекта, изменяя размер и формат.
            """
            field = getattr(obj, field_name)
            if field and hasattr(field, 'path') and os.path.exists(field.path):
                try:
                    with Image.open(field.path) as image:
                        resized_image = resize(image, original_filename=field.name)

                        # Пропускаем обработку, если изображение меньше max_width
                        if resized_image is None:
                            return

                        old_path = field.path  # Запоминаем старый путь
                        field.save(resized_image.name, resized_image, save=False)
                        obj.save()

                        # Перемещаем старое изображение в архив
                        archive_old_file(old_path)
                except Exception as e:
                    self.stderr.write(f"Error processing {field.name}: {e}")

        # Обрабатываем модели
        for model, field_name in [
            (Event, 'image'),
            (EventGallery, 'local_image'),
            (Course, 'image'),
            (Gallery, 'img'),
            (Certificate, 'img'),
        ]:
            for instance in model.objects.all():
                resize_and_save_image(instance, field_name)

        self.stdout.write(self.style.SUCCESS('All images have been resized, converted to WebP, and old files archived.'))
