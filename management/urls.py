from django.urls import path

from .views import (
    ActivityCloseView,
    ActivityCreateView,
    ActivityDeleteView,
    ActivityListView,
    ActivityStatsExportView,
    ActivityStatsView,
    ActivityStatusUpdateView,
    ActivityUpdateView,
    UserBulkCreateView,
    UserBulkDeleteView,
    ManagementDashboardView,
    SiteSettingsView,
    UserBulkResetView,
    UserBulkRoleUpdateView,
    UserDeleteView,
    UserListView,
    UserResetView,
)

app_name = 'management'

urlpatterns = [
    path('', ManagementDashboardView.as_view(), name='dashboard'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/bulk-create/', UserBulkCreateView.as_view(), name='user_bulk_create'),
    path('users/bulk-reset/', UserBulkResetView.as_view(), name='user_bulk_reset'),
    path('users/bulk-delete/', UserBulkDeleteView.as_view(), name='user_bulk_delete'),
    path('users/bulk-role/', UserBulkRoleUpdateView.as_view(), name='user_bulk_role'),
    path('users/reset/<int:pk>/', UserResetView.as_view(), name='user_reset'),
    path('users/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('activities/', ActivityListView.as_view(), name='activity_list'),
    path('activities/create/', ActivityCreateView.as_view(), name='activity_create'),
    path('activities/<int:pk>/edit/', ActivityUpdateView.as_view(), name='activity_edit'),
    path('activities/<int:pk>/close/', ActivityCloseView.as_view(), name='activity_close'),
    path('activities/<int:pk>/delete/', ActivityDeleteView.as_view(), name='activity_delete'),
    path('activities/<int:activity_id>/stats/', ActivityStatsView.as_view(), name='activity_stats'),
    path(
        'activities/<int:activity_id>/stats/export/<str:kind>/<str:fmt>/',
        ActivityStatsExportView.as_view(),
        name='activity_stats_export',
    ),
    path(
        'activities/<int:activity_id>/stats/status/',
        ActivityStatusUpdateView.as_view(),
        name='activity_status_update',
    ),
    path('site-settings/', SiteSettingsView.as_view(), name='site_settings'),
]
