from django.urls import path
from . import views

app_name = 'masters'

urlpatterns = [
    path('', views.MastersListView.as_view(), name='index'),
]
