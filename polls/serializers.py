from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Poll, Option, Vote

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

    class Meta:
        model = Poll
        fields = ("id", "title", "description", "expiry_date", "created_by", "options")
        read_only_fields = ("created_by",)

    def create(self, validated_data):
        # Options are created in the view
        return super().create(validated_data)


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for votes."""
    class Meta:
        model = Vote
        fields = ("id", "poll", "option", "user")
        read_only_fields = ("user",)
