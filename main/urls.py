from django.urls import path

from .views import (index, other_page, profile, user_activate,
                    BBLoginView, BBLogout, ChangeUserInfoView, BBPasswordChangeView, RegisterDoneView, RegisterUserView, 
                    DeleteUserView, BBPasswordResetView, BBPasswordResetDoneView, BBPasswordResetConfirmView)

app_name = 'main'
urlpatterns = [
    path('<str:page>/', other_page, name = 'other'),
    path('', index, name='index'),
    path('accounts/register/activate/<str:sign>', user_activate, name = 'register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name = 'register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name = 'register'),
    path('accounts/login/', BBLoginView.as_view(), name = 'login'),
    path('accounts/logout/', BBLogout.as_view(), name='logout'),
    path('accounts/password/reset/done/', BBPasswordResetDoneView.as_view(), name = 'password_reset_done'),
    path('accounts/password/reset/', BBPasswordResetView.as_view(), name = 'password_reset'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name = 'password_change'),
    path('accounts/reset/<uidb64>/<token>/', BBPasswordResetConfirmView.as_view(), name = 'confirm_password_reset'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name = 'profile_delete'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name = 'profile_change'),
    path('accounts/profile/', profile, name = 'profile'),

]