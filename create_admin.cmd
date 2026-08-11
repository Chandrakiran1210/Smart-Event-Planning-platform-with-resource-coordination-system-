@echo off
cd /d c:\Users\kiran\Desktop\EVENT
.
.venv\Scripts\python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','event_system.settings'); import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.filter(username='admin').first();
if u is None:
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin@1234')
else:
    u.is_staff = True; u.is_superuser = True; u.email = 'admin@example.com'; u.set_password('Admin@1234'); u.save()"
