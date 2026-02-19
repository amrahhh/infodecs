from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """Register a new user and return JWT tokens.

    **POST /api/auth/register/**

    No authentication required. Returns access and refresh tokens upon
    successful registration so the user is immediately logged in.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(description="Register a new user account.")
    def create(self, request, *args, **kwargs):
        """Handle user registration and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    """Blacklist the provided refresh token to log out the user.

    **POST /api/auth/logout/**

    Requires authentication. The client must send a JSON body with
    ``{"refresh": "<token>"}``.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(description="Log out by blacklisting the refresh token.")
    def post(self, request):
        """Blacklist the provided refresh token."""
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or already blacklisted token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_205_RESET_CONTENT,
        )
