from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, UserConfirmation
from .serializers import RegisterSerializer


class RegistrationHandler:
    """Handles user registration and confirmation setup."""

    def __init__(self, data):
        self.data = data
        self.serializer = RegisterSerializer(data=data)

    def register_user(self):
        if self.serializer.is_valid():
            user = self.serializer.save()
            user.is_active = False
            user.save()

            confirmation, created = UserConfirmation.objects.get_or_create(user=user)
            if not created:
                confirmation.regenerate_code()

            return Response(
                {"message": "User registered successfully. Please check your email for the confirmation code."},
                status=status.HTTP_201_CREATED
            )
        return Response(self.serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmationHandler:
    """Handles user confirmation logic."""

    def __init__(self, data):
        self.username = data.get("username")
        self.code = data.get("code")

    def confirm_user(self):
        if not self.username or not self.code:
            return Response(
                {"error": "Both 'username' and 'code' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=self.username)
            confirmation = UserConfirmation.objects.get(user=user)

            if confirmation.is_expired():
                return Response(
                    {"error": "Confirmation code has expired. Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if confirmation.code != self.code:
                return Response(
                    {"error": "Invalid confirmation code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.is_active = True
            user.save()
            confirmation.delete()

            return Response(
                {"message": "User confirmed successfully."},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserConfirmation.DoesNotExist:
            return Response(
                {"error": "Invalid confirmation code."},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterAPIView(APIView):
    def post(self, request):
        handler = RegistrationHandler(request.data)
        return handler.register_user()


class ConfirmUserAPIView(APIView):
    def post(self, request):
        handler = ConfirmationHandler(request.data)
        return handler.confirm_user()
