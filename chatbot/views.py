import os

from dotenv import load_dotenv

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from google import genai

from events.models import (
    Event,
    EventRegistration,
    EventCategory,
    EventWishlist,
    Venue,
    Resource,
)

from accounts.models import UserProfile


# =========================================================
# LOAD .ENV FILE
# =========================================================

load_dotenv()


# =========================================================
# GEMINI CLIENT
# =========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# GET EVENT SYSTEM INFORMATION
# =========================================================

def get_event_system_context():

    total_events = Event.objects.count()

    pending_events = Event.objects.filter(
        approval_status="PENDING"
    ).count()

    approved_events = Event.objects.filter(
        approval_status="APPROVED"
    ).count()

    rejected_events = Event.objects.filter(
        approval_status="REJECTED"
    ).count()

    upcoming_events = Event.objects.filter(
        status="Upcoming"
    ).count()

    active_events = Event.objects.filter(
        status="Active"
    ).count()

    completed_events = Event.objects.filter(
        status="Completed"
    ).count()

    cancelled_events = Event.objects.filter(
        status="Cancelled"
    ).count()

    total_registrations = EventRegistration.objects.count()

    total_users = UserProfile.objects.filter(
        role="USER"
    ).count()

    total_organizers = UserProfile.objects.filter(
        role="ORGANIZER"
    ).count()

    total_categories = EventCategory.objects.count()

    total_wishlists = EventWishlist.objects.count()

    total_venues = Venue.objects.count()

    total_resources = Resource.objects.count()


    # =====================================================
    # EVENT DETAILS
    # =====================================================

    events = Event.objects.all().order_by("-created_at")[:30]

    event_details = []

    for event in events:

        event_details.append({

            "name": event.name,

            "category": str(event.category),

            "organizer": event.organizer,

            "mode": event.event_mode,

            "venue": event.venue,

            "location": event.location,

            "start_date": str(event.start_date),

            "end_date": str(event.end_date),

            "registration_deadline": (
                str(event.registration_deadline)
                if event.registration_deadline
                else None
            ),

            "fee": str(event.event_fee),

            "max_participants": event.max_participants,

            "approval_status": event.approval_status,

            "status": event.status,

            "description": event.description,

        })


    return {

        "dashboard": {

            "total_events": total_events,

            "pending_events": pending_events,

            "approved_events": approved_events,

            "rejected_events": rejected_events,

            "upcoming_events": upcoming_events,

            "active_events": active_events,

            "completed_events": completed_events,

            "cancelled_events": cancelled_events,

            "total_registrations": total_registrations,

            "total_users": total_users,

            "total_organizers": total_organizers,

            "total_categories": total_categories,

            "total_wishlists": total_wishlists,

            "total_venues": total_venues,

            "total_resources": total_resources,

        },

        "events": event_details,

    }


# =========================================================
# CHATBOT API
# =========================================================

@require_POST
def ask_ai(request):

    question = request.POST.get(
        "message",
        ""
    ).strip()


    # =====================================================
    # EMPTY MESSAGE
    # =====================================================

    if not question:

        return JsonResponse({

            "success": False,

            "answer": "Please enter a message."

        })


    # =====================================================
    # CHECK GEMINI KEY
    # =====================================================

    if not GEMINI_API_KEY:

        return JsonResponse({

            "success": False,

            "answer": (
                "Gemini API key is not configured. "
                "Please check your .env file."
            )

        })


    try:

        # =================================================
        # GET DATABASE INFORMATION
        # =================================================

        system_data = get_event_system_context()


        # =================================================
        # AI SYSTEM INSTRUCTIONS
        # =================================================

        system_prompt = """

You are the Smart Event AI Assistant for an Event Management System.

You are a friendly, helpful and intelligent assistant.

You can answer two types of questions:

1. General questions
2. Questions about the Event Management System


IMPORTANT RULES:

When the user asks about the Event Management System,
use ONLY the database information provided below.

Never invent:

- events
- users
- registrations
- organizers
- venues
- resources
- categories
- statistics
- dates
- fees

If the database information does not contain the answer,
say that the information is not available.

For general questions, answer normally and helpfully.

Do not tell the user that you are using database information.

Do not mention Python, Django, Gemini, API calls or
internal implementation unless the user specifically
asks about the technical implementation.

Keep answers clear and reasonably concise.

For event questions, provide useful details.

You are the Smart Event AI Assistant for this website.


DATABASE INFORMATION:

""" + str(system_data)


        # =================================================
        # GEMINI REQUEST
        # =================================================

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=question,

            config={
                "system_instruction": system_prompt,
            },

        )


        # =================================================
        # GET GEMINI ANSWER
        # =================================================

        answer = response.text


        # =================================================
        # RETURN SUCCESS
        # =================================================

        return JsonResponse({

            "success": True,

            "answer": answer,

        })


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as error:

        print()
        print("=" * 70)
        print("CHATBOT ERROR")
        print("=" * 70)
        print(repr(error))
        print("=" * 70)
        print()


        return JsonResponse({

            "success": False,

            "answer": (
                "AI Error: "
                + str(error)
            ),

        })