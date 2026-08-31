import json
import uuid

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from farms.models import Farm
from plots.models import Plot

from iot.models import Device, SensorReading


class SensorReadingApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='farmer', password='test-password')
        farm = Farm.objects.create(owner=self.user, name='Test Farm', total_area=10)
        plot = Plot.objects.create(farm=farm, name='Plot A', area=2)
        self.device = Device.objects.create(device_id='esp32-001', plot=plot)

    def test_accepts_reading_for_active_device(self):
        response = self.client.post(
            reverse('iot_sensor_reading'),
            data=json.dumps({'soil_moisture': 42.5, 'temperature': 25.1, 'humidity': 61}),
            content_type='application/json',
            headers={'X-Device-Key': str(self.device.device_key)},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SensorReading.objects.count(), 1)
        self.device.refresh_from_db()
        self.assertIsNotNone(self.device.last_seen)

    def test_rejects_unknown_device_key(self):
        response = self.client.post(
            reverse('iot_sensor_reading'),
            data=json.dumps({'soil_moisture': 42.5}),
            content_type='application/json',
            headers={'X-Device-Key': str(uuid.uuid4())},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(SensorReading.objects.count(), 0)


class DeviceCrudTests(TestCase):
    def setUp(self):
        # Create User 1
        self.user1 = User.objects.create_user(username='farmer1', password='password1')
        self.farm1 = Farm.objects.create(owner=self.user1, name='Farm 1', total_area=10)
        self.plot1 = Plot.objects.create(farm=self.farm1, name='Plot 1', area=5)
        self.device1 = Device.objects.create(device_id='device-1', name='Sensor 1', plot=self.plot1)

        # Create User 2
        self.user2 = User.objects.create_user(username='farmer2', password='password2')
        self.farm2 = Farm.objects.create(owner=self.user2, name='Farm 2', total_area=20)
        self.plot2 = Plot.objects.create(farm=self.farm2, name='Plot 2', area=8)
        self.device2 = Device.objects.create(device_id='device-2', name='Sensor 2', plot=self.plot2)

    def test_device_list_only_shows_owned_devices(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.get(reverse('device_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sensor 1')
        self.assertNotContains(response, 'Sensor 2')

    def test_device_form_only_shows_owned_plots(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.get(reverse('device_create'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        plots_in_form = list(form.fields['plot'].queryset)
        self.assertIn(self.plot1, plots_in_form)
        self.assertNotIn(self.plot2, plots_in_form)

    def test_device_create_creates_device(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.post(reverse('device_create'), {
            'device_id': 'new-esp-32',
            'name': 'New Sensor',
            'plot': self.plot1.pk
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Device.objects.filter(device_id='new-esp-32', plot=self.plot1).exists())

    def test_cannot_create_device_on_other_user_plot(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.post(reverse('device_create'), {
            'device_id': 'malicious-esp',
            'name': 'Malicious Sensor',
            'plot': self.plot2.pk
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('plot', form.errors)

    def test_device_detail_displays_info(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.get(reverse('device_detail', kwargs={'pk': self.device1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'device-1')
        
    def test_cannot_view_other_user_device_detail(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.get(reverse('device_detail', kwargs={'pk': self.device2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_device_update_updates_device(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.post(reverse('device_update', kwargs={'pk': self.device1.pk}), {
            'device_id': 'device-1',
            'name': 'Updated Sensor 1',
            'plot': self.plot1.pk
        })
        self.assertEqual(response.status_code, 302)
        self.device1.refresh_from_db()
        self.assertEqual(self.device1.name, 'Updated Sensor 1')

    def test_device_regenerate_key_regenerates_key(self):
        self.client.login(username='farmer1', password='password1')
        old_key = self.device1.device_key
        response = self.client.post(reverse('device_regenerate_key', kwargs={'pk': self.device1.pk}))
        self.assertEqual(response.status_code, 302)
        self.device1.refresh_from_db()
        self.assertNotEqual(self.device1.device_key, old_key)

    def test_cannot_regenerate_key_for_other_user_device(self):
        self.client.login(username='farmer1', password='password1')
        old_key = self.device2.device_key
        response = self.client.post(reverse('device_regenerate_key', kwargs={'pk': self.device2.pk}))
        self.assertEqual(response.status_code, 404)
        self.device2.refresh_from_db()
        self.assertEqual(self.device2.device_key, old_key)

    def test_device_delete_deletes_device(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.post(reverse('device_delete', kwargs={'pk': self.device1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Device.objects.filter(pk=self.device1.pk).exists())

    def test_cannot_delete_other_user_device(self):
        self.client.login(username='farmer1', password='password1')
        response = self.client.post(reverse('device_delete', kwargs={'pk': self.device2.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Device.objects.filter(pk=self.device2.pk).exists())
