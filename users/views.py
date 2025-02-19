from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserCustomSerializer, UserRegistrationSerializer
from rest_framework.authtoken.models import Token
from quizzes.serializers import QuizSerializer
from questions.serializers import QuestionSerializer
from .premissions import IsCreator
from rest_framework.permissions import IsAuthenticated

class RegisterUserView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            user_data = UserCustomSerializer(user).data
            return Response({
                'message': 'User registered successfully',
                'token': token.key,
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        if request.data.get('refresh_token', False):
            token.delete()
            token = Token.objects.create(user=user)

        user_data = UserCustomSerializer(user).data
        return Response({
            'user': user_data,
            'token': token.key
        })

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not user.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserCustomSerializer(user).data, status=status.HTTP_200_OK)

class UserCreationsView(APIView):
    permission_classes = [IsCreator]
    def get(self, request):
        user = request.user
        quizzes = user.created_quizzes()
        questions = user.created_questions()
        return Response({
            'questions': QuestionSerializer(questions, many=True).data,
            'quizzes': QuizSerializer(quizzes, many=True).data
        }, status=status.HTTP_200_OK)


class ChangeRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        requested = request.data.get('role')

        if requested is None:
            return Response({'error': 'Role not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(requested, str) and requested.strip().lower() not in ['creator', 'admin']:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        if requested.strip().lower() == 'admin':
            if user.is_admin:
                return Response({'error': 'User is already an admin'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_admin = True
            user.is_staff = True

        # if not admin, then creator
        else:
            if user.is_creator:
                return Response({'error': 'User is already a creator'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_creator = True

        user.save()
        return Response({'message': 'Role changed successfully'}, status=status.HTTP_200_OK)
