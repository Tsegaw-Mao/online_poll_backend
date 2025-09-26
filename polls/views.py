# polls/views.py
from rest_framework import viewsets, generics, status, permissions, filters as drf_filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.views import APIView

from django.db import transaction
from django.db.models import F, Sum, Count, Value
from django.db.models.functions import Coalesce

from django_filters.rest_framework import DjangoFilterBackend

from .models import Poll, Option, Vote, User
from .serializers import PollSerializer, UserSerializer, OptionSerializer, VoteSerializer
from .filters import PollFilter


# ---------------- User Registration ----------------
class UserRegisterView(generics.CreateAPIView):
    """Public endpoint for user registration."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# ---------------- Poll CRUD ----------------
class PollViewSet(viewsets.ModelViewSet):
    """CRUD for Polls + list options + results."""
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    # Filters, ordering
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = PollFilter
    ordering_fields = ['created_at', 'expiry_date', 'id', 'title', 'total_votes']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        # annotate total_votes (sum of option.vote_count) for fast ordering & returning
        return Poll.objects.prefetch_related('options').annotate(
            total_votes=Coalesce(Sum('options__vote_count'), Value(0))
        )

    def perform_create(self, serializer):
        options_data = self.request.data.get("options", [])
        poll = serializer.save(created_by=self.request.user)
        # create poll options
        for text in options_data:
            Option.objects.create(poll=poll, text=text)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def results(self, request, pk=None):
        """
        Return aggregated results for a poll:
        - uses Count on Vote table to get accurate counts (single query per options set)
        - returns list of options with vote_count (from aggregation)
        """
        poll = get_object_or_404(Poll, id=pk)

        # aggregate vote counts per option (single-query)
        options_qs = Option.objects.filter(poll=poll).annotate(vote_count_agg=Count('votes'))
        options = [
            {"id": o.id, "text": o.text, "vote_count": o.vote_count_agg}
            for o in options_qs
        ]

        # total votes via count on Vote table
        total_votes = Vote.objects.filter(poll=poll).count()

        return Response({
            "poll_id": poll.id,
            "title": poll.title,
            "total_votes": total_votes,
            "options": options
        })


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

    # Use transaction + F() update for atomic increment
    with transaction.atomic():
        Vote.objects.create(user=request.user, poll=poll, option=option)
        Option.objects.filter(pk=option.pk).update(vote_count=F('vote_count') + 1)

    return Response({"message": "Vote cast successfully."}, status=201)
