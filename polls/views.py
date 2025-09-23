from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Poll, Option, Vote, User
from .serializers import PollSerializer, UserSerializer


# ---------------- User Registration ----------------
class UserRegisterView(generics.CreateAPIView):
    """Public endpoint for user registration."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# ---------------- Logout ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting their refresh token."""
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token required."}, status=400)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=200)
    except Exception:
        return Response({"error": "Invalid token."}, status=400)


# ---------------- Poll CRUD ----------------
class PollViewSet(viewsets.ModelViewSet):
    """CRUD for Polls + list options + results."""
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        options_data = self.request.data.get("options", [])
        poll = serializer.save(created_by=self.request.user)
        # create poll options
        for text in options_data:
            Option.objects.create(poll=poll, text=text)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()


# ---------------- Voting ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cast_vote(request):
    """Allow authenticated users to vote once per poll."""
    poll_id = request.data.get("poll")
    option_id = request.data.get("option")

    poll = get_object_or_404(Poll, id=poll_id)
    option = get_object_or_404(Option, id=option_id, poll=poll)

    # Prevent duplicate vote
    if Vote.objects.filter(user=request.user, poll=poll).exists():
        return Response({"error": "You have already voted on this poll."}, status=400)

    # Prevent voting on expired polls
    if not poll.is_active:
        return Response({"error": "This poll is closed."}, status=400)

    Vote.objects.create(user=request.user, poll=poll, option=option)
    option.vote_count += 1
    option.save()

    return Response({"message": "Vote cast successfully."}, status=201)
