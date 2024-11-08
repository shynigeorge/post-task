from django.contrib import admin

from home.models import CustomUser, Post

admin.site.register(CustomUser)
admin.site.register(Post)