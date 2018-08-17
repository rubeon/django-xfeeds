from django.contrib import admin
from ..models.media import CachedImage

class CachedImageAdmin(admin.ModelAdmin):
    pass
admin.site.register(CachedImage, CachedImageAdmin)

