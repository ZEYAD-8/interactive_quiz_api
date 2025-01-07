from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserCustomSerializer, UserRegistrationSerializer
from rest_framework.authtoken.models import Token
from quizzes.serializers import QuizSerializer, QuestionSerializer

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

class UserProfileView(APIView):

    def get(self, request):
        user = request.user
        return Response(UserCustomSerializer(user).data, status=status.HTTP_200_OK)

class UserCreatedQuizzesView(APIView):

    def get(self, request):
        user = request.user
        quizzes = user.created_quizzes()
        return Response(QuizSerializer(quizzes, many=True).data, status=status.HTTP_200_OK)

class UserCreatedQuestionsView(APIView):
    
    def get(self, request):
        user = request.user
        questions = user.created_questions()
        return Response(QuestionSerializer(questions, many=True).data, status=status.HTTP_200_OK)
