from django.urls import path

from . import views

app_name = 'csgoanalysis_app'
urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('game/', views.get_games, name='get_games'),
    path('game/<int:game_id>/', views.get_game, name='get_game'),
    path('game/<int:game_id>/round/', views.get_rounds, name='get_rounds'),
    path('game/<int:game_id>/round/<int:round_id>/', views.get_round, name='get_round'),
    path('upload/', views.upload_file, name='upload_file'),
    path('upload/<str:name>/', views.upload_file, name='upload_file_name'),
]