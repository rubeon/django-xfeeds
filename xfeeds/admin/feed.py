from django.contrib import admin
from ..models.feed import Feed
from ..models.feed import FeedItem

class FeedAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feed, FeedAdmin)

class FeedItemAdmin(admin.ModelAdmin):
    list_display = ('source', 'title', 'author')
admin.site.register(FeedItem, FeedItemAdmin)
