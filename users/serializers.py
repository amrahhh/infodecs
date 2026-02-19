"""
Serializers for the users (authentication) application.
"""

from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration.

    Requires username, email, password, and password confirmation.
    """

    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        """Ensure the two password fields match."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create a new user with the validated data."""
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user
