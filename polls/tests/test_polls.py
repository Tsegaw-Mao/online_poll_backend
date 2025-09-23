# polls/tests/test_polls.py
from django.utils import timezone
from django.contrib.auth import get_user_model   # ✅ use this instead of auth.User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from polls.models import Poll, Option, Vote
from datetime import timedelta

User = get_user_model()   # ✅ this points to polls.User now



class PollSystemTest(APITestCase):
    def setUp(self):
        # Setup API client and base user
        self.client = APIClient()
        self.user_data = {"username": "testuser", "password": "password123"}
        self.user = User.objects.create_user(**self.user_data)

        # Common URLs
        self.login_url = reverse("token_obtain_pair")  # JWT login
        self.register_url = reverse("user-register")   # user registration
        self.polls_url = reverse("poll-list")          # /api/polls/
        self.docs_url = "/api/docs/"                   # swagger docs

    def authenticate(self):
        """Helper: login and set JWT auth header for protected endpoints"""
        response = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ---------------- Authentication ----------------
    def test_user_signup_and_login(self):
        """✅ Tests that a new user can register and log in (User Story 1.1 & 1.2)"""
        response = self.client.post(self.register_url, {"username": "newuser", "password": "pass1234"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.login_url, {"username": "newuser", "password": "pass1234"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # JWT token returned

    def test_logout(self):
        """✅ Tests that an authenticated user can log out (User Story 1.3)"""
        # 1️⃣ Log in to get tokens
        login_response = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]
    
        # 2️⃣ Set auth header with access token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    
        # 3️⃣ Call logout endpoint with refresh token in request body
        response = self.client.post(reverse("user-logout"), {"refresh": refresh_token}, format="json")
    
        # 4️⃣ Assert logout success
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful.")
    


    # ---------------- Poll Management ----------------
    def test_create_poll_with_options(self):
        """✅ Tests poll creation with title, description, expiry date, and multiple options (User Story 2.1 & 2.2)"""
        self.authenticate()
        payload = {
            "title": "Best programming language?",
            "description": "Vote for your favorite.",
            "expiry_date": (timezone.now() + timedelta(days=1)).isoformat(),
            "options": ["Python", "JavaScript", "Go"]
        }
        response = self.client.post(self.polls_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Poll.objects.count(), 1)
        self.assertEqual(Option.objects.count(), 3)

    def test_list_polls(self):
        """✅ Tests listing all active polls (User Story 2.3)"""
        Poll.objects.create(
            title="Sample Poll",
            description="Description",
            expiry_date=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        response = self.client.get(self.polls_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_view_poll_details(self):
        """✅ Tests retrieving a poll with all its options (User Story 2.4)"""
        poll = Poll.objects.create(
            title="Favorite Fruit",
            description="Choose one.",
            expiry_date=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        Option.objects.create(poll=poll, text="Apple")
        Option.objects.create(poll=poll, text="Banana")

        response = self.client.get(reverse("poll-detail", args=[poll.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["options"]), 2)

    # ---------------- Voting System ----------------
    def test_cast_vote(self):
        """✅ Tests that an authenticated user can cast exactly one vote (User Story 3.1)"""
        self.authenticate()
        poll = Poll.objects.create(
            title="Best OS",
            description="Choose one.",
            expiry_date=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        option = Option.objects.create(poll=poll, text="Linux")

        response = self.client.post(reverse("vote"), {"poll": poll.id, "option": option.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)

    def test_prevent_duplicate_votes(self):
        """✅ Tests system prevents duplicate votes per user per poll (User Story 3.2)"""
        self.authenticate()
        poll = Poll.objects.create(
            title="Best OS",
            description="Choose one.",
            expiry_date=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        option = Option.objects.create(poll=poll, text="Linux")

        # First vote works
        self.client.post(reverse("vote"), {"poll": poll.id, "option": option.id}, format="json")
        # Second vote should fail
        response = self.client.post(reverse("vote"), {"poll": poll.id, "option": option.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_only_in_active_polls(self):
        """✅ Tests votes are rejected on expired/inactive polls (User Story 3.3)"""
        self.authenticate()
        poll = Poll.objects.create(
            title="Expired Poll",
            description="You can't vote here.",
            expiry_date=timezone.now() - timedelta(days=1),  # already expired
            created_by=self.user
        )
        option = Option.objects.create(poll=poll, text="Option1")

        response = self.client.post(reverse("vote"), {"poll": poll.id, "option": option.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------- Results & Analytics ----------------
    def test_view_poll_results(self):
        """✅ Tests real-time poll results with vote counts (User Story 4.1)"""
        poll = Poll.objects.create(
            title="Favorite Color",
            description="Choose one.",
            expiry_date=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        option1 = Option.objects.create(poll=poll, text="Red", vote_count=2)
        option2 = Option.objects.create(poll=poll, text="Blue", vote_count=3)

        response = self.client.get(reverse("poll-detail", args=[poll.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["options"][0]["vote_count"], option1.vote_count)
        self.assertEqual(response.data["options"][1]["vote_count"], option2.vote_count)

    # ---------------- API Documentation ----------------
    def test_swagger_docs_available(self):
        """✅ Tests that Swagger UI is served at /api/docs/ (User Story 5.1)"""
        response = self.client.get(self.docs_url)
        self.assertIn(response.status_code, [200, 301, 302])  # docs available

    # ---------------- Error Handling ----------------
    def test_invalid_vote_request(self):
        """✅ Tests error handling for invalid poll/option (User Story 5.2)"""
        self.authenticate()
        response = self.client.post(reverse("vote"), {"poll": 999, "option": 999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
