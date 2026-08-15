from django.urls import path

from . import views

urlpatterns = [
    path("data/", views.quiz_data),
    path("analytics/", views.analytics),
    path("session/", views.quiz_session_get),
    path("session/save/", views.quiz_session),
]
