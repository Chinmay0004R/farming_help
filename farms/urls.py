from django.urls import path
from . import views

urlpatterns = [
    path('money/', views.money_view, name='money'),
    path('diary/', views.diary_view, name='diary'),
    path('reminders/', views.reminders_view, name='reminders'),
    path('', views.farm_list_view, name='farm_list'),
    path('create/', views.farm_create_view, name='farm_create'),
    path('<int:pk>/', views.farm_detail_view, name='farm_detail'),
    path('<int:pk>/edit/', views.farm_update_view, name='farm_update'),
    path('<int:pk>/delete/', views.farm_delete_view, name='farm_delete'),
]
