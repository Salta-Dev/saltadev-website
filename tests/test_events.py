"""Tests for the events app."""

from datetime import timedelta

import pytest
from content.models import Event
from django.urls import reverse
from django.utils import timezone
from events.forms import EventForm


@pytest.fixture
def user_event_data():
    """Return default event data for creation."""
    return {
        "title": "User Test Event",
        "description": "A test event description",
        "location": "Salta, Argentina",
        "photo": "https://example.com/photo.jpg",
        "link": "https://example.com/register",
    }


@pytest.fixture
def approved_event(db, collaborator_user, user_event_data):
    """Create and return an approved event with creator."""
    return Event.objects.create(
        **user_event_data,
        slug="approved-test-event",
        creator=collaborator_user,
        status=Event.Status.APPROVED,
        event_start_date=timezone.now() + timedelta(days=7),
    )


@pytest.fixture
def user_pending_event(db, collaborator_user, user_event_data):
    """Create and return a pending event with creator."""
    data = user_event_data.copy()
    data["title"] = "Pending Event"
    return Event.objects.create(
        **data,
        slug="pending-event",
        creator=collaborator_user,
        status=Event.Status.PENDING,
        event_start_date=timezone.now() + timedelta(days=14),
    )


@pytest.fixture
def user_rejected_event(db, collaborator_user, user_event_data):
    """Create and return a rejected event with creator."""
    data = user_event_data.copy()
    data["title"] = "Rejected Event"
    return Event.objects.create(
        **data,
        slug="rejected-event",
        creator=collaborator_user,
        status=Event.Status.REJECTED,
        event_start_date=timezone.now() + timedelta(days=21),
    )


class TestEventForm:
    """Tests for the EventForm."""

    def test_title_required(self):
        """Test title is required."""
        form = EventForm(
            data={
                "title": "",
                "description": "Description",
            }
        )
        assert not form.is_valid()
        assert "title" in form.errors

    def test_title_whitespace_only_invalid(self):
        """Test whitespace-only title is invalid."""
        form = EventForm(
            data={
                "title": "   ",
                "description": "Description",
            }
        )
        assert not form.is_valid()
        assert "title" in form.errors

    def test_date_time_combination(self):
        """Test date and time are combined correctly."""
        form = EventForm(
            data={
                "title": "Test Event",
                "description": "Description",
                "start_date": "2025-03-15",
                "start_time": "18:00",
            }
        )
        assert form.is_valid()
        cleaned = form.clean()
        assert cleaned["event_start_date"] is not None
        assert cleaned["event_start_date"].hour == 18
        assert cleaned["event_start_date"].minute == 0

    def test_date_only_without_time(self):
        """Test date without time uses midnight."""
        form = EventForm(
            data={
                "title": "Test Event",
                "description": "Description",
                "start_date": "2025-03-15",
            }
        )
        assert form.is_valid()
        cleaned = form.clean()
        assert cleaned["event_start_date"] is not None
        assert cleaned["event_start_date"].hour == 0
        assert cleaned["event_start_date"].minute == 0

    def test_end_before_start_invalid(self):
        """Test end date before start date is invalid."""
        form = EventForm(
            data={
                "title": "Test Event",
                "description": "Description",
                "start_date": "2025-03-20",
                "start_time": "18:00",
                "end_date": "2025-03-15",
                "end_time": "20:00",
            }
        )
        assert not form.is_valid()
        assert "__all__" in form.errors

    def test_end_after_start_valid(self):
        """Test end date after start date is valid."""
        form = EventForm(
            data={
                "title": "Test Event",
                "description": "Description",
                "start_date": "2025-03-15",
                "start_time": "18:00",
                "end_date": "2025-03-15",
                "end_time": "20:00",
            }
        )
        assert form.is_valid()

    @pytest.mark.django_db
    def test_slug_generation(self):
        """Test slug is auto-generated from title."""
        form = EventForm(
            data={
                "title": "My Amazing Event",
                "description": "Description",
            }
        )
        assert form.is_valid()
        event = form.save(commit=False)
        assert event.slug == "my-amazing-event"

    @pytest.mark.django_db
    def test_slug_collision_handling(self, approved_event):
        """Test slug collision generates unique slug."""
        form = EventForm(
            data={
                "title": "User Test Event",  # Same as existing event
                "description": "Description",
            }
        )
        assert form.is_valid()
        new_event = form.save(commit=False)
        assert new_event.slug != approved_event.slug
        assert new_event.slug.startswith("user-test-event")

    def test_auto_date_display(self):
        """Test date display is auto-generated."""
        form = EventForm(
            data={
                "title": "Test Event",
                "description": "Description",
                "start_date": "2025-03-15",
                "start_time": "18:00",
            }
        )
        assert form.is_valid()
        event = form.save(commit=False)
        assert "15 de Marzo" in event.event_date_display

    def test_auto_time_display(self):
        """Test time display is auto-generated."""
        form = EventForm(
            data={
                "title": "Test Event",
                "description": "Description",
                "start_date": "2025-03-15",
                "start_time": "18:30",
            }
        )
        assert form.is_valid()
        event = form.save(commit=False)
        assert "18:30" in event.event_time_display

    @pytest.mark.django_db
    def test_init_populates_split_fields(self, event):
        """Test form init populates split date/time fields from instance."""
        form = EventForm(instance=event)
        assert form.fields["start_date"].initial is not None


class TestEventModel:
    """Tests for the Event model."""

    def test_is_pending(self, user_pending_event):
        """Test is_pending property."""
        assert user_pending_event.is_pending is True

    def test_is_approved(self, approved_event):
        """Test is_approved property."""
        assert approved_event.is_approved is True

    def test_can_edit_by_creator(self, approved_event, collaborator_user):
        """Test creator can edit their event."""
        assert approved_event.can_edit(collaborator_user) is True

    def test_can_edit_by_admin(self, approved_event, admin_user):
        """Test admin can edit any event."""
        assert approved_event.can_edit(admin_user) is True

    def test_can_edit_by_moderator(self, approved_event, moderator_user):
        """Test moderator can edit any event."""
        assert approved_event.can_edit(moderator_user) is True

    def test_can_edit_by_other_user(self, approved_event, member_user):
        """Test member cannot edit others' events."""
        assert approved_event.can_edit(member_user) is False

    def test_can_approve_by_admin(self, approved_event, admin_user):
        """Test admin can approve events."""
        assert approved_event.can_approve(admin_user) is True

    def test_can_approve_by_moderator(self, approved_event, moderator_user):
        """Test moderator can approve events."""
        assert approved_event.can_approve(moderator_user) is True

    def test_can_approve_by_collaborator(self, approved_event, collaborator_user):
        """Test collaborator cannot approve events."""
        assert approved_event.can_approve(collaborator_user) is False

    def test_str_representation(self, approved_event):
        """Test string representation of event."""
        assert str(approved_event) == "User Test Event"


@pytest.mark.django_db
class TestEventViews:
    """Tests for event views."""

    def test_events_list_public(self, client, approved_event):
        """Test events list is publicly accessible."""
        response = client.get(reverse("events"))
        assert response.status_code == 200

    def test_events_list_only_approved(self, client, approved_event, user_pending_event):
        """Test events list shows only approved events."""
        response = client.get(reverse("events"))
        assert approved_event.title in response.content.decode()
        assert user_pending_event.title not in response.content.decode()

    def test_my_events_requires_login(self, client):
        """Test my events requires authentication."""
        response = client.get(reverse("my_events"))
        assert response.status_code == 302

    def test_my_events_requires_permission(self, client, member_user):
        """Test member without permission is redirected."""
        client.force_login(member_user)
        response = client.get(reverse("my_events"))
        assert response.status_code == 302

    def test_my_events_shows_own_events(self, client, collaborator_user, approved_event):
        """Test my events shows user's own events."""
        client.force_login(collaborator_user)
        response = client.get(reverse("my_events"))
        assert response.status_code == 200
        assert approved_event.title in response.content.decode()

    def test_pending_events_requires_login(self, client):
        """Test pending events requires authentication."""
        response = client.get(reverse("pending_events"))
        assert response.status_code == 302

    def test_pending_events_requires_admin(self, client, collaborator_user):
        """Test pending events requires admin/moderator."""
        client.force_login(collaborator_user)
        response = client.get(reverse("pending_events"))
        assert response.status_code == 302

    def test_pending_events_shows_pending(
        self, client, moderator_user, user_pending_event, approved_event
    ):
        """Test pending events shows only pending events."""
        client.force_login(moderator_user)
        response = client.get(reverse("pending_events"))
        assert response.status_code == 200
        assert user_pending_event.title in response.content.decode()
        assert approved_event.title not in response.content.decode()

    def test_create_requires_login(self, client):
        """Test create requires authentication."""
        response = client.get(reverse("event_create"))
        assert response.status_code == 302

    def test_create_requires_permission(self, client, member_user):
        """Test member without permission is redirected."""
        client.force_login(member_user)
        response = client.get(reverse("event_create"))
        assert response.status_code == 302

    def test_create_get_returns_form(self, client, collaborator_user):
        """Test create GET returns form."""
        client.force_login(collaborator_user)
        response = client.get(reverse("event_create"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_create_collaborator_sets_pending(self, client, collaborator_user):
        """Test collaborator creating event sets PENDING status."""
        client.force_login(collaborator_user)
        response = client.post(
            reverse("event_create"),
            {
                "title": "New Event",
                "description": "Description",
                "location": "Salta",
            },
        )
        assert response.status_code == 302
        event = Event.objects.get(title="New Event")
        assert event.status == Event.Status.PENDING

    def test_create_admin_sets_approved(self, client, admin_user):
        """Test admin creating event sets APPROVED status."""
        client.force_login(admin_user)
        response = client.post(
            reverse("event_create"),
            {
                "title": "Admin Event",
                "description": "Description",
                "location": "Salta",
            },
        )
        assert response.status_code == 302
        event = Event.objects.get(title="Admin Event")
        assert event.status == Event.Status.APPROVED

    def test_create_moderator_sets_approved(self, client, moderator_user):
        """Test moderator creating event sets APPROVED status."""
        client.force_login(moderator_user)
        response = client.post(
            reverse("event_create"),
            {
                "title": "Moderator Event",
                "description": "Description",
                "location": "Salta",
            },
        )
        assert response.status_code == 302
        event = Event.objects.get(title="Moderator Event")
        assert event.status == Event.Status.APPROVED

    def test_edit_requires_login(self, client, approved_event):
        """Test edit requires authentication."""
        response = client.get(reverse("event_edit", kwargs={"pk": approved_event.pk}))
        assert response.status_code == 302

    def test_edit_only_by_creator_or_admin(self, client, member_user, approved_event):
        """Test member cannot edit others' events."""
        client.force_login(member_user)
        response = client.get(reverse("event_edit", kwargs={"pk": approved_event.pk}))
        assert response.status_code == 302

    def test_edit_by_creator(self, client, collaborator_user, approved_event):
        """Test creator can edit event."""
        client.force_login(collaborator_user)
        response = client.get(reverse("event_edit", kwargs={"pk": approved_event.pk}))
        assert response.status_code == 200

    def test_edit_updates_event(self, client, collaborator_user, approved_event):
        """Test edit POST updates event."""
        client.force_login(collaborator_user)
        response = client.post(
            reverse("event_edit", kwargs={"pk": approved_event.pk}),
            {
                "title": "Updated Event",
                "description": approved_event.description,
                "location": approved_event.location,
            },
        )
        assert response.status_code == 302
        approved_event.refresh_from_db()
        assert approved_event.title == "Updated Event"

    def test_delete_requires_login(self, client, approved_event):
        """Test delete requires authentication."""
        response = client.get(reverse("event_delete", kwargs={"pk": approved_event.pk}))
        assert response.status_code == 302

    def test_delete_confirmation(self, client, collaborator_user, approved_event):
        """Test delete GET shows confirmation page."""
        client.force_login(collaborator_user)
        response = client.get(reverse("event_delete", kwargs={"pk": approved_event.pk}))
        assert response.status_code == 200

    def test_delete_removes_event(self, client, collaborator_user, approved_event):
        """Test delete POST removes event."""
        client.force_login(collaborator_user)
        event_pk = approved_event.pk
        response = client.post(reverse("event_delete", kwargs={"pk": event_pk}))
        assert response.status_code == 302
        assert not Event.objects.filter(pk=event_pk).exists()

    def test_delete_forbidden_for_others(self, client, member_user, approved_event):
        """Test delete is forbidden for non-owners."""
        client.force_login(member_user)
        response = client.post(reverse("event_delete", kwargs={"pk": approved_event.pk}))
        assert response.status_code == 302
        assert Event.objects.filter(pk=approved_event.pk).exists()

    def test_approve_requires_login(self, client, user_pending_event):
        """Test approve requires authentication."""
        response = client.get(reverse("event_approve", kwargs={"pk": user_pending_event.pk}))
        assert response.status_code == 302

    def test_approve_requires_admin(self, client, collaborator_user, user_pending_event):
        """Test collaborator cannot approve events."""
        client.force_login(collaborator_user)
        response = client.get(reverse("event_approve", kwargs={"pk": user_pending_event.pk}))
        assert response.status_code == 302

    def test_approve_confirmation_page(self, client, moderator_user, user_pending_event):
        """Test approve GET shows confirmation page."""
        client.force_login(moderator_user)
        response = client.get(reverse("event_approve", kwargs={"pk": user_pending_event.pk}))
        assert response.status_code == 200

    def test_approve_sets_status_approved(self, client, moderator_user, user_pending_event):
        """Test approve POST sets status to APPROVED."""
        client.force_login(moderator_user)
        response = client.post(
            reverse("event_approve", kwargs={"pk": user_pending_event.pk})
        )
        assert response.status_code == 302
        user_pending_event.refresh_from_db()
        assert user_pending_event.status == Event.Status.APPROVED

    def test_approve_sets_approved_by(self, client, moderator_user, user_pending_event):
        """Test approve sets approved_by to the approving user."""
        client.force_login(moderator_user)
        client.post(reverse("event_approve", kwargs={"pk": user_pending_event.pk}))
        user_pending_event.refresh_from_db()
        assert user_pending_event.approved_by == moderator_user

    def test_approve_sets_approved_at(self, client, moderator_user, user_pending_event):
        """Test approve sets approved_at timestamp."""
        client.force_login(moderator_user)
        client.post(reverse("event_approve", kwargs={"pk": user_pending_event.pk}))
        user_pending_event.refresh_from_db()
        assert user_pending_event.approved_at is not None

    def test_reject_requires_login(self, client, user_pending_event):
        """Test reject requires authentication."""
        response = client.get(reverse("event_reject", kwargs={"pk": user_pending_event.pk}))
        assert response.status_code == 302

    def test_reject_requires_admin(self, client, collaborator_user, user_pending_event):
        """Test collaborator cannot reject events."""
        client.force_login(collaborator_user)
        response = client.get(reverse("event_reject", kwargs={"pk": user_pending_event.pk}))
        assert response.status_code == 302

    def test_reject_confirmation_page(self, client, moderator_user, user_pending_event):
        """Test reject GET shows confirmation page."""
        client.force_login(moderator_user)
        response = client.get(reverse("event_reject", kwargs={"pk": user_pending_event.pk}))
        assert response.status_code == 200

    def test_reject_sets_status_rejected(self, client, moderator_user, user_pending_event):
        """Test reject POST sets status to REJECTED."""
        client.force_login(moderator_user)
        response = client.post(reverse("event_reject", kwargs={"pk": user_pending_event.pk}))
        assert response.status_code == 302
        user_pending_event.refresh_from_db()
        assert user_pending_event.status == Event.Status.REJECTED
