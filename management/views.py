import random
import string

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from openpyxl import Workbook

from checkin.models import Activity, ActivityParticipation, CheckInRecord
from core.models import SystemConfig


User = get_user_model()


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_superuser

    def handle_no_permission(self):  # pragma: no cover - view-level redirect
        messages.error(self.request, '您没有权限访问此页面')
        return redirect('checkin:dashboard')


class ManagementDashboardView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = 'management/dashboard.html'


class BulkUserCreateView(LoginRequiredMixin, AdminOnlyMixin, View):
    template_name = 'management/bulk_user_create.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        raw_ids = request.POST.get('student_ids', '')
        student_ids = [sid.strip() for sid in raw_ids.split() if sid.strip()]

        def generate_random_password():
            length = 12
            chars = string.ascii_letters + string.digits + '!@#$%^&*'
            return ''.join(random.choice(chars) for _ in range(length))

        created_users: list[dict[str, str]] = []
        for student_id in student_ids:
            if User.objects.filter(student_id=student_id).exists():
                continue
            password = generate_random_password()
            user = User.objects.create_user(student_id=student_id, password=password)
            created_users.append({'student_id': student_id, 'initial_password': password})

        if created_users:
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="users_export.xlsx"'

            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = '用户列表'
            worksheet.append(['学号', '初始密码'])
            for user_data in created_users:
                worksheet.append([user_data['student_id'], user_data['initial_password']])
            workbook.save(response)
            return response

        messages.success(request, f'成功创建 {len(created_users)} 个用户')
        return redirect('management:dashboard')


class ActivityCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Activity
    template_name = 'management/activity_form.html'
    fields = ['name', 'description', 'start_time', 'end_time']
    success_url = reverse_lazy('management:dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        participant_field = self.request.POST.get('participants', '')
        participant_ids = [pid.strip() for pid in participant_field.split() if pid.strip()]
        for user_id in participant_ids:
            ActivityParticipation.objects.get_or_create(
                activity=self.object, user_id=user_id, defaults={'can_participate': True}
            )
        messages.success(self.request, '活动创建成功')
        return response


class CheckInStatsView(LoginRequiredMixin, AdminOnlyMixin, View):
    def get(self, request, activity_id):
        activity = get_object_or_404(Activity, id=activity_id)
        records = CheckInRecord.objects.filter(activity=activity).select_related('user')

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="checkin_stats_{activity_id}.xlsx"'

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = '签到统计'
        worksheet.append(['学号', '签到时间', 'IP地址'])

        for record in records:
            worksheet.append([
                record.user.student_id,
                record.checkin_time.strftime('%Y-%m-%d %H:%M:%S'),
                record.ip_address,
            ])

        workbook.save(response)
        return response


class SiteSettingsView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = SystemConfig
    template_name = 'management/site_settings.html'
    fields = ['site_title', 'site_logo', 'technician_contact']
    success_url = reverse_lazy('management:dashboard')

    def get_object(self):
        obj, _ = SystemConfig.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        messages.success(self.request, '网站设置已更新')
        return super().form_valid(form)
