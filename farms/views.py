from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext as _
from iot.models import SensorReading
from crops.models import CropCycle
from .models import Farm, Expense, Sale, DiaryEntry, Reminder
from .forms import FarmForm, ExpenseForm, SaleForm, DiaryEntryForm, ReminderForm
from .weather import get_forecast


@login_required
def dashboard_view(request):
    farms = Farm.objects.filter(owner=request.user)
    weather_forecasts = [forecast for farm in farms if (forecast := get_forecast(farm))]
    cycles = list(
        CropCycle.objects.filter(plot__farm__owner=request.user)
        .select_related('crop', 'plot', 'plot__farm')[:6]
    )
    readings = SensorReading.objects.filter(
        device__plot__farm__owner=request.user
    ).select_related('device__plot').order_by('-recorded_at')

    latest_by_plot = {}
    for reading in readings:
        latest_by_plot.setdefault(reading.device.plot_id, reading)

    field_checks = []
    for farm in farms:
        for plot in farm.plots.all():
            reading = latest_by_plot.get(plot.pk)
            moisture = reading.soil_moisture if reading else None
            if moisture is None:
                status = 'unknown'
                status_label = _('Sensor data is not available')
            elif moisture < 30:
                status = 'dry'
                status_label = _('The field may need water')
            else:
                status = 'good'
                status_label = _('Watering is not needed right now')
            field_checks.append({
                'plot': plot,
                'reading': reading,
                'status': status,
                'status_label': status_label,
            })

    dry_fields = [field for field in field_checks if field['status'] == 'dry']
    sensor_alerts = []
    for field in field_checks:
        reading = field['reading']
        if reading and reading.temperature is not None and reading.temperature >= 36:
            sensor_alerts.append(_('Temperature is high today - %(field)s: %(temperature)s°C') % {'field': field['plot'].name, 'temperature': reading.temperature})
        if reading is None and field['plot'].iot_devices.exists():
            sensor_alerts.append(_('%(field)s has not sent sensor data') % {'field': field['plot'].name})
    total_expenses = Expense.objects.filter(owner=request.user).aggregate(total=Sum('amount'))['total'] or 0
    total_sales = sum(sale.total_amount for sale in Sale.objects.filter(owner=request.user))
    reminders = Reminder.objects.filter(owner=request.user, is_done=False, due_date__gte=timezone.localdate())[:3]
    context = {
        'farms': farms,
        'cycles': cycles,
        'field_checks': field_checks[:4],
        'dry_fields': dry_fields,
        'sensor_alerts': sensor_alerts,
        'farmer_name': request.user.first_name or request.user.username,
        'total_expenses': total_expenses,
        'total_sales': total_sales,
        'profit': total_sales - total_expenses,
        'reminders': reminders,
        'weather_forecasts': weather_forecasts,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def money_view(request):
    expenses = Expense.objects.filter(owner=request.user).select_related('farm')
    sales = Sale.objects.filter(owner=request.user).select_related('farm')
    expense_form = ExpenseForm(request.POST or None, user=request.user)
    sale_form = SaleForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        form = expense_form if form_type == 'expense' else sale_form
        if form.is_valid():
            record = form.save(commit=False)
            record.owner = request.user
            record.save()
            messages.success(request, _('Entry saved.'))
            return redirect('money')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_sales = sum(sale.total_amount for sale in sales)
    return render(request, 'farms/money.html', {
        'expenses': expenses[:8], 'sales': sales[:8], 'expense_form': expense_form,
        'sale_form': sale_form, 'total_expenses': total_expenses,
        'total_sales': total_sales, 'profit': total_sales - total_expenses,
    })


@login_required
def diary_view(request):
    entries = DiaryEntry.objects.filter(owner=request.user).select_related('plot')[:12]
    form = DiaryEntryForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        entry = form.save(commit=False)
        entry.owner = request.user
        entry.save()
        messages.success(request, _('Today\'s entry saved.'))
        return redirect('diary')
    return render(request, 'farms/diary.html', {'entries': entries, 'form': form})


@login_required
def reminders_view(request):
    reminders = Reminder.objects.filter(owner=request.user)
    form = ReminderForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if request.POST.get('action') == 'complete':
            reminder = get_object_or_404(reminders, pk=request.POST.get('reminder_id'))
            reminder.is_done = True
            reminder.save(update_fields=['is_done'])
            return redirect('reminders')
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.owner = request.user
            reminder.save()
            messages.success(request, _('Reminder saved.'))
            return redirect('reminders')
    return render(request, 'farms/reminders.html', {'reminders': reminders, 'form': form})


@login_required
def farm_list_view(request):
    farms = Farm.objects.filter(owner=request.user)
    return render(request, 'farms/farm_list.html', {'farms': farms})


@login_required
def farm_create_view(request):
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            farm.save()
            messages.success(request, _('Farm "%(name)s" created successfully!') % {'name': farm.name})
            return redirect('farm_detail', pk=farm.pk)
    else:
        form = FarmForm()
    return render(request, 'farms/farm_form.html', {'form': form, 'title': 'Add New Farm'})


@login_required
def farm_detail_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    plots = farm.plots.all()
    return render(request, 'farms/farm_detail.html', {'farm': farm, 'plots': plots})


@login_required
def farm_update_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, _('Farm "%(name)s" updated successfully!') % {'name': farm.name})
            return redirect('farm_detail', pk=farm.pk)
    else:
        form = FarmForm(instance=farm)
    return render(request, 'farms/farm_form.html', {'form': form, 'title': f'Edit {farm.name}'})


@login_required
def farm_delete_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = farm.name
        farm.delete()
        messages.success(request, _('Farm "%(name)s" deleted successfully.') % {'name': name})
        return redirect('farm_list')
    return render(request, 'farms/farm_confirm_delete.html', {'farm': farm})
