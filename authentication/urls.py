from django.urls import path

from .views import CustomLoginView, CustomLogoutView, RequiredPasswordChangeView

app_name = 'authentication'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-change-required/', RequiredPasswordChangeView.as_view(), name='password_change_required'),
]
