#/movies/admin_apis
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import CustomUser
from movies.models import Movie, Review
from movies.serializers import MovieAdminSerializer


class AdminMovieManagement(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = MovieAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)