from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from .models import Activity, ActivityParticipation, CheckInRecord


class CheckInDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'checkin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        activities = Activity.objects.filter(
            participants=user,
            start_time__lte=now,
            end_time__gte=now,
            is_active=True,
        ).select_related('created_by').prefetch_related('checkins')

        activity_list = []
        for activity in activities:
            has_checked_in = CheckInRecord.objects.filter(activity=activity, user=user).exists()
            checkin_time = None
            if has_checked_in:
                checkin = CheckInRecord.objects.filter(activity=activity, user=user).first()
                checkin_time = checkin.checkin_time

            activity_list.append(
                {
                    'activity': activity,
                    'has_checked_in': has_checked_in,
                    'checkin_time': checkin_time,
                }
            )

        context['activities'] = activity_list
        context['current_time'] = now
        return context


class CheckInAPIView(LoginRequiredMixin, View):
    def post(self, request, activity_id):
        try:
            activity = Activity.objects.get(
                id=activity_id,
                is_active=True,
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now(),
            )
        except Activity.DoesNotExist:
            return JsonResponse({'success': False, 'error': '活动不存在或已结束'})

        allowed = ActivityParticipation.objects.filter(
            activity=activity, user=request.user, can_participate=True
        ).exists()
        if not allowed:
            return JsonResponse({'success': False, 'error': '您无权参与此活动'})

        if CheckInRecord.objects.filter(activity=activity, user=request.user).exists():
            return JsonResponse({'success': False, 'error': '您已签到过此活动'})

        CheckInRecord.objects.create(
            activity=activity,
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return JsonResponse({'success': True, 'message': '签到成功'})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip