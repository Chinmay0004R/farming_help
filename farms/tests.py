from unittest.mock import patch

from django.test import TestCase

from .weather import get_forecast


class WeatherServiceTests(TestCase):
	def test_forecast_contains_rainfall_and_weather_alerts(self):
		geocoding = {'results': [{'latitude': 18.52, 'longitude': 73.85, 'name': 'Pune'}]}
		forecast = {
			'daily': {
				'time': ['2026-08-27', '2026-08-28'],
				'weather_code': [1, 2],
				'temperature_2m_max': [31, 29],
				'temperature_2m_min': [23, 22],
				'precipitation_sum': [8, 2],
				'precipitation_probability_max': [75, 45],
				'wind_speed_10m_max': [10, 12],
			}
		}
		farm = type('FarmStub', (), {'pk': 1, 'location': 'Pune'})()
		with patch('farms.weather._get_json', side_effect=[geocoding, forecast]):
			result = get_forecast(farm)

		self.assertEqual(result['rainfall_total'], 10)
		self.assertEqual(len(result['days']), 2)
		self.assertEqual(result['alerts'][0]['kind'], 'irrigation')
		self.assertEqual(result['alerts'][0]['title'], 'Irrigation advice')
		self.assertEqual(result['alerts'][1]['kind'], 'spraying')

	def test_provider_failure_is_ignored(self):
		farm = type('FarmStub', (), {'pk': 2, 'location': 'Unknown'})()
		with patch('farms.weather._get_json', side_effect=OSError):
			self.assertIsNone(get_forecast(farm))

# Create your tests here.
