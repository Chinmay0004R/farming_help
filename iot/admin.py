from django.contrib import admin

from .models import Device, SensorReading


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_id', 'plot', 'is_active', 'last_seen')
    search_fields = ('name', 'device_id', 'plot__name')
    list_filter = ('is_active',)


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'soil_moisture', 'temperature', 'humidity', 'recorded_at')
    list_filter = ('device',)
    date_hierarchy = 'recorded_at'