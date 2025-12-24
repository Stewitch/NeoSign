from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
import qrcode
import io

from .models import Activity, ActivityParticipation, CheckInRecord


class CheckInDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'checkin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        activities = Activity.objects.filter(participants=user, is_active=True).select_related('created_by').prefetch_related('checkins')

        activity_list = []
        for activity in activities:
            if not activity.is_open_for(now):
                continue
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
                    'is_creator': activity.created_by_id == user.id,
                    'qr_interval': max(activity.qr_refresh_interval_s or 30, 10),
                }
            )

        context['activities'] = activity_list
        context['current_time'] = now
        return context


class CheckInAPIView(LoginRequiredMixin, View):
    def post(self, request, activity_id):
        activity = get_object_or_404(Activity, id=activity_id, is_active=True)
        if not activity.is_open_for(timezone.now()):
            return JsonResponse({'success': False, 'error': _('活动不在开放时间')})

        allowed = ActivityParticipation.objects.filter(
            activity=activity, user=request.user, can_participate=True
        ).exists()
        if not allowed:
            return JsonResponse({'success': False, 'error': _('您无权参与此活动')})

        if CheckInRecord.objects.filter(activity=activity, user=request.user).exists():
            return JsonResponse({'success': False, 'error': _('您已签到过此活动')})

        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        if activity.location_enabled:
            try:
                lat_v = float(lat)
                lng_v = float(lng)
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'error': _('缺少或无效的位置参数')})
            if not self._within_radius(activity, lat_v, lng_v):
                return JsonResponse({'success': False, 'error': _('不在签到范围内')})

        token = request.POST.get('qr_token')
        if activity.qr_enabled and not activity.is_valid_qr_token(token, timezone.now()):
            return JsonResponse({'success': False, 'error': _('二维码已过期或无效')})

        CheckInRecord.objects.create(
            activity=activity,
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            latitude=float(lat) if lat else None,
            longitude=float(lng) if lng else None,
        )

        return JsonResponse({'success': True, 'message': _('签到成功')})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _within_radius(self, activity: Activity, lat: float, lng: float) -> bool:
        if not (activity.location_lat and activity.location_lng and activity.location_radius_m):
            return True
        # Haversine formula
        from math import radians, sin, cos, asin, sqrt
        R = 6371000.0
        dlat = radians(lat - activity.location_lat)
        dlng = radians(lng - activity.location_lng)
        a = sin(dlat/2)**2 + cos(radians(activity.location_lat)) * cos(radians(lat)) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        distance = R * c
        return distance <= float(activity.location_radius_m or 0)


class PresenterOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        activity_id = self.kwargs.get('activity_id')
        activity = Activity.objects.filter(id=activity_id).first()
        if not activity:
            return False
        user = self.request.user
        return user.is_superuser or user.is_admin or activity.created_by_id == user.id


class CheckInQRPresenterView(LoginRequiredMixin, PresenterOnlyMixin, TemplateView):
    template_name = 'checkin/qr_presenter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = get_object_or_404(Activity, id=self.kwargs['activity_id'])
        context['activity'] = activity
        context['interval'] = max(activity.qr_refresh_interval_s or 30, 10)
        return context


class CheckInQRImageView(LoginRequiredMixin, PresenterOnlyMixin, View):
    def get(self, request, activity_id):
        activity = get_object_or_404(Activity, id=activity_id)
        token = activity.current_qr_token(timezone.now())
        img = qrcode.make(token)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return HttpResponse(buf.getvalue(), content_type='image/png')


class CheckInQRScanView(LoginRequiredMixin, TemplateView):
    template_name = 'checkin/qr_scan.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = get_object_or_404(Activity, id=self.kwargs['activity_id'])
        context['activity'] = activity
        return context