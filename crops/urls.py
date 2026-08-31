from django.urls import path
from . import views

urlpatterns = [
    # Crops
    path('catalog/', views.crop_list_view, name='crop_list'),
    path('catalog/add/', views.crop_create_view, name='crop_create'),
    path('catalog/<int:pk>/edit/', views.crop_update_view, name='crop_update'),
    path('catalog/<int:pk>/delete/', views.crop_delete_view, name='crop_delete'),
    
    # Crop Cycles
    path('cycles/', views.cropcycle_list_view, name='cropcycle_list'),
    path('cycles/add/', views.cropcycle_create_view, name='cropcycle_create'),
    path('cycles/<int:pk>/', views.cropcycle_detail_view, name='cropcycle_detail'),
    path('cycles/<int:pk>/edit/', views.cropcycle_update_view, name='cropcycle_update'),
    path('cycles/<int:pk>/delete/', views.cropcycle_delete_view, name='cropcycle_delete'),

    # Harvests
    path('cycles/<int:cycle_pk>/harvests/add/', views.harvest_create_view, name='harvest_create'),
    path('harvests/<int:pk>/edit/', views.harvest_update_view, name='harvest_update'),
    path('harvests/<int:pk>/delete/', views.harvest_delete_view, name='harvest_delete'),
]
