from django.db import models
from .models import *
import logging

log = logging.getLogger(__name__)

player_types = [('tplayer_' + str(i + 1), i) for i in range(5)] + [('ctplayer_' + str(i + 1), i+5) for i in range(5)]
grenade_lengths = {'Smoke Grenade': 18, 'Incendiary Grenade': 7, 'Molotov': 7}  # seconds
vertigo_divider = 11680
nuke_divider = -482


def get_radar_slice(z, map_name):
    if map_name == "de_vertigo" and z < vertigo_divider:
        return 1
    if map_name == "de_nuke" and z < nuke_divider:
        return 1
    return 0


class RoundPlayerDto(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.TextField()
    team = models.TextField()
    # decoygrenade = []
    # flashbang = []
    # hegrenade = []
    # smokegrenade = []
    # activeweapon = []
    # armor = []
    equipmentvaluefreezetimeend = models.PositiveSmallIntegerField()
    # equipmentvaluefreezetimeend = []
    # eyex = []
    # eyey = []
    # eyez = []
    # firegrenades = []
    fires = []
    hasarmor = Bit1BooleanField()
    # hasbomb = []
    hasdefuse = []
    hashelmet = Bit1BooleanField()
    hp = []
    # isairborne = []
    # isalive = []
    isblinded = []
    # isbot = []
    # isdefusing = []
    # isducking = []
    # isduckinginprogress = []
    # isplanting = []
    # isreloading = []
    # isscoped = []
    # isunduckinginprogress = []
    mainweapon = []
    # ping = []
    # secondaryweapon = []
    # velocityx = []
    # velocityy = []
    # velocityz = []
    a = []
    # viewy = []
    x = []
    y = []
    # z = []
    # zoomlevel = []
    radarSlice = []

    @staticmethod
    def create(frame, player_type, player, id_, round_, map_name):
        log.debug(f"Creating round player with id: {id_} and name: {player.name}")
        player_dto = RoundPlayerDto()
        player_dto.id = id_
        player_dto.name = player.name
        player_dto.team = 'T' if id_ < 5 else 'CT'
        # player_dto.decoygrenade = list(frame.values_list(player_type + '_decoygrenade', flat=True))
        # player_dto.flashbang = list(frame.values_list(player_type + '_flashbang', flat=True))
        # player_dto.hegrenade = list(frame.values_list(player_type + '_hegrenade', flat=True))
        # player_dto.smokegrenade = list(frame.values_list(player_type + '_smokegrenade', flat=True))
        # player_dto.activeweapon = list(frame.values_list(player_type + '_activeweapon', flat=True))
        # player_dto.armor = list(frame.values_list(player_type + '_armor', flat=True)) # not used
        player_dto.equipmentvaluefreezetimeend = next(iter(frame.values(player_type + '_equipmentvaluefreezetimeend').first().values()))
        # player_dto.equipmentvaluefreezetimeend = list(frame.values_list(player_type + '_equipmentvaluefreezetimeend', flat=True))
        # player_dto.eyex = list(frame.values_list(player_type + '_eyex', flat=True))
        # player_dto.eyey = list(frame.values_list(player_type + '_eyey', flat=True))
        # player_dto.eyez = list(frame.values_list(player_type + '_eyez', flat=True))
        # player_dto.firegrenades = list(frame.values_list(player_type + '_firegrenades', flat=True))
        ticks = list(frame.values_list('tick', flat=True))
        ticks_fire = list(Weaponfire.objects.filter(matchid_id=round_.matchid_id, roundnum=round_.roundnum, playerid=player.id).values_list("tick_parsed_id", flat=True))
        player_dto.fires = [tick in ticks_fire for tick in ticks]
        player_dto.hasarmor = any([x >= 15 for x in list(frame.values_list(player_type + '_armor', flat=True))])
        # player_dto.hasbomb = list(frame.values_list(player_type + '_hasbomb', flat=True))
        player_dto.hasdefuse = list(frame.values_list(player_type + '_hasdefuse', flat=True))
        player_dto.hashelmet = any(list(frame.values_list(player_type + '_hashelmet', flat=True)))
        player_dto.hp = list(frame.values_list(player_type + '_hp', flat=True))
        # player_dto.isairborne = list(frame.values_list(player_type + '_isairborne', flat=True))
        # player_dto.isalive = list(frame.values_list(player_type + '_isalive', flat=True))
        player_dto.isblinded = list(frame.values_list(player_type + '_isblinded', flat=True))
        # player_dto.isbot = list(frame.values_list(player_type + '_isbot', flat=True))
        # player_dto.isdefusing = list(frame.values_list(player_type + '_isdefusing', flat=True))
        # player_dto.isducking = list(frame.values_list(player_type + '_isducking', flat=True))
        # player_dto.isduckinginprogress = list(frame.values_list(player_type + '_isduckinginprogress', flat=True))
        # player_dto.isplanting = list(frame.values_list(player_type + '_isplanting', flat=True))
        # player_dto.isreloading = list(frame.values_list(player_type + '_isreloading', flat=True))
        # player_dto.isscoped = list(frame.values_list(player_type + '_isscoped', flat=True))
        # player_dto.isunduckinginprogress = list(frame.values_list(player_type + '_isunduckinginprogress', flat=True))
        player_dto.mainweapon = list(frame.values_list(player_type + '_mainweapon', flat=True))
        # player_dto.ping = list(frame.values_list(player_type + '_ping', flat=True))
        # player_dto.secondaryweapon = list(frame.values_list(player_type + '_secondaryweapon', flat=True))
        # player_dto.velocityx = list(frame.values_list(player_type + '_velocityx', flat=True))
        # player_dto.velocityy = list(frame.values_list(player_type + '_velocityy', flat=True))
        # player_dto.velocityz = list(frame.values_list(player_type + '_velocityz', flat=True))
        player_dto.a = list(frame.values_list(player_type + '_viewx', flat=True))
        # player_dto.viewy = list(frame.values_list(player_type + '_viewy', flat=True))
        player_dto.x = list(frame.values_list(player_type + '_x', flat=True))
        player_dto.y = list(frame.values_list(player_type + '_y', flat=True))
        # player_dto.z = list(frame.values_list(player_type + '_y', flat=True))
        # player_dto.zoomlevel = list(frame.values_list(player_type + '_zoomlevel', flat=True))
        player_dto.radarSlice = [get_radar_slice(z, map_name) for z in list(frame.values_list(player_type + '_z', flat=True))]
        return player_dto


class RoundBombDto(models.Model):
    x = []
    y = []
    state = []
    radarSlice = []

    @staticmethod
    def create(frame, map_name):
        log.debug(f"Creating round bomb")
        round_bomb_dto = RoundBombDto()
        round_bomb_dto.x = list(frame.values_list('bomb_x', flat=True))
        round_bomb_dto.y = list(frame.values_list('bomb_y', flat=True))
        round_bomb_dto.state = list(frame.values_list('bombplanted', flat=True))
        round_bomb_dto.radarSlice = [get_radar_slice(z, map_name) for z in list(frame.values_list('bomb_z', flat=True))]
        return round_bomb_dto


class RoundGrenadeDto(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    type = models.TextField()
    start = models.IntegerField()
    end = models.IntegerField()
    radarSlice = models.SmallIntegerField()

    @staticmethod
    def create(row, start_tick, tick_rate, parse_rate, map_name):
        log.debug(f"Creating round grenade")
        round_grenade_dto = RoundGrenadeDto()
        round_grenade_dto.x = row.grenadex
        round_grenade_dto.y = row.grenadey
        round_grenade_dto.type = row.grenadetype
        round_grenade_dto.start = (row.destroyTick_parsed_id - start_tick) / parse_rate
        round_grenade_dto.end = round_grenade_dto.start + grenade_lengths.get(round_grenade_dto.type, 0) * tick_rate / parse_rate
        round_grenade_dto.end += 1 if round_grenade_dto.end == round_grenade_dto.start else 0
        round_grenade_dto.radarSlice = get_radar_slice(row.grenadez, map_name)
        return round_grenade_dto


class RoundDto(models.Model):
    roundNumber = models.PositiveSmallIntegerField()
    tName = models.TextField()
    ctName = models.TextField()
    tScore = models.PositiveSmallIntegerField()
    ctScore = models.PositiveSmallIntegerField()
    length = models.IntegerField()
    clockTime = []
    CTpredictions = []
    players = [None] * 10
    bomb = RoundBombDto()
    grenades = []

    @staticmethod
    def from_round(round_):
        log.info(f"Creating round with number: {round_.roundnum}")
        round_dto = RoundDto()
        round_dto.roundNumber = round_.roundnum
        round_dto.tName = round_.tteam
        round_dto.ctName = round_.ctteam
        round_dto.tScore = round_.tscore
        round_dto.ctScore = round_.ctscore
        frame = Frame.objects.filter(matchid_id=round_.matchid_id, roundnum=round_.roundnum)
        round_dto.length = frame.count()
        round_dto.clockTime = list(frame.values_list('clocktime', flat=True))
        round_dto.CTpredictions = list(frame.values_list('ctPrediction', flat=True))
        game = Game.objects.filter(id=round_.matchid_id).get()
        tick_rate = game.tickrate
        parse_rate = game.parserate
        map_name = game.mapname
        for i, (player_type, id_) in enumerate(player_types):
            round_dto.players[i] = RoundPlayerDto.create(
                frame, player_type, frame.select_related(player_type).first().__getattribute__(player_type), id_, round_, map_name)
                # frame[:5], player_type, frame.select_related(player_type).first().__getattribute__(player_type), id_)
        round_dto.bomb = RoundBombDto.create(frame, map_name)
        start_tick = frame.first().tick
        for grenade in Grenade.objects.filter(matchid_id=round_.matchid_id, roundnum=round_.roundnum):
            round_dto.grenades.append(RoundGrenadeDto.create(grenade, start_tick, tick_rate, parse_rate, map_name))
        return round_dto

    class Meta:
        managed = False
