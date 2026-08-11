from django import forms
from django.utils import timezone

from .models import (
    Event,
    EventCategory,
    Venue,
    Resource,
)

# =========================================================
# EVENT CATEGORY FORM
# =========================================================

class EventCategoryForm(forms.ModelForm):

    class Meta:
        model = EventCategory

        fields = [
    'name',
    'category_code',
    'priority',
    'description',
    'category_image',
]
        widgets = {
                    'category_image': forms.ClearableFileInput(
    attrs={
        'accept': 'image/*'
    }
),
            'name': forms.Select(
                choices=[
                    ('', '-- Select Category --'),
                    ('Job Opportunities', 'Job Opportunities'),
                    ('Internships', 'Internships'),
                    ('Hackathons & Coding Contests', 'Hackathons & Coding Contests'),
                    ('Technical Workshops', 'Technical Workshops'),
                    ('Training & Certification', 'Training & Certification'),
                    ('Higher Education', 'Higher Education'),
                    ('Competitive Exams', 'Competitive Exams'),
                    ('Career Fairs & Job Fairs', 'Career Fairs & Job Fairs'),
                    ('Tech Talks & Seminars', 'Tech Talks & Seminars'),
                    ('Startup & Entrepreneurship', 'Startup & Entrepreneurship'),
                ]
            ),

            'category_code': forms.TextInput(
                attrs={
                    'placeholder': 'Example: JOB01'
                }
            ),

            'priority': forms.Select(),

            'description': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Enter category description...'
                }
            ),
        }


# =========================================================
# EVENT FORM
# =========================================================

class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["venue"].queryset = Venue.objects.filter(
            is_available=True
        )

        self.fields["venue"].empty_label = "Select Venue"

    class Meta:

        model = Event

        fields = [

            'name',

            'category',

            'event_image',

            'banner_image',

            'event_mode',

            'venue',

            'location',

            'google_map',

            'website',

            'registration_link',

            'start_date',

            'end_date',

            'registration_deadline',

            'event_fee',

            'max_participants',

            'eligibility',

            'organizer',

            'contact_person',

            'contact_email',

            'contact_phone',

            'tags',

            'requirements',

            'status',

            'description',

        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'placeholder': 'Event Name'
            }),

            'category': forms.Select(),

            'event_image': forms.ClearableFileInput(attrs={
                'accept': 'image/*'
            }),

            'banner_image': forms.ClearableFileInput(attrs={
                'accept': 'image/*'
            }),

            'event_mode': forms.Select(),

            'venue': forms.Select(),

            'location': forms.TextInput(attrs={
                'placeholder': 'City / State'
            }),

            'google_map': forms.URLInput(attrs={
                'placeholder': 'Google Maps Link'
            }),

            'website': forms.URLInput(attrs={
                'placeholder': 'Official Website'
            }),

            'registration_link': forms.URLInput(attrs={
                'placeholder': 'Registration Link'
            }),

            'start_date': forms.DateInput(attrs={
                'type': 'date'
            }),

            'end_date': forms.DateInput(attrs={
                'type': 'date'
            }),

            'registration_deadline': forms.DateInput(attrs={
                'type': 'date'
            }),

            'event_fee': forms.NumberInput(attrs={
                'placeholder': '0'
            }),

            'max_participants': forms.NumberInput(attrs={
                'placeholder': '100'
            }),

            'eligibility': forms.TextInput(attrs={
                'placeholder': 'Eligibility'
            }),

            'organizer': forms.TextInput(attrs={
                'placeholder': 'Organizer Name'
            }),

            'contact_person': forms.TextInput(attrs={
                'placeholder': 'Contact Person'
            }),

            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'Email'
            }),

            'contact_phone': forms.TextInput(attrs={
                'placeholder': 'Phone Number'
            }),

            'tags': forms.TextInput(attrs={
                'placeholder': 'AI, Hackathon, Workshop'
            }),

            'requirements': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Requirements'
            }),

            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Event Description'
            }),

            'status': forms.Select(),

        }

    def clean(self):

        cleaned_data = super().clean()

        start = cleaned_data.get('start_date')

        end = cleaned_data.get('end_date')

        deadline = cleaned_data.get('registration_deadline')

        if start and end and end < start:

            self.add_error(
                'end_date',
                'End date cannot be before start date.'
            )

        if start and deadline and deadline > start:

            self.add_error(
                'registration_deadline',
                'Registration deadline must be before start date.'
            )

        return cleaned_data


    # =========================================================
# VENUE FORM
# =========================================================

class VenueForm(forms.ModelForm):

    class Meta:

        model = Venue

        fields = [

            "name",

            "location",

            "capacity",

            "description",

            "is_available",

        ]


# =========================================================
# RESOURCE FORM
# =========================================================

class ResourceForm(forms.ModelForm):

    class Meta:

        model = Resource

        fields = [

            "name",

            "resource_type",

            "quantity",

            "available_quantity",

            "description",

        ]