from django.conf.urls import url
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

from blog import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'articles', views.ArticleViewSet)
router.register(r'article-ratings', views.ArticleRatingViewSet)
router.register(r'images', views.ImageViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

]