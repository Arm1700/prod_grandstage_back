import os
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from main.models import Event, EventGallery, Course, Gallery, Certificate
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def resize(image: Image.Image, quality: int = 85, max_width: int = 1200,
           original_filename: str = 'image') -> InMemoryUploadedFile:
    """
    Сжимает изображение до заданной ширины (max_width), сохраняя пропорции.
    """
    if image.width <= max_width:
        return None  # Если ширина меньше max_width, возвращаем None

    width_percent = max_width / float(image.width)
    new_height = int(image.height * width_percent)
    image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

    img_io = BytesIO()
    image.save(img_io, format='WebP', quality=quality)
    img_io.seek(0)

    file_name = os.path.splitext(original_filename)[0] + '.webp'

    return InMemoryUploadedFile(img_io, None, file_name, 'image/webp', img_io.tell(), None)

def delete_resized_images():
    """
    Удаляет все файлы с суффиксом '_resized.webp' во всех папках внутри MEDIA_ROOT.
    """
    media_root = settings.MEDIA_ROOT
    for dirpath, dirnames, filenames in os.walk(media_root):
        for filename in filenames:
            if filename.endswith('_resized.webp'):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

def delete_old_file(file_path):
    """
    Удаляет старый файл с дополнительной отладкой, если это файл с суффиксом _resized.webp.
    """
    try:
        print(f"Attempting to delete file: {file_path}")  # Вывод полного пути
        if os.path.exists(file_path):
            # Изменяем права на файл перед удалением (если необходимо)
            os.chmod(file_path, 0o777)  # Разрешаем чтение, запись и выполнение для всех
            # Добавляем небольшую задержку перед удалением, чтобы файл был освобожден
            time.sleep(0.1)  # Задержка 100 миллисекунд
            os.remove(file_path)
            print(f"Old file {file_path} deleted.")
        else:
            print(f"File {file_path} does not exist.")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

class Command(BaseCommand):
    help = 'Resize images to a maximum width, compress them to WebP, and delete old files'

    def handle(self, *args, **kwargs):
        def resize_and_save_image(obj, field_name):
            """
            Обрабатывает изображение в указанном поле объекта, изменяя размер и формат.
            """
            field = getattr(obj, field_name)
            if field and field.name:
                try:
                    old_path = os.path.join(settings.MEDIA_ROOT, field.name)
                    if os.path.exists(old_path):  # Проверяем существование файла перед обработкой
                        with Image.open(old_path) as image:
                            resized_image = resize(image, original_filename=field.name)

                            if resized_image is None:
                                print(f"Image {field.name} is smaller than max_width, skipping.")
                                return  # Если изображение меньше max_width, ничего не делаем

                            # Получаем путь и имя файла без расширения
                            base_path = os.path.dirname(old_path)  # Путь к папке с изображениями
                            original_name = os.path.splitext(os.path.basename(field.name))[0]  # Без расширения
                            new_filename = os.path.join(base_path,
                                                        f"{original_name}_resized.webp")  # Новый файл с суффиксом _resized

                            # Удаляем старый файл, если он существует
                            delete_old_file(old_path)

                            # Сохраняем новый файл с WebP форматом
                            with open(new_filename, 'wb') as f:
                                f.write(resized_image.read())  # Используем read, чтобы записать данные из InMemoryUploadedFile

                            # Обновляем путь в модели, используя относительный путь
                            field.name = os.path.relpath(new_filename, settings.MEDIA_ROOT)  # Путь относительно MEDIA_ROOT

                            # Сохраняем объект модели с новым файлом
                            obj.save()  # Сохраняем модель, чтобы обновить поле изображения


                except Exception as e:
                    print(f"Error processing {field.name}: {e}")

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

        # После обработки всех изображений вызываем удаление всех старых файлов _resized.webp
        delete_resized_images()

        self.stdout.write(self.style.SUCCESS('All images have been resized, converted to WebP, old files deleted, and database updated.'))
