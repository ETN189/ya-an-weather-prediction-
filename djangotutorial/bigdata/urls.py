from django.urls import path

from . import views

urlpatterns = [
    path("score/", views.score, name="score"),
    path("weather/", views.weather, name="weather"),
    path("ai-prediction/", views.ai_prediction, name="ai_prediction"),
    path("GetTodayWea", views.get_today_wea, name="get_today_wea"),
    path("weather-charts/meta", views.weather_charts_meta, name="weather_charts_meta"),
    path("weather-charts/refresh", views.refresh_weather_charts, name="refresh_weather_charts"),
]