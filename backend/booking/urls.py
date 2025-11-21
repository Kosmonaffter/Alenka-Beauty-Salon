from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='service_list'),
    path(
        'book/<int:procedure_id>/',
        views.BookingCreateView.as_view(),
        name='create_booking_with_service',
    ),
    path('book/', views.BookingCreateView.as_view(), name='create_booking'),
    path(
        'phone-confirmation/',
        views.PhoneConfirmationView.as_view(),
        name='phone_confirmation',
    ),
    path(
        'success/<uuid:booking_id>/',
        views.BookingSuccessView.as_view(),
        name='booking_success',
    ),
    path('ajax/masters/', views.get_available_masters, name='ajax_masters'),
    path('ajax/times/', views.get_available_times, name='ajax_times'),
]
