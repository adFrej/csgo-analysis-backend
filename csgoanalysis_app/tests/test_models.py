from django.test import TestCase
from unittest.mock import patch
from django_mock_queries.query import MockSet, MockModel

from ..models import *
from ..gameModelsDto import *
from ..gameSerializers import *
from ..roundModelsDto import *
from ..roundSerializers import *


class ModelsTests(TestCase):
    game = Game(id=1, matchname="test_name", createdtimestamp="2023-01-15T15:16:17", mapname="test_map", parserate=32,
                tickrate=128)

    mock_game = MockSet(game)
    patch_game = patch("csgoanalysis_app.models.Game.objects", mock_game)

    player_1 = Player(id=1, name="test_player1")
    player_2 = Player(id=2, name="test_player2")
    player_3 = Player(id=3, name="test_player3")
    player_4 = Player(id=4, name="test_player4")
    player_5 = Player(id=5, name="test_player5")
    player_6 = Player(id=6, name="test_player6")
    player_7 = Player(id=7, name="test_player7")
    player_8 = Player(id=8, name="test_player8")
    player_9 = Player(id=9, name="test_player9")
    player_10 = Player(id=10, name="test_player10")

    frame = Frame(matchid_id=game.id, ctplayer_1=player_1, ctplayer_2=player_2, ctplayer_3=player_3,
                  ctplayer_4=player_4, ctplayer_5=player_5, tplayer_1=player_6,
                  tplayer_2=player_7, tplayer_3=player_8, tplayer_4=player_9,
                  tplayer_5=player_10, clocktime="01:50", roundnum=1, tick=64, bombplanted=False, ctPrediction=0,
                  **{f"ctplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                  **{f"tplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                  **{f"ctplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                  **{f"tplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                  **{f"ctplayer_{i}_hasdefuse": True for i in range(1, 6)},
                  **{f"tplayer_{i}_hasdefuse": False for i in range(1, 6)},
                  **{f"ctplayer_{i}_hashelmet": False for i in range(1, 6)},
                  **{f"tplayer_{i}_hashelmet": True for i in range(1, 6)},
                  **{f"ctplayer_{i}_hp": 100 for i in range(1, 6)},
                  **{f"tplayer_{i}_hp": 90 for i in range(1, 6)},
                  **{f"ctplayer_{i}_isblinded": False for i in range(1, 6)},
                  **{f"tplayer_{i}_isblinded": True for i in range(1, 6)},
                  **{f"ctplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                  **{f"tplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                  **{f"ctplayer_{i}_viewx": 50 for i in range(1, 6)},
                  **{f"tplayer_{i}_viewx": 60 for i in range(1, 6)},
                  **{f"ctplayer_{i}_x": 1000 for i in range(1, 6)},
                  **{f"tplayer_{i}_x": 900 for i in range(1, 6)},
                  **{f"ctplayer_{i}_y": 800 for i in range(1, 6)},
                  **{f"tplayer_{i}_y": 700 for i in range(1, 6)})

    mock_eliminations = MockSet(
        Elimination(matchid_id=frame.matchid_id, attackerid=1, assisterid=2, victimid=6, isteamkill=False),
        Elimination(matchid_id=frame.matchid_id, attackerid=1, assisterid=3, victimid=7, isteamkill=False),
        Elimination(matchid_id=frame.matchid_id, attackerid=2, assisterid=1, victimid=10, isteamkill=False),
        Elimination(matchid_id=frame.matchid_id, attackerid=8, assisterid=9, victimid=1, isteamkill=False),
    )
    patch_eliminations = patch("csgoanalysis_app.models.Elimination.objects", mock_eliminations)

    mock_damages = MockSet(
        Damage(matchid_id=frame.matchid_id, attackerid=1, isfriendlyfire=False, hpdamagetaken=50),
        Damage(matchid_id=frame.matchid_id, attackerid=1, isfriendlyfire=False, hpdamagetaken=50),
        Damage(matchid_id=frame.matchid_id, attackerid=1, isfriendlyfire=False, hpdamagetaken=50),
        Damage(matchid_id=frame.matchid_id, attackerid=2, isfriendlyfire=False, hpdamagetaken=50),
    )
    patch_damages = patch("csgoanalysis_app.models.Damage.objects", mock_damages)

    mock_damages_agg = MockSet(
        MockModel(matchid_id=frame.matchid_id, attackerid=1, sumDmg=150),
        MockModel(matchid_id=frame.matchid_id, attackerid=2, sumDmg=50),
    )

    mock_flashes = MockSet(
        Flash(matchid_id=frame.matchid_id, attackerid=1, flashduration=3.0),
        Flash(matchid_id=frame.matchid_id, attackerid=1, flashduration=3.0),
        Flash(matchid_id=frame.matchid_id, attackerid=1, flashduration=3.0),
        Flash(matchid_id=frame.matchid_id, attackerid=2, flashduration=3.0),
    )
    patch_flashes = patch("csgoanalysis_app.models.Flash.objects", mock_flashes)

    mock_flashes_agg = MockSet(
        MockModel(matchid_id=frame.matchid_id, attackerid=1, countFlash=3, sumDuration=9.0),
        MockModel(matchid_id=frame.matchid_id, attackerid=2, countFlash=1, sumDuration=3.0),
    )

    round = Round(matchid_id=game.id, roundnum=frame.roundnum, tteam="test_tteam", ctteam="test_ctteam", tscore=0,
                  ctscore=0, roundendreason="TerroristsWin", endtickcorrect=100)

    mock_rounds = MockSet(
        round,
        Round(matchid_id=game.id, roundnum=2, tteam="test_tteam", ctteam="test_ctteam"),
        Round(matchid_id=game.id, roundnum=3, tteam="test_tteam", ctteam="test_ctteam"),
        Round(matchid_id=game.id, roundnum=4, tteam="test_tteam", ctteam="test_ctteam"),
        Round(matchid_id=game.id, roundnum=5, tteam="test_tteam", ctteam="test_ctteam"),
    )
    patch_rounds = patch("csgoanalysis_app.models.Round.objects", mock_rounds)

    mock_frame = MockSet(frame,
                         Frame(matchid_id=game.id, ctplayer_1=player_1, ctplayer_2=player_2, ctplayer_3=player_3,
                               ctplayer_4=player_4, ctplayer_5=player_5, tplayer_1=player_6,
                               tplayer_2=player_7, tplayer_3=player_8, tplayer_4=player_9,
                               tplayer_5=player_10, clocktime="01:50", roundnum=1, tick=96, bombplanted=True,
                               ctPrediction=1,
                               **{f"ctplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                               **{f"tplayer_{i}_equipmentvaluefreezetimeend": i * 1000 for i in range(1, 6)},
                               **{f"ctplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                               **{f"tplayer_{i}_armor": (i % 2) * 100 for i in range(1, 6)},
                               **{f"ctplayer_{i}_hasdefuse": True for i in range(1, 6)},
                               **{f"tplayer_{i}_hasdefuse": False for i in range(1, 6)},
                               **{f"ctplayer_{i}_hashelmet": False for i in range(1, 6)},
                               **{f"tplayer_{i}_hashelmet": True for i in range(1, 6)},
                               **{f"ctplayer_{i}_hp": 100 for i in range(1, 6)},
                               **{f"tplayer_{i}_hp": 90 for i in range(1, 6)},
                               **{f"ctplayer_{i}_isblinded": False for i in range(1, 6)},
                               **{f"tplayer_{i}_isblinded": True for i in range(1, 6)},
                               **{f"ctplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                               **{f"tplayer_{i}_mainweapon": "test_weapon" for i in range(1, 6)},
                               **{f"ctplayer_{i}_viewx": 50 for i in range(1, 6)},
                               **{f"tplayer_{i}_viewx": 60 for i in range(1, 6)},
                               **{f"ctplayer_{i}_x": 1000 for i in range(1, 6)},
                               **{f"tplayer_{i}_x": 900 for i in range(1, 6)},
                               **{f"ctplayer_{i}_y": 800 for i in range(1, 6)},
                               **{f"tplayer_{i}_y": 700 for i in range(1, 6)}))
    patch_frame = patch("csgoanalysis_app.models.Frame.objects", mock_frame)

    mock_weaponfire = MockSet(
        Weaponfire(matchid_id=game.id, roundnum=round.roundnum, playerid=player_6.id, tick_parsed_id=frame.tick))
    patch_weaponfire = patch("csgoanalysis_app.models.Weaponfire.objects", mock_weaponfire)

    mock_rating = MockSet(
        Rating(matchid_id=game.id, roundnum=round.roundnum, playerid=player_1.id, tick_id=frame.tick, gainvalue=10.0,
               type="kill"),
        Rating(matchid_id=game.id, roundnum=round.roundnum, playerid=player_1.id, tick_id=frame.tick, gainvalue=10.0,
               type="kill"),
        Rating(matchid_id=game.id, roundnum=round.roundnum, playerid=player_1.id, tick_id=frame.tick, gainvalue=10.0,
               type="kill"),
        Rating(matchid_id=game.id, roundnum=round.roundnum, playerid=player_2.id, tick_id=frame.tick, gainvalue=10.0,
               type="kill"),
    )
    patch_rating = patch("csgoanalysis_app.models.Rating.objects", mock_rating)

    mock_grenades = MockSet(
        Grenade(matchid_id=game.id, roundnum=round.roundnum, throwerid=player_1.id, destroyTick_parsed_id=frame.tick,
                grenadez=1000),
    )
    patch_grenades = patch("csgoanalysis_app.models.Grenade.objects", mock_grenades)

    @patch_eliminations
    @patch_rating
    @patch("csgoanalysis_app.models.Damage.objects.filter")
    @patch("csgoanalysis_app.models.Flash.objects.filter")
    def test_player_dto_create(self, mock_flashes, mock_damages):
        mock_damages.return_value.values.return_value.order_by.return_value.annotate.return_value = self.mock_damages_agg
        mock_flashes.return_value.values.return_value.order_by.return_value.annotate.return_value = self.mock_flashes_agg

        result = PlayerDto.create(self.player_1, self.frame.matchid_id, self.mock_rounds.count(),
                                  Elimination.objects.filter(matchid_id=self.frame.matchid_id, isteamkill=False),
                                  Damage.objects.filter(matchid_id=self.frame.matchid_id, isfriendlyfire=False).values(
                                      'attackerid')
                                  .order_by('attackerid').annotate(sumDmg=models.Sum('hpdamagetaken')),
                                  Flash.objects.filter(matchid_id=self.frame.matchid_id).values('attackerid').order_by(
                                      'attackerid') \
                                  .annotate(countFlash=models.Count('attackerid'),
                                            sumDuration=models.Sum('flashduration')))

        self.assertEqual(result.name, self.player_1.name)
        self.assertEqual(result.kills, 2)
        self.assertEqual(result.assists, 1)
        self.assertEqual(result.deaths, 1)
        self.assertEqual(result.damage, 150)
        self.assertEqual(result.flashedEnemies, 3)
        self.assertEqual(result.flashedEnemiesDuration, 9)
        self.assertEqual(result.rating, 6)

    @patch_rounds
    @patch_frame
    @patch_eliminations
    @patch_rating
    @patch("csgoanalysis_app.models.Damage.objects.filter")
    @patch("csgoanalysis_app.models.Flash.objects.filter")
    def test_game_dto_from_game(self, mock_flashes, mock_damages):
        mock_damages.return_value.values.return_value.order_by.return_value.annotate.return_value = self.mock_damages_agg
        mock_flashes.return_value.values.return_value.order_by.return_value.annotate.return_value = self.mock_flashes_agg

        result = GameDto.from_game(self.game)

        self.assertEqual(result.map, self.game.mapname)
        self.assertEqual(result.roundsPlayed, 5)
        self.assertEqual(result.teams.lastTSide.name, "test_ctteam")
        self.assertEqual(result.teams.lastCTSide.name, "test_tteam")
        self.assertEqual(result.teams.lastTSide.players[0].name, self.player_1.name)
        self.assertEqual(result.teams.lastCTSide.players[0].name, self.player_6.name)
        self.assertEqual(result.teams.lastTSide.players[1].name, self.player_2.name)
        self.assertEqual(result.teams.lastCTSide.players[1].name, self.player_7.name)

    @patch_frame
    @patch_game
    @patch_weaponfire
    @patch_rating
    @patch_grenades
    def test_round_dto_from_round(self):
        result = RoundDto.from_round(self.round)

        self.assertEqual(result.roundNumber, self.round.roundnum)
        self.assertEqual(result.tName, self.round.tteam)
        self.assertEqual(result.ctName, self.round.ctteam)
        self.assertEqual(result.tScore, self.round.tscore)
        self.assertEqual(result.ctScore, self.round.ctscore)
        self.assertEqual(result.length, 2)
        self.assertEqual(result.winningCondition, "elimination")
        self.assertEqual(result.winningMoment, 2)
        self.assertEqual(result.clockTime, ["01:50"] * 2)
        self.assertEqual(result.CTpredictions, [0, 1])
        self.assertEqual(result.players[0].id, 0)
        self.assertEqual(result.players[0].name, "test_player6")
        self.assertEqual(result.players[0].team, "T")
        self.assertEqual(result.players[0].equipmentValueFreezetimeEnd, 1000)
        self.assertEqual(result.players[0].fires, [True, False])
        self.assertEqual(result.players[0].hasArmor, True)
        self.assertEqual(result.players[0].hasDef, [False] * 2)
        self.assertEqual(result.players[0].hasHelmet, True)
        self.assertEqual(result.players[0].hp, [90] * 2)
        self.assertEqual(result.players[0].isBlinded, [True] * 2)
        self.assertEqual(result.players[0].mainWeapon, ["test_weapon"] * 2)
        self.assertEqual(result.players[0].a, [60] * 2)
        self.assertEqual(result.players[0].x, [900] * 2)
        self.assertEqual(result.players[0].y, [700] * 2)
        self.assertEqual(result.grenades[0].start, 0)
        self.assertEqual(result.grenades[0].end, 1)
