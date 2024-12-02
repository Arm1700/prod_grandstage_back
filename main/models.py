from adminsortable.models import SortableMixin
from django.db import models
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

class Event(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_EVENT)
    image = models.ImageField(upload_to='event_gallery_photos/', blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class EventGallery(models.Model):
    event = models.ForeignKey(Event,related_name='event_galleries', on_delete=models.CASCADE)
    local_image = models.ImageField(upload_to='event_gallery_images/', blank=True, null=True)
    image_url = models.URLField(default='https://eduma.thimpress.com/wp-content/uploads/2022/07/thumnail-cate-7'
                                        '-170x170.png', max_length=255, blank=True, null=True)
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


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='course_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)
    desc = models.TextField(default='', blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)  # Ensure the base save is called
        images = form.cleaned_data.get('img', [])
        for image in images:
            Gallery.objects.create(course=obj, img=image)


class Gallery(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='gallery_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Gallery {self.id} - {self.course.name}" if self.course else "Gallery"


class Certificate(models.Model):
    img = models.ImageField(upload_to='certificate_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Certificate {self.id} "


