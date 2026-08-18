"""
URL configuration for event_system project.
"""

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Django Admin
    path(
        'admin/',
        admin.site.urls
    ),

    # Event Management Application
    path(
        '',
        include('events.urls')
    ),

    # Smart Event AI Chatbot
    path(
        'chatbot/',
        include('chatbot.urls')
    ),

]


# Media files during development
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )