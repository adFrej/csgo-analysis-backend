from rest_framework import serializers
from .models import *
from .roundModelsDto import *


class RoundPlayerRatingDtoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundPlayerRatingDto
        fields = ['type', 'gainValue']


class RoundPlayerDtoSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()

    class Meta:
        model = RoundPlayerDto
        fields = ['id', 'name', 'team', 'equipmentValueFreezetimeEnd', 'fires', 'hasArmor', 'hasDef', 'hasHelmet',
                  'hp', 'isBlinded', 'mainWeapon', 'a', 'x', 'y', 'radarSlice', 'sumRating', 'ratings']
        # fields = ['id', 'name', 'team', 'decoygrenade', 'flashbang', 'hegrenade', 'smokegrenade', 'activeweapon',
        #           'equipmentvaluefreezetimeend', 'eyex', 'eyey', 'eyez', 'firegrenades', 'hasarmor', 'hasbomb',
        #           'hasdefuse', 'hashelmet', 'hp', 'isairborne', 'isalive', 'isblinded', 'isbot', 'isdefusing',
        #           'isducking', 'isduckinginprogress', 'isplanting', 'isreloading', 'isscoped', 'isunduckinginprogress',
        #           'mainweapon', 'ping', 'secondaryweapon', 'velocityx', 'velocityy', 'velocityz', 'viewx', 'viewy',
        #           'x', 'y', 'z', 'zoomlevel']

    def get_ratings(self, instance):
        return RoundPlayerRatingDtoSerializer(instance.ratings, many=True).data


class RoundBombDtoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundBombDto
        fields = ['x', 'y', 'state', 'radarSlice']


class RoundGrenadeDtoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundGrenadeDto
        fields = ['x', 'y', 'type', 'start', 'end', 'radarSlice']


class RoundDtoSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()
    bomb = serializers.SerializerMethodField()
    grenades = serializers.SerializerMethodField()

    class Meta:
        model = RoundDto
        fields = ['roundNumber', 'winningSide', 'tName', 'ctName', 'tScore', 'ctScore', 'length', 'winningCondition',
                  'winningMoment', 'clockTime', 'importantMoments', 'CTpredictions', 'players', 'bomb', 'grenades']

    def get_players(self, instance):
        return RoundPlayerDtoSerializer(instance.players, many=True).data

    def get_bomb(self, instance):
        return RoundBombDtoSerializer(instance.bomb).data

    def get_grenades(self, instance):
        return RoundGrenadeDtoSerializer(instance.grenades, many=True).data
