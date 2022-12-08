from django.db import models
from .models import *
import logging

log = logging.getLogger(__name__)


class PlayerDto(models.Model):
    name = models.TextField()
    kills = models.IntegerField()
    assists = models.IntegerField()
    deaths = models.IntegerField()

    @staticmethod
    def create(player, game_id):
        log.debug(f"Creating game player with id: {player.id} and name: {player.name}")
        elimination = Elimination.objects
        player_dto = PlayerDto()
        player_dto.name = player.name
        player_dto.kills = elimination.filter(matchid_id=game_id, attackerid=player.id).count()
        player_dto.assists = elimination.filter(matchid_id=game_id, assisterid=player.id).count()
        player_dto.deaths = elimination.filter(matchid_id=game_id, victimid=player.id).count()
        return player_dto

    class Meta:
        managed = False


class TeamDto(models.Model):
    name = models.TextField()
    players = []

    @staticmethod
    def create(team_name, game_id, player_types):
        frame = Frame.objects.filter(matchid_id=game_id)
        team_dto = TeamDto()
        team_dto.name = team_name
        team_dto.players = [PlayerDto.create(frame.select_related(player_type).first().
                            __getattribute__(player_type), game_id) for player_type in player_types]
        return team_dto

    class Meta:
        managed = False


class TeamsDto(models.Model):
    lastTSide = TeamDto()
    lastCTSide = TeamDto()

    @staticmethod
    def create(rounds, game_id):
        teams_dto = TeamsDto()
        teams_dto.lastCTSide = TeamDto.create(rounds.order_by('roundnum').first().tteam,
                                             game_id, ['tplayer_'+str(i+1) for i in range(5)])
        teams_dto.lastTSide = TeamDto.create(rounds.order_by('roundnum').first().ctteam,
                                              game_id, ['ctplayer_'+str(i+1) for i in range(5)])
        return teams_dto

    class Meta:
        managed = False


class GameDto(models.Model):
    map = models.TextField()
    roundsPlayed = models.PositiveSmallIntegerField()
    teams = TeamsDto()

    @staticmethod
    def from_game(game):
        log.info(f"Creating game with id: {game.id}")
        rounds = Round.objects.filter(matchid_id=game.id)
        game_dto = GameDto()
        game_dto.map = game.mapname
        game_dto.roundsPlayed = rounds.count()
        game_dto.teams = TeamsDto.create(rounds, game.id)
        return game_dto

    class Meta:
        managed = False
