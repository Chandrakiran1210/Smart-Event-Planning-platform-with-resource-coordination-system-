from django.contrib import admin

from .models import Event, EventCategory, EventRegistration, EventWishlist, Notification, ThemePreference, UserSettings

admin.site.register(EventCategory)
admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(EventWishlist)
admin.site.register(Notification)
admin.site.register(UserSettings)
admin.site.register(ThemePreference)
