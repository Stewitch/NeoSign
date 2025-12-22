from django.urls import path

from .views import InstallationWelcomeView

app_name = 'installation'

urlpatterns = [
    path('', InstallationWelcomeView.as_view(), name='welcome'),
]
