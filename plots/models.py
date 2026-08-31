from django.db import models
from farms.models import Farm
from django.utils.translation import gettext_lazy as _

class Plot(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='plots')
    name = models.CharField(max_length=255)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Area in acres"))
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    irrigation_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.farm.name})"
