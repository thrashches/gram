from django.contrib import admin

from .models import User

admin.site.empty_value_display = '--Пусто--'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
