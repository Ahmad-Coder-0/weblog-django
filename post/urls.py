from django.urls import path
from . import views
from django.contrib.auth import views as AuthViews

app_name = 'post'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<str:category>', views.post_list, name='post_list_category'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('tickets/', views.TicketCreateView.as_view(), name='tickets'),
    path('posts/<int:pk>/comment',
         views.PostCommentView.as_view(), name='post_comment'),
    path('search/', views.SearchView.as_view(), name='search_post'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/add-post', views.add_post, name="add_post"),
    path('profile/delete-post/<int:pk>', views.delete_post, name='delete_post'),
    path('profile/edit-post/<int:pk>', views.edit_post, name="edit_post"),
    path('login/', AuthViews.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', AuthViews.LogoutView.as_view(), name='logout'),
    path('password-change/', AuthViews.PasswordChangeView.as_view(success_url='done'),
         name="password_change"),
    path('password-change/done/', AuthViews.PasswordChangeDoneView.as_view(),
         name="password_change_done"),
    path('password-reset/', AuthViews.PasswordResetView.as_view(success_url='done'),
         name='password_reset'),
    path('password-reset/done/', AuthViews.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', AuthViews.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complate/', AuthViews.PasswordResetCompleteView.as_view(),
         name='password_reset_complate'),
    path('register/', views.register, name="register"),
    path('profile/edit-user-profile/', views.edit_profile, name='edit_profile'),
    path('profile-view/<int:user_id>/', views.profile_view, name='profile_view'),
]
