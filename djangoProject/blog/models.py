import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.
class ProcessedPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='data')

class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analisedImage = models.ForeignKey(ProcessedPhoto, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=5000)
    status = models.BooleanField(default=False)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)


    def return_ratings(self):
        return len(ArticleRating.objects.filter(article=self))

    def average_rating(self):
        suma = 0
        allRatings = ArticleRating.objects.filter(article=self)
        ratingNum = len(allRatings)
        if ratingNum < 1:
            return 0
        for rating in allRatings:
            suma += rating.value
        return suma / ratingNum

class ArticleRating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'article'),)
        index_together = (('user', 'article'),)
