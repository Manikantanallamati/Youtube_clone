from django.shortcuts import render
from core.search.document import VideoDocument

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from .forms import VideoUploadForm
from .models import Video,Profile,Comment
import random
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def video_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = VideoDocument.search().query("match", title=query).to_queryset()
    return render(request, 'video_search.html', {'results': results, 'query': query})

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    session_key = f'viewed_video_{video.id}'
    if not request.session.get(session_key, False):
        video.views += 1
        video.save(update_fields=['views'])
        request.session[session_key] = True
    return render(request, 'video_detail.html', {'video': video})

def landing_page(request):
    query = request.GET.get('q', '')
    if query:
        videos = VideoDocument.search().query("match", title=query).to_queryset()
    else:
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

def load_comments(request, video_id):
    top_level_comments = Comment.objects.filter(video_id=video_id, parent__isnull=True).order_by('-created_at')

    def serialize(comment):
        return {
            "id": comment.id,
            "user": comment.user.username,
            "comment": comment.comment,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
            "replies": [
                {
                    "id": reply.id,
                    "user": reply.user.username,
                    "comment": reply.comment,
                    "created_at": reply.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for reply in comment.replies.all().order_by('created_at')
            ]
        }

    data = {"comments": [serialize(c) for c in top_level_comments]}
    return JsonResponse(data)

@require_POST
@login_required
def add_comment(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    text = request.POST.get('text')
    parent_id = request.POST.get('parent_id')

    if not text:
        return JsonResponse({'error': 'Empty comment'}, status=400)

    parent = None
    if parent_id:
        try:
            parent = Comment.objects.get(id=parent_id)
        except Comment.DoesNotExist:
            pass

    comment = Comment.objects.create(
        video=video,
        user=request.user,
        comment=text,
        parent=parent
    )

    return JsonResponse({
    'user': comment.user.username,
    'comment': comment.comment,
    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
    'parent_id': parent.id if parent else None, 
    'id': comment.id
})

from django.http import JsonResponse
from .models import Comment

def get_comments(request, video_id):
    comments = Comment.objects.filter(video_id=video_id, parent=None).order_by('-created_at')
    
    def serialize_comment(comment):
        return {
            'id': comment.id,
            'user': comment.user.username,
            'comment': comment.text,
            'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M"),
            'replies': [
                {
                    'id': reply.id,
                    'user': reply.user.username,
                    'comment': reply.text,
                    'created_at': reply.created_at.strftime("%Y-%m-%d %H:%M")
                } for reply in comment.replies.all().order_by('created_at')
            ]
        }

    data = {
        'comments': [serialize_comment(comment) for comment in comments]
    }
    return JsonResponse(data)


@login_required
def edit_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, uploaded_by=request.user)

    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard') 
    else:
        form = VideoUploadForm(instance=video)

    return render(request, 'edit_video.html', {'form': form, 'video': video})

@login_required
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, uploaded_by=request.user)

    if request.method == 'POST':
        video.delete()
        return redirect('user_dashboard')

    return render(request, 'confirm_delete.html', {'video': video})