from django.contrib import admin
from .models import Farm

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'total_area', 'created_at')
    search_fields = ('name', 'owner__username', 'location')
