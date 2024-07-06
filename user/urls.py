from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings/', views.settings, name='settings'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('post/', views.post, name='post'),
    path('like-post/', views.like_post, name='like_post'),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('follow/', views.follow, name='follow'),
    path('edit_post/', views.edit_post, name='edit_post'),
    path('delete_post/', views.delete_post, name='delete_post'),
    path('edit_password/', views.edit_password, name='edit_password')
]
