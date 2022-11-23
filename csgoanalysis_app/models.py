from django.db import models
from django_mysql.models import Bit1BooleanField


class Game(models.Model):
    id = models.SmallAutoField(db_column='ID', primary_key=True)
    demoname = models.TextField(db_column='demoName', blank=True, null=True)
    matchname = models.TextField(db_column='matchName', blank=True, null=True)
    clientname = models.TextField(db_column='clientName', blank=True, null=True)
    mapname = models.TextField(db_column='mapName', blank=True, null=True)
    tickrate = models.PositiveIntegerField(db_column='tickRate', blank=True, null=True)
    playbackticks = models.PositiveIntegerField(db_column='playbackTicks', blank=True, null=True)
    parserate = models.PositiveIntegerField(db_column='parseRate', blank=True, null=True)
    createdtimestamp = models.DateTimeField(db_column='createdTimestamp', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'game'


class Round(models.Model):
    roundnum = models.PositiveSmallIntegerField(db_column='roundNum', primary_key=True)
    matchid = models.ForeignKey(Game, models.DO_NOTHING, db_column='matchID')
    starttick = models.PositiveIntegerField(db_column='startTick', blank=True, null=True)
    freezetimeendtick = models.PositiveIntegerField(db_column='freezeTimeEndTick', blank=True, null=True)
    endtick = models.PositiveIntegerField(db_column='endTick', blank=True, null=True)
    endofficialtick = models.PositiveIntegerField(db_column='endOfficialTick', blank=True, null=True)
    tscore = models.PositiveSmallIntegerField(db_column='tScore', blank=True, null=True)
    ctscore = models.PositiveSmallIntegerField(db_column='ctScore', blank=True, null=True)
    endtscore = models.PositiveSmallIntegerField(db_column='endTScore', blank=True, null=True)
    endctscore = models.PositiveSmallIntegerField(db_column='endCTScore', blank=True, null=True)
    tteam = models.TextField(db_column='tTeam', blank=True, null=True)
    ctteam = models.TextField(db_column='ctTeam', blank=True, null=True)
    winningside = models.CharField(db_column='winningSide', max_length=2, blank=True, null=True)
    winningteam = models.TextField(db_column='winningTeam', blank=True, null=True)
    losingteam = models.TextField(db_column='losingTeam', blank=True, null=True)
    roundendreason = models.TextField(db_column='roundEndReason', blank=True, null=True)
    ctfreezetimeendeqval = models.PositiveIntegerField(db_column='ctFreezeTimeEndEqVal', blank=True, null=True)
    ctroundstarteqval = models.PositiveIntegerField(db_column='ctRoundStartEqVal', blank=True, null=True)
    ctroundspendmoney = models.PositiveIntegerField(db_column='ctRoundSpendMoney', blank=True, null=True)
    ctbuytype = models.TextField(db_column='ctBuyType', blank=True, null=True)
    tfreezetimeendeqval = models.PositiveIntegerField(db_column='tFreezeTimeEndEqVal', blank=True, null=True)
    troundstarteqval = models.PositiveIntegerField(db_column='tRoundStartEqVal', blank=True, null=True)
    troundspendmoney = models.PositiveIntegerField(db_column='tRoundSpendMoney', blank=True, null=True)
    tbuytype = models.TextField(db_column='tBuyType', blank=True, null=True)
    endtickcorrect = models.PositiveIntegerField(db_column='endTickCorrect', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'round'
        unique_together = (('matchid', 'roundnum'),)


class Player(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    steamid = models.CharField(db_column='steamID', max_length=17, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    teamname = models.TextField(db_column='teamName', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'player'


class Frame(models.Model):
    matchid = models.ForeignKey('Game', models.DO_NOTHING, db_column='matchID')
    roundnum = models.PositiveSmallIntegerField(db_column='roundNum')
    tick = models.PositiveIntegerField(primary_key=True)
    ctplayer_1 = models.ForeignKey('Player', models.DO_NOTHING, related_name='ct1', db_column='ctPlayer_1_ID', blank=True, null=True)
    ctplayer_2 = models.ForeignKey('Player', models.DO_NOTHING, related_name='ct2', db_column='ctPlayer_2_ID', blank=True, null=True)
    ctplayer_3 = models.ForeignKey('Player', models.DO_NOTHING, related_name='ct3', db_column='ctPlayer_3_ID', blank=True, null=True)
    ctplayer_4 = models.ForeignKey('Player', models.DO_NOTHING, related_name='ct4', db_column='ctPlayer_4_ID', blank=True, null=True)
    ctplayer_5 = models.ForeignKey('Player', models.DO_NOTHING, related_name='ct5', db_column='ctPlayer_5_ID', blank=True, null=True)
    tplayer_1 = models.ForeignKey('Player', models.DO_NOTHING, related_name='t1', db_column='tPlayer_1_ID', blank=True, null=True)
    tplayer_2 = models.ForeignKey('Player', models.DO_NOTHING, related_name='t2', db_column='tPlayer_2_ID', blank=True, null=True)
    tplayer_3 = models.ForeignKey('Player', models.DO_NOTHING, related_name='t3', db_column='tPlayer_3_ID', blank=True, null=True)
    tplayer_4 = models.ForeignKey('Player', models.DO_NOTHING, related_name='t4', db_column='tPlayer_4_ID', blank=True, null=True)
    tplayer_5 = models.ForeignKey('Player', models.DO_NOTHING, related_name='t5', db_column='tPlayer_5_ID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'frame'
        unique_together = (('matchid', 'tick'),)
