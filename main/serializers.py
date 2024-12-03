from rest_framework import serializers
from .models import Course, Gallery, Event,  EventGallery


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'img', 'order']


class EventGallerySerializer(serializers.ModelSerializer):
    event_gallery_name = serializers.CharField(source='event.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = EventGallery
        fields = ['id', 'event', 'event_gallery_name', 'image', 'order']


    def get_image(self, obj):
        # Используем `obj` для доступа к полям модели
        if obj.local_image:
            return obj.local_image.url
        elif obj.image_url:
            return obj.image_url
        return None

class GallerySerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Gallery
        fields = ['id', 'course', 'course_name', 'img', 'order']



class EventSerializer(serializers.ModelSerializer):
    available_slots = serializers.ReadOnlyField()
    event_galleries = EventGallerySerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = (

            'id', 'start_date', 'end_date', 'title','description','place','status', 'image', 'available_slots',
            'order', 'event_galleries')

class CourseSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, source='gallery_set')

    class Meta:
        model = Course
        fields = ['id', 'name', 'image', 'order', 'desc', 'galleries']


class ContactFormSerializer(serializers.Serializer):
    studentName = serializers.CharField(max_length=255, required=True)
    dob = serializers.DateField(required=True)
    address = serializers.CharField(max_length=500, required=True)
    primaryPhone = serializers.RegexField(regex=r'^\+?\d+$', required=True)
    secondaryPhone = serializers.RegexField(regex=r'^\+?\d+$', required=False, allow_blank=True)
    parentName = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    emergencyContact = serializers.CharField(max_length=255, required=True)
    minorName = serializers.CharField(max_length=255, required=True)
    minorAge = serializers.IntegerField(required=True)
    signature = serializers.CharField(max_length=255, required=True)
    date = serializers.DateField(required=True)
    Zelle = serializers.CharField(max_length=20, required=False)
    policies = serializers.ListField(
        child=serializers.BooleanField(), required=True
    )
    waiver = serializers.BooleanField(required=True)