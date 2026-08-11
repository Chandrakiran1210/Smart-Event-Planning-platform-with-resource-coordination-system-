from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import Event, EventCategory, EventRegistration


class EventRegistrationTests(TestCase):
    def test_duplicate_registration_is_prevented(self):
        user = get_user_model().objects.create_user(username='alice', email='alice@example.com', password='secret123')
        category = EventCategory.objects.create(name='Tech', description='Technology events')
        event = Event.objects.create(
            name='Python Workshop',
            category=category,
            start_date='2026-08-01',
            end_date='2026-08-01',
            location='Hyderabad',
            status='Upcoming',
            description='Hands-on Python lab',
        )

        EventRegistration.objects.create(user=user, event=event)

        with self.assertRaises(IntegrityError):
            EventRegistration.objects.create(user=user, event=event)
