from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Crop, CropCycle, Harvest
from .forms import CropForm, CropCycleForm, HarvestForm

@login_required
def crop_list_view(request):
    crops = Crop.objects.filter(user=request.user)
    return render(request, 'crops/crop_list.html', {'crops': crops})

@login_required
def crop_create_view(request):
    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.user = request.user
            crop.save()
            messages.success(request, _('Crop "%(name)s" created successfully!') % {'name': crop.name})
            return redirect('crop_list')
    else:
        form = CropForm()
    return render(request, 'crops/crop_form.html', {'form': form, 'title': 'Add New Crop'})

@login_required
def crop_update_view(request, pk):
    crop = get_object_or_404(Crop, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, _('Crop "%(name)s" updated successfully!') % {'name': crop.name})
            return redirect('crop_list')
    else:
        form = CropForm(instance=crop)
    return render(request, 'crops/crop_form.html', {'form': form, 'title': f'Edit {crop.name}'})

@login_required
def crop_delete_view(request, pk):
    crop = get_object_or_404(Crop, pk=pk, user=request.user)
    if request.method == 'POST':
        name = crop.name
        crop.delete()
        messages.success(request, _('Crop "%(name)s" deleted successfully.') % {'name': name})
        return redirect('crop_list')
    return render(request, 'crops/crop_confirm_delete.html', {'crop': crop})


@login_required
def cropcycle_list_view(request):
    cycles = CropCycle.objects.filter(plot__farm__owner=request.user).select_related('plot', 'crop')
    return render(request, 'crops/cropcycle_list.html', {'cycles': cycles})

@login_required
def cropcycle_create_view(request):
    if request.method == 'POST':
        form = CropCycleForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Crop cycle created successfully!'))
            return redirect('cropcycle_list')
    else:
        form = CropCycleForm(user=request.user)
    return render(request, 'crops/cropcycle_form.html', {'form': form, 'title': 'Add New Crop Cycle'})

@login_required
def cropcycle_update_view(request, pk):
    cycle = get_object_or_404(CropCycle, pk=pk, plot__farm__owner=request.user)
    if request.method == 'POST':
        form = CropCycleForm(request.POST, instance=cycle, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Crop cycle updated successfully!'))
            return redirect('cropcycle_list')
    else:
        form = CropCycleForm(instance=cycle, user=request.user)
    return render(request, 'crops/cropcycle_form.html', {'form': form, 'title': f'Edit Crop Cycle for {cycle.plot.name}'})

@login_required
def cropcycle_delete_view(request, pk):
    cycle = get_object_or_404(CropCycle, pk=pk, plot__farm__owner=request.user)
    if request.method == 'POST':
        cycle.delete()
        messages.success(request, _('Crop cycle deleted successfully.'))
        return redirect('cropcycle_list')
    return render(request, 'crops/cropcycle_confirm_delete.html', {'cycle': cycle})

@login_required
def cropcycle_detail_view(request, pk):
    cycle = get_object_or_404(CropCycle, pk=pk, plot__farm__owner=request.user)
    harvests = cycle.harvests.all()
    return render(request, 'crops/cropcycle_detail.html', {'cycle': cycle, 'harvests': harvests})

@login_required
def harvest_create_view(request, cycle_pk):
    cycle = get_object_or_404(CropCycle, pk=cycle_pk, plot__farm__owner=request.user)
    if request.method == 'POST':
        form = HarvestForm(request.POST)
        if form.is_valid():
            harvest = form.save(commit=False)
            harvest.crop_cycle = cycle
            harvest.save()
            messages.success(request, _('Harvest recorded successfully!'))
            return redirect('cropcycle_detail', pk=cycle.pk)
    else:
        form = HarvestForm()
    return render(request, 'crops/harvest_form.html', {'form': form, 'title': f'Record Harvest for {cycle.crop.name}', 'cycle': cycle})

@login_required
def harvest_update_view(request, pk):
    harvest = get_object_or_404(Harvest, pk=pk, crop_cycle__plot__farm__owner=request.user)
    if request.method == 'POST':
        form = HarvestForm(request.POST, instance=harvest)
        if form.is_valid():
            form.save()
            messages.success(request, _('Harvest updated successfully!'))
            return redirect('cropcycle_detail', pk=harvest.crop_cycle.pk)
    else:
        form = HarvestForm(instance=harvest)
    return render(request, 'crops/harvest_form.html', {'form': form, 'title': 'Edit Harvest', 'cycle': harvest.crop_cycle})

@login_required
def harvest_delete_view(request, pk):
    harvest = get_object_or_404(Harvest, pk=pk, crop_cycle__plot__farm__owner=request.user)
    cycle_pk = harvest.crop_cycle.pk
    if request.method == 'POST':
        harvest.delete()
        messages.success(request, _('Harvest deleted successfully.'))
        return redirect('cropcycle_detail', pk=cycle_pk)
    return render(request, 'crops/harvest_confirm_delete.html', {'harvest': harvest})
