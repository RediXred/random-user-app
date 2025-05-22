from django.urls import path
from . import views


app_name = 'users'
urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('<int:user_id>/', views.user_detail, name='user_detail'),
    path('random/', views.user_random, name='user_random'),
    path("load/", views.load_users, name="load_users"),
    path('load-form/', views.load_users_form, name='load_users_form'),
    path('messages/', views.user_messages, name='user_messages'),
]