"""
Tests for user authentication endpoints.

Covers registration, login, logout, and validation errors.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestRegistration:
    """Tests for POST /api/auth/register/."""

    url = reverse("auth-register")

    def test_register_success(self, api_client):
        """A valid registration returns 201 with user data and tokens."""
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["user"]["username"] == "newuser"
        assert "access" in data["tokens"]
        assert "refresh" in data["tokens"]

    def test_register_password_mismatch(self, api_client):
        """Mismatched passwords return 400."""
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass1!",
            "password2": "DifferentPass2!",
        }
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 400

    def test_register_duplicate_username(self, api_client, user):
        """Registering with an existing username returns 400."""
        payload = {
            "username": "testuser",
            "email": "another@example.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:
    """Tests for POST /api/auth/login/."""

    url = reverse("auth-login")

    def test_login_success(self, api_client, user):
        """Valid credentials return 200 with access and refresh tokens."""
        payload = {"username": "testuser", "password": "TestPass123!"}
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_login_invalid_credentials(self, api_client, user):
        """Invalid credentials return 401."""
        payload = {"username": "testuser", "password": "WrongPassword!"}
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 401


@pytest.mark.django_db
class TestLogout:
    """Tests for POST /api/auth/logout/."""

    url = reverse("auth-logout")

    def test_logout_success(self, auth_client, user):
        """Provide a valid refresh token and receive 205."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        response = auth_client.post(self.url, {"refresh": str(refresh)}, format="json")

        assert response.status_code == 205

    def test_logout_unauthenticated(self, api_client):
        """Unauthenticated logout returns 401."""
        response = api_client.post(self.url, {"refresh": "fake"}, format="json")

        assert response.status_code == 401


@pytest.mark.django_db
class TestTokenRefresh:
    """Tests for POST /api/auth/token/refresh/."""

    url = reverse("auth-token-refresh")

    def test_refresh_success(self, api_client, user):
        """A valid refresh token returns a new access token."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        response = api_client.post(self.url, {"refresh": str(refresh)}, format="json")

        assert response.status_code == 200
        data = response.json()
        assert "access" in data

    def test_refresh_invalid_token(self, api_client):
        """An invalid refresh token returns 401."""
        response = api_client.post(self.url, {"refresh": "invalid-token"}, format="json")

        assert response.status_code == 401
