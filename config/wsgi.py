"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

# Autonomous Production Self-Healing: Auto-migrate & Auto-seed on startup
try:
    from django.core.management import call_command
    from django.db import connection
    tables = connection.introspection.table_names()
    if 'auth_user' not in tables:
        print("[FarmPulse WSGI] Initializing database schema...")
        call_command('migrate', interactive=False)
        print("[FarmPulse WSGI] Migrations complete.")

    from django.contrib.auth.models import User
    if not User.objects.filter(username='miriam').exists():
        print("[FarmPulse WSGI] Auto-seeding Miriam Chiphaka 10-year dataset...")
        import runpy
        runpy.run_module('seed_miriam_chiphaka', run_name='__main__')
        print("[FarmPulse WSGI] Miriam Chiphaka seeded successfully.")
except Exception as exc:
    print(f"[FarmPulse WSGI Startup Notice]: {exc}")

