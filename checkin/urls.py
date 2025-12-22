from django.urls import path

from .views import CheckInAPIView, CheckInDashboardView

app_name = 'checkin'

urlpatterns = [
    path('', CheckInDashboardView.as_view(), name='dashboard'),
    path('api/checkin/<int:activity_id>/', CheckInAPIView.as_view(), name='checkin_api'),
]