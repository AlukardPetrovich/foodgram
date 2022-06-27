from django.contrib import admin
from users.models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
