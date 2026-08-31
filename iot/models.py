import uuid

from django.db import models
from plots.models import Plot


class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    device_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='iot_devices')
    name = models.CharField(max_length=100, default='ESP32 sensor')
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.device_id})'


class SensorReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    soil_moisture = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperature = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    battery_voltage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    recorded_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
