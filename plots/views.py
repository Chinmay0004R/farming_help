import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from farms.models import Farm
from iot.models import SensorReading
from .models import Plot
from .forms import PlotForm


@login_required
def plot_create_view(request, farm_pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    if request.method == 'POST':
        form = PlotForm(request.POST)
        if form.is_valid():
            plot = form.save(commit=False)
            plot.farm = farm
            plot.save()
            messages.success(request, _('Field "%(plot)s" added to %(farm)s.') % {'plot': plot.name, 'farm': farm.name})
            return redirect('farm_detail', pk=farm.pk)
    else:
        form = PlotForm()
    return render(request, 'plots/plot_form.html', {'form': form, 'farm': farm, 'title': 'Add New Plot'})


@login_required
def plot_detail_view(request, pk):
    plot = get_object_or_404(Plot, pk=pk, farm__owner=request.user)
    latest_reading = SensorReading.objects.filter(device__plot=plot).first()
    
    # Fetch recent readings for historical charts (limit to last 100 entries)
    historical_readings = SensorReading.objects.filter(device__plot=plot).order_by('-recorded_at')[:100]
    # Reverse so that time runs left-to-right (chronological) in the chart
    historical_readings = list(reversed(historical_readings))
    
    readings_data = []
    for r in historical_readings:
        readings_data.append({
            'recorded_at': r.recorded_at.isoformat(),
            'soil_moisture': float(r.soil_moisture) if r.soil_moisture is not None else None,
            'temperature': float(r.temperature) if r.temperature is not None else None,
            'humidity': float(r.humidity) if r.humidity is not None else None,
            'battery_voltage': float(r.battery_voltage) if r.battery_voltage is not None else None,
        })
    readings_json = json.dumps(readings_data, cls=DjangoJSONEncoder)
    
    context = {
        'plot': plot,
        'latest_reading': latest_reading,
        'readings_json': readings_json,
    }
    return render(request, 'plots/plot_detail.html', context)


@login_required
def plot_update_view(request, pk):
    plot = get_object_or_404(Plot, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        form = PlotForm(request.POST, instance=plot)
        if form.is_valid():
            form.save()
            messages.success(request, _('Field "%(name)s" updated.') % {'name': plot.name})
            return redirect('plot_detail', pk=plot.pk)
    else:
        form = PlotForm(instance=plot)
    return render(request, 'plots/plot_form.html', {'form': form, 'farm': plot.farm, 'title': f'Edit {plot.name}'})


@login_required
def plot_delete_view(request, pk):
    plot = get_object_or_404(Plot, pk=pk, farm__owner=request.user)
    farm_pk = plot.farm.pk
    if request.method == 'POST':
        name = plot.name
        plot.delete()
        messages.success(request, _('Field "%(name)s" deleted.') % {'name': name})
        return redirect('farm_detail', pk=farm_pk)
    return render(request, 'plots/plot_confirm_delete.html', {'plot': plot})
