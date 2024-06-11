from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('settings/', views.settings, name='settings'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/',views.profile, name='profile'),
    path('upload/', views.upload, name='upload')
]