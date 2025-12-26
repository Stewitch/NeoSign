from django.contrib import admin

from .models import Activity, ActivityParticipation, CheckInRecord


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_time', 'end_time', 'is_active')
	list_filter = ('is_active',)
	search_fields = ('name',)


@admin.register(ActivityParticipation)
class ActivityParticipationAdmin(admin.ModelAdmin):
	list_display = ('activity', 'user', 'can_participate')
	list_filter = ('can_participate',)


@admin.register(CheckInRecord)
class CheckInRecordAdmin(admin.ModelAdmin):
	list_display = ('activity', 'user', 'checkin_time', 'ip_address')
	search_fields = ('user__username', 'activity__name')
