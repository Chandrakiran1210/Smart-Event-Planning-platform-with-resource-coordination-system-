# Generated manually to extend the existing event workflow.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('accounts', '0002_alter_userprofile_id'), ('events', '0003_event_eligibility_event_event_mode_and_more')]
    operations = [
        migrations.AddField(model_name='event', name='approval_status', field=models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING', 'Pending approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='APPROVED', max_length=12)),
        migrations.AddField(model_name='event', name='owner', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organized_events', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='event', name='review_note', field=models.TextField(blank=True)),
        migrations.AddField(model_name='event', name='reviewed_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='event', name='reviewed_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_events', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='event', name='submitted_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='eventregistration', name='attended', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='eventregistration', name='attended_at', field=models.DateTimeField(blank=True, null=True)),
    ]
