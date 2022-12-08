from rest_framework import serializers
from .models import *
from .roundModelsDto import *


class RoundPlayerDtoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundPlayerDto
        fields = ['id', 'name', 'team', 'equipmentvaluefreezetimeend', 'fires', 'hasarmor', 'hasdefuse', 'hashelmet',
                  'hp', 'isblinded', 'mainweapon', 'viewx', 'x', 'y']
        # fields = ['id', 'name', 'team', 'decoygrenade', 'flashbang', 'hegrenade', 'smokegrenade', 'activeweapon',
        #           'equipmentvaluefreezetimeend', 'eyex', 'eyey', 'eyez', 'firegrenades', 'hasarmor', 'hasbomb',
        #           'hasdefuse', 'hashelmet', 'hp', 'isairborne', 'isalive', 'isblinded', 'isbot', 'isdefusing',
        #           'isducking', 'isduckinginprogress', 'isplanting', 'isreloading', 'isscoped', 'isunduckinginprogress',
        #           'mainweapon', 'ping', 'secondaryweapon', 'velocityx', 'velocityy', 'velocityz', 'viewx', 'viewy',
        #           'x', 'y', 'z', 'zoomlevel']


class RoundDtoSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()

    class Meta:
        model = RoundDto
        fields = ['roundNumber', 'tName', 'ctName', 'tScore', 'ctScore', 'length', 'clockTime', 'CTpredictions', 'players']

    def get_players(self, instance):
        return RoundPlayerDtoSerializer(instance.players, many=True).data
