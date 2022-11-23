from django.db import models
from .models import *


class PlayerDto(models.Model):
    name = models.TextField
    kills = models.IntegerField
    assists = models.IntegerField
    deaths = models.IntegerField

    @staticmethod
    def create(player_name):
        player_dto = PlayerDto()
        player_dto.name = player_name
        player_dto.kills = 3
        player_dto.assists = 2
        player_dto.deaths = 1
        return player_dto

    class Meta:
        managed = False


class TeamDto(models.Model):
    name = models.TextField
    players = []

    @staticmethod
    def create(team_name, game_id, player_types):
        team_dto = TeamDto()
        team_dto.name = team_name
        team_dto.players = [PlayerDto.create(Frame.objects.filter(matchid=game_id).select_related(player_type).first().
                            __getattribute__(player_type).name) for player_type in player_types]
        return team_dto

    class Meta:
        managed = False


class TeamsDto(models.Model):

    @staticmethod
    def create(game_id):
        teams_dto = TeamsDto()
        teams_dto.lastTSide = TeamDto.create(Round.objects.filter(matchid=game_id).order_by('roundnum').last().tteam,
                                             game_id, ['tplayer_'+str(i+1) for i in range(5)])
        teams_dto.lastCTSide = TeamDto.create(Round.objects.filter(matchid=game_id).order_by('roundnum').last().ctteam,
                                              game_id, ['ctplayer_'+str(i+1) for i in range(5)])
        return teams_dto

    class Meta:
        managed = False


class GameDto(models.Model):
    map = models.TextField
    roundsPlayed = models.IntegerField

    @staticmethod
    def from_game(game):
        game_dto = GameDto()
        game_dto.map = game.mapname
        game_dto.roundsPlayed = Round.objects.filter(matchid=game.id).count()
        game_dto.teams = TeamsDto.create(game.id)
        return game_dto

    class Meta:
        managed = False
