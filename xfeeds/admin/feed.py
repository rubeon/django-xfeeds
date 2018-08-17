from django.contrib import admin
from ..models.feed import Feed
from ..models.feed import FeedItem
from ..models.feed import FeedCategory
from ..models.feed import FeedItemCategory

class FeedAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feed, FeedAdmin)

class FeedItemAdmin(admin.ModelAdmin):
    list_display = ('source', 'title', 'author')
admin.site.register(FeedItem, FeedItemAdmin)

class FeedCategoryAdmin(admin.ModelAdmin):
    # list_display = ('source', 'title', 'author')
    pass
admin.site.register(FeedCategory, FeedCategoryAdmin)

class FeedItemCategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(FeedItemCategory, FeedItemCategoryAdmin)
