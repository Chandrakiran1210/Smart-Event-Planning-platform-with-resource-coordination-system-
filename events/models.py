from django.contrib.auth.models import User
from django.db import models


# =========================================================
# EVENT CATEGORY
# =========================================================

class EventCategory(models.Model):

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    name = models.CharField(
        max_length=100,
        unique=True
    )

    category_code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    description = models.TextField(
        blank=True
    )
    category_image = models.ImageField(
    upload_to='category_images/',
    blank=True,
    null=True
)

    def __str__(self):
        return self.name


# =========================================================
# EVENT
# =========================================================

class Event(models.Model):

    APPROVAL_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Hybrid', 'Hybrid'),
    ]

    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        EventCategory,
        on_delete=models.CASCADE,
        related_name='events'
    )

    event_image = models.ImageField(
        upload_to='event_images/',
        blank=True,
        null=True
    )

    banner_image = models.ImageField(
        upload_to='event_banners/',
        blank=True,
        null=True
    )

    organizer = models.CharField(
        max_length=200,
        blank=True
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events'
    )

    event_mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='Offline'
    )

    venue = models.CharField(
        max_length=250,
        blank=True
    )

    location = models.CharField(
        max_length=250,
        blank=True
    )

    google_map = models.URLField(
        blank=True
    )

    registration_link = models.URLField(
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    start_date = models.DateField()

    end_date = models.DateField()

    registration_deadline = models.DateField(
        null=True,
        blank=True
    )

    event_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    eligibility = models.CharField(
        max_length=300,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    requirements = models.TextField(
        blank=True
    )

    tags = models.CharField(
        max_length=300,
        blank=True
    )

    contact_person = models.CharField(
        max_length=150,
        blank=True
    )

    contact_email = models.EmailField(
        blank=True
    )

    contact_phone = models.CharField(
        max_length=20,
        blank=True
    )

    approval_status = models.CharField(
        max_length=12,
        choices=APPROVAL_CHOICES,
        default='APPROVED'
    )

    review_note = models.TextField(
        blank=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_events'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Upcoming'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.name

# =========================================================
# EVENT REGISTRATION
# =========================================================

class EventRegistration(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )
    attended = models.BooleanField(default=False)
    attended_at = models.DateTimeField(null=True, blank=True)

    qr_code = models.ImageField(
    upload_to='qr_codes/',
    blank=True,
    null=True
)

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_user_event_registration'
            )

        ]

    def __str__(self):
        return f'{self.user.username} -> {self.event.name}'


# =========================================================
# EVENT WISHLIST
# =========================================================

class EventWishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='wishlist_entries'
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_user_event_wishlist'
            )

        ]


# =========================================================
# NOTIFICATIONS
# =========================================================

class Notification(models.Model):

    TYPE_CHOICES = [

        ('INFO', 'Information'),

        ('SUCCESS', 'Success'),

        ('WARNING', 'Warning'),

        ('ERROR', 'Error'),

    ]

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE,

        related_name='notifications'

    )

    title = models.CharField(

        max_length=200

    )

    message = models.TextField()

    event = models.ForeignKey(

        Event,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='notifications'

    )

    notification_type = models.CharField(

        max_length=20,

        choices=TYPE_CHOICES,

        default='INFO'

    )

    icon = models.CharField(

        max_length=30,

        default='🔔',

        blank=True

    )

    action_url = models.CharField(

        max_length=300,

        blank=True

    )

    is_read = models.BooleanField(

        default=False

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    class Meta:

        ordering = ['-created_at']

        verbose_name = "Notification"

        verbose_name_plural = "Notifications"

    def __str__(self):

        return f"{self.title} - {self.user.username}"

# =========================================================
# VENUE MANAGEMENT
# =========================================================

class Venue(models.Model):

    name = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=255
    )

    capacity = models.PositiveIntegerField()

    description = models.TextField(
        blank=True
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# =========================================================
# RESOURCE MANAGEMENT
# =========================================================

class Resource(models.Model):

    RESOURCE_TYPES = [

        ("PROJECTOR", "Projector"),
        ("MIC", "Microphone"),
        ("SPEAKER", "Speaker"),
        ("CHAIR", "Chair"),
        ("TABLE", "Table"),
        ("LIGHT", "Lighting"),
        ("OTHER", "Other"),

    ]

    name = models.CharField(
        max_length=200
    )

    resource_type = models.CharField(
        max_length=30,
        choices=RESOURCE_TYPES
    )

    quantity = models.PositiveIntegerField()

    available_quantity = models.PositiveIntegerField()

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name
    

# =========================================================
# USER SETTINGS
# =========================================================

class UserSettings(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings'
    )

    theme_mode = models.CharField(
        max_length=20,
        default='light'
    )

    accent_color = models.CharField(
        max_length=20,
        default='#2563eb'
    )

    sidebar_color = models.CharField(
        max_length=20,
        default='#111827'
    )

    topbar_color = models.CharField(
        max_length=20,
        default='#ffffff'
    )

    # ==========================================
    # GLOBAL THEME SETTINGS
    # ==========================================

    navbar_color = models.CharField(
        max_length=20,
        default='#2563eb'
    )

    sidebar_color = models.CharField(
        max_length=20,
        default='#1f2937'
    )

    footer_color = models.CharField(
        max_length=20,
        default='#111827'
    )

    font_size = models.PositiveIntegerField(
        default=16
    )

    # ==========================================
    # PAGE COLORS
    # ==========================================

    dashboard_color = models.CharField(
        max_length=20,
        default='#2563eb'
    )

    available_events_color = models.CharField(
        max_length=20,
        default='#8b5cf6'
    )

    joined_events_color = models.CharField(
        max_length=20,
        default='#16a34a'
    )

    wishlist_color = models.CharField(
        max_length=20,
        default='#ec4899'
    )

    calendar_color = models.CharField(
        max_length=20,
        default='#14b8a6'
    )

    profile_color = models.CharField(
        max_length=20,
        default='#f59e0b'
    )

    settings_color = models.CharField(
        max_length=20,
        default='#6366f1'
    )

    def __str__(self):
        return self.user.username


# =========================================================
# THEME PREFERENCE
# =========================================================

class ThemePreference(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='theme_preference'
    )

    theme_name = models.CharField(
        max_length=20,
        default='light'
    )

    accent_color = models.CharField(
        max_length=20,
        default='#2563eb'
    )

    def __str__(self):
        return self.user.username

# =========================================================
# EVENT RESOURCE
# =========================================================

class EventResource(models.Model):

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="event_resources"
    )

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="resource_events"
    )

    quantity_required = models.PositiveIntegerField(
        default=1
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.event.name} - {self.resource.name}"