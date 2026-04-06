from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('redeem/<str:prize_id>/', views.redeem_prize, name='redeem_prize'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]