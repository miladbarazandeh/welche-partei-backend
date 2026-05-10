from django.urls import path

from . import views

urlpatterns = [
    path("politicians/random/", views.random_politician),
    path("politicians/search/", views.politician_search),
    path("politicians/<slug:reference>/stats/", views.politician_stats),
    path("answers/", views.submit_answer),
    path("stats/", views.stats),
    path("session/stats/", views.session_stats),
    path("parties/", views.parties),
    path("global-stats/", views.global_stats),
]
