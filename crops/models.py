from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from plots.models import Plot

User = get_user_model()

class Crop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crops', help_text=_("Farmer who owns this crop entry"))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    variety = models.CharField(max_length=100, blank=True, null=True)
    typical_cycle_days = models.PositiveIntegerField(help_text=_("Typical duration from sowing to harvest in days"), blank=True, null=True)
    expected_yield_per_acre = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Expected yield per acre (for example, kg or tons)"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.variety:
            return f"{self.name} - {self.variety}"
        return self.name

    class Meta:
        unique_together = ('user', 'name', 'variety')

class CropCycle(models.Model):
    GROWTH_STAGES = [
        ('Planned', 'Planned'),
        ('Sown', 'Sown'),
        ('Vegetative', 'Vegetative'),
        ('Flowering', 'Flowering'),
        ('Fruiting', 'Fruiting'),
        ('Harvesting', 'Harvesting'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='crop_cycles')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, related_name='cycles')
    season = models.CharField(max_length=50, help_text=_("For example, Kharif, Rabi, Summer"))
    sowing_date = models.DateField()
    expected_harvest_date = models.DateField(blank=True, null=True)
    actual_harvest_date = models.DateField(blank=True, null=True)
    growth_stage = models.CharField(max_length=20, choices=GROWTH_STAGES, default='Planned')
    
    expected_yield = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Expected total yield for this field"), blank=True, null=True)
    actual_yield = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Actual total yield for this field"), blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crop.name} on {self.plot.name} ({self.season})"

    class Meta:
        ordering = ['-sowing_date']

class Harvest(models.Model):
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.CASCADE, related_name='harvests')
    date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Quantity harvested"))
    grade_or_quality = models.CharField(max_length=100, blank=True, null=True, help_text=_("For example, Grade A, Premium, Regular"))
    moisture_content = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text=_("Moisture percentage, if applicable"))
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Harvest on {self.date} for {self.crop_cycle}"

    class Meta:
        ordering = ['-date']

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Harvest)
@receiver(post_delete, sender=Harvest)
def update_crop_cycle_yield(sender, instance, **kwargs):
    cycle = instance.crop_cycle
    total = cycle.harvests.aggregate(total_yield=Sum('quantity'))['total_yield']
    cycle.actual_yield = total if total else 0
    # Use update to avoid triggering other saves if not needed, but save() is fine here
    cycle.save(update_fields=['actual_yield'])
