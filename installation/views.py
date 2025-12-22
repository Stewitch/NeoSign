from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.views import View
from django.utils.translation import gettext as _

from core.models import SystemConfig


User = get_user_model()


class InstallationWelcomeView(View):
    template_name = 'installation/welcome.html'

    def get(self, request):
        config, _ = SystemConfig.objects.get_or_create(pk=1)
        return render(request, self.template_name, {'config': config})

    def post(self, request):
        config, _ = SystemConfig.objects.get_or_create(pk=1)
        site_title = request.POST.get('site_title', config.site_title)
        technician_contact = request.POST.get('technician_contact', '')
        config.site_title = site_title
        config.technician_contact = technician_contact
        config.installed = True
        config.save()
        messages.success(request, _('安装完成，您现在可以登录系统'))
        return redirect('authentication:login')
