from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from .forms import VideoUploadForm
from .models import Video
import random



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
