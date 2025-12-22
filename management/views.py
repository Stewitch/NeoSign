from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from django.conf import settings
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from checkin.models import Activity, ActivityParticipation, CheckInRecord
from datetime import datetime, time, timedelta
from core.models import SystemConfig
from .utils import (
    export_table_to_csv,
    export_table_to_xlsx,
    generate_random_password,
    parse_users_from_csv_upload,
    parse_users_from_text,
)


User = get_user_model()

# Use a slightly lower iteration PBKDF2 hasher for bulk imports to improve speed.
# Users are still forced to change password on first login (first_login=True).
_bulk_hasher = PBKDF2PasswordHasher()
_bulk_hasher.iterations = getattr(settings, 'BULK_CREATE_PBKDF2_ITERATIONS', 120000)


def _bulk_hash_password(raw_password: str) -> str:
    return _bulk_hasher.encode(password=raw_password, salt=_bulk_hasher.salt())


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_superuser

    def handle_no_permission(self):  # pragma: no cover - view-level redirect
        messages.error(self.request, '您没有权限访问此页面')
        return redirect('checkin:dashboard')


class ManagementDashboardView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = 'management/dashboard.html'


class UserListView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = 'management/user_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        users = User.objects.all().order_by('-created_at')
        if query:
            users = users.filter(Q(student_id__icontains=query) | Q(first_name__icontains=query))
        paginator = Paginator(users, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['query'] = query
        return context


class UserResetView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_admin or user.is_superuser:
            messages.warning(request, '管理员账号请单独处理，无法在此重置')
            return redirect('management:user_list')
        new_password = generate_random_password()
        user.set_password(new_password)
        user.first_login = True
        user.save(update_fields=['password', 'first_login'])
        messages.success(request, f'已为 {user.student_id} 重置密码')
        return redirect('management:user_list')


class UserDeleteView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_admin or user.is_superuser:
            messages.warning(request, '管理员账号请单独处理，无法在此删除')
            return redirect('management:user_list')
        user.delete()
        messages.success(request, f'已删除用户 {user.student_id}')
        return redirect('management:user_list')


class UserBulkResetView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request):
        user_ids = request.POST.getlist('user_ids')
        fmt = request.POST.get('format', 'xlsx')
        users = User.objects.filter(id__in=user_ids, is_admin=False, is_superuser=False)
        if not users.exists():
            messages.warning(request, '未选择用户')
            return redirect('management:user_list')

        rows = []
        for user in users:
            password = generate_random_password()
            user.set_password(password)
            user.first_login = True
            user.save(update_fields=['password', 'first_login'])
            rows.append([user.student_id, password])

        headers = ['学号', '新密码']
        filename = 'user_password_reset'
        if fmt == 'csv':
            return export_table_to_csv(headers, rows, filename)
        return export_table_to_xlsx(headers, rows, filename)


class UserBulkDeleteView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request):
        user_ids = request.POST.getlist('user_ids')
        selected_ids = {uid for uid in user_ids if uid}
        if not selected_ids:
            messages.warning(request, '未选择可删除的用户（管理员不会在此删除）')
            return redirect('management:user_list')

        users = User.objects.filter(id__in=selected_ids, is_admin=False, is_superuser=False)
        deletable_count = users.count()
        if deletable_count == 0:
            messages.warning(request, '未选择可删除的用户（管理员不会在此删除）')
            return redirect('management:user_list')

        protected_count = max(len(selected_ids) - deletable_count, 0)
        users.delete()
        msg = f'已删除 {deletable_count} 个用户'
        if protected_count:
            msg += f'，跳过 {protected_count} 个管理员'
        messages.success(request, msg)
        return redirect('management:user_list')


class UserBulkRoleUpdateView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request):
        user_ids = request.POST.getlist('user_ids')
        role = request.POST.get('role')
        if not user_ids:
            messages.warning(request, '未选择用户')
            return redirect('management:user_list')

        role_flags = {
            'normal': {'is_staff': False, 'is_admin': False, 'is_superuser': False},
            'staff': {'is_staff': True, 'is_admin': False, 'is_superuser': False},
            'admin': {'is_staff': True, 'is_admin': True, 'is_superuser': False},
        }.get(role)

        if role_flags is None:
            messages.warning(request, '无效的身份选择')
            return redirect('management:user_list')

        qs = User.objects.filter(id__in=user_ids, is_superuser=False)
        updated = qs.update(**role_flags)
        skipped = len(user_ids) - updated
        msg = f'已更新 {updated} 个用户身份'
        if skipped:
            msg += f'，跳过 {skipped} 个系统管理员'
        messages.success(request, msg)
        return redirect('management:user_list')


class UserBulkCreateView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request):
        fmt = request.POST.get('format', 'xlsx')
        text = request.POST.get('student_ids', '')
        user_map = parse_users_from_text(text)

        file = request.FILES.get('csv_file')
        if file and (file.name or '').lower().endswith('.csv'):
            csv_map = parse_users_from_csv_upload(file)
            # Prefer non-empty names from CSV
            for sid, name in csv_map.items():
                if sid not in user_map or name:
                    user_map[sid] = name

        incoming_ids = list(user_map.keys())
        existing_ids = set(
            User.objects.filter(student_id__in=incoming_ids).values_list('student_id', flat=True)
        )

        pending = []
        for student_id, name in user_map.items():
            if student_id in existing_ids:
                continue
            password = generate_random_password()
            pending.append((student_id, name or '', password))

        if not pending:
            messages.success(request, '成功创建 0 个用户（全部为重复或输入为空）')
            return redirect('management:user_list')

        users_to_create = [
            User(
                student_id=sid,
                first_name=name,
                password=_bulk_hash_password(pwd),
                first_login=True,
            )
            for sid, name, pwd in pending
        ]
        User.objects.bulk_create(users_to_create, batch_size=1000)

        headers = ['学号', '初始密码']
        rows = [[sid, pwd] for sid, _, pwd in pending]
        filename = 'users_export'
        if fmt == 'csv':
            return export_table_to_csv(headers, rows, filename)
        return export_table_to_xlsx(headers, rows, filename)


class ActivityListView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = 'management/activity_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = Activity.objects.all().order_by('-start_time').select_related('created_by')
        paginator = Paginator(activities, self.paginate_by)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ActivityCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Activity
    template_name = 'management/activity_form.html'
    fields = [
        'name', 'description', 'start_time', 'end_time',
        'repeat_type', 'window_start_time', 'window_end_time',
        'location_enabled', 'location_lat', 'location_lng', 'location_radius_m',
        'qr_enabled', 'qr_refresh_interval_s',
    ]
    success_url = reverse_lazy('management:activity_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().order_by('student_id')
        context['selected_user_ids'] = []
        context['is_edit'] = False
        context['weekday_selected'] = []
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        apply_repeat_and_time(self.request, form)
        apply_checkin_mode(self.request, form)
        response = super().form_valid(form)
        participant_ids = [int(uid) for uid in self.request.POST.getlist('participants') if uid]
        for user_id in participant_ids:
            ActivityParticipation.objects.get_or_create(
                activity=self.object, user_id=user_id, defaults={'can_participate': True}
            )
        messages.success(self.request, '活动创建成功')
        return response


class ActivityUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Activity
    template_name = 'management/activity_form.html'
    fields = [
        'name', 'description', 'start_time', 'end_time', 'is_active',
        'repeat_type', 'window_start_time', 'window_end_time',
        'location_enabled', 'location_lat', 'location_lng', 'location_radius_m',
        'qr_enabled', 'qr_refresh_interval_s',
    ]
    success_url = reverse_lazy('management:activity_list')

    def get_initial(self):
        initial = super().get_initial()
        participants = self.object.participants.values_list('student_id', flat=True)
        initial['participants'] = ' '.join(participants)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = self.object.participants.values_list('id', flat=True)
        context['users'] = User.objects.all().order_by('student_id')
        context['selected_user_ids'] = list(participants)
        context['is_edit'] = True
        context['weekday_selected'] = self.object.repeat_weekdays or []
        return context

    def form_valid(self, form):
        apply_repeat_and_time(self.request, form)
        apply_checkin_mode(self.request, form)
        response = super().form_valid(form)
        participant_ids = {int(uid) for uid in self.request.POST.getlist('participants') if uid}
        user_ids = set(participant_ids)

        # remove old participants not in new set
        ActivityParticipation.objects.filter(activity=self.object).exclude(user_id__in=user_ids).delete()
        # add new participants
        for uid in user_ids:
            ActivityParticipation.objects.get_or_create(
                activity=self.object, user_id=uid, defaults={'can_participate': True}
            )

        messages.success(self.request, '活动已更新')
        return response


class ActivityCloseView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(Activity, pk=pk)
        activity.is_active = False
        activity.end_time = timezone.now()
        activity.save(update_fields=['is_active', 'end_time'])
        messages.success(request, '活动已提前结束')
        return redirect('management:activity_list')


class ActivityStatsView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = 'management/activity_stats.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = get_object_or_404(Activity, id=self.kwargs['activity_id'])
        checked_qs = CheckInRecord.objects.filter(activity=activity).select_related('user')
        checked_users = set(checked_qs.values_list('user_id', flat=True))
        participants_qs = activity.participants.all()
        unchecked_qs = participants_qs.exclude(id__in=checked_users)

        checked_paginator = Paginator(checked_qs, self.paginate_by)
        unchecked_paginator = Paginator(unchecked_qs, self.paginate_by)
        context['activity'] = activity
        context['checked_page'] = checked_paginator.get_page(self.request.GET.get('checked_page'))
        context['unchecked_page'] = unchecked_paginator.get_page(self.request.GET.get('unchecked_page'))
        context['checked_count'] = checked_qs.count()
        context['total_participants'] = participants_qs.count()
        context['unchecked_count'] = context['total_participants'] - context['checked_count']
        return context


class ActivityStatsExportView(LoginRequiredMixin, AdminOnlyMixin, View):
    def get(self, request, activity_id, kind, fmt):
        activity = get_object_or_404(Activity, id=activity_id)
        headers = ['学号', '姓名', '签到时间', 'IP地址']

        checked_qs = CheckInRecord.objects.filter(activity=activity).select_related('user')
        checked_ids = set(checked_qs.values_list('user_id', flat=True))
        participants_qs = activity.participants.all()

        if kind == 'checked':
            rows = [
                [
                    record.user.student_id,
                    record.user.first_name,
                    record.checkin_time.strftime('%Y-%m-%d %H:%M:%S'),
                    record.ip_address,
                ]
                for record in checked_qs
            ]
        else:
            rows = [
                [user.student_id, user.first_name, '', '']
                for user in participants_qs.exclude(id__in=checked_ids)
            ]

        filename = f'activity_{activity_id}_{kind}_export'
        if fmt == 'csv':
            return export_table_to_csv(headers, rows, filename)
        return export_table_to_xlsx(headers, rows, filename)


class SiteSettingsView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = SystemConfig
    template_name = 'management/site_settings.html'
    fields = [
        'site_title', 'site_logo', 'technician_contact', 'map_api_key',
        'password_length', 'password_require_uppercase', 'password_require_lowercase',
        'password_require_digits', 'password_require_symbols', 'password_symbols'
    ]
    success_url = reverse_lazy('management:dashboard')

    def get_object(self):
        obj, _ = SystemConfig.objects.get_or_create(pk=1)
        return obj

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        text_fields = ['site_title', 'technician_contact', 'map_api_key', 'password_symbols']
        for name in text_fields:
            if name in form.fields:
                form.fields[name].widget.attrs.update({'class': 'form-control'})
        if 'password_length' in form.fields:
            form.fields['password_length'].widget.attrs.update({'class': 'form-control', 'min': 6})
        if 'site_logo' in form.fields:
            form.fields['site_logo'].widget.attrs.update({'class': 'form-control'})
        return form

    def form_valid(self, form):
        messages.success(self.request, '网站设置已更新')
        return super().form_valid(form)


def apply_repeat_and_time(request, form):
    tz = timezone.get_current_timezone()

    repeat_type = form.cleaned_data.get('repeat_type') or 'none'
    weekdays = [int(x) for x in request.POST.getlist('repeat_weekdays') if x]
    if repeat_type == 'weekly' and len(weekdays) >= 7:
        repeat_type = 'daily'
        weekdays = []
    form.instance.repeat_type = repeat_type
    form.instance.repeat_weekdays = weekdays if repeat_type == 'weekly' else []

    # time windows
    window_mode = request.POST.get('window_mode', 'range')
    start_time_str = request.POST.get('window_start_time')
    end_time_str = request.POST.get('window_end_time')
    duration_min = request.POST.get('window_duration_minutes')

    if start_time_str:
        form.instance.window_start_time = time.fromisoformat(start_time_str)
    if window_mode == 'duration' and start_time_str and duration_min:
        minutes = int(duration_min)
        base = datetime.combine(datetime.today(), form.instance.window_start_time)
        form.instance.window_end_time = (base + timedelta(minutes=minutes)).time()
    elif end_time_str:
        form.instance.window_end_time = time.fromisoformat(end_time_str)

    # date handling
    if repeat_type == 'none':
        # single event uses start_time/end_time from form input (datetime-local)
        return
    start_date_str = request.POST.get('repeat_start_date')
    end_date_str = request.POST.get('repeat_end_date')
    if start_date_str:
        dt = datetime.fromisoformat(start_date_str)
        form.instance.start_time = tz.localize(datetime.combine(dt.date(), time(0, 0)))
    if end_date_str:
        dt = datetime.fromisoformat(end_date_str)
        form.instance.end_time = tz.localize(datetime.combine(dt.date(), time(23, 59, 59)))
    else:
        # no end date -> far future
        form.instance.end_time = tz.localize(datetime.combine(form.instance.start_time.date(), time(23, 59, 59))) + timedelta(days=3650)


def apply_checkin_mode(request, form):
    mode = request.POST.get('checkin_mode', 'basic')
    form.instance.location_enabled = mode in ['location', 'both']
    form.instance.qr_enabled = mode in ['qr', 'both']
