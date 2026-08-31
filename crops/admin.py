from django.contrib import admin
from .models import Crop, CropCycle

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'variety', 'typical_cycle_days', 'expected_yield_per_acre', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'variety')

@admin.register(CropCycle)
class CropCycleAdmin(admin.ModelAdmin):
    list_display = ('plot', 'crop', 'season', 'sowing_date', 'growth_stage')
    list_filter = ('season', 'growth_stage', 'sowing_date')
    search_fields = ('plot__name', 'crop__name', 'season')

from .models import Harvest

@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ('crop_cycle', 'date', 'quantity', 'grade_or_quality')
    list_filter = ('date', 'grade_or_quality')
    search_fields = ('crop_cycle__crop__name', 'crop_cycle__plot__name')
