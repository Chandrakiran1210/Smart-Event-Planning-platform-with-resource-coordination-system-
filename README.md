# Smart Event Planning Platform with Resource Coordination System

A web-based event management and resource coordination platform developed using Django.

The system provides a centralized platform for administrators, organizers, and users to create, manage, review, discover, and register for events. It also provides venue and resource coordination, event approval, QR-based event access, notifications, and chatbot assistance.

---

## 📌 Project Overview

The **Smart Event Planning Platform with Resource Coordination System** is designed to simplify the complete event management process.

The platform connects:

- Administrators
- Event Organizers
- Event Participants / Users

Organizers can create and manage events, while administrators can review and approve events. Users can discover approved events, register for them, add events to their wishlist, and access event information through QR codes.

The system also helps coordinate venues and resources to reduce scheduling conflicts.

---

## ✨ Main Features

### 👨‍💼 Administrator Module

- Administrator login
- Admin dashboard
- User management
- Organizer management
- Event management
- Event approval and rejection
- Category management
- Venue management
- Resource management
- Event registration monitoring
- Participant management
- Notifications
- Reports
- QR code management
- Profile and account settings

---

### 🧑‍💼 Organizer Module

- Organizer registration
- Organizer login
- Organizer dashboard
- Create events
- Edit events
- Delete events
- Submit events for admin approval
- Track event approval status
- View event participants
- Manage event information
- Generate event QR codes
- Manage profile
- Account settings

---

### 👤 User Module

- User registration
- User login
- User dashboard
- Browse available events
- Search events
- Filter events
- View event details
- Register for events
- View joined events
- Add events to wishlist
- Remove events from wishlist
- Calendar
- Notifications
- Profile management
- Account settings

---

## 📅 Event Management

The platform supports the following event information:

- Event name
- Category
- Event image
- Banner image
- Event mode
- Venue
- Location
- Google Maps link
- Website
- Registration link
- Start date
- End date
- Registration deadline
- Event fee
- Maximum participants
- Eligibility
- Organizer
- Contact person
- Contact email
- Contact phone
- Tags
- Requirements
- Description

---

## 🏢 Resource Coordination

The system provides resource coordination for events.

Resources can include:

- Equipment
- Facilities
- Event materials
- Other required resources

The platform maintains resource quantities and available quantities to help organizers plan their events effectively.

---

## 🏟️ Venue Management

Administrators can manage event venues.

Venue information includes:

- Venue name
- Location
- Capacity
- Description

The system also checks venue availability when events are created or edited to help prevent overlapping bookings for the same venue and dates.

---

## 🔄 Event Approval Workflow

```text
Organizer
    |
    v
Create Event
    |
    v
Submit Event
    |
    v
Administrator Review
    |
    +------------------+
    |                  |
    v                  v
Approve             Reject
    |
    v
Event Becomes
Available
    |
    v
Users Can Register
