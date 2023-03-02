from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


class UserAdmin(UserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name'
    )
    list_filter = ('email', 'first_name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
