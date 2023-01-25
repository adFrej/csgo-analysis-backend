from rest_framework import serializers
from .gameModelsDto import *


class PlayerDtoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerDto
        fields = ['name', 'kills', 'assists', 'deaths', 'kd', 'killsPerRound', 'damage', 'adr', 'kast',
                  'flashedEnemies', 'flashedEnemiesDuration', 'rating']


class TeamDtoSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()

    class Meta:
        model = TeamDto
        fields = ['name', 'players']

    def get_players(self, instance):
        return PlayerDtoSerializer(instance.players, many=True).data


class TeamsDtoSerializer(serializers.ModelSerializer):
    lastTSide = TeamDtoSerializer()
    lastCTSide = TeamDtoSerializer()

    class Meta:
        model = TeamsDto
        fields = ['lastTSide', 'lastCTSide']

    def create(self, validated_data):
        teams = TeamsDto.objects.create(**validated_data)
        lastTSide_data = validated_data.pop('lastTSide')
        lastCTSide_data = validated_data.pop('lastCTSide')
        TeamDto.objects.create(teams=teams, **lastTSide_data)
        TeamDto.objects.create(teams=teams, **lastCTSide_data)
        return teams


class GameDtoSerializer(serializers.ModelSerializer):
    teams = TeamsDtoSerializer()

    class Meta:
        model = GameDto
        fields = ['id', 'name', 'createdTimestamp', 'map', 'roundsPlayed', 'teams']

    def create(self, validated_data):
        game = GameDto.objects.create(**validated_data)
        teams_data = validated_data.pop('teams')
        TeamsDto.objects.create(game=game, **teams_data)
        return game


class GameSmallDtoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameDto
        fields = ['id', 'name', 'createdTimestamp', 'map']
