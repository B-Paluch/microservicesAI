from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

from .IsOwner import IsOwner
from .models import Article, ArticleRating, ProcessedPhoto
from .serializers import ArticleSerializer, ArticleRatingSerializer, UserSerializer, PhotoSerializer

from rest_framework.authentication import SessionAuthentication


class SessionCsrfExemptAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsOwner()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['POST'])
    def rate_article(self, request, pk=None):
        if 'value' in request.data:
            article = Article.objects.get(id=pk)
            value = request.data['value']
            user = request.user

            try:
                rating = ArticleRating.objects.get(user=user.id, article=article.id)
                rating.value = value
                rating.save()
                serializer = ArticleRatingSerializer(rating, many=False)
                response = {'message': 'Zmieniono ocenę artykułu', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)
            except:
                rating = ArticleRating.objects.create(user=user, article=article.id, value=value)
                serializer = ArticleRatingSerializer(rating, many=False)
                response = {'message': 'Oceniono artykuł', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)

        else:
            response = {'message': 'Nieprawidłowe wykorzystanie, nie podano oceny artykułu.'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([SessionCsrfExemptAuthentication])
class ImageViewSet(viewsets.ModelViewSet):
    queryset = ProcessedPhoto.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = (AllowAny,)


class ArticleRatingViewSet(viewsets.ModelViewSet):
    queryset = ArticleRating.objects.all()
    serializer_class = ArticleRatingSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        response = {'message': 'Niedozwolona metoda!'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        response = {'message': 'Niedozwolona metoda!'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PUT', 'POST'])
@authentication_classes([SessionCsrfExemptAuthentication])
def censor_article(request, id):
    if request.method == 'POST':
        article = Article.objects.get(id=id)
        article.status = True
        article.save()
        return Response({"message": "Article is ok! Thats great! It has been activated!"})
    if request.method == 'PUT':
        article = Article.objects.get(id=id)
        article.status = True
        put = QueryDict(request.body)
        print(put)
        article.title = put['title']
        article.description = put['description']
        article.save()
        return Response({"message": "Article is profane! But no worries! It has been changed!"})