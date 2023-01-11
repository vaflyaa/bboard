from django.urls import path

from .views import index, other_page, profile, BBLoginView, BBLogout, ChangeUserInfoView

app_name = 'main'
urlpatterns = [
    path('<str:page>/', other_page, name = 'other'),
    path('', index, name='index'),
    path('accounts/login/', BBLoginView.as_view(), name = 'login'),
    path('accounts/logout/', BBLogout.as_view(), name='logout'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name = 'profile_change'),
    path('accounts/profile/', profile, name = 'profile'),

]