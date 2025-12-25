from django.urls import path
from .views import FaviconView, AmapSecurityKeyView

app_name = 'core'

urlpatterns = [
    path('favicon.ico', FaviconView.as_view(), name='favicon'),
    path('api/amap-security/', AmapSecurityKeyView.as_view(), name='amap_security'),
]
