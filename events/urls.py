from django.urls import path
from . import views

urlpatterns = [

    path('', views.home_view, name='home'),

    path('signup/', views.signup_view, name='signup'),
    path('organizer/signup/', views.organizer_signup_view, name='organizer_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ==========================
    # CATEGORY
    # ==========================

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),


# =========================================================
# VENUE MANAGEMENT
# =========================================================

path(
    'venues/',
    views.venue_list,
    name='venue_list'
),

path(
    'venues/create/',
    views.venue_create,
    name='venue_create'
),

path(
    'venues/<int:pk>/edit/',
    views.venue_edit,
    name='venue_edit'
),

path(
    'venues/<int:pk>/delete/',
    views.venue_delete,
    name='venue_delete'
),

# =========================================================
# RESOURCE MANAGEMENT
# =========================================================

path(
    'resources/',
    views.resource_list,
    name='resource_list'
),

path(
    'resources/create/',
    views.resource_create,
    name='resource_create'
),

path(
    'resources/<int:pk>/edit/',
    views.resource_edit,
    name='resource_edit'
),

path(
    'resources/<int:pk>/delete/',
    views.resource_delete,
    name='resource_delete'
),

    # ==========================
    # EVENTS
    # ==========================

    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:pk>/submit/', views.submit_event, name='submit_event'),
    path('events/<int:pk>/review/', views.review_event, name='review_event'),

    path(
        'events/<int:pk>/participants/',
        views.event_participants,
        name='event_participants'
    ),

    path(
        'events/<int:pk>/participants/<int:registration_pk>/attendance/',
        views.toggle_attendance,
        name='toggle_attendance'
    ),

    # ==========================
    # AVAILABLE EVENTS
    # ==========================

    path('available-events/', views.available_events, name='available_events'),

    path(
        'available-events/<int:pk>/',
        views.event_detail,
        name='event_detail'
    ),
    path(
    'events/<int:pk>/qr/',
    views.event_qr,
    name='event_qr'
    ),

    path(
        'join-event/<int:pk>/',
        views.join_event,
        name='join_event'
    ),

    path(
        'joined-events/',
        views.my_joined_events,
        name='my_joined_events'
    ),

    # ==========================
    # WISHLIST
    # ==========================

    path('wishlist/', views.wishlist_view, name='wishlist'),

    path(
        'wishlist/add/<int:pk>/',
        views.add_to_wishlist,
        name='add_to_wishlist'
    ),

    path(
        'wishlist/remove/<int:pk>/',
        views.remove_from_wishlist,
        name='remove_from_wishlist'
    ),

    # ==========================
    # CALENDAR
    # ==========================

    path(
        'calendar/',
        views.calendar_view,
        name='calendar'
    ),

    path(
        'calendar/events/',
        views.calendar_events,
        name='calendar_events'
    ),

    # ==========================
    # NOTIFICATIONS
    # ==========================

    path(
        'notifications/',
        views.notifications_view,
        name='notifications'
    ),

    path(
        'notifications/<int:pk>/read/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

    path(
        'notifications/read-all/',
        views.mark_all_notifications_read,
        name='mark_all_notifications_read'
    ),

    path(
        'notifications/<int:pk>/delete/',
        views.delete_notification,
        name='delete_notification'
    ),

    # ==========================
    # PROFILE
    # ==========================

    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('theme/', views.theme_settings, name='theme_settings'),
    path(
    'change-password/',
    views.change_password,
    name='password_change'
),
    # ==========================
    # ADMIN
    # ==========================

    path('users/', views.manage_users, name='manage_users'),
    path('reports/', views.reports, name='reports'),

    # ==========================
    # CONTACT
    # ==========================

    path('contact/', views.contact, name='contact'),

    

]