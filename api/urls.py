from django.urls import path

from .views import bbs, bb_detail, rubrics

urlpatterns = [
    path('bbs/<int:pk>/', bb_detail),
    path('bbs/', bbs),
    path('rubrics/', rubrics)
]