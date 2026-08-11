from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('accounts', '0002_alter_userprofile_id')]
    operations = [
        migrations.AddField(model_name='userprofile', name='bio', field=models.TextField(blank=True)),
        migrations.AddField(model_name='userprofile', name='organization', field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name='userprofile', name='role', field=models.CharField(choices=[('USER', 'User'), ('ORGANIZER', 'Organizer')], default='USER', max_length=12)),
    ]
