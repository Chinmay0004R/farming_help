from django.urls import path
from . import views

urlpatterns = [
    path('farm/<int:farm_pk>/plot/create/', views.plot_create_view, name='plot_create'),
    path('<int:pk>/', views.plot_detail_view, name='plot_detail'),
    path('<int:pk>/edit/', views.plot_update_view, name='plot_update'),
    path('<int:pk>/delete/', views.plot_delete_view, name='plot_delete'),
]
