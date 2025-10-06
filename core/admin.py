from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WasteCategory, WasteItem, Match

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('WasteHub Profile', {
            'fields': ('user_type', 'phone', 'address')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('WasteHub Profile', {
            'fields': ('user_type', 'phone', 'address', 'email')
        }),
    )

@admin.register(WasteCategory)
class WasteCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(WasteItem)
class WasteItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'poster', 'category', 'quantity', 'unit', 'location', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'location', 'poster__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('waste_item', 'collector', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('waste_item__title', 'collector__username', 'message')
    readonly_fields = ('created_at',)
