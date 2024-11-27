from adminsortable.models import SortableMixin
from django.db import models


class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('happening', 'Happening'),
        ('completed', 'Completed'),
    ]
    MONTH_CHOICES = [
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
    day = models.PositiveIntegerField()
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    title = models.CharField(max_length=100)
    hour = models.CharField(max_length=50)
    place = models.CharField(max_length=100)
    event_description = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to='event_gallery_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)  # Ensure the base save is called
        images = form.cleaned_data.get('img', [])
        for image in images:
            EventGallery.objects.create(course=obj, img=image)


class EventGallery(models.Model):
    event = models.ForeignKey(Event,related_name='event_galleries', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='event-gallery_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Event gallery {self.id} - {self.event.title}" if self.event else "Event Gallery"


class Outcome(models.Model):
    event = models.ForeignKey(Event, related_name='outcomes', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


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

