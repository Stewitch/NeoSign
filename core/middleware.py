from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone, translation
from django.shortcuts import redirect

from .models import SystemConfig
from checkin.models import Activity


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


class ActivityAutoCloseMiddleware:
    """Auto-close expired activities on management requests.
    - Single events (repeat_type='none'): end_time < now -> is_active=False
    - Repeating events (daily/weekly): end_time date < today -> is_active=False
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only run on management pages to reduce overhead
        if request.path.startswith('/manage/'):
            try:
                now = timezone.now()
                today = timezone.localdate()
                # Close single-shot events past their end_time
                Activity.objects.filter(
                    repeat_type='none', is_active=True, end_time__lt=now
                ).update(is_active=False)
                # Close repeating events beyond their overall end date (if set)
                Activity.objects.filter(
                    is_active=True
                ).exclude(repeat_type='none').filter(
                    end_time__isnull=False, end_time__date__lt=today
                ).update(is_active=False)
            except (OperationalError, ProgrammingError):
                # DB not ready during installation/migration
                pass

        return self.get_response(request)


class ConfigLocaleMiddleware:
    """Apply language and timezone from SystemConfig per request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang_activated = False
        tz_activated = False
        try:
            cfg = SystemConfig.objects.first()
            if cfg:
                if cfg.timezone_str:
                    try:
                        timezone.activate(cfg.timezone_str)
                        tz_activated = True
                    except Exception:
                        pass
                if cfg.language_code:
                    translation.activate(cfg.language_code)
                    lang_activated = True
        except (OperationalError, ProgrammingError):
            cfg = None

        response = self.get_response(request)

        if lang_activated:
            translation.deactivate()
        if tz_activated:
            timezone.deactivate()
        return response
