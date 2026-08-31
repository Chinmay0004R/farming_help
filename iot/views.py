import json
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from .forms import DeviceForm
from .models import Device, SensorReading


def _decimal(payload, field_name):
    value = payload.get(field_name)
    if value in (None, ''):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f'{field_name} must be a number')


@csrf_exempt
def sensor_reading_view(request):
    if request.method != 'POST':
           return JsonResponse({'error': _('POST required')}, status=405)

    try:
        payload = json.loads(request.body)
        if not isinstance(payload, dict):
            raise ValueError(_('Payload must be an object'))
        device_key = request.headers.get('X-Device-Key')
        device = Device.objects.get(device_key=device_key, is_active=True)
        recorded_at = payload.get('recorded_at')
        recorded_at = datetime.fromisoformat(recorded_at) if recorded_at else timezone.now()
        if timezone.is_naive(recorded_at):
            recorded_at = timezone.make_aware(recorded_at)
        reading = SensorReading.objects.create(
            device=device,
            soil_moisture=_decimal(payload, 'soil_moisture'),
            temperature=_decimal(payload, 'temperature'),
            humidity=_decimal(payload, 'humidity'),
            battery_voltage=_decimal(payload, 'battery_voltage'),
            recorded_at=recorded_at,
        )
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': _('Request body must be valid JSON')}, status=400)
    except Device.DoesNotExist:
        return JsonResponse({'error': _('Invalid or inactive device key')}, status=401)
    except (ValueError, OverflowError):
        return JsonResponse({'error': _('Invalid reading payload')}, status=400)

    device.last_seen = timezone.now()
    device.save(update_fields=['last_seen'])
    return JsonResponse({'id': reading.pk, 'status': 'accepted'}, status=201)


@login_required
def device_list_view(request):
    devices = Device.objects.filter(plot__farm__owner=request.user).select_related('plot', 'plot__farm')
    return render(request, 'iot/device_list.html', {'devices': devices})


@login_required
def device_create_view(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST, user=request.user)
        if form.is_valid():
            device = form.save(commit=False)
            if not device.device_id:
                # Generate a fallback short unique ID if left blank
                device.device_id = f"esp32-{uuid.uuid4().hex[:8]}"
            device.save()
            messages.success(request, _('Device "%(name)s" successfully registered.') % {'name': device.name})
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm(user=request.user)
    return render(request, 'iot/device_form.html', {'form': form, 'title': 'Register IoT Device'})


@login_required
def device_detail_view(request, pk):
    device = get_object_or_404(Device, pk=pk, plot__farm__owner=request.user)
    latest_reading = device.readings.first()
    
    # Generate dynamic API URL based on request host
    proto = 'https' if request.is_secure() else 'http'
    api_url = f"{proto}://{request.get_host()}/iot/readings/"
    
    # Pre-filled firmware code template
    arduino_sketch = f"""#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_SSID = "your-wifi-name";
const char* WIFI_PASSWORD = "your-wifi-password";

const char* API_URL = "{api_url}";
const char* DEVICE_KEY = "{device.device_key}";

void setup() {{
  Serial.begin(115200);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {{
    delay(500);
    Serial.print(".");
  }}

  Serial.println("\\nESP32 connected");
}}

void loop() {{
  if (WiFi.status() == WL_CONNECTED) {{
    HTTPClient http;

    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-Key", DEVICE_KEY);

    // Replace these hardcoded readings with actual sensor code
    // e.g., soilMoisture = (analogRead(34) / 4095.0) * 100.0;
    float soilMoisture = 42.5;
    float temperature = 25.1;
    float humidity = 61.0;
    float batteryVoltage = 4.1;

    String payload = "{{";
    payload += "\\"soil_moisture\\":" + String(soilMoisture, 2) + ",";
    payload += "\\"temperature\\":" + String(temperature, 2) + ",";
    payload += "\\"humidity\\":" + String(humidity, 2) + ",";
    payload += "\\"battery_voltage\\":" + String(batteryVoltage, 2);
    payload += "}}";

    int responseCode = http.POST(payload);

    Serial.print("HTTP response: ");
    Serial.println(responseCode);
    Serial.println(http.getString());

    http.end();
  }}

  delay(60000); // Send reading every 60 seconds
}}
"""
    
    context = {
        'device': device,
        'latest_reading': latest_reading,
        'arduino_sketch': arduino_sketch,
    }
    return render(request, 'iot/device_detail.html', context)


@login_required
def device_update_view(request, pk):
    device = get_object_or_404(Device, pk=pk, plot__farm__owner=request.user)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Device "%(name)s" updated successfully.') % {'name': device.name})
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device, user=request.user)
    return render(request, 'iot/device_form.html', {'form': form, 'title': f'Edit {device.name}', 'device': device})


@login_required
def device_regenerate_key_view(request, pk):
    if request.method == 'POST':
        device = get_object_or_404(Device, pk=pk, plot__farm__owner=request.user)
        device.device_key = uuid.uuid4()
        device.save(update_fields=['device_key'])
        messages.success(request, _('Device key for "%(name)s" has been regenerated.') % {'name': device.name})
        return redirect('device_detail', pk=device.pk)
    return redirect('device_list')


@login_required
def device_delete_view(request, pk):
    device = get_object_or_404(Device, pk=pk, plot__farm__owner=request.user)
    if request.method == 'POST':
        name = device.name
        device.delete()
        messages.success(request, _('Device "%(name)s" deleted successfully.') % {'name': name})
        return redirect('device_list')
    return render(request, 'iot/device_confirm_delete.html', {'device': device})