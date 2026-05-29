from django.urls import path
from . import views

app_name = 'post'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('tickets/', views.tickets, name='tickets'),
    path('posts/<int:pk>/comment', views.post_comment, name='post_comment'),
    path('search/', views.search_post, name='search_post'),
    path('profile/', views.profile, name='profile'),
    path('profile/add-post', views.add_post, name="add_post")
]
