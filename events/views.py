from django.contrib import messages

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)

from django.contrib.auth.forms import PasswordChangeForm

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)

from django.contrib.auth.models import User

from django.db.models import Count, Q

from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
import base64

from django.utils import timezone

from django.views.decorators.http import require_POST

import qrcode
from io import BytesIO
from django.core.files import File
from accounts.forms import (
    OrganizerSignUpForm,
    SignUpForm,
)

from accounts.models import UserProfile

from .forms import (
    EventCategoryForm,
    EventForm,
    VenueForm,
    ResourceForm,
)

from .models import (
    Event,
    EventCategory,
    EventRegistration,
    EventWishlist,
    Notification,
    ThemePreference,
    UserSettings,
    Venue,
)
from .models import (
    Event,
    EventCategory,
    EventRegistration,
    EventWishlist,
    Notification,
    ThemePreference,
    UserSettings,
    Venue,
    Resource,
    EventResource,
)
# =========================================================
# CREATE NOTIFICATION
# =========================================================

def create_notification(

    user,

    title,

    message,

    notification_type="INFO",

    event=None,

    icon="🔔",

    action_url=""

):

    Notification.objects.create(

        user=user,

        title=title,

        message=message,

        notification_type=notification_type,

        event=event,

        icon=icon,

        action_url=action_url,

    )
# =========================================================
# ROLE HELPERS
# =========================================================

def is_admin(user):
    return user.is_authenticated and user.is_staff


def is_organizer(user):
    return (
        user.is_authenticated
        and not user.is_staff
        and getattr(user, 'profile', None)
        and user.profile.role == 'ORGANIZER'
    )


def user_or_organizer(user):
    return user.is_authenticated and not user.is_staff


def notify(user, message, event=None):
    Notification.objects.create(
        user=user,
        message=message,
        event=event
    )


# =========================================================
# SIGNUP
# =========================================================

def signup_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    form = SignUpForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        user = form.save()

        UserProfile.objects.create(
            user=user,
            full_name=form.cleaned_data['full_name'],
            phone_number=form.cleaned_data['phone_number']
        )

        UserSettings.objects.create(user=user)
        ThemePreference.objects.create(user=user)

        login(request, user)

        messages.success(
            request,
            'Your user account has been created.'
        )

        return redirect('user_dashboard')

    return render(
        request,
        'events/auth.html',
        {
            'form': form,
            'mode': 'signup'
        }
    )


# =========================================================
# ORGANIZER SIGNUP
# =========================================================

def organizer_signup_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    form = OrganizerSignUpForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        user = form.save()

        UserProfile.objects.create(
            user=user,
            role='ORGANIZER',
            full_name=form.cleaned_data['full_name'],
            phone_number=form.cleaned_data['phone_number'],
            organization=form.cleaned_data['organization']
        )

        UserSettings.objects.create(user=user)
        ThemePreference.objects.create(user=user)

        login(request, user)

        messages.success(
            request,
            'Organizer account created. You can now prepare an event for approval.'
        )

        return redirect('organizer_dashboard')

    return render(
        request,
        'events/auth.html',
        {
            'form': form,
            'mode': 'organizer_signup'
        }
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('home')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(
        request,
        'events/auth.html',
        {
            'mode': 'login'
        }
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required
def logout_view(request):

    logout(request)

    return redirect('login')


# =========================================================
# HOME
# =========================================================

@login_required
def home_view(request):

    if is_admin(request.user):
        return redirect('admin_dashboard')

    if is_organizer(request.user):
        return redirect('organizer_dashboard')

    return redirect('user_dashboard')



# =========================================================
# ADMIN DASHBOARD
# =========================================================

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):

    events = (
        Event.objects
        .select_related('category', 'owner')
        .order_by('-created_at')
    )

    registrations = EventRegistration.objects.all()

    pending_events = events.filter(
        approval_status='PENDING'
    )

    context = {

        'events': events[:10],

        'pending_events': pending_events,

        'total_events': events.count(),

        'approved_events':
            events.filter(
                approval_status='APPROVED'
            ).count(),

        'pending_count':
            pending_events.count(),

        'total_users':
            User.objects.filter(
                is_staff=False
            ).count(),

        'total_organizers':
            UserProfile.objects.filter(
                role='ORGANIZER'
            ).count(),

        'total_registrations':
            registrations.count(),

        'notifications':
            request.user.notifications
            .order_by('-created_at')[:8],

        'unread_notifications_count':
            request.user.notifications
            .filter(is_read=False)
            .count(),

        'recent_activities': [

            "New user registered",

            "New event created",

            "Category added",

            "Event approved",

            "Profile updated",

        ],

    }

    return render(

        request,

        'events/admin_dashboard.html',

        context

    )

# =========================================================
# ORGANIZER DASHBOARD
# =========================================================

@login_required
@user_passes_test(is_organizer)
def organizer_dashboard(request):

    events = (
        Event.objects
        .filter(owner=request.user)
        .select_related('category')
        .annotate(
            participant_count=Count('registrations')
        )
        .order_by('-created_at')
    )

    context = {

        'events': events,

        'total_events':
            events.count(),

        'pending_count':
            events.filter(
                approval_status='PENDING'
            ).count(),

        'approved_count':
            events.filter(
                approval_status='APPROVED'
            ).count(),

        'registration_count':
            EventRegistration.objects.filter(
                event__owner=request.user
            ).count(),

        'notifications':
            request.user.notifications
            .order_by('-created_at')[:8],

        'unread_notifications_count':
            request.user.notifications
            .filter(is_read=False)
            .count(),
    }

    return render(
        request,
        'events/organizer_dashboard.html',
        context
    )


# =========================================================
# USER DASHBOARD
# =========================================================

@login_required
@user_passes_test(user_or_organizer)
def user_dashboard(request):

    events = (
        Event.objects
        .filter(
            approval_status='APPROVED'
        )
        .exclude(
            status__in=[
                'Cancelled',
                'Completed'
            ]
        )
        .select_related('category')
        .order_by('start_date')
    )

    joined_events = events.filter(
        registrations__user=request.user
    )

    context = {

        'events':
            events[:6],

        'available_events_count':
            events.count(),

        'joined_events_count':
            joined_events.count(),

        'wishlist_count':
            EventWishlist.objects.filter(
                user=request.user
            ).count(),

        'notifications':
            request.user.notifications
            .order_by('-created_at')[:8],

        'unread_notifications_count':
            request.user.notifications
            .filter(is_read=False)
            .count(),
    }

    return render(
        request,
        'events/user_dashboard.html',
        context
    )


# =========================================================
# CATEGORY LIST
# =========================================================

@login_required
@user_passes_test(is_admin)
def category_list(request):

    categories = (
        EventCategory.objects
        .annotate(
            event_count=Count('events')
        )
        .order_by('name')
    )

    return render(
        request,
        'events/category_list.html',
        {
            'categories': categories
        }
    )


# =========================================================
# CREATE CATEGORY
# =========================================================

@login_required
@user_passes_test(is_admin)
def category_create(request):

    if request.method == "POST":

        form = EventCategoryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category created successfully."
            )

            return redirect("category_list")

    else:

        form = EventCategoryForm()

    return render(
        request,
        "events/category_form.html",
        {
            "form": form,
            "title": "Create Category",
        },
    )
# =========================================================
# EDIT CATEGORY
# =========================================================

@login_required
@user_passes_test(is_admin)
def category_edit(request, pk):

    category = get_object_or_404(
        EventCategory,
        pk=pk
    )

    if request.method == "POST":

        form = EventCategoryForm(
            request.POST,
            request.FILES,
            instance=category
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category updated successfully."
            )

            return redirect("category_list")

    else:

        form = EventCategoryForm(
            instance=category
        )

    return render(
        request,
        "events/category_form.html",
        {
            "form": form,
            "title": "Edit Category",
        },
    )


# =========================================================
# DELETE CATEGORY
# =========================================================

@require_POST
@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):

    category = get_object_or_404(
        EventCategory,
        pk=pk
    )

    category.delete()

    messages.success(
        request,
        'Category deleted.'
    )

    return redirect('category_list')


# =========================================================
# EVENT LIST
# =========================================================

@login_required
def event_list(request):

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------

    if is_admin(request.user):

        events = Event.objects.select_related(
            'category',
            'owner'
        )

    # -----------------------------------------------------
    # ORGANIZER
    # -----------------------------------------------------

    elif is_organizer(request.user):

        events = Event.objects.filter(
            owner=request.user
        ).select_related(
            'category'
        )

    else:

        return HttpResponseForbidden(
            'Only organizers and administrators can manage events.'
        )

    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    status_filter = request.GET.get(
        'status'
    )

    if status_filter in [
        'Upcoming',
        'Active',
        'Completed',
        'Cancelled'
    ]:

        events = events.filter(
            status=status_filter
        )

    # -----------------------------------------------------
    # APPROVAL FILTER
    # -----------------------------------------------------

    approval_filter = request.GET.get(
        'approval'
    )

    if approval_filter in [
        'DRAFT',
        'PENDING',
        'APPROVED',
        'REJECTED'
    ]:

        events = events.filter(
            approval_status=approval_filter
        )

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    category_filter = request.GET.get(
        'category'
    )

    if category_filter:

        events = events.filter(
            category_id=category_filter
        )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        events = events.filter(

            Q(name__icontains=search)

            |

            Q(organizer__icontains=search)

            |

            Q(location__icontains=search)

            |

            Q(category__name__icontains=search)
        )

    # -----------------------------------------------------
    # PARTICIPANT COUNT
    # -----------------------------------------------------

    events = (
        events
        .annotate(
            participant_count=Count(
                'registrations',
                distinct=True
            )
        )
        .order_by('-created_at')
    )

    context = {

        'events':
            events,

        'categories':
            EventCategory.objects.order_by(
                'name'
            ),

        'selected_status':
            status_filter,

        'selected_approval':
            approval_filter,

        'selected_category':
            category_filter,

        'search':
            search,
    }

    return render(
        request,
        'events/event_list.html',
        context
    )


# =========================================================
# CREATE EVENT
# =========================================================
@login_required
def event_create(request):

    if not (
        is_admin(request.user)
        or is_organizer(request.user)
    ):
        return HttpResponseForbidden(
            "Only administrators and organizers can create events."
        )

    if request.method == "POST":

        form = EventForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # -----------------------------------------
            # Conflict Detection
            # -----------------------------------------

            venue = form.cleaned_data.get("venue")

            start_date = form.cleaned_data.get("start_date")

            end_date = form.cleaned_data.get("end_date")

            conflict = Event.objects.filter(
                venue=venue,
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exists()

            if conflict:

                messages.error(
                    request,
                    "This venue is already booked for the selected dates."
                )

                return render(
                    request,
                    "events/event_form.html",
                    {
                        "form": form,
                        "title": "Create Event",
                    },
                )

            event = form.save(commit=False)

            event.owner = request.user

            if is_admin(request.user):

                event.organizer = (
                    event.organizer
                    or "Administrator"
                )

                event.approval_status = "APPROVED"

                event.reviewed_by = request.user

                event.reviewed_at = timezone.now()

            else:

                profile = getattr(
                    request.user,
                    "profile",
                    None
                )

                event.organizer = (
                    event.organizer
                    or profile.organization
                    or request.user.username
                )

                event.approval_status = "DRAFT"

            event.save()

            create_notification(

                request.user,

                "Event Created",

                f'Your event "{event.name}" was created successfully.',

                "SUCCESS",

                event,

                "📅"

            )

            messages.success(
                request,
                "Event created successfully."
            )

            return redirect("event_list")

    else:

        form = EventForm()

    return render(
        request,
        "events/event_form.html",
        {
            "form": form,
            "title": "Create Event",
        },
    )


# =========================================================
# EVENT PERMISSION
# =========================================================

def can_manage_event(user, event):

    return (
        is_admin(user)
        or (
            is_organizer(user)
            and event.owner_id == user.id
        )
    )


# =========================================================
# EDIT EVENT
# =========================================================

@login_required
def event_edit(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk
    )

    if not can_manage_event(
        request.user,
        event
    ):
        return HttpResponseForbidden(
            "You cannot edit this event."
        )

    if request.method == "POST":

        form = EventForm(
            request.POST,
            request.FILES,
            instance=event
        )

        if form.is_valid():

            # -----------------------------------------
            # Conflict Detection
            # -----------------------------------------

            venue = form.cleaned_data.get("venue")

            start_date = form.cleaned_data.get("start_date")

            end_date = form.cleaned_data.get("end_date")

            conflict = Event.objects.filter(
                venue=venue,
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(
                pk=event.pk
            ).exists()

            if conflict:

                messages.error(
                    request,
                    "This venue is already booked for the selected dates."
                )

                return render(
                    request,
                    "events/event_form.html",
                    {
                        "form": form,
                        "title": "Edit Event",
                        "event": event,
                    },
                )

            event = form.save()

            if (
                is_organizer(request.user)
                and event.approval_status == "APPROVED"
            ):

                event.approval_status = "PENDING"

                event.submitted_at = timezone.now()

                event.save()

            create_notification(

                request.user,

                "Event Updated",

                f'Your event "{event.name}" was updated successfully.',

                "INFO",

                event,

                "✏️"

            )

            messages.success(
                request,
                "Event updated successfully."
            )

            return redirect(
                "event_list"
            )

    else:

        form = EventForm(
            instance=event
        )

    return render(
        request,
        "events/event_form.html",
        {
            "form": form,
            "title": "Edit Event",
            "event": event,
        },
    )


# =========================================================
# DELETE EVENT
# =========================================================

@require_POST
@login_required
def event_delete(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk
    )

    if not can_manage_event(
        request.user,
        event
    ):

        return HttpResponseForbidden(
            'You cannot delete this event.'
        )

    event.delete()

    messages.success(
        request,
        'Event deleted.'
    )

    return redirect(
        'event_list'
    )


# =========================================================
# SUBMIT EVENT
# =========================================================

@require_POST
@login_required
@user_passes_test(is_organizer)
def submit_event(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk,
        owner=request.user
    )

    event.approval_status = 'PENDING'

    event.submitted_at = timezone.now()

    event.review_note = ''

    event.save(
        update_fields=[
            'approval_status',
            'submitted_at',
            'review_note'
        ]
    )

    admins = User.objects.filter(
        is_staff=True
    )

    for admin in admins:

        notify(
            admin,
            f'{request.user.username} submitted {event.name} for approval.',
            event
        )

    notify(
        request.user,
        f'{event.name} was submitted for admin approval.',
        event
    )

    messages.success(
        request,
        'Event submitted for approval.'
    )

    return redirect(
        'event_list'
    )


# =========================================================
# REVIEW EVENT
# =========================================================

@login_required
@user_passes_test(is_admin)
def review_event(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk
    )

    if request.method == 'POST':

        decision = request.POST.get(
            'decision'
        )

        if decision not in (
            'APPROVED',
            'REJECTED'
        ):

            messages.error(
                request,
                'Select approve or reject.'
            )

            return redirect(
                'review_event',
                pk=pk
            )

        event.approval_status = decision

        event.review_note = request.POST.get(
            'review_note',
            ''
        ).strip()

        event.reviewed_by = request.user

        event.reviewed_at = timezone.now()

        event.save()

        if event.owner:

            notify(
                event.owner,
                f'{event.name} was {decision.lower()}. {event.review_note}'.strip(),
                event
            )

        messages.success(
            request,
            f'Event {decision.lower()}.'
        )

        return redirect(
            'admin_dashboard'
        )

    return render(
        request,
        'events/review_event.html',
        {
            'event': event
        }
    )


# =========================================================
# AVAILABLE EVENTS
# =========================================================

@login_required
@user_passes_test(user_or_organizer)
def available_events(request):

    events = (
        Event.objects
        .filter(
            approval_status='APPROVED'
        )
        .exclude(
            status__in=[
                'Cancelled',
                'Completed'
            ]
        )
        .select_related(
            'category',
            'owner'
        )
    )

    category = request.GET.get(
        'category'
    )

    mode = request.GET.get(
        'mode'
    )

    search = request.GET.get(
        'search'
    )

    if category:

        events = events.filter(
            category_id=category
        )

    if mode:

        events = events.filter(
            event_mode=mode
        )

    if search:

        events = events.filter(

            Q(name__icontains=search)

            |

            Q(description__icontains=search)

            |

            Q(organizer__icontains=search)
        )

    events = (
        events
        .annotate(
            participant_count=Count(
                'registrations',
                distinct=True
            )
        )
        .order_by('start_date')
    )

    return render(
        request,
        'events/available_events.html',
        {

            'events':
                events,

            'categories':
                EventCategory.objects.order_by(
                    'name'
                ),

            'today':
                timezone.localdate()
        }
    )


# =========================================================
# EVENT DETAIL
# =========================================================

@login_required
@user_passes_test(user_or_organizer)
def event_detail(request, pk):

    event = get_object_or_404(

        Event.objects.select_related(
            'category',
            'owner'
        ),

        pk=pk,

        approval_status='APPROVED'
    )

    context = {

        'event':
            event,

        'is_joined':
            EventRegistration.objects.filter(
                user=request.user,
                event=event
            ).exists(),

        'is_wishlisted':
            EventWishlist.objects.filter(
                user=request.user,
                event=event
            ).exists(),

        'participant_count':
            event.registrations.count(),
    }

    return render(
        request,
        'events/event_detail.html',
        context
    )

# =========================================================
# EVENT QR CODE
# =========================================================

@login_required
def event_qr(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk
    )

    # Admin can view any event QR
    # Organizer can view only their own event QR

    if not (
        is_admin(request.user)
        or (
            is_organizer(request.user)
            and event.owner_id == request.user.id
        )
    ):
        return HttpResponseForbidden(
            'You cannot view the QR code for this event.'
        )

    # URL that the QR code will open

    event_url = (
    f"http://10.138.53.159:8000"
    f"{reverse('event_detail', args=[event.pk])}"
)
    # Generate QR Code

    qr = qrcode.make(event_url)

    # =====================================================
    # DOWNLOAD QR WITH EVENT DETAILS
    # =====================================================

    if request.GET.get('download') == '1':

        from PIL import Image, ImageDraw

        qr = qr.convert('RGB')

        # QR size
        qr_size = 500

        qr = qr.resize(
            (qr_size, qr_size)
        )

        # Poster size
        poster_width = 700
        poster_height = 1050

        poster = Image.new(
            'RGB',
            (poster_width, poster_height),
            'white'
        )

        draw = ImageDraw.Draw(poster)

        # Center QR code

        qr_x = (poster_width - qr_size) // 2
        qr_y = 120

        poster.paste(
            qr,
            (qr_x, qr_y)
        )

        # Event details

        details = [
            f"EVENT: {event.name}",
            f"Category: {event.category}",
            f"Organizer: {event.organizer}",
            f"Date: {event.start_date} - {event.end_date}",
            f"Mode: {event.event_mode}",
            f"Venue: {event.venue or 'Not specified'}",
            f"Location: {event.location or 'Not specified'}",
            f"Registration Fee: Rs. {event.event_fee}",
            f"Registration Deadline: "
            f"{event.registration_deadline or 'Not specified'}",
        ]

        # Starting position below QR

        y_position = 650

        draw.text(
            (poster_width // 2, 70),
            "EVENT REGISTRATION",
            fill='black',
            anchor='mm'
        )

        draw.text(
            (poster_width // 2, 95),
            "Scan QR Code to Register",
            fill='black',
            anchor='mm'
        )

        for detail in details:

            draw.text(
                (50, y_position),
                detail,
                fill='black'
            )

            y_position += 38

        # Save poster

        buffer = BytesIO()

        poster.save(
            buffer,
            format='PNG'
        )

        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='image/png'
        )

        response[
            'Content-Disposition'
        ] = (
            f'attachment; '
            f'filename="event_qr_{event.pk}.png"'
        )

        return response

    # =====================================================
    # DISPLAY QR ON PAGE
    # =====================================================

    buffer = BytesIO()

    qr.save(
        buffer,
        format='PNG'
    )

    # Convert QR image to base64

    qr_code = base64.b64encode(
        buffer.getvalue()
    ).decode()

    context = {
        'event': event,
        'qr_code': qr_code,
        'event_url': event_url,
    }

    return render(
        request,
        'events/event_qr.html',
        context
    )

# =========================================================
# JOIN EVENT
# =========================================================

@require_POST
@login_required
@user_passes_test(user_or_organizer)
def join_event(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk,
        approval_status='APPROVED'
    )

    today = timezone.localdate()

    if event.status in (
        'Cancelled',
        'Completed'
    ):

        messages.error(
            request,
            'Registration is closed for this event.'
        )

    elif (
        event.registration_deadline
        and event.registration_deadline < today
    ):

        messages.error(
            request,
            'Registration is closed for this event.'
        )

    elif (
        event.max_participants
        and event.registrations.count()
        >= event.max_participants
    ):

        messages.error(
            request,
            'This event is full.'
        )

    elif EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).exists():

        messages.info(
            request,
            'You have already joined this event.'
        )

    else:

        registration = EventRegistration.objects.create(
            user=request.user,
            event=event
        )

        # =====================================
        # Generate QR Code
        # =====================================

        qr_data = (
            f"User: {request.user.username}\n"
            f"Event: {event.name}\n"
            f"Registration ID: {registration.id}"
        )

        qr = qrcode.make(qr_data)

        buffer = BytesIO()

        qr.save(
            buffer,
            format="PNG"
        )

        filename = f"qr_{registration.id}.png"

        registration.qr_code.save(
            filename,
            File(buffer),
            save=True
        )

        notify(
            request.user,
            f'You joined {event.name}.',
            event
        )

        if event.owner:

            notify(
                event.owner,
                f'{request.user.username} joined {event.name}.',
                event
            )

        messages.success(
            request,
            'You joined the event successfully.'
        )

    return redirect(
        request.POST.get('next')
        or 'my_joined_events'
    )

# =========================================================
# MY JOINED EVENTS
# =========================================================

@login_required
@user_passes_test(user_or_organizer)
def my_joined_events(request):

    registrations = (
        EventRegistration.objects
        .filter(
            user=request.user
        )
        .select_related(
            'event__category'
        )
        .order_by('-joined_at')
    )

    return render(
        request,
        'events/my_joined_events.html',
        {
            'registrations':
                registrations
        }
    )


# =========================================================
# WISHLIST
# =========================================================

@login_required
def wishlist_view(request):

    # -----------------------------------------------------
    # ADMIN - VIEW ALL USER WISHLISTS
    # -----------------------------------------------------

    if is_admin(request.user):

        wishlist_entries = (
            EventWishlist.objects
            .select_related(
                'user',
                'event',
                'event__category'
            )
            .order_by(
                'user__username',
                '-event__created_at'
            )
        )

        return render(
            request,
            'events/wishlist.html',
            {
                'wishlist_entries':
                    wishlist_entries,

                'admin_view':
                    True,
            }
        )

    # -----------------------------------------------------
    # NORMAL USER / ORGANIZER
    # -----------------------------------------------------

    events = (
        Event.objects
        .filter(
            wishlist_entries__user=request.user,
            approval_status='APPROVED'
        )
        .select_related('category')
        .order_by('-created_at')
    )

    return render(
        request,
        'events/wishlist.html',
        {
            'events':
                events,

            'admin_view':
                False,
        }
    )


# =========================================================
# ADD WISHLIST
# =========================================================

@require_POST
@login_required
@user_passes_test(user_or_organizer)
def add_to_wishlist(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk,
        approval_status='APPROVED'
    )

    _, created = (
        EventWishlist.objects
        .get_or_create(
            user=request.user,
            event=event
        )
    )

    if created:

        messages.success(
            request,
            'Event added to your wishlist.'
        )

    else:

        messages.info(
            request,
            'This event is already in your wishlist.'
        )

    return redirect(
        request.POST.get('next')
        or 'wishlist'
    )


# =========================================================
# REMOVE WISHLIST
# =========================================================

@require_POST
@login_required
@user_passes_test(user_or_organizer)
def remove_from_wishlist(request, pk):

    EventWishlist.objects.filter(
        user=request.user,
        event_id=pk
    ).delete()

    messages.success(
        request,
        'Event removed from wishlist.'
    )

    return redirect(
        'wishlist'
    )


# =========================================================
# CALENDAR
# =========================================================

@login_required
def calendar_view(request):

    from calendar import monthrange
    from datetime import date
    from django.db.models import Q

    # Get selected month/year from URL
    today = date.today()

    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))

        if month < 1 or month > 12:
            raise ValueError

    except (ValueError, TypeError):

        year = today.year
        month = today.month


    # Approved events + events joined by current user
    events = (
        Event.objects
        .filter(
            Q(approval_status="APPROVED")
            |
            Q(registrations__user=request.user)
        )
        .distinct()
        .order_by("start_date")
    )


    # Calendar information
    first_weekday, days_in_month = monthrange(
        year,
        month
    )

    # Python: Monday = 0
    # We need Sunday = 0
    first_weekday = (first_weekday + 1) % 7


    # Create calendar weeks
    weeks = []

    week = []

    # Empty cells before first day
    for _ in range(first_weekday):

        week.append(None)


    # Add days
    for day_number in range(1, days_in_month + 1):

        current_day = date(
            year,
            month,
            day_number
        )

        day_events = []

        for event in events:

            if event.start_date and event.end_date:

                if (
                    event.start_date <= current_day
                    <= event.end_date
                ):

                    day_events.append(event)

            elif event.start_date:

                if event.start_date == current_day:

                    day_events.append(event)


        week.append({
            "date": current_day,
            "day": day_number,
            "events": day_events,
            "is_today": current_day == today,
        })


        # Saturday
        if len(week) == 7:

            weeks.append(week)

            week = []


    # Remaining cells
    if week:

        while len(week) < 7:

            week.append(None)

        weeks.append(week)


    # Previous month
    if month == 1:

        previous_year = year - 1
        previous_month = 12

    else:

        previous_year = year
        previous_month = month - 1


    # Next month
    if month == 12:

        next_year = year + 1
        next_month = 1

    else:

        next_year = year
        next_month = month + 1


    month_name = date(
        year,
        month,
        1
    ).strftime("%B %Y")


    return render(

        request,

        "events/calendar.html",

        {
            "weeks": weeks,

            "month_name": month_name,

            "year": year,

            "month": month,

            "previous_year": previous_year,

            "previous_month": previous_month,

            "next_year": next_year,

            "next_month": next_month,

        }

    )

# =========================================================
# NOTIFICATIONS
# =========================================================

@login_required
def notifications_view(request):

    notifications = (
        request.user.notifications
        .select_related('event')
        .order_by('-created_at')
    )

    return render(
        request,
        'events/notifications.html',
        {
            'notifications':
                notifications,

            'unread_notifications_count':
                notifications.filter(
                    is_read=False
                ).count(),
        }
    )


# =========================================================
# MARK NOTIFICATION READ
# =========================================================

@require_POST
@login_required
def mark_notification_read(request, pk):

    request.user.notifications.filter(
        pk=pk
    ).update(
        is_read=True
    )

    return redirect(
        'notifications'
    )


# =========================================================
# MARK ALL NOTIFICATIONS READ
# =========================================================

@require_POST
@login_required
def mark_all_notifications_read(request):

    request.user.notifications.filter(
        is_read=False
    ).update(
        is_read=True
    )

    messages.success(
        request,
        'All notifications marked as read.'
    )

    return redirect(
        'notifications'
    )


# =========================================================
# DELETE NOTIFICATION
# =========================================================

@require_POST
@login_required
def delete_notification(request, pk):

    request.user.notifications.filter(
        pk=pk
    ).delete()

    messages.success(
        request,
        'Notification deleted.'
    )

    return redirect(
        'notifications'
    )


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        profile.full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        request.user.first_name = profile.full_name

        request.user.email = request.POST.get(
            "email",
            ""
        ).strip()

        profile.phone_number = request.POST.get(
            "phone_number",
            ""
        ).strip()

        profile.organization = request.POST.get(
            "organization",
            ""
        ).strip()

        profile.bio = request.POST.get(
            "bio",
            ""
        ).strip()

        if request.FILES.get("profile_picture"):

            profile.profile_picture = request.FILES.get(
                "profile_picture"
            )

        request.user.save()

        profile.save()

        create_notification(

            request.user,

            "Profile Updated",

            "Your profile has been updated successfully.",

            "SUCCESS",

            None,

            "👤"

        )

        messages.success(

            request,

            "Profile updated successfully."

        )

        return redirect(
            "profile"
        )

    joined_events_count = EventRegistration.objects.filter(

        user=request.user

    ).count()

    wishlist_count = EventWishlist.objects.filter(

        user=request.user

    ).count()

    notification_count = Notification.objects.filter(

        user=request.user,

        is_read=False

    ).count()

    context = {

        "profile": profile,

        "joined_events_count": joined_events_count,

        "wishlist_count": wishlist_count,

        "notification_count": notification_count,

    }

    return render(

        request,

        "events/profile.html",

        context

    )

# =========================================================
# SETTINGS
# =========================================================

@login_required
def settings_view(request):

    settings, _ = UserSettings.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        # ==========================================
        # ACCOUNT SETTINGS
        # ==========================================

        email = request.POST.get(
            "email",
            ""
        ).strip()

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        phone_number = request.POST.get(
            "phone_number",
            ""
        ).strip()

        organization = request.POST.get(
            "organization",
            ""
        ).strip()


        # ==========================================
        # UPDATE USER
        # ==========================================

        request.user.email = email

        request.user.save()


        # ==========================================
        # UPDATE USER PROFILE
        # ==========================================

        try:

            profile = request.user.profile

            profile.full_name = full_name
            profile.phone_number = phone_number
            profile.organization = organization

            profile.save()

        except UserProfile.DoesNotExist:

            pass


        # ==========================================
        # APPEARANCE
        # ==========================================

        theme = request.POST.get(
            "theme",
            "light"
        )

        accent_color = request.POST.get(
            "accent_color",
            "#2563eb"
        )


        settings.theme_mode = theme
        settings.accent_color = accent_color

        settings.save()


        # ==========================================
        # NOTIFICATION
        # ==========================================

        create_notification(

            request.user,

            "Settings Updated",

            "Your account settings have been updated successfully.",

            "SUCCESS",

            None,

            "⚙️"

        )


        messages.success(

            request,

            "Settings updated successfully."

        )


        return redirect(
            "settings"
        )


    # ==========================================
    # DISPLAY SETTINGS PAGE
    # ==========================================

    return render(

        request,

        "events/settings.html",

        {
            "settings": settings
        }

    )
# =========================================================
# THEME SETTINGS
# =========================================================

@login_required
def theme_settings(request):

    settings, _ = UserSettings.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        page_name = request.POST.get(
            "page_name",
            "dashboard"
        )

        accent_color = request.POST.get(
            "accent_color",
            "#2563eb"
        )

        sidebar_color = request.POST.get(
            "sidebar_color",
            "#111827"
        )

        topbar_color = request.POST.get(
            "topbar_color",
            "#ffffff"
        )

        page_colors = {
            "dashboard": "dashboard_color",
            "events": "dashboard_color",
            "available_events": "available_events_color",
            "joined_events": "joined_events_color",
            "wishlist": "wishlist_color",
            "calendar": "calendar_color",
            "profile": "profile_color",
            "settings": "settings_color",
            "categories": "dashboard_color",
            "venues": "dashboard_color",
            "resources": "dashboard_color",
            "admin_dashboard": "dashboard_color",
        }

        field_name = page_colors.get(page_name)

        if field_name:
            setattr(
                settings,
                field_name,
                accent_color
            )

        # Save sidebar and topbar colors
        settings.sidebar_color = sidebar_color
        settings.topbar_color = topbar_color

        settings.save()

        ThemePreference.objects.update_or_create(
            user=request.user,
            defaults={
                "theme_name": page_name,
                "accent_color": accent_color,
            }
        )

        messages.success(
            request,
            "Theme saved successfully."
        )

        return redirect("theme_settings")

    return render(
        request,
        "events/theme.html",
        {
            "settings": settings,
            "dashboard_color": settings.dashboard_color,
            "available_events_color": settings.available_events_color,
            "joined_events_color": settings.joined_events_color,
            "wishlist_color": settings.wishlist_color,
            "calendar_color": settings.calendar_color,
            "profile_color": settings.profile_color,
            "settings_color": settings.settings_color,
            "sidebar_color": settings.sidebar_color,
            "topbar_color": settings.topbar_color,
        }
    )

# =========================================================
# EVENT PARTICIPANTS
# =========================================================

@login_required
def event_participants(request, pk):

    event = get_object_or_404(
        Event,
        pk=pk
    )

    # Admin can view any event.
    # Organizer can view only own event.

    if not (
        is_admin(request.user)
        or (
            is_organizer(request.user)
            and event.owner_id == request.user.id
        )
    ):

        return HttpResponseForbidden(
            'You cannot view participants for this event.'
        )

    registrations = (
        event.registrations
        .select_related(
            'user',
            'user__profile'
        )
        .order_by(
            'user__username'
        )
    )

    attendance_filter = request.GET.get(
        'attendance'
    )

    if attendance_filter == 'present':

        registrations = registrations.filter(
            attended=True
        )

    elif attendance_filter == 'absent':

        registrations = registrations.filter(
            attended=False
        )

    context = {

        'event':
            event,

        'registrations':
            registrations,

        'attendance_filter':
            attendance_filter,

        'present_count':
            event.registrations.filter(
                attended=True
            ).count(),

        'absent_count':
            event.registrations.filter(
                attended=False
            ).count(),

        'total_participants':
            event.registrations.count(),
    }

    return render(
        request,
        'events/event_members.html',
        context
    )


# =========================================================
# TOGGLE ATTENDANCE
# =========================================================

@require_POST
@login_required
def toggle_attendance(
    request,
    pk,
    registration_pk
):

    event = get_object_or_404(
        Event,
        pk=pk
    )

    if not (
        is_admin(request.user)
        or (
            is_organizer(request.user)
            and event.owner_id == request.user.id
        )
    ):

        return HttpResponseForbidden(
            'You cannot update attendance for this event.'
        )

    registration = get_object_or_404(
        EventRegistration,
        pk=registration_pk,
        event=event
    )

    registration.attended = (
        not registration.attended
    )

    registration.attended_at = (
        timezone.now()
        if registration.attended
        else None
    )

    registration.save(
        update_fields=[
            'attended',
            'attended_at'
        ]
    )

    messages.success(
        request,
        'Attendance updated.'
    )

    return redirect(
        'event_participants',
        pk=pk
    )


# =========================================================
# MANAGE USERS / ORGANIZERS
# =========================================================

@login_required
@user_passes_test(is_admin)
def manage_users(request):

    search = request.GET.get(
        "search",
        ""
    )

    role = request.GET.get(
        "role",
        ""
    )

    profiles = (
        UserProfile.objects
        .select_related("user")
        .all()
        .order_by("full_name")
    )

    if search:

        profiles = profiles.filter(

            Q(full_name__icontains=search) |

            Q(user__username__icontains=search) |

            Q(user__email__icontains=search)

        )

    if role:

        profiles = profiles.filter(
            role=role
        )

    context = {

        "profiles": profiles,

        "search": search,

        "selected_role": role,

        "total_users":
            UserProfile.objects.filter(
                role="USER"
            ).count(),

        "total_organizers":
            UserProfile.objects.filter(
                role="ORGANIZER"
            ).count(),

        "total_admins":
            UserProfile.objects.filter(
                role="ADMIN"
            ).count(),

    }

    return render(

        request,

        "events/manage_users.html",

        context

    )


# =========================================================
# REPORTS
# =========================================================

@login_required
@user_passes_test(is_admin)
def reports(request):

    categories = (
        EventCategory.objects
        .annotate(
            event_count=Count(
                'events',
                distinct=True
            ),

            registration_count=Count(
                'events__registrations',
                distinct=True
            )
        )
        .order_by(
            '-registration_count',
            'name'
        )
    )

    events = (
        Event.objects
        .annotate(
            participant_count=Count(
                'registrations',
                distinct=True
            )
        )
        .select_related(
            'category'
        )
        .order_by(
            '-participant_count'
        )[:10]
    )

    context = {

        'categories':
            categories,

        'events':
            events,

        'total_events':
            Event.objects.count(),

        'total_registrations':
            EventRegistration.objects.count(),

        'total_categories':
            EventCategory.objects.count(),

        'total_organizers':
            UserProfile.objects.filter(
                role='ORGANIZER'
            ).count(),
    }

    return render(
        request,
        'events/reports.html',
        context
    )


# =========================================================
# CONTACT / MESSAGES
# =========================================================

def contact(request):

    if request.method == 'POST':

        messages.success(
            request,
            'Your message has been received.'
        )

        return redirect(
            'contact'
        )

    return render(
        request,
        'events/contact.html'
    )



@login_required
def calendar_events(request):

    events = Event.objects.filter(
        approval_status="APPROVED"
    )

    data = []

    for event in events:

        if event.status == "Upcoming":
            color = "#2563eb"

        elif event.status == "Active":
            color = "#16a34a"

        elif event.status == "Completed":
            color = "#6b7280"

        else:
            color = "#dc2626"

        data.append({

            "id": event.id,

            "title": event.name,

            "start": str(event.start_date),

            "end": str(event.end_date),

            "url": f"/available-events/{event.id}/",

            "backgroundColor": color,

            "borderColor": color,

        })

    return JsonResponse(data, safe=False)

# =========================================================
# CHANGE PASSWORD
# =========================================================

@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(

            request.user,

            request.POST

        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(

                request,

                user

            )

            create_notification(

                request.user,

                "Password Changed",

                "Your account password has been changed successfully.",

                "SUCCESS",

                None,

                "🔒"

            )

            messages.success(

                request,

                "Password changed successfully."

            )

            return redirect("settings")

    else:

        form = PasswordChangeForm(

            request.user

        )

    return render(

        request,

        "events/change_password.html",

        {

            "form": form

        }

    )

# =========================================================
# VENUE MANAGEMENT
# =========================================================

@login_required
def venue_list(request):

    venues = Venue.objects.all().order_by("name")

    return render(
        request,
        "events/venue_list.html",
        {
            "venues": venues
        }
    )


@login_required
def venue_create(request):

    if request.method == "POST":

        form = VenueForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Venue created successfully."
            )

            return redirect("venue_list")

    else:

        form = VenueForm()

    return render(
        request,
        "events/venue_form.html",
        {
            "form": form,
            "title": "Create Venue"
        }
    )


@login_required
def venue_edit(request, pk):

    venue = get_object_or_404(
        Venue,
        pk=pk
    )

    if request.method == "POST":

        form = VenueForm(
            request.POST,
            instance=venue
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Venue updated successfully."
            )

            return redirect("venue_list")

    else:

        form = VenueForm(instance=venue)

    return render(
        request,
        "events/venue_form.html",
        {
            "form": form,
            "title": "Edit Venue"
        }
    )


@login_required
@require_POST
def venue_delete(request, pk):

    venue = get_object_or_404(
        Venue,
        pk=pk
    )

    venue.delete()

    messages.success(
        request,
        "Venue deleted successfully."
    )

    return redirect("venue_list")


# =========================================================
# RESOURCE MANAGEMENT
# =========================================================

@login_required
def resource_list(request):

    resources = Resource.objects.all().order_by("name")

    return render(
        request,
        "events/resource_list.html",
        {
            "resources": resources
        }
    )


@login_required
def resource_create(request):

    if request.method == "POST":

        form = ResourceForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Resource created successfully."
            )

            return redirect("resource_list")

    else:

        form = ResourceForm()

    return render(
        request,
        "events/resource_form.html",
        {
            "form": form,
            "title": "Add Resource"
        }
    )


@login_required
def resource_edit(request, pk):

    resource = get_object_or_404(
        Resource,
        pk=pk
    )

    if request.method == "POST":

        form = ResourceForm(
            request.POST,
            instance=resource
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Resource updated successfully."
            )

            return redirect("resource_list")

    else:

        form = ResourceForm(instance=resource)

    return render(
        request,
        "events/resource_form.html",
        {
            "form": form,
            "title": "Edit Resource"
        }
    )


@login_required
@require_POST
def resource_delete(request, pk):

    resource = get_object_or_404(
        Resource,
        pk=pk
    )

    resource.delete()

    messages.success(
        request,
        "Resource deleted successfully."
    )

    return redirect("resource_list")