from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('logout/',views.logout_view,name='logout'),
    path('upload/', views.upload_video, name='upload_video'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('video/<int:video_id>/<str:reaction>/', views.react_video, name='react_video'),
    path('dashboard/',views.user_dashboard,name='user_dashboard'),
    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
]
