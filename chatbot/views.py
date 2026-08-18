import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from openai import OpenAI

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
# OPENAI CLIENT
# =========================================================

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
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


    # -----------------------------------------------------
    # EVENT DETAILS
    # -----------------------------------------------------

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


    if not question:

        return JsonResponse({
            "success": False,
            "answer": "Please enter a message."
        })


    try:

        # Get current database information
        system_data = get_event_system_context()


        # -------------------------------------------------
        # SYSTEM INSTRUCTIONS
        # -------------------------------------------------

        system_prompt = """
You are the Smart Event AI Assistant for an Event Management System.

You are a friendly, intelligent conversational assistant.

Your job is to answer the user's questions naturally.

You can answer TWO types of questions:

1. General questions
2. Questions about the user's Event Management System


IMPORTANT:

When the user asks about their Event Management System,
use the database information provided below.

Never invent event numbers, users, registrations,
organizers, venues or other database information.

If the database information does not contain the answer,
say that you don't have that information.

For general questions, answer normally and helpfully.

You should behave like a natural chatbot.

Do NOT tell the user that you are using database context.

Do NOT mention Python, Django, API calls or internal code
unless the user specifically asks about the technical
implementation.

Keep normal answers reasonably concise.

For event management questions, provide useful details.

Database information:

""" + str(system_data)


        # -------------------------------------------------
        # OPENAI REQUEST
        # -------------------------------------------------

        response = client.responses.create(

            model="gpt-5-mini",

            instructions=system_prompt,

            input=question,

        )


        answer = response.output_text


        return JsonResponse({

            "success": True,

            "answer": answer,

        })


    except Exception as error:

        print("CHATBOT ERROR:", error)

        return JsonResponse({

            "success": False,

            "answer": (
                "Sorry, I couldn't connect to the AI service "
                "right now. Please try again."
            ),

        })