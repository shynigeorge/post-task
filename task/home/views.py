from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from home.serializers import *
from home.models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'OK',
                'message': 'User created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        serializer = CustomUserSerializer(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data,  
        })
    
    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only authenticated users can create posts
def create_post(request):
    if request.method == 'POST':
        # Get the logged-in user (request.user is automatically set by the authentication system)
        user = request.user

        # Get tags (which are the users) from the request data
        tags_data = request.data.get('tags', [])

        # Ensure that tags_data is a list of integers (user IDs)
        if not isinstance(tags_data, list):
            return Response({"error": "tags must be a list of integers (user IDs)"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that all tags are integers
        try:
            tags_data = [int(tag) for tag in tags_data]
        except ValueError:
            return Response({"error": "All tags must be integers"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the CustomUser instances that correspond to the provided tag IDs
        tags = CustomUser.objects.filter(id__in=tags_data)

        # Prepare data for post creation
        data = {
            'user': user.id,  # Assign logged-in user as the post creator
            'title': request.data.get('title'),
            'description': request.data.get('description'),
            'tags': tags_data,  # Pass only the tag IDs (not instances)
        }

        # Serialize the post data
        serializer = PostSerializer(data=data)

        if serializer.is_valid():
            serializer.save()  # Save the post
            return Response({
                'status': 'OK',
                'message': 'Post created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        # Return errors if serializer is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_publish(request, post_id):
    try:
        post = Post.objects.get(id=post_id, user=request.user)
        post.is_published = not post.is_published
        post.save()
        return Response({"is_published": post.is_published}, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({"error": "Post not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_posts(request):
    # Query the top 10 published posts ordered by like count in descending order
    top_posts = Post.objects.filter(is_published=True).annotate(like_count=Count('likes')).order_by('-like_count')[:10]  # Adjust the number to limit top N posts

    # Serialize the data
    serializer = PostListSerializer(top_posts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        # Fetch the post by ID
        post = Post.objects.get(id=post_id)

        # Get or create the Like instance for this user and post
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        # Toggle the 'liked' status
        like.liked = not like.liked
        like.save()

        # Prepare response message
        message = 'Post liked' if like.liked else 'Post unliked'
        return Response({'message': message}, status=status.HTTP_200_OK)

    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)