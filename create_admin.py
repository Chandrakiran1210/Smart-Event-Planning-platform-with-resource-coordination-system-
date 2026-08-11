import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_system.settings')
import django
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'Admin@1234'

user = User.objects.filter(username=username).first()
if user is None:
    User.objects.create_superuser(username, email, password)
else:
    user.is_staff = True
    user.is_superuser = True
    user.email = email
    user.set_password(password)
    user.save()
print('Admin account ready:', username, email)
