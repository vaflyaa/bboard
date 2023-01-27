from django.urls import path

from .views import bbs, bb_detail

urlpatterns = [
    path('bbs/<int:pk>/', bb_detail),
    path('bbs/', bbs),
]