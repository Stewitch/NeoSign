from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _

from .forms import CustomAuthenticationForm, RequiredPasswordChangeForm


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        if user.first_login:
            messages.warning(self.request, _('首次登录，请修改密码'))
            return redirect('authentication:password_change_required')

        if user.is_admin or user.is_superuser:
            return redirect('management:dashboard')
        return redirect('checkin:dashboard')

    def get_success_url(self):  # pragma: no cover - redirect handled in form_valid
        return reverse_lazy('checkin:dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('authentication:login')


class RequiredPasswordChangeView(PasswordChangeView):
    template_name = 'authentication/password_change_required.html'
    form_class = RequiredPasswordChangeForm
    success_url = reverse_lazy('checkin:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        user.first_login = False
        user.save(update_fields=['first_login'])
        messages.success(self.request, _('密码修改成功'))
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.first_login:
            return redirect('checkin:dashboard')
        return super().dispatch(request, *args, **kwargs)
