import os
from django.core.management.base import BaseCommand
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from main.models import Event, EventGallery, Course, Gallery, Certificate
from django.conf import settings


def compress_and_convert_to_webp(image: Image.Image, quality: int = 85,
                                 original_filename: str = 'image') -> InMemoryUploadedFile:
    """Сжимает и конвертирует изображение в формат WebP, и создаёт файл с новым именем."""
    # Создаём новый буфер для изображения
    img_io = BytesIO()
    # Конвертируем изображение в формат WebP
    image.save(img_io, format='WebP', quality=quality)
    img_io.seek(0)

    # Создаём имя файла, если оно не передано
    file_name = original_filename.split('.')[0] + '.webp'

    # Возвращаем обработанное изображение как InMemoryUploadedFile
    return InMemoryUploadedFile(img_io, None, file_name, 'image/webp', img_io.tell(), None)


class Command(BaseCommand):
    help = 'Convert all old images to WebP format with compression and remove old images'

    def handle(self, *args, **kwargs):
        # Функция для обработки фотографий в модели
        def process_image_field(obj, field_name):
            field = getattr(obj, field_name)
            if field:
                # Если это ImageField, получаем имя файла
                original_filename = field.name if hasattr(field, 'name') else 'image'

                # Открываем изображение
                image = Image.open(field)

                # Преобразуем в формат WebP с уменьшением качества
                webp_image = compress_and_convert_to_webp(image, original_filename=original_filename)

                # Обновляем поле изображения в объекте
                setattr(obj, field_name, webp_image)

                # Сохраняем объект
                obj.save()

                # Закрываем изображение после использования
                image.close()

                # Удаляем старое изображение, если оно существует
                if hasattr(field, 'path') and os.path.exists(field.path):
                    try:
                        os.remove(field.path)
                        self.stdout.write(self.style.SUCCESS(f'Old image removed: {field.path}'))
                    except PermissionError:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to delete old image: {field.path} - File is in use'))

                self.stdout.write(self.style.SUCCESS(f'Converted and saved image for {obj}'))

        # Обрабатываем все события
        events = Event.objects.all()
        for event in events:
            process_image_field(event, 'image')

        # Обрабатываем галереи для событий
        galleries = EventGallery.objects.all()
        for gallery in galleries:
            process_image_field(gallery, 'local_image')

        # Обрабатываем курсы
        courses = Course.objects.all()
        for course in courses:
            process_image_field(course, 'image')

        # Обрабатываем галереи для курсов
        course_galleries = Gallery.objects.all()
        for gallery in course_galleries:
            process_image_field(gallery, 'img')

        # Обрабатываем сертификаты
        certificates = Certificate.objects.all()
        for certificate in certificates:
            process_image_field(certificate, 'img')

        self.stdout.write(self.style.SUCCESS('All images have been converted to WebP format.'))
