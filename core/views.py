from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from .forms import VideoUploadForm
from .models import Video,Profile
import random
from django.contrib.auth.models import User


def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'video_detail.html', {'video': video})

def landing_page(request):
    videos = Video.objects.all().order_by('-uploaded_at')
    return render(request, 'landing.html', {'videos': videos})

def logout_view(request):
    logout(request)
    return redirect('landing')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    videos = list(Video.objects.all())
    random.shuffle(videos)
    return render(request, 'home.html', {'videos': videos})

@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploaded_by = request.user
            video.save()
            return redirect('landing') 
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})

@login_required
def react_video(request, video_id, reaction):
    video = get_object_or_404(Video, id=video_id)
    user = request.user

    if reaction == 'like':
        video.disliked_by.remove(user)
        if user in video.liked_by.all():
            video.liked_by.remove(user) 
        else:
            video.liked_by.add(user)

    elif reaction == 'dislike':
        video.liked_by.remove(user)
        if user in video.disliked_by.all():
            video.disliked_by.remove(user)
        else:
            video.disliked_by.add(user)

    return redirect('video_detail', video_id=video.id)


@login_required
def user_dashboard(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    videos = Video.objects.filter(uploaded_by=request.user)
    videos_count = videos.count()

    context = {
        'videos': videos,
        'videos_count': videos_count,
        'followers_count': profile.followers.count(),
        'following_count': profile.following.count(),
        'followers': profile.followers.all(),
        'following': profile.following.all(),
    }

    return render(request, 'dashboard.html', context)

@login_required
def toggle_follow(request, user_id):
    current_user_profile, _ = Profile.objects.get_or_create(user=request.user)

    target_user = get_object_or_404(User, id=user_id)
    target_profile, _ = Profile.objects.get_or_create(user=target_user)

    if target_profile in current_user_profile.following.all():
        current_user_profile.following.remove(target_profile)
    else:
        current_user_profile.following.add(target_profile)

    return redirect(request.META.get('HTTP_REFERER', '/'))