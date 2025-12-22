from django.urls import path

from .views import (
    ActivityCreateView,
    BulkUserCreateView,
    CheckInStatsView,
    ManagementDashboardView,
    SiteSettingsView,
)

app_name = 'management'

urlpatterns = [
    path('', ManagementDashboardView.as_view(), name='dashboard'),
    path('users/bulk-create/', BulkUserCreateView.as_view(), name='bulk_user_create'),
    path('activities/create/', ActivityCreateView.as_view(), name='activity_create'),
    path('activities/<int:activity_id>/stats/', CheckInStatsView.as_view(), name='activity_stats'),
    path('site-settings/', SiteSettingsView.as_view(), name='site_settings'),
]
