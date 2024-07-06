from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from.models import Profile, Posts, LikePost, FollowerCount
from django.http import HttpResponse, JsonResponse
import os
from itertools import chain
from django.db.models import Q


@login_required(login_url='login')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []

    user_following = FollowerCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    # Include the current user in the list of users to fetch posts for
    user_following_list.append(request.user)

    # Get posts from users that the current user is following and the user's own posts
    feed = Posts.objects.filter(user__in=user_following_list).order_by('-created_at')

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed})

@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image')
        bio = request.POST.get('bio')

        if image: # if
            if user_profile.profile_pic == 'default-profile-pic.png':
                user_profile.profile_pic = image

            else:
                os.remove(f'media/{user_profile.profile_pic}')
                user_profile.profile_pic = image
        if bio:
            user_profile.bio = bio

        user_profile.save()
        messages.success(request, 'Profile updated successfully.')

    return render(request, 'settings.html', {'user_profile': user_profile})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']

        if password == password2:
                
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')

            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
        
            else:

                user = User.objects.create_user(username=username, email=email, password=password, first_name=firstName, last_name=lastName)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, fname=firstName, lname=lastName)
                new_profile.save()

                return redirect('settings')

        else:
            messages.info(request, 'Passwords do not Match')
            return redirect('signup')

    else:
        return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        
        else:
            messages.info(request, 'Credentials Invalid ')
            return redirect('login')

    else:
        return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Posts.objects.filter(user=pk)
    user_post_length = len(user_posts)
    follower_count = FollowerCount.objects.filter(user=pk).count()
    following_count = FollowerCount.objects.filter(follower=pk).count()

    follower = request.user.username
    user = pk

    if FollowerCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    
    else:
        button_text = 'Follow'

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'follower_count': follower_count,
        'following_count': following_count
    }

    return render(request, 'profile.html', context)

@login_required(login_url='login')
def post(request):
    if request.method == 'POST':
        user = request.user.username
        img=request.FILES['image']
        caption=request.POST['caption']

        new_post = Posts.objects.create(user=user, image=img, caption=caption)
        new_post.save()

        return redirect('/')

    else: 
        return render(request, 'post.html')

@login_required(login_url='login')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Posts.objects.get(id_post=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.likes = post.likes + 1
    else:
        like_filter.delete()
        post.likes = post.likes - 1
    
    post.save()
    return redirect('/')
    
@login_required(login_url='login')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect(f'/profile/{user}')
        
        else:
            new_follower = FollowerCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect(f'/profile/{user}')
    else:
        return redirect('/')

def edit_post(request): #Work in pogress
    post_id = request.GET.get('post_id')
    post = Posts.objects.get(id_post=post_id)

    if request == 'POST':
        caption = request.POST.get('caption')

        if caption:
            post.caption = caption
    
    return redirect('/profile')

def delete_post(request): # Work in progress
    post_id = request.GET.get('post_id')
    post = Posts.objects.get(id_post=post_id)

    if request == 'POST':
        post.delete()
        return redirect('profile/')

@login_required # Work in progress
def edit_password(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        old_password = request.POST['oldpassword']
        new_password = request.POST.get('newpassword')

        user_object.save()
        return redirect('/')

    return render(request, 'edit_password.html')

def delete_user(request): # Work in progress
    pass
