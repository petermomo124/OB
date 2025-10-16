# core/context_processors.py
from django.db import connections
from django.db.utils import OperationalError


def database_status(request):
    """
    Context processor to add database status to templates
    """

    def check_database_health():
        try:
            db_conn = connections['default']
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except OperationalError:
            return False

    return {
        'database_healthy': check_database_health(),
    }