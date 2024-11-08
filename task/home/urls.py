from django.urls import path
from home.views import *

urlpatterns = [
    path('register/',register_user,name='register'),
    path('login/',login,name='login'),
    path('create_post/',create_post, name='create_post'),
    path('posts/<int:post_id>/', toggle_publish, name='toggle_publish'),
    path('posts/', top_posts, name='list_posts'),
    path('like/<int:post_id>/', like_post, name='like_post'),
]