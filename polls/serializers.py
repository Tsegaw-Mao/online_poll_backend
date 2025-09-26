from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Poll, Option, Vote
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"]
        )
        return user


class OptionSerializer(serializers.ModelSerializer):
    """Serializer for poll options with vote count."""
    class Meta:
        model = Option
        fields = ("id", "text", "vote_count")


class PollSerializer(serializers.ModelSerializer):
    """Serializer for polls with nested options."""
    options = OptionSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField()
    # provide expiry_date as-is (keeps original name) and created_at already exists
    # total_votes will be provided by queryset annotation (if present)
    total_votes = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Poll
        fields = ("id", "title", "description", "expiry_date", "created_by", "created_at", "options", "total_votes")
        read_only_fields = ("created_by",)

    def get_created_by(self, obj):
        if obj.created_by:
            return getattr(obj.created_by, "username", None)
        return None

    def create(self, validated_data):
        # Options are created in the view (as before)
        return super().create(validated_data)


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for votes."""
    class Meta:
        model = Vote
        fields = ("id", "poll", "option", "user")
        read_only_fields = ("user",)
