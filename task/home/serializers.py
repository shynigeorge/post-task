from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Post, Like


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'password', 'phone_no']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value



class PostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())  # User who created the post
    tags = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)  # Tags as list of user IDs

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'description', 'tags', 'created_at']
        read_only_fields = ['created_at']

        # created_at is automatically handled by the database


class PostListSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.name', read_only=True)  # Display the user's name instead of ID

    class Meta:
        model = Post
        fields = ['id', 'user_name', 'title', 'description', 'tags', 'is_published', 'like_count', 'formatted_date']

    def get_like_count(self, obj):
        # Count the number of likes for each post where `liked=True`
        return obj.likes.filter(liked=True).count()

    def get_formatted_date(self, obj):
        # Format the `created_at` date as dd-mm-yyyy
        return obj.created_at.strftime('%d-%m-%Y')