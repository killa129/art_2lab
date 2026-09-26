from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("painting_detail/<str:id>/", views.painting_detail, name="painting_detail"),
    path("set_theme/", views.set_theme, name="set_theme"),
]