from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, UserConfirmation
from .serializers import RegisterSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {"message": "User registered successfully. Please check your email for the confirmation code."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmUserAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        code = request.data.get("code")
        if not username or not code:
            return Response(
                {"error": "Both 'username' and 'code' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
            confirmation = UserConfirmation.objects.get(user=user, code=code)

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
