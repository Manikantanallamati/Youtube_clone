from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('logout/',views.logout_view,name='logout')
]
