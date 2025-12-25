from django.urls import path
from .views import FaviconView

app_name = 'core'

urlpatterns = [
    path('favicon.ico', FaviconView.as_view(), name='favicon'),
]
