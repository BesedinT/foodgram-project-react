from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Follow, User


class UserAdmin(UserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'recipes_count', 'follower_count', 'following_count'
    )
    list_filter = ('email', 'first_name',)

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def follower_count(self, obj):
        return obj.follower.count()

    @admin.display(description='Кол-во подписок')
    def following_count(self, obj):
        return obj.following.count()


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.unregister(Group)
