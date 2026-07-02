from django.urls import path
from .views import send_notification, list_logs
urlpatterns = [
    path('send/', send_notification),
    path('logs/', list_logs),
]
