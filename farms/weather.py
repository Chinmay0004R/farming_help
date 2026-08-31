import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _


GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'
FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'
FORECAST_DAYS = 5


def _get_json(url, params):
    request = Request(f'{url}?{urlencode(params)}', headers={'User-Agent': 'FarmApp/1.0'})
    with urlopen(request, timeout=5) as response:
        return json.load(response)


def _location_for(farm):
    latitude = getattr(farm, 'latitude', None)
    longitude = getattr(farm, 'longitude', None)
    if latitude is not None and longitude is not None:
        return {
            'latitude': float(latitude),
            'longitude': float(longitude),
            'name': farm.location or _('Selected location'),
        }
    if not farm.location:
        return None
    cache_key = f'farm-weather-location:{farm.pk}:{farm.location.strip().lower()}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    data = _get_json(GEOCODING_URL, {
        'name': farm.location,
        'count': 1,
        'language': 'en',
        'format': 'json',
    })
    result = (data.get('results') or [None])[0]
    if not result:
        return None
    location = {
        'latitude': result['latitude'],
        'longitude': result['longitude'],
        'name': result.get('name') or farm.location,
    }
    cache.set(cache_key, location, getattr(settings, 'WEATHER_CACHE_SECONDS', 900))
    return location


def get_forecast(farm):
    """Return a compact forecast for a farm, or None when weather is unavailable."""
    try:
        location = _location_for(farm)
        if not location:
            return None
        cache_key = f'farm-weather-forecast:{farm.pk}:{location["latitude"]}:{location["longitude"]}'
        cached = cache.get(cache_key)
        if cached:
            forecast = dict(cached)
            forecast['alerts'] = _alerts(forecast['today'])
            return forecast
        data = _get_json(FORECAST_URL, {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'daily': ','.join([
                'weather_code', 'temperature_2m_max', 'temperature_2m_min',
                'precipitation_sum', 'precipitation_probability_max',
                'wind_speed_10m_max',
            ]),
            'timezone': 'auto',
            'forecast_days': FORECAST_DAYS,
        })
        daily = data.get('daily', {})
        dates = daily.get('time', [])
        days = []
        for index, date in enumerate(dates):
            days.append({
                'date': date,
                'weather_code': _at(daily, 'weather_code', index),
                'max_temperature': _at(daily, 'temperature_2m_max', index),
                'min_temperature': _at(daily, 'temperature_2m_min', index),
                'rainfall': _at(daily, 'precipitation_sum', index),
                'rain_probability': _at(daily, 'precipitation_probability_max', index),
                'wind_speed': _at(daily, 'wind_speed_10m_max', index),
            })
        if not days:
            return None
        forecast = {
            'location': location['name'],
            'days': days,
            'today': days[0],
            'rainfall_total': round(sum(day['rainfall'] or 0 for day in days), 1),
        }
        cache.set(cache_key, forecast, getattr(settings, 'WEATHER_CACHE_SECONDS', 900))
        forecast['alerts'] = _alerts(forecast['today'])
        return forecast
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError):
        return None


def _at(data, key, index):
    values = data.get(key, [])
    return values[index] if index < len(values) else None


def _alerts(today):
    alerts = []
    rain_probability = today['rain_probability'] or 0
    rainfall = today['rainfall'] or 0
    wind_speed = today['wind_speed'] or 0
    if rain_probability >= 60 or rainfall >= 5:
        alerts.append({
            'kind': 'irrigation',
            'title': _('Irrigation advice'),
            'message': _('Rain is likely today. Consider delaying irrigation.'),
        })
    elif rain_probability < 40 and rainfall < 1:
        alerts.append({
            'kind': 'irrigation',
            'title': _('Irrigation advice'),
            'message': _('Little rain is expected. Check soil moisture before watering.'),
        })
    if rain_probability >= 40 or rainfall >= 1 or wind_speed >= 15:
        alerts.append({
            'kind': 'spraying',
            'title': _('Spraying advice'),
            'message': _('Conditions may reduce spray effectiveness. Consider postponing spraying.'),
        })
    return alerts