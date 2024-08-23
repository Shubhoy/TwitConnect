
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newpost, name="newpost"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("profile/follow/<int:postuser_id>", views.follow,name="follow"),
    path("profile/unfollow/<int:postuser_id>", views.unfollow,name="unfollow"),
    path("following", views.following,name="following"),
    path("editing/<int:post_id>", views.editing,name="editing"),    
    path("like", views.like,name="like"),    
    path("dislike", views.dislike,name="dislike"),    
]
