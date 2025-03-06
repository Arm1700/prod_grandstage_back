from django.contrib import admin
from .forms import GalleryForm, EventGalleryForm
from .models import Course, Gallery, Certificate, Event,  EventGallery
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from django.utils.safestring import mark_safe

def get_image_preview(image_url):
    if image_url:
        return mark_safe(f'''
            <a href="#" onclick="openModal('{image_url}')">
                <img src="{image_url}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;" />
            </a>

            <div id="imageModal" class="modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8);"
                 onclick="closeModal(event)">
                <span onclick="closeModal()" style="position: absolute; top: 10px; right: 20px; color: white; font-size: 30px; cursor: pointer;">&times;</span>
                <img id="modalImage" style="margin: auto; display: block; max-width: 90%; max-height: 90%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
            </div>

            <script>
                function openModal(imageUrl) {{
                    document.getElementById("modalImage").src = imageUrl;
                    document.getElementById("imageModal").style.display = "block";
                }}

                function closeModal(event) {{
                    if (event.target === document.getElementById("imageModal") || event.target === document.querySelector('span')) {{
                        document.getElementById("imageModal").style.display = "none";
                    }}
                }}
            </script>
        ''')
    return "No Image"


class GalleryInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Gallery
    extra = 0
    fields = ['img', 'preview', 'order']
    readonly_fields = ['preview']
    sortable_field_name = "order"

    def preview(self, obj):
        if obj.img:
            return get_image_preview(obj.img.url)
        return "No Image"

    preview.short_description = "Preview"


class EventGalleryInline(SortableInlineAdminMixin, admin.TabularInline):
    model = EventGallery
    extra = 0
    fields = ['preview', 'local_image', 'order']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.local_image:
            return get_image_preview(obj.local_image.url)
        return "No Image"

    preview.short_description = "Preview"



@admin.register(Course)
class CourseAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [GalleryInline]
    form = GalleryForm
    list_display = ['name', 'preview',  'order']
    ordering = ['order']
    readonly_fields = ['preview']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Handling multiple images for Gallery
        images = form.cleaned_data.get('images')
        if images:
            for image in images:
                Gallery.objects.create(course=obj, img=image)


    def preview(self, obj):
        if obj.image:
            return get_image_preview(obj.image.url)
        return "No Image"

    preview.short_description = "Preview"


@admin.register(Certificate)
class CertificateAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'preview', 'order')
    fields = ['img', 'order']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.img:
            return get_image_preview(obj.img.url)
        return "No Image"

    preview.short_description = "Preview"




@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'preview', 'order')
    fields = ['course', 'img', 'order']
    readonly_fields = ['preview']

    def preview(self, obj):
        return get_image_preview(obj.img.url if obj.img else None)

    preview.short_description = "Preview"



@admin.register(Event)
class EventAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [EventGalleryInline]
    form = EventGalleryForm
    list_display = ('id', 'title','description','place', 'start_date', 'end_date', 'status', 'preview', 'order')
    field = '__all__'
    search_fields = ['title', 'description']
    list_filter = ['status']
    ordering = ['order']
    readonly_fields = ['preview']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        images = form.cleaned_data.get('images', [])
        print("Images received:", images)  # Отладка
        if images:
            for image in images:
                EventGallery.objects.create(event=obj, local_image=image)

    def preview(self, obj):
        return get_image_preview(obj.image.url if obj.image else None)

    preview.short_description = "Preview"