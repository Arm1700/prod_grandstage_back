from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import date

STATUS_CHOICES_EVENT = [
    ('upcoming', 'Upcoming'),
    ('happening', 'Happening'),
    ('completed', 'Completed'),
]
STATUS_CHOICES = [
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]


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


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(default='Default description', max_length=255)
    place = models.CharField(default='Default place', max_length=255)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_EVENT)
    image = models.ImageField(upload_to='event_gallery_photos/', blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Обрабатываем и сжимаем изображение перед сохранением
        if self.image:
            image = Image.open(self.image)
            image = image.convert('RGB')  # Преобразуем в RGB для WebP
            self.image = compress_and_convert_to_webp(image)
        super().save(*args, **kwargs)


class EventGallery(models.Model):
    event = models.ForeignKey(Event, related_name='event_galleries', on_delete=models.CASCADE)
    local_image = models.ImageField(upload_to='event_gallery_images/', blank=True, null=True)
    image_url = models.URLField(
        default='https://eduma.thimpress.com/wp-content/uploads/2022/07/thumnail-cate-7-170x170.png', max_length=255,
        blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Event gallery {self.id} - {self.event.title}" if self.event else "Event Gallery"

    def get_image(self):
        if self.local_image:
            return self.local_image.url
        elif self.image_url:
            return self.image_url
        return None

    def save(self, *args, **kwargs):
        # Обрабатываем изображение перед сохранением
        if self.local_image:
            image = Image.open(self.local_image)
            image = image.convert('RGB')  # Преобразуем в RGB для WebP
            self.local_image = compress_and_convert_to_webp(image)
        super().save(*args, **kwargs)


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='course_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)
    desc = models.TextField(default='', blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Обрабатываем изображение перед сохранением
        if self.image:
            image = Image.open(self.image)
            image = image.convert('RGB')  # Преобразуем в RGB для WebP
            self.image = compress_and_convert_to_webp(image)
        super().save(*args, **kwargs)


class Gallery(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='gallery_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Gallery {self.id} - {self.course.name}" if self.course else "Gallery"

    def save(self, *args, **kwargs):
        # Обрабатываем изображение перед сохранением
        if self.img:
            image = Image.open(self.img)
            image = image.convert('RGB')  # Преобразуем в RGB для WebP
            self.img = compress_and_convert_to_webp(image)
        super().save(*args, **kwargs)


class Certificate(models.Model):
    img = models.ImageField(upload_to='certificate_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Certificate {self.id}"

    def save(self, *args, **kwargs):
        # Обрабатываем изображение перед сохранением
        if self.img:
            image = Image.open(self.img)
            image = image.convert('RGB')  # Преобразуем в RGB для WebP
            self.img = compress_and_convert_to_webp(image)
        super().save(*args, **kwargs)
