from django.contrib import admin
from .models import Video,Comment,Profile,UserFollowing,UserSettings

admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(UserSettings)
admin.site.register(UserFollowing)

# Register your models here.
