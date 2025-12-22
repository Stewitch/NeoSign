from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import redirect

from .models import SystemConfig


class InstallationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/install/') or request.path.startswith('/static/'):
            return self.get_response(request)

        try:
            if not SystemConfig.objects.filter(installed=True).exists():
                return redirect('installation:welcome')
        except (OperationalError, ProgrammingError):
            return redirect('installation:welcome')

        return self.get_response(request)
