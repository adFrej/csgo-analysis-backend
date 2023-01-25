from django.db import models
from .models import *
import logging

log = logging.getLogger(__name__)


class PlayerDto(models.Model):
    name = models.TextField()
    kills = models.IntegerField()
    assists = models.IntegerField()
    deaths = models.IntegerField()
    kd = models.FloatField()
    killsPerRound = models.FloatField()
    damage = models.IntegerField()
    adr = models.FloatField()
    kast = models.FloatField()
    flashedEnemies = models.IntegerField()
    flashedEnemiesDuration = models.FloatField()
    rating = models.FloatField()

    @staticmethod
    def create(player, game_id, n_rounds, kills, damages, flashes):
        log.debug(f"Creating game player with id: {player.id} and name: {player.name}")
        player_dto = PlayerDto()
        player_dto.name = player.name
        player_dto.kills = kills.filter(attackerid=player.id).count()
        player_dto.assists = kills.filter(assisterid=player.id).count()
        player_dto.deaths = Elimination.objects.filter(matchid_id=game_id, victimid=player.id).count()
        player_dto.kd = player_dto.kills / (player_dto.deaths if player_dto.deaths != 0 else 1)
        player_dto.killsPerRound = player_dto.kills / n_rounds
        try:
            player_dto.damage = damages.filter(attackerid=player.id).get()['sumDmg']
        except models.ObjectDoesNotExist:
            player_dto.damage = 0
        player_dto.adr = player_dto.damage / n_rounds
        rounds_kill = list(kills.filter(attackerid=player.id).values_list('roundnum', flat=True))
        rounds_assist = list(kills.filter(assisterid=player.id).values_list('roundnum', flat=True))
        rounds_deaths = list(Elimination.objects.filter(matchid_id=game_id, victimid=player.id).values_list('roundnum', flat=True))
        rounds_traded = list(kills.filter(victimid=player.id, istrade=True).values_list('roundnum', flat=True))
        rounds_kast = [r for r in range(1, n_rounds+1) if r not in rounds_deaths or r in rounds_kill or r in rounds_assist or r in rounds_traded]
        player_dto.kast = len(rounds_kast) / n_rounds * 100
        try:
            flash = flashes.filter(attackerid=player.id).get()
        except models.ObjectDoesNotExist:
            flash = {'countFlash': 0, 'sumDuration': 0.0}
        player_dto.flashedEnemies = flash['countFlash']
        player_dto.flashedEnemiesDuration = flash['sumDuration']
        player_dto.rating = Rating.objects.filter(matchid_id=game_id, playerid=player.id)\
            .aggregate(rating=models.Sum('gainvalue'))['rating'] / n_rounds
        return player_dto

    class Meta:
        managed = False


class TeamDto(models.Model):
    name = models.TextField()
    players = []

    @staticmethod
    def create(team_name, game_id, n_rounds, player_types, kills, damages, flashes):
        frame = Frame.objects.filter(matchid_id=game_id)
        team_dto = TeamDto()
        team_dto.name = team_name
        team_dto.players = [PlayerDto.create(frame.select_related(player_type).first().
                            __getattribute__(player_type), game_id, n_rounds, kills, damages, flashes)
                            for player_type in player_types]
        return team_dto

    class Meta:
        managed = False


class TeamsDto(models.Model):
    lastTSide = TeamDto()
    lastCTSide = TeamDto()

    @staticmethod
    def create(rounds, game_id, n_rounds):
        teams_dto = TeamsDto()
        damages = Damage.objects.filter(matchid_id=game_id, isfriendlyfire=False).values('attackerid')\
            .order_by('attackerid').annotate(sumDmg=models.Sum('hpdamagetaken'))
        kills = Elimination.objects.filter(matchid_id=game_id, isteamkill=False)
        flashes = Flash.objects.filter(matchid_id=game_id).values('attackerid').order_by('attackerid')\
            .annotate(countFlash=models.Count('attackerid'), sumDuration=models.Sum('flashduration'))
        teams_dto.lastCTSide = TeamDto.create(rounds.order_by('roundnum').first().tteam,
                                              game_id, n_rounds, ['tplayer_'+str(i+1) for i in range(5)], kills, damages, flashes)
        teams_dto.lastTSide = TeamDto.create(rounds.order_by('roundnum').first().ctteam,
                                             game_id, n_rounds, ['ctplayer_'+str(i+1) for i in range(5)], kills, damages, flashes)
        return teams_dto

    class Meta:
        managed = False


class GameDto(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.TextField()
    createdTimestamp = models.DateTimeField()
    map = models.TextField()
    roundsPlayed = models.PositiveSmallIntegerField()
    teams = TeamsDto()

    @staticmethod
    def from_game(game):
        log.info(f"Creating game with id: {game.id}")
        rounds = Round.objects.filter(matchid_id=game.id)
        game_dto = GameDto()
        game_dto.id = game.id
        game_dto.name = game.matchname
        game_dto.createdTimestamp = game.createdtimestamp
        game_dto.map = game.mapname
        game_dto.roundsPlayed = rounds.count()
        game_dto.teams = TeamsDto.create(rounds, game.id, game_dto.roundsPlayed)
        return game_dto

    class Meta:
        managed = False


class GameSmallDto(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.TextField()
    createdTimestamp = models.DateTimeField()
    map = models.TextField()

    @staticmethod
    def from_game(game):
        log.debug(f"Creating small game with id: {game.id}")
        game_dto = GameSmallDto()
        game_dto.id = game.id
        game_dto.name = game.matchname
        game_dto.createdTimestamp = game.createdtimestamp
        game_dto.map = game.mapname
        return game_dto

    class Meta:
        managed = False
