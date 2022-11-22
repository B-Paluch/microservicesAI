import json
import os

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from kafka import KafkaProducer
from rest_framework import serializers

from blog.models import Article, ArticleRating, ProcessedPhoto

producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_HOST', "localhost:9092"),
                         value_serializer=lambda v: json.dumps(v, cls=DjangoJSONEncoder).encode('utf-8'))


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedPhoto
        fields = ('id', 'name', 'photo')

    def create(self, validated_data):
        producer.send('photoSavedToBlog', {
            "service": "blog",
            "value": "The photo has been saved on blog."
        })
        photo = ProcessedPhoto.objects.create(**validated_data)
        return photo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        producer.send('articleUpdated', {
            "service": "blog",
            "value": "User has been created."
        })
        user = User.objects.create_user(**validated_data)
        return user


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'analisedImage', 'title', 'description', 'user', 'status', 'return_ratings', 'average_rating')

    def create(self, validated_data):
        article = super().create(validated_data)
        print('uwu')
        producer.send('articleUpdated', {
            "service": "blog",
            "value": "Article has been created."
        })
        producer.send('articleSaved', article.id)
        return article

    def update(self, instance, validated_data):
        article = super().update(instance, validated_data)
        producer.send('articleUpdated', {
            "service": "blog",
            "value": "Article has been updated."
        })
        producer.send('articleSaved', article.id)
        return article

class ArticleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRating
        fields = ('id', 'article', 'user', 'article')
