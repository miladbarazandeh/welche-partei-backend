from django.urls import path

from . import views

urlpatterns = [
    path("countries/", views.countries),
    path("countries/<slug:country>/config/", views.country_config),
    path("countries/<slug:country>/politicians/random/", views.random_politician),
    path("countries/<slug:country>/politicians/search/", views.politician_search),
    path(
        "countries/<slug:country>/politicians/<slug:reference>/stats/",
        views.politician_stats,
    ),
    path("countries/<slug:country>/answers/", views.submit_answer),
    path("countries/<slug:country>/stats/", views.stats),
    path("countries/<slug:country>/session/stats/", views.session_stats),
    path("countries/<slug:country>/parties/", views.parties),
    path("countries/<slug:country>/global-stats/", views.global_stats),
]
