from django.urls import path

from . import views


urlpatterns = [
    path('readings/', views.sensor_reading_view, name='iot_sensor_reading'),
    path('devices/', views.device_list_view, name='device_list'),
    path('devices/create/', views.device_create_view, name='device_create'),
    path('devices/<int:pk>/', views.device_detail_view, name='device_detail'),
    path('devices/<int:pk>/edit/', views.device_update_view, name='device_update'),
    path('devices/<int:pk>/regenerate-key/', views.device_regenerate_key_view, name='device_regenerate_key'),
    path('devices/<int:pk>/delete/', views.device_delete_view, name='device_delete'),
]