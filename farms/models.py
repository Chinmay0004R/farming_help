from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Farm(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    total_area = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Total area in acres"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.owner.username}"


class Expense(models.Model):
    CATEGORIES = [
        ('seeds', _('Seeds')), ('fertilizer', _('Fertilizer')), ('water', _('Water')),
        ('labour', _('Labour')), ('tractor', _('Tractor')), ('transport', _('Transport')),
        ('other', _('Other')),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farm_expenses')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='expenses', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='other')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']


class Sale(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farm_sales')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='sales', blank=True, null=True)
    crop_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=30, default='क्विंटल')
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return self.quantity * self.price_per_unit

    class Meta:
        ordering = ['-date', '-created_at']


class DiaryEntry(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diary_entries')
    plot = models.ForeignKey('plots.Plot', on_delete=models.CASCADE, related_name='diary_entries', blank=True, null=True)
    date = models.DateField()
    title = models.CharField(max_length=120)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']


class Reminder(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farm_reminders')
    plot = models.ForeignKey('plots.Plot', on_delete=models.CASCADE, related_name='reminders', blank=True, null=True)
    title = models.CharField(max_length=160)
    due_date = models.DateField()
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_done', 'due_date']
