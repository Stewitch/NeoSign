from django.urls import path

from .views import (
    CheckInAPIView,
    CheckInDashboardView,
    CheckInQRImageView,
    CheckInQRPresenterView,
    CheckInQRScanView,
)

app_name = 'checkin'

urlpatterns = [
    path('', CheckInDashboardView.as_view(), name='dashboard'),
    path('api/checkin/<int:activity_id>/', CheckInAPIView.as_view(), name='checkin_api'),
    path('qr/<int:activity_id>/presenter/', CheckInQRPresenterView.as_view(), name='qr_presenter'),
    path('qr/<int:activity_id>/image.png', CheckInQRImageView.as_view(), name='qr_image'),
    path('qr/<int:activity_id>/scan/', CheckInQRScanView.as_view(), name='qr_scan'),
]