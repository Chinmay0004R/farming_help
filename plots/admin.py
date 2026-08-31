from django.contrib import admin
from .models import Plot

@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'area', 'soil_type', 'created_at')
    search_fields = ('name', 'farm__name', 'soil_type')
    list_filter = ('farm',)
