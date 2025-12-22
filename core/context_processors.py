from django.db.utils import OperationalError, ProgrammingError

from .models import SystemConfig


def system_config(request):
    try:
        config = SystemConfig.objects.first()
    except (OperationalError, ProgrammingError):
        config = None
    return {'config': config}
